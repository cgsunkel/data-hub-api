# Generated by Django 2.1.3 on 2018-12-18 16:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0054_trading_name_add_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='is_turnover_estimated',
            field=models.BooleanField(blank=True, help_text='Only used when duns_number is set.', null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='turnover',
            field=models.BigIntegerField(blank=True, help_text='In USD. Only used when duns_number is set.', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
