# Generated by Django 2.0.5 on 2018-06-11 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0043_investmentproject_project_manager_first_assigned_on'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='investmentproject',
            options={'default_permissions': ('add', 'change_all', 'delete'), 'permissions': (('read_all_investmentproject', 'Can read all investment project'), ('read_associated_investmentproject', 'Can read associated investment project'), ('change_associated_investmentproject', 'Can change associated investment project'), ('read_investmentproject_document', 'Can read investment project document'), ('change_stage_to_won_investmentproject', 'Can change investment project stage to won'))},
        ),
    ]