# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-18 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0072_auto_20170617_0155'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasheet',
            name='setting_locked',
            field=models.BooleanField(default=False),
        ),
    ]