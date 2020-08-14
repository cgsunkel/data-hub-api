from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from datahub.core.viewsets import CoreViewSet
from datahub.investment.investor_profile.models import LargeCapitalInvestorProfile
from datahub.investment.investor_profile.serializers import LargeCapitalInvestorProfileSerializer


class LargeCapitalInvestorProfileViewSet(CoreViewSet):
    """Large capital investor profile view set."""

    serializer_class = LargeCapitalInvestorProfileSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, )
    filterset_fields = ('investor_company_id',)
    ordering = ('-created_on')
    ordering_fields = ('created_on', 'modified_on', 'investor_company')
    queryset = LargeCapitalInvestorProfile.objects.all()
