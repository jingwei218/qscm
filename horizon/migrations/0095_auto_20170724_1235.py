# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-24 12:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0094_auto_20170724_1203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='setting',
            name='model',
        ),
        migrations.AddField(
            model_name='datasheetfield',
            name='quantity_type',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='datasheetfield',
            name='quantity_uom',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='horizon.UoM'),
        ),
    ]
