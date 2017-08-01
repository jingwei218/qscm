# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-18 12:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0088_auto_20170717_1351'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datasheet',
            old_name='xl_template_created',
            new_name='xltemplate_created',
        ),
        migrations.AddField(
            model_name='datasheet',
            name='xltemplate_filename',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
