# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-23 11:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qsite', '0002_auto_20160923_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='lang_dc',
            field=models.CharField(max_length=30),
        ),
    ]
