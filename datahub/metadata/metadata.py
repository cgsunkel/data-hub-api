from . import models
from .filters import ServiceFilterSet
from .registry import registry
from .serializers import SectorSerializer, ServiceSerializer, TeamSerializer

registry.register(metadata_id='business-type', model=models.BusinessType)
registry.register(metadata_id='country', model=models.Country)
registry.register(metadata_id='employee-range', model=models.EmployeeRange)
registry.register(
    filter_fields={
        'level': ['lte'],
    },
    metadata_id='sector',
    model=models.Sector,
    queryset=models.Sector.objects.select_related(
        'parent',
        'parent__parent',
    ),
    serializer=SectorSerializer,
)
registry.register(
    filter_class=ServiceFilterSet,
    metadata_id='service',
    model=models.Service,
    serializer=ServiceSerializer
)
registry.register(metadata_id='team-role', model=models.TeamRole)
registry.register(
    metadata_id='team',
    model=models.Team,
    queryset=models.Team.objects.select_related('role', 'uk_region', 'country'),
    serializer=TeamSerializer
),
registry.register(metadata_id='title', model=models.Title)
registry.register(metadata_id='turnover', model=models.TurnoverRange)
registry.register(metadata_id='uk-region', model=models.UKRegion)
registry.register(metadata_id='headquarter-type', model=models.HeadquarterType)
registry.register(metadata_id='company-classification', model=models.CompanyClassification)
registry.register(metadata_id='investment-type', model=models.InvestmentType)
registry.register(metadata_id='fdi-type', model=models.FDIType)
registry.register(metadata_id='referral-source-activity', model=models.ReferralSourceActivity)
registry.register(metadata_id='referral-source-website', model=models.ReferralSourceWebsite)
registry.register(metadata_id='referral-source-marketing', model=models.ReferralSourceMarketing)
registry.register(
    metadata_id='investment-business-activity',
    model=models.InvestmentBusinessActivity
)
registry.register(
    metadata_id='investment-strategic-driver',
    model=models.InvestmentStrategicDriver
)
registry.register(metadata_id='salary-range', model=models.SalaryRange)
registry.register(metadata_id='investment-project-stage', model=models.InvestmentProjectStage)
registry.register(metadata_id='fdi-value', model=models.FDIValue)
