from django.db import models


# Create your models here.
class Book(models.Model):
    bid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    publish_date = models.DateField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)


class ReportTemplate(models.Model):
    tid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)


class TemplateElement(models.Model):
    node_id = models.IntegerField(blank=True, null=True)
    node = models.CharField(max_length=100, blank=False, null=False)
    status = models.CharField(max_length=10, blank=False, null=False)
    positionX = models.FloatField(blank=True, null=True)
    positionY = models.FloatField(blank=True, null=True)
    width = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    modelName = models.CharField(max_length=100, blank=True, null=True)
    columns = models.TextField(blank=True, null=True)
    filterConditions = models.TextField(blank=True, null=True)
    html = models.TextField(blank=True, null=True)
    reportTemplate = models.ForeignKey(ReportTemplate, blank=True, null=True)
