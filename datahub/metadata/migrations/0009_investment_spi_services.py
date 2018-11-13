# Generated by Django 2.0.4 on 2018-05-14 10:43
from pathlib import PurePath

from django.db import migrations
from django.db.migrations import RunPython
from datahub.core.migration_utils import load_yaml_data_in_migration


def load_investment_spi_services(apps, schema_editor):
    load_yaml_data_in_migration(
        apps,
        PurePath(__file__).parent / '0009_investment_spi_services.yaml'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0008_add_policy_feedback_service'),
    ]

    operations = [
        RunPython(load_investment_spi_services, RunPython.noop),
    ]
