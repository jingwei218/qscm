# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 12:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0036_auto_20170215_1235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datasheet',
            name='data_fields',
        ),
    ]
