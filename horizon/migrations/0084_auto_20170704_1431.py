# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-04 14:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0083_remove_schemesetting_locked'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cost',
            old_name='data_sheet_element',
            new_name='datasheet_element',
        ),
        migrations.RenameField(
            model_name='datasheetsetting',
            old_name='data_sheet',
            new_name='datasheet',
        ),
    ]
