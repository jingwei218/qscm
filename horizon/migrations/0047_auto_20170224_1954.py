# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 19:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0046_auto_20170224_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricecondition',
            name='high',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pricecondition',
            name='low',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
