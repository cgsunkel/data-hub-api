# Generated by Django 2.0.4 on 2018-04-13 09:31

from pathlib import PurePath

from django.core.management import call_command
from django.db import migrations


def load_initial_communication_channels(apps, schema_editor):
    CommunicationChannels = apps.get_model('interaction', 'CommunicationChannel')

    # only load the fixtures if there aren't any already in the database
    # this is because we don't know if they have been changed via the django admin.
    if not CommunicationChannels.objects.exists():
        call_command(
            'loaddata',
            PurePath(__file__).parent / '0025_initial_communication_channels.yaml'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0024_add_policy_area_and_type_20180321_1201'),
    ]

    operations = [
        migrations.RunPython(load_initial_communication_channels, migrations.RunPython.noop)
    ]
