# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-02 01:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0099_location_geo'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
    ]