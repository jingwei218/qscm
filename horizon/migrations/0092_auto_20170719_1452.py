# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-19 14:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0091_auto_20170718_1338'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datasheet',
            old_name='xltemplate_filelink',
            new_name='xltemplate_file_fullpath',
        ),
        migrations.RenameField(
            model_name='datasheet',
            old_name='xltemplate_filename',
            new_name='xltemplate_file_name',
        ),
        migrations.RemoveField(
            model_name='datasheet',
            name='xltemplate_created',
        ),
    ]