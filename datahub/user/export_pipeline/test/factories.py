import factory.fuzzy

from datahub.company.test.factories import AdviserFactory, CompanyFactory
from datahub.user.export_pipeline.models import ExportPipelineList


class ExportPipelineListFactory(factory.django.DjangoModelFactory):
    """Factory for ExportPipelineList."""

    category = ExportPipelineList.Category.LEADS
    adviser = factory.SubFactory(AdviserFactory)
    created_by = factory.SelfAttribute('adviser')

    class Meta:
        model = 'export_pipeline.ExportPipelineList'


class ExportPipelineItemFactory(factory.django.DjangoModelFactory):
    """Factory for ExportPipelineItem."""

    list = factory.SubFactory(ExportPipelineListFactory)
    company = factory.SubFactory(CompanyFactory)
    created_by = factory.SubFactory(AdviserFactory)

    class Meta:
        model = 'export_pipeline.ExportPipelineItem'
