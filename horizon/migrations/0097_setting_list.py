# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-13 01:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0096_auto_20170806_0707'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='list',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]