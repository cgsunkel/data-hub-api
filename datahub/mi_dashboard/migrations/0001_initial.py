# Generated by Django 2.1.3 on 2018-12-18 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MIInvestmentProject',
            fields=[
                ('dh_fdi_project_id', models.UUIDField(primary_key=True, serialize=False)),
                ('sector_cluster', models.CharField(max_length=255)),
                ('uk_region_name', models.CharField(max_length=255)),
                ('land_date', models.DateField(blank=True, null=True)),
                ('financial_year', models.CharField(max_length=255)),
                ('overseas_region', models.CharField(max_length=255)),
                ('project_url', models.TextField()),
                ('country_url', models.TextField()),
                ('project_fdi_value', models.CharField(max_length=255)),
                ('top_level_sector_name', models.CharField(blank=True, max_length=255, null=True)),
                ('status_collapsed', models.CharField(max_length=255)),
                ('actual_land_date', models.DateField(blank=True, null=True)),
                ('project_reference', models.CharField(max_length=255)),
                ('total_investment', models.DecimalField(blank=True, decimal_places=0, max_digits=19, null=True)),
                ('number_new_jobs', models.IntegerField(null=True)),
                ('number_safeguarded_jobs', models.IntegerField(null=True)),
                ('investor_company_country', models.CharField(max_length=255)),
                ('stage_name', models.CharField(max_length=255)),
                ('sector_name', models.TextField(blank=True, null=True)),
                ('archived', models.BooleanField()),
                ('investment_type_name', models.CharField(max_length=255)),
                ('status_name', models.CharField(max_length=255)),
                ('level_of_involvement_name', models.CharField(max_length=255)),
                ('simplified_level_of_involvement', models.CharField(max_length=255)),
                ('possible_uk_region_names', models.CharField(blank=True, max_length=255, null=True)),
                ('actual_uk_region_names', models.CharField(blank=True, max_length=255, null=True)),
                ('estimated_land_date', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
