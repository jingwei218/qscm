# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-19 12:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0050_auto_20170519_1840'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datasheetfield',
            old_name='data_field',
            new_name='display_field',
        ),
        migrations.RenameField(
            model_name='pricesheetfield',
            old_name='price_field',
            new_name='display_field',
        ),
        migrations.RemoveField(
            model_name='displayfield',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='displayfield',
            name='display_name_through_attribute',
        ),
        migrations.AddField(
            model_name='datasheetfield',
            name='display_name',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pricesheetfield',
            name='display_name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
