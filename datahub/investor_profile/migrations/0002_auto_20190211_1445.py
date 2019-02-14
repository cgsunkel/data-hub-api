# Generated by Django 2.1.4 on 2019-02-11 14:45

from pathlib import PurePath

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from datahub.core.migration_utils import load_yaml_data_in_migration
import uuid


metadata_files = [
    'asset_interest_class.yaml',
    'background_checks_conducted.yaml',
    'construction_risk.yaml',
    'deal_ticket_size.yaml',
    'desired_deal_role.yaml',
    'equity_percentage.yaml',
    'investor_type.yaml',
    'large_capital_investment_type.yaml',
    'profile_type.yaml',
    'relationship_health.yaml',
    'restriction.yaml',
    'return_rate.yaml',
    'time_horizon.yaml'
]


def load_metadata(apps, schema_editor):
    for file_name in metadata_files:
        load_yaml_data_in_migration(
            apps,
            PurePath(__file__).parent / f'../fixtures/{file_name}',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0021_delete_companyclassification'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0063_populate_company_address_fields'),
        ('investor_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetClassInterest',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('asset_interest_sector', models.CharField(max_length=255)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BackgroundChecksConducted',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConstructionRisk',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DealTicketSize',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DesiredDealRole',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EquityPercentage',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LargeCapitalInvestmentType',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvestorType',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RelationshipHealth',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Restriction',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReturnRate',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeHorizon',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='client_contacts',
            field=models.ManyToManyField(blank=True, related_name='investor_profiles', to='company.Contact'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='dit_relationship_manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='investor_profiles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='investable_capital',
            field=models.DecimalField(blank=True, decimal_places=0, help_text='Investable capital amount in USD', max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='investor_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='notes_on_locations',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='other_countries_considering',
            field=models.ManyToManyField(blank=True, help_text='The other countries being considered for investment', related_name='_investorprofile_other_countries_considering_+', to='metadata.Country'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='uk_region_locations',
            field=models.ManyToManyField(blank=True, related_name='_investorprofile_uk_region_locations_+', to='metadata.UKRegion', verbose_name='possible UK regions'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='construction_risks',
            field=models.ManyToManyField(blank=True, related_name='_investorprofile_construction_risks_+', to='investor_profile.ConstructionRisk'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='deal_ticket_sizes',
            field=models.ManyToManyField(blank=True, related_name='+', to='investor_profile.DealTicketSize'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='desired_deal_roles',
            field=models.ManyToManyField(blank=True, related_name='_investorprofile_desired_deal_role_+', to='investor_profile.DesiredDealRole'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='investment_types',
            field=models.ManyToManyField(blank=True, related_name='_investorprofile_investment_types_+', to='investor_profile.LargeCapitalInvestmentType'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='investor_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='investor_profile.InvestorType'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='minimum_equity_percentage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='investor_profile.EquityPercentage'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='minimum_return_rate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='investor_profile.ReturnRate'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='relationship_health',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='investor_profile.RelationshipHealth'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='time_horizons',
            field=models.ManyToManyField(blank=True, related_name='_investorprofile_time_horizon_+', to='investor_profile.TimeHorizon'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='restrictions',
            field=models.ManyToManyField(blank=True, related_name='_investorprofile_restrictions_+', to='investor_profile.Restriction'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='asset_classes_of_interest',
            field=models.ManyToManyField(blank=True, related_name='_investorprofile_asset_class_of_interest_+', to='investor_profile.AssetClassInterest'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='background_checks_conducted',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='investor_profile.BackgroundChecksConducted'),
        ),
        migrations.AddField(
            model_name='investorprofile',
            name='dit_advisors',
            field=models.ManyToManyField(blank=True,
                                         related_name='_investorprofile_dit_advisors_+',
                                         to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(load_metadata, migrations.RunPython.noop),
    ]
