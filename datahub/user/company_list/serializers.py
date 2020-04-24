from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy
from rest_framework import serializers
from rest_framework.settings import api_settings

from datahub.company.models import Company
from datahub.core.serializers import NestedRelatedField
from datahub.user.company_list.models import CompanyList, CompanyListItem, PipelineItem

CANT_ADD_ARCHIVED_COMPANY_MESSAGE = gettext_lazy(
    "An archived company can't be added to the pipeline.",
)
COMPANY_ALREADY_EXISTS_MESSAGE = gettext_lazy(
    "This company already exists in the pipeline for this user.",
)


class CompanyListSerializer(serializers.ModelSerializer):
    """Serialiser for a company list."""

    # This is an annotation on the query set
    item_count = serializers.ReadOnlyField()

    class Meta:
        model = CompanyList
        fields = (
            'id',
            'item_count',
            'name',
            'created_on',
        )


class CompanyListItemSerializer(serializers.ModelSerializer):
    """Serialiser for company list items."""

    company = NestedRelatedField(
        Company,
        # If this list of fields is changed, update the equivalent list in the QuerySet.only()
        # call in the queryset module
        extra_fields=('archived', 'name', 'trading_names'),
    )
    latest_interaction = serializers.SerializerMethodField()

    def get_latest_interaction(self, obj):
        """
        Construct a latest interaction object from the latest_interaction_id,
        latest_interaction_date and latest_interaction_subject query set annotations.
        """
        if not obj.latest_interaction_id:
            return None

        return {
            'id': obj.latest_interaction_id,
            'created_on': obj.latest_interaction_created_on,
            # For consistency with the main interaction API, only return the date part.
            # See InteractionSerializer for more information
            'date': obj.latest_interaction_date.date(),
            'subject': obj.latest_interaction_subject,
            'dit_participants': obj.latest_interaction_dit_participants or [],
        }

    class Meta:
        model = CompanyListItem
        fields = (
            'company',
            'created_on',
            'latest_interaction',
        )


class ExportPipelineItemSerializer(serializers.ModelSerializer):
    """Serialiser for export pipeline list items."""

    company = NestedRelatedField(
        Company,
        # If this list of fields is changed, update the equivalent list in the QuerySet.only()
        # call in the queryset module
        extra_fields=('name', 'turnover', 'export_potential'),
    )

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new instance using this serializer

        :return: created instance
        validates to make sure:
        - an archived company will not be added
        - existing company is not added to the same adviser
        """
        company = validated_data.get('company')
        adviser = validated_data.get('adviser')

        if company.archived:
            errors = {
                api_settings.NON_FIELD_ERRORS_KEY: CANT_ADD_ARCHIVED_COMPANY_MESSAGE,
            }
            raise serializers.ValidationError(errors)

        if PipelineItem.objects.filter(
            company=company,
            adviser=adviser,
        ).exists():
            errors = {
                api_settings.NON_FIELD_ERRORS_KEY: COMPANY_ALREADY_EXISTS_MESSAGE,
            }
            raise serializers.ValidationError(errors)

        return super().create(validated_data)

    class Meta:
        model = PipelineItem
        fields = (
            'id',
            'company',
            'status',
            'created_on',
        )
        read_only_fields = (
            'id',
            'company',
            'created_on',
        )
