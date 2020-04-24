import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse

from datahub.company.test.factories import CompanyFactory
from datahub.core.test_utils import APITestMixin, create_test_user
from datahub.user.company_list.models import PipelineItem

pipeline_collection_url = reverse('api-v4:company-list:pipelineitem-collection')


class TestAddPipelineItemView(APITestMixin):
    """Tests for adding a pipeline item."""

    def test_returns_401_if_unauthenticated(self, api_client):
        """Test that a 401 is returned if the user is unauthenticated."""
        response = api_client.post(pipeline_collection_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        'permission_codenames,expected_status',
        (
            ([], status.HTTP_403_FORBIDDEN),
            (['view_pipelineitem'], status.HTTP_403_FORBIDDEN),
            (['add_pipelineitem'], status.HTTP_403_FORBIDDEN),
            (['view_company', 'add_pipelineitem'], status.HTTP_201_CREATED),
        ),
    )
    def test_permission_checking(self, permission_codenames, expected_status, api_client):
        """Test that the expected status is returned for various user permissions."""
        user = create_test_user(permission_codenames=permission_codenames, dit_team=None)
        api_client = self.create_api_client(user=user)
        company = CompanyFactory()
        pipeline_status = PipelineItem.Status.LEADS
        response = api_client.post(
            pipeline_collection_url,
            data={
                'company': {
                    'id': str(company.pk),
                },
                'status': pipeline_status,
            },
        )
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        'request_data,expected_errors',
        (
            pytest.param(
                {},
                {
                    'company': ['This field is required.'],
                    'status': ['This field is required.'],
                },
                id='company and status are omitted',
            ),
            pytest.param(
                {
                    'company': None,
                },
                {
                    'company': ['This field may not be null.'],
                    'status': ['This field is required.'],
                },
                id='company is null and status is omitted',
            ),
            pytest.param(
                {
                    'status': None,
                },
                {
                    'company': ['This field is required.'],
                    'status': ['This field may not be null.'],
                },
                id='company is omitted and status is null',
            ),
            pytest.param(
                {
                    'company': '',
                    'status': '',
                },
                {
                    'company': ['This field may not be null.'],
                    'status': ['"" is not a valid choice.'],
                },
                id='company and status are empty strings',
            ),
            pytest.param(
                {
                    'company': '',
                    'status': PipelineItem.Status.LEADS,
                },
                {
                    'company': ['This field may not be null.'],
                },
                id='company is empty string',
            ),
            pytest.param(
                {
                    'company': lambda: str(CompanyFactory().pk),
                    'status': '',
                },
                {
                    'status': ['"" is not a valid choice.'],
                },
                id='status is empty string',
            ),
        ),
    )
    def test_validation(self, request_data, expected_errors):
        """Test validation."""
        permission_codenames = ['view_company', 'add_pipelineitem']
        user = create_test_user(permission_codenames=permission_codenames, dit_team=None)
        api_client = self.create_api_client(user=user)
        response = api_client.post(
            pipeline_collection_url,
            data=request_data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_errors

    @freeze_time('2017-04-19 15:25:30.986208')
    def test_successfully_create_a_pipeline_item(self):
        """Test that a pipeline item can be created."""
        permission_codenames = ['view_company', 'add_pipelineitem']
        user = create_test_user(permission_codenames=permission_codenames, dit_team=None)
        api_client = self.create_api_client(user=user)
        company = CompanyFactory()
        pipeline_status = PipelineItem.Status.LEADS
        response = api_client.post(
            pipeline_collection_url,
            data={
                'company': {
                    'id': str(company.pk),
                },
                'status': pipeline_status,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()
        assert response_data == {
            'id': response_data['id'],
            'company': {
                'id': str(company.pk),
                'name': company.name,
                'export_potential': company.export_potential,
                'turnover': company.turnover,
            },
            'status': pipeline_status,
            'created_on': '2017-04-19T15:25:30.986208Z',
        }

        pipeline_item = PipelineItem.objects.get(pk=response_data['id'])

        # adviser should be set to the authenticated user
        assert pipeline_item.adviser == user
        assert pipeline_item.created_by == user
        assert pipeline_item.modified_by == user
