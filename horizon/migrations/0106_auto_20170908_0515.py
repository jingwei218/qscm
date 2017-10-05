# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 21:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0105_datasheet_data_locked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='element',
        ),
        migrations.AddField(
            model_name='location',
            name='datasheet_element',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='horizon.DataSheetElement'),
        ),
    ]