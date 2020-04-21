import pytest

from datahub.user.export_pipeline.test.factories import (
    ExportPipelineItemFactory,
    ExportPipelineListFactory,
)

pytestmark = pytest.mark.django_db


class TestExportPipelineList:
    """Tests ExportPipelineList model"""

    def test_str(self):
        """Test the human friendly string representation of the object"""
        export_pipeline_list = ExportPipelineListFactory()
        status = f'{export_pipeline_list.category} – {export_pipeline_list.adviser}'
        assert str(export_pipeline_list) == status


class TestExportPipelineItem:
    """Tests ExportPipelineItem model"""

    def test_str(self):
        """Test the human friendly string representation of the object"""
        export_pipeline_item = ExportPipelineItemFactory()
        status = f'{export_pipeline_item.company} – {export_pipeline_item.list}'
        assert str(export_pipeline_item) == status
