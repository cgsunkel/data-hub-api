import uuid

from django.conf import settings
from django.db import models

from datahub.core.models import BaseModel


class ExportPipelineList(BaseModel):
    """Pre-defined export pipeline list holding companies."""

    class Category(models.TextChoices):
        LEADS = ('leads', 'Leads')
        IN_PROGRESS = ('in_progress', 'In progress')
        EXPORT_WINS = ('export_wins', 'Export wins')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    category = models.CharField(
        max_length=settings.CHAR_FIELD_MAX_LENGTH,
        choices=Category.choices,
    )
    adviser = models.ForeignKey(
        'company.Advisor',
        on_delete=models.CASCADE,
        related_name='export_pipeline_lists',
    )

    def __str__(self):
        """Human-friendly representation."""
        return f'{self.category} – {self.adviser}'


class ExportPipelineItem(BaseModel):
    """
    Export pipeline item on a user's personal list of companies.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    list = models.ForeignKey(
        ExportPipelineList,
        models.CASCADE,
        related_name='export_pipeline_items',
    )
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='export_pipeline_items',
    )

    def __str__(self):
        """Human-friendly representation."""
        return f'{self.company} – {self.list}'
