# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-22 13:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0057_datasheetelement_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datasheetelement',
            old_name='date',
            new_name='start_date',
        ),
    ]
