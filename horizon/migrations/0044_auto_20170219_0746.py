# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-19 07:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0043_datafield_attribute_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datafield',
            old_name='attribute_name',
            new_name='display_name',
        ),
        migrations.RenameField(
            model_name='datafield',
            old_name='name',
            new_name='display_name_through_attribute',
        ),
    ]