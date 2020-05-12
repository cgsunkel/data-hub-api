# Generated by Django 3.0.6 on 2020-05-12 15:29

from django.db import migrations


def remove_permission(apps, schema_editor):
    """Remove `change_stage_to_won_investmentproject` permission."""
    permission_model = apps.get_model('auth', 'Permission')

    # This also removes the group
    permission_model.objects.filter(
        codename='change_stage_to_won_investmentproject',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0002_add_change_to_any_stage_permission'),
    ]

    operations = [
        migrations.RunPython(remove_permission, elidable=True),
        migrations.AlterModelOptions(
            name='investmentproject',
            options={'default_permissions': ('add', 'change_all', 'delete', 'view_all'), 'permissions': (('view_associated_investmentproject', 'Can view associated investment project'), ('change_associated_investmentproject', 'Can change associated investment project'), ('export_investmentproject', 'Can export investment project'), ('view_investmentproject_document', 'Can view investment project document'), ('change_to_any_stage_investmentproject', 'Can change investment project to any stage'))},
        ),
    ]
