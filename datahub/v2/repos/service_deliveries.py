import colander
from django.utils import encoding

from datahub.interaction.models import ServiceDelivery, ServiceOffer
from datahub.v2.exceptions import RepoDataValidation
from datahub.v2.schemas.service_deliveries import ServiceDeliverySchema

from . import utils


class ServiceDeliveryDatabaseRepo:
    """DB repo."""

    def __init__(self, config=None):
        """Initialise the repo using the config."""
        self.model_class = ServiceDelivery
        self.schema_class = ServiceDeliverySchema
        self.config = config
        self.url_builder = config['url_builder']

    def validate(self, data):
        """Validate the data against the schema, raising DRF friendly validation errors."""
        try:
            self.schema_class().deserialize(data)
        except colander.Invalid as e:
            raise RepoDataValidation(
                detail=e.asdict()
            )

    def get(self, object_id):
        """Get and return a single object by its id."""
        entity = self.model_class.objects.get(id=object_id)
        data = utils.model_to_json_api_data(entity, self.schema_class(), url_builder=self.url_builder)
        return utils.build_repo_response(data=data)

    def filter(self, company_id=utils.DEFAULT, contact_id=utils.DEFAULT, offset=0, limit=100):
        """Filter objects."""
        filters = {}
        if company_id != utils.DEFAULT:
            filters['company__pk'] = company_id
        if contact_id != utils.DEFAULT:
            filters['contact__pk'] = contact_id
        start, end = offset, offset + limit
        entities = list(self.model_class.objects.filter(**filters).all()[start:end])
        data = [utils.model_to_json_api_data(entity, self.schema_class(), self.url_builder) for entity in entities]
        return utils.build_repo_response(data=data)

    def upsert(self, data):
        """Insert or update an object."""
        model_id = data.get('id', None)
        if model_id:
            data = utils.merge_db_data_and_request_data(
                model_id,
                data,
                self.model_class,
                self.schema_class,
                url_builder=self.url_builder
            )
        self.validate(data)
        data = self.inject_service_offer(data)
        return utils.json_api_to_model(data, self.model_class)

    def inject_service_offer(self, data):
        """Add the service offer, looking one up by team, service and event."""
        dit_team_id = utils.extract_id_for_relationship_from_data(data, 'dit_team')
        service_id = utils.extract_id_for_relationship_from_data(data, 'service')
        event_id = utils.extract_id_for_relationship_from_data(data, 'event')
        service_offer_id = self.get_service_offer_id(
            dit_team_id=dit_team_id,
            service_id=service_id,
            event_id=event_id
        )
        if not service_offer_id:
            raise RepoDataValidation(
                detail={'relationships.service': 'This combination of service and service provider does not exist.'}
            )
        else:
            data['relationships'].update({
                'service_offer': {
                    'data': {
                        'type': 'ServiceOffer',
                        'id': service_offer_id
                    },
                }
            })
            return data

    @staticmethod
    def get_service_offer_id(dit_team_id, service_id, event_id):
        """Check that the combination of dit_team, service and event results into a valid service offer.

        If True if returns the service offer id, if not it returns None.
        """
        try:
            query = dict(
                dit_team_id=dit_team_id,
                service_id=service_id,
                event_id=event_id
            )
            service_offer = ServiceOffer.objects.filter(**query).first()
            if not service_offer:
                return None
            return encoding.force_text(service_offer.pk)
        except ServiceOffer.DoesNotExist:
            return None
