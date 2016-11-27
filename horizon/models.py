from django.db import models


class Project(models.Model):
    pass


class Vendor(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)


class Service(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=False)
    related_service = models.ManyToManyField('self')
    level = models.IntegerField(blank=False, null=False)


#计算表中的每一行
class Element(models.Model):
    pid = models.IntegerField(primary_key=True)
    project = models.ManyToManyField(Project)
    vendor = models.ForeignKey(Vendor)
    service = models.ForeignKey(Service)


#地理信息
class Geo(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40, blank=False)
    related_geo = models.ForeignKey('self', null=True) #可回代自身，如：一个省有多个市
    level = models.IntegerField(blank=False, null=False)


class Quantity(models.Model):
    quantity = models.FloatField(blank=False)
    uom = models.CharField(max_length=10, blank=False)
    element = models.ForeignKey(Element)


#计费单位
class ChargeableQuantity(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=False)
    converting_factor = models.FloatField(blank=True, null=True) #转换率，如：333公斤/立方米
    comparison = models.CharField(max_length=3, choices=(('min', 'Minimum'),('max', 'Maximum')), blank=True, null=True) #计算计费单位量的比较方式
    target = models.IntegerField() #需要转换成计费单位的目标，指向该目标的序列的下标
    base = models.IntegerField() #与转换后的计费单位进行比较的基准单位，指向该基准单位的下标
    element = models.OneToOneField(Element)

    def __str__(self):
        return self.name + ' ' + str(self.converting_factor)


class PriceCondition(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    low = models.FloatField(default=0)
    high = models.FloatField(default=0)


class Price(models.Model):
    pid = models.IntegerField(primary_key=True)
    price = models.FloatField(blank=True, null=True)
    price_condition = models.ForeignKey(PriceCondition)
    element = models.ForeignKey(Element)


#订单
class Order(models.Model):
    number = models.IntegerField(primary_key=True)
    costs = models.TextField(null=True)

    def __str__(self):
        return str(self.number)
