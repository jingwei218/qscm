# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 20:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0047_auto_20170224_1954'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('pid', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=3)),
                ('long_name', models.CharField(max_length=20)),
            ],
        ),
    ]
