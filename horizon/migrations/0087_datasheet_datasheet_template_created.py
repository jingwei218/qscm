# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-17 13:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0086_auto_20170709_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasheet',
            name='datasheet_template_created',
            field=models.BooleanField(default=False),
        ),
    ]
