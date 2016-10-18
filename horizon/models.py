from django.db import models


#服务
class Service(models.Model):
    name = models.CharField(max_length=50, blank=False)
    data_type = models.ForeignKey(DataType)

    def __str__(self):
        return self.name


#地理信息
class Geo(models.Model):
    name = models.CharField(max_length=40, blank=False)
    pid = models.CharField(max_length=6, blank=False)
    rgeo = models.ForeignKey('self', null=True) #可回代自身，如：一个省有多个市
    data_type = models.ForeignKey(DataType)


#位置信息
class Location(models.Model):
    name = models.CharField(max_length=255, blank=False)
    geo = models.ManyToManyField(Geo)
    seq = models.IntegerField(blank=True, null=False)  # 仅在存在多个位置信息的服务中使用，如：运输


#订单
class Order(models.Model):
    number = models.IntegerField()
    data_type = models.ForeignKey(DataType)

    def __str__(self):
        return self.number
