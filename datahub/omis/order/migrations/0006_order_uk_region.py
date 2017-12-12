# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-08 10:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0011_add_default_id_for_metadata'),
        ('order', '0005_order_billing_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='uk_region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='metadata.UKRegion'),
        ),
    ]
