from django.test import TestCase
from .models import DataSheet
from .calculation import load_xl_datasheet

file_fullpath='/home/jingwei/Downloads/48006_new_asldfkj_alsdnvla.xlsx'
datasheet=DataSheet.objects.get(pid=48006)

load_xl_datasheet(file_fullpath, datasheet)
