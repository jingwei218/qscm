# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 13:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('horizon', '0031_auto_20170213_1313'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datasheet',
            old_name='uom',
            new_name='uoms',
        ),
    ]
