from django.db import models


# Create your models here.
class Book(models.Model):
    bid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    publish_date = models.DateField(blank=True, null=True)
    price = models.CharField(max_length=255, blank=True, null=True)


class PrintableElement(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    positionX = models.FloatField(blank=False, null=False)
    positionY = models.FloatField(blank=False, null=False)
    height = models.FloatField(blank=False, null=False)
    width = models.FloatField(blank=False, null=False)
