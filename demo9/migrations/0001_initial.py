# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-12 12:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('bid', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('author', models.CharField(blank=True, max_length=255, null=True)),
                ('publish_date', models.DateField(blank=True, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReportTemplate',
            fields=[
                ('tid', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TemplateElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_id', models.IntegerField(blank=True, null=True)),
                ('node', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=10)),
                ('positionX', models.FloatField(blank=True, null=True)),
                ('positionY', models.FloatField(blank=True, null=True)),
                ('width', models.FloatField(blank=True, null=True)),
                ('height', models.FloatField(blank=True, null=True)),
                ('modelName', models.CharField(blank=True, max_length=100, null=True)),
                ('columns', models.TextField(blank=True, null=True)),
                ('filterConditions', models.TextField(blank=True, null=True)),
                ('html', models.TextField(blank=True, null=True)),
                ('reportTemplate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='demo9.ReportTemplate')),
            ],
        ),
    ]
