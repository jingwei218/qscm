# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-19 12:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0051_auto_20170519_1200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datasheetfield',
            name='display_field',
        ),
        migrations.RemoveField(
            model_name='element',
            name='locations',
        ),
        migrations.RemoveField(
            model_name='location',
            name='type',
        ),
        migrations.AddField(
            model_name='location',
            name='element',
            field=models.ForeignKey(default=10240001, on_delete=django.db.models.deletion.CASCADE, to='horizon.Element'),
            preserve_default=False,
        ),
    ]
