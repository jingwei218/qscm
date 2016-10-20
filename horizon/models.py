from django.db import models


class Project(models.Model):
    pass


#计算表中的每一行
class Element(models.Model):
    pid = models.IntegerField(primary_key=True)
    project = models.ManyToManyField(Project)


class Service(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=False)
    related_service = models.ManyToManyField('self')
    element = models.ManyToManyField(Element)


#地理信息
class Geo(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, blank=False)
    related_geo = models.ForeignKey('self', null=True) #可回代自身，如：一个省有多个市


#位置信息
class Location(models.Model):
    name = models.CharField(max_length=255, blank=False)
    geo = models.ManyToManyField(Geo)
    element = models.ManyToManyField(Element)


#计费单位
class ChargeableUnit(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=False)
    display_uom = models.CharField(max_length=10, blank=False) #显示的计费单位
    base_uom = models.CharField(max_length=10, blank=True, null=True) #基准计量单位，如公斤
    convertable_uom = models.CharField(max_length=10, blank=True, null=True) #需转换的计量单位，如：立方米
    converting_factor = models.FloatField(blank=True, null=True) #转换率，如：333公斤/立方米
    comparible = models.CharField(max_length=3, choices=(('min', 'Minimum'),('max', 'Maximum')), blank=True, null=True) #比大比小
    element = models.ManyToManyField(Element)

    def __str__(self):
        return self.name + ' ' + self.uom + ' ' + str(self.converting_factor) + ' ' + str(self.convertable_uom)


class Price(models.Model):
    pid = models.IntegerField(primary_key=True)
    rate = models.FloatField(blank=True, null=True)
    element = models.ForeignKey(Element)


class PriceCondition(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    low = models.FloatField(default=0)
    high = models.FloatField(default=0)
    price = models.ManyToManyField(Price)


#订单
class Order(models.Model):
    number = models.IntegerField(primary_key=True)
    costs = models.TextField(null=True)

    def __str__(self):
        return str(self.number)
