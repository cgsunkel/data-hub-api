# Generated by Django 3.0.5 on 2020-04-23 16:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0104_company_dnb_investigation_id'),
        ('company_list', '0012_remove_is_legacy_default_from_database'),
    ]

    operations = [
        migrations.CreateModel(
            name='PipelineItem',
            fields=[
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('leads', 'Leads'), ('in_progress', 'In progress'), ('export_wins', 'Export wins')], max_length=255)),
                ('adviser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pipeline_list_items', to='company.Company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='pipelineitem',
            constraint=models.UniqueConstraint(fields=('adviser', 'company'), name='unique_adviser_and_company'),
        ),
    ]
