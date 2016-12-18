from django.db import models
from django.contrib.auth.models import User


class HorizonUser(User):

    def __str__(self):
        return self.username


# 项目总表，包含设置、数据表、价格表等
class Horizon(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    owner = models.ManyToManyField(HorizonUser)  # 项目总表的拥有者

    def __str__(self):
        return self.name


# 设置选项
class Setting(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)  # 设置描述
    type = models.CharField(max_length=20, blank=False, null=True)  # 数据类型
    note = models.CharField(max_length=255, blank=True, null=True)  # 备注

    def __str__(self):
        return self.name


# 设置项目的值
class SettingOption(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    setting = models.ManyToManyField(Setting)  # 任一设置项目可以有多个设置选项值，同样的选项值可以被不同设置项目试用

    def __str__(self):
        return self.name


# 项目总表设置
class HorizonSetting(models.Model):
    pid = models.IntegerField(primary_key=True)
    settings = models.ManyToManyField(Setting)
    values = models.CharField(max_length=255, blank=False, null=False)
    horizon = models.OneToOneField(Horizon)

    def __str__(self):
        return self.horizon.name


# 价格表，每个供应商可以有多份价格表
class PriceSheet(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)  # 价格表描述


class DataSheet(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)  # 数据表描述


# 企业
class Company(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False) #公司名称
    register_number = models.CharField(max_length=30, blank=False, null=False)  # 税务登记号
    note = models.TextField(blank=True, null=True)  # 备注


# 产品，可以是企业类型、服务或者物品
class Category(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=False, null=False)
    related_category = models.ForeignKey('self', null=True)
    level = models.IntegerField(blank=False, null=False)
    company = models.ManyToManyField(Company)


# 计算表中的每一行即价格表/数据表中的每个元素
class Element(models.Model):
    pid = models.IntegerField(primary_key=True)
    category = models.ForeignKey(Category)  # 每个元素只有一个产品类别，多个元素可以包含于一个类别下
    price_sheet = models.ManyToManyField(PriceSheet)
    data_sheet = models.ManyToManyField(DataSheet)
    company = models.ForeignKey(Company)  # 每个元素对应一个供应商)


# 地理信息
class Geo(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, blank=False, null=False)
    related_geo = models.ForeignKey('self', null=True)  # 可回代自身，如：一个省有多个市
    level = models.IntegerField(blank=False, null=False)
    element = models.ManyToManyField(Element)  # 每个元素可对应多个地理信息，每个地理信息可被不同元素调用

    def __str__(self):
        temp_name = self.name
        g = self.related_geo
        while g is not None:
            temp_name = g.name + '|' + temp_name
            g = g.related_geo
        return temp_name


# 计量单位，用于标注数量的单位
class UoM(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10, blank=False, null=False)
    long_name = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name


# 计费数量
class ChargeableQuantity(models.Model):
    value = models.FloatField(blank=False)
    converting_factor = models.FloatField(blank=True, null=True)  # 转换率，如：333公斤/立方米
    comparison = models.CharField(max_length=3, choices=(('min', 'Minimum'), ('max', 'Maximum')), blank=True,
                                  null=True)  # 计算计费单位量的比较方式


# 数量
class Quantity(models.Model):
    value = models.FloatField(blank=False)
    role = models.CharField(max_length=10, blank=True, null=True)  # 设定数量的角色，可以是计算计费数量的基数或者是被折算的数
    uom = models.ForeignKey(UoM)  # 每个数量都有一个计量单位
    chargeable_quantity = models.ForeignKey(ChargeableQuantity)  # 每个计费数量对应一个或多个数量
    element = models.ForeignKey(Element)  # 每个元素有一个或多个数量


# 计价条件
class PriceCondition(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    low = models.FloatField(default=0)
    high = models.FloatField(default=0)


# 价格
class Price(models.Model):
    pid = models.IntegerField(primary_key=True)  # 用于价格排序
    value = models.FloatField(blank=True, null=True)  # 价格值
    price_condition = models.ForeignKey(PriceCondition)  # 计价条件，一个计价条件可以对应多个元素中的价格
    element = models.ForeignKey(Element)  # 一个元素可有多个价格


# 成本
class Cost(models.Model):
    pid = models.IntegerField(primary_key=True)  # 用于成本排序
    value = models.FloatField()
    price_condition = models.ForeignKey(PriceCondition)  # 计价条件，一个计价条件可以对应多个元素中的成本
    element = models.ForeignKey(Element)  # 一个元素可有多个成本


# 可供选择的服务：招标、对账
class Service(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)




