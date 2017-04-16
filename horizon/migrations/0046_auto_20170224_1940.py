# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0045_auto_20170220_1310'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pricesheet',
            name='elements',
        ),
        migrations.AddField(
            model_name='pricesheet',
            name='price_sheet_elements',
            field=models.ManyToManyField(to='horizon.PriceSheetElement'),
        ),
    ]
