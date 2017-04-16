from django.db import models
from django.contrib.auth.models import User


# 用户
class HorizonUser(User):
    permissions = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


# 可供选择的服务：招标、对账
class Service(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)  # 服务项目名称
    code_name = models.CharField(max_length=50, blank=False, null=False)  #服务项目代号
    note = models.CharField(max_length=255, blank=True, null=True)  # 服务内容描述
    owners = models.ManyToManyField(HorizonUser)  # 可用服务的用户

    def __str__(self):
        return self.name


class Currency(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=3)
    long_name = models.CharField(max_length=20)


# 设置选项中可选的值。有些设置为文字或数字，则没有可选值。
class SettingOption(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.name


# 设置选项
class Setting(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)  # 设置描述
    type = models.CharField(max_length=20, blank=False, null=True)  # 数据类型
    note = models.CharField(max_length=255, blank=True, null=True)  # 备注
    model = models.CharField(max_length=255, blank=True, null=True)  # 指向须展开的model，如：数据表列标题
    level = models.IntegerField()  # 标注设置所适用层：0代表scheme层，1代表datasheet层
    setting_options = models.ManyToManyField(SettingOption)  # 任一设置项目可以有多个设置选项值，同样的选项值可以被不同设置项目使用

    def __str__(self):
        return self.name


# 产品，可以是企业类型、服务或者物品
class Category(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=False, null=False)
    related_category = models.ForeignKey('self', null=True)
    level = models.IntegerField(blank=False, null=False)

    def ls(self):
        templs = list()
        templs.append(self.name)
        c = self.related_category
        while c is not None:
            templs.append(c.name)
            c = c.related_category
        return templs

    def __str__(self):
        return "|".join(self.ls())


# 企业
class Company(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False) #公司名称
    register_number = models.CharField(max_length=30, blank=False, null=False)  # 公司注册号
    note = models.TextField(blank=True, null=True)  # 备注
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return str(self.pid) + '|' + self.name + '|' + self.category.name


# 地理信息
class Geo(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, blank=False, null=False)
    related_geo = models.ForeignKey('self', null=True)  # 可回代自身，如：一个省有多个市
    level = models.IntegerField(blank=False, null=False)

    def ls(self):  # 生成地理信息各层级的列表
        templs = list()
        templs.append(self.name)
        c = self.related_geo
        while c is not None:
            templs.append(c.name)
            c = c.related_geo
        return templs

    def __str__(self):  # 生成地理信息各层级的组合字符串
        return "|".join(self.ls())

    class Meta:
        verbose_name = 'Geography'


# 用于数据的地理位置信息
class Location(models.Model):
    pid = models.IntegerField(primary_key=True)
    geo = models.ForeignKey(Geo)
    type = models.CharField(max_length=4, choices=(('from', 'From'), ('to', 'To'), ('via', 'Via'), ('at', 'At')))
    sequence = models.IntegerField(default=0)

    def __str__(self):
        return self.geo.name

    class Meta:
        ordering = ['sequence']


# 招标项目总表，包含设置、数据表、价格表等
class Scheme(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    owners = models.ManyToManyField(HorizonUser)  # 项目总表的拥有者
    setting_locked = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['pid']


# 项目总表设置
class SchemeSetting(models.Model):
    pid = models.IntegerField(primary_key=True)
    setting = models.ForeignKey(Setting)  # 对应的某个设置项
    scheme = models.ForeignKey(Scheme)  # Scheme一一对应其自有的设置
    value = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.setting.name

    class Meta:
        ordering = ['pid']


# 计算表中的每一行即价格表/数据表中的每个元素
class Element(models.Model):
    pid = models.IntegerField(primary_key=True)
    category = models.ForeignKey(Category)  # 每个元素只有一个产品类别，多个元素可以包含于一个类别下
    company = models.ForeignKey(Company)  # 每个元素对应一个供应商
    locations = models.ManyToManyField(Location)

    def __str__(self):
        return self.company.name + ' ' + str(self.category)


# 数据元素，基于元素内容，额外有数量信息
class DataSheetElement(models.Model):
    pid = models.IntegerField(primary_key=True)
    element = models.ForeignKey(Element)

    def __str__(self):
        return self.element.category.name + ' ' + self.element.locations + ' ' + self.element.company.name

    class Meta:
        ordering = ['pid']


# 计量单位，用于标注数量的单位
class UoM(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10, blank=False, null=False)
    long_name = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['pid']


# 数量
class Quantity(models.Model):
    value = models.FloatField(blank=True, null=True)
    role = models.CharField(max_length=10, blank=True, null=True)  # 设定数量的角色，可以是计算计费数量的基数或者是转换量
    uom = models.ForeignKey(UoM, blank=True, null=True)  # 每个数量都有一个计量单位，空单位即表示次数
    converting_factor = models.FloatField(blank=True, null=True)  # 转换率，如：333公斤/立方米，仅对转换量适用
    comparison = models.CharField(max_length=3, choices=(('min', 'Minimum'), ('max', 'Maximum')), blank=True,
                                  null=True)  # 计算计费单位量的比较方式，仅对转换量适用
    data_sheet_element = models.ForeignKey(DataSheetElement)  # 每个元素有一个或多个数量

    def __str__(self):
        return str(self.value) + ' x ' + self.uom.name


# 价格表行
class PriceSheetElement(models.Model):
    pid = models.IntegerField(primary_key=True)
    element = models.ForeignKey(Element)


# 计价条件
class PriceCondition(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    low = models.FloatField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)
    uom = models.ForeignKey(UoM)


# 价格
class Price(models.Model):
    pid = models.IntegerField(primary_key=True)  # 用于价格排序
    value = models.FloatField(blank=True, null=True)  # 价格值
    currency = models.ForeignKey(Currency)
    price_conditions = models.ManyToManyField(PriceCondition)  # 计价条件，例，一个价格可以对应重量和体积双重条件
    price_sheet_element = models.ForeignKey(PriceSheetElement)


# 价格表，每个供应商可以有多份价格表
class PriceSheet(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)  # 价格表描述
    scheme = models.ForeignKey(Scheme)
    price_sheet_elements = models.ManyToManyField(PriceSheetElement)

    def __str__(self):
        return self.name


# 表格字段
class DataField(models.Model):
    pid = models.IntegerField(primary_key=True)
    model_name = models.CharField(max_length=30, blank=True, null=True)
    through = models.CharField(max_length=30, blank=True, null=True)
    display_name = models.CharField(max_length=30, blank=True, null=True)
    display_name_through_attribute = models.CharField(max_length=30, blank=True, null=True)


# 数据表
class DataSheet(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)  # 数据表描述
    scheme = models.ForeignKey(Scheme)
    data_sheet_elements = models.ManyToManyField(DataSheetElement)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['pid']


class DataSheetField(models.Model):
    data_sheet = models.ForeignKey(DataSheet)
    data_field = models.ForeignKey(DataField)
    sequence = models.IntegerField()

    def __str__(self):
        return self.data_field.display_name

    class Meta:
        ordering = ['sequence']


class DataSheetSetting(models.Model):
    pid = models.IntegerField(primary_key=True)
    setting = models.ForeignKey(Setting)
    data_sheet = models.ForeignKey(DataSheet)
    value = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.setting.name

    class Meta:
        ordering = ['pid']


# 成本
class Cost(models.Model):
    pid = models.IntegerField(primary_key=True)  # 前部与DataSheetElement的pid相同，后部为price condition的pid
    value = models.FloatField()
    total = models.BooleanField()
    data_sheet_element = models.ForeignKey(DataSheetElement)  # 一个数据表元素可有多个成本








