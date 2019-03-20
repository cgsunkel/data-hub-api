from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django_pglocks import advisory_lock

from datahub.search.apps import get_search_app, get_search_app_by_model, get_search_apps
from datahub.search.bulk_sync import sync_app
from datahub.search.migrate_utils import resync_after_migrate


logger = get_task_logger(__name__)


@shared_task(acks_late=True, priority=9)
def sync_all_models():
    """
    Task that starts sub-tasks to sync all models to Elasticsearch.

    acks_late is set to True so that the task restarts if interrupted.

    priority is set to the lowest priority (for Redis, 0 is the highest priority).
    """
    for search_app in get_search_apps():
        sync_model.apply_async(
            args=(search_app.name,),
        )


@shared_task(acks_late=True, priority=9, queue='long-running')
def sync_model(search_app_name):
    """
    Task that syncs a single model to Elasticsearch.

    acks_late is set to True so that the task restarts if interrupted.

    priority is set to the lowest priority (for Redis, 0 is the highest priority).
    """
    search_app = get_search_app(search_app_name)
    sync_app(search_app)


@shared_task(acks_late=True, max_retries=15, autoretry_for=(Exception,), retry_backoff=1)
def sync_object_task(search_app_name, pk):
    """
    Syncs a single object to Elasticsearch.

    If an error occurs, the task will be automatically retried with an exponential back-off.
    The wait between attempts is approximately 2 ** attempt_num seconds (with some jitter
    added).

    This task is named sync_object_task to avoid a conflict with sync_object.
    """
    from datahub.search.sync_object import sync_object

    search_app = get_search_app(search_app_name)
    sync_object(search_app, pk)


@shared_task(
    bind=True,
    acks_late=True,
    max_retries=15,
    priority=6,
    autoretry_for=(Exception,),
    retry_backoff=1,
)
def sync_related_objects_task(
    self,
    related_model_label,
    related_obj_pk,
    related_obj_field_name,
    related_obj_filter=None,
):
    """
    Syncs objects related to another object via a specified field.

    For example, this task would sync the interactions of a company if given the following
    arguments:
        related_model_label='company.Company'
        related_obj_pk=company.pk
        related_obj_field_name='interactions'

    Note that a lower priority (higher number) is used for syncing related objects, as syncing
    them is less important than syncing the primary object that was modified.

    If an error occurs, the task will be automatically retried with an exponential back-off.
    The wait between attempts is approximately 2 ** attempt_num seconds (with some jitter
    added).
    """
    related_model = apps.get_model(related_model_label)
    related_obj = related_model.objects.get(pk=related_obj_pk)
    manager = getattr(related_obj, related_obj_field_name)
    if related_obj_filter:
        manager = manager.filter(**related_obj_filter)
    queryset = manager.values_list('pk', flat=True)
    search_app = get_search_app_by_model(manager.model)

    for pk in queryset:
        sync_object_task.apply_async(args=(search_app.name, pk), priority=self.priority)


@shared_task(
    bind=True,
    acks_late=True,
    priority=7,
    max_retries=5,
    default_retry_delay=60,
    queue='long-running',
)
def complete_model_migration(self, search_app_name, new_mapping_hash):
    """
    Completes a migration by performing a full resync, updating aliases and removing old indices.
    """
    search_app = get_search_app(search_app_name)
    if search_app.es_model.get_target_mapping_hash() != new_mapping_hash:
        warning_message = f"""Unexpected target mapping hash. This indicates that the task was \
generated by either a newer or an older version of the app. This could happen during a blue-green \
deployment where a new app instance creates the task and it's picked up by an old Celery instance.

Rescheduling the {search_app_name} search app migration to attempt to resolve the conflict...
"""
        logger.warning(warning_message)
        raise self.retry()

    with advisory_lock(f'leeloo-resync_after_migrate-{search_app_name}', wait=False) as lock_held:
        if not lock_held:
            logger.warning(
                f'Another complete_model_migration task is in progress for the {search_app_name} '
                f'search app. Aborting...',
            )
            return

        resync_after_migrate(search_app)
