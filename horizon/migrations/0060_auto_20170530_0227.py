# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-30 02:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0059_price_uom'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasheetfield',
            name='field_type',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='pricesheetfield',
            name='field_type',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]