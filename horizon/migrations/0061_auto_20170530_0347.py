# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-30 03:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0060_auto_20170530_0227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasheetfield',
            name='sequence',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]