from django.db import models
from django.contrib.auth.models import User


# ========================= Platform Level ========================= #
# 平台基础信息
class HorizonSetting(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    value = models.CharField(max_length=50, blank=True, null=True)


# 货币单位
class Currency(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=3)
    long_name = models.CharField(max_length=20)


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
        return str(self.pid) + '|' + self.name


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


# 用户
class HorizonUser(User):
    default_language = models.CharField(max_length=4, blank=True, null=True)
    permissions = models.CharField(max_length=100, blank=True, null=True)
    company = models.ForeignKey(Company, default=6707)

    def __str__(self):
        return self.username
        

# 可供选择的服务：招标、对账
class Service(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)  # 服务项目名称
    code_name = models.CharField(max_length=50, blank=False, null=False)  # 服务项目代号
    note = models.CharField(max_length=255, blank=True, null=True)  # 服务内容描述
    owners = models.ManyToManyField(HorizonUser)  # 可用服务的用户

    def __str__(self):
        return self.name


# ========================= Scheme ========================= #
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


# ========================= Settings ========================= #
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


# ========================= Element Level ========================= #
# 计算表中的每一行即价格表/数据表中的每个元素
class Element(models.Model):
    pid = models.IntegerField(primary_key=True)


# 用于数据的地理位置信息
class Location(models.Model):
    pid = models.IntegerField(primary_key=True)
    geo = models.ForeignKey(Geo)
    element = models.ForeignKey(Element)
    sequence = models.IntegerField()

    def __str__(self):
        return self.geo.name

    class Meta:
        ordering = ['sequence']


# 数据表元素，基于元素，但数据表元素可以是重复信息
class DataSheetElement(models.Model):
    pid = models.IntegerField(primary_key=True)
    start_date = models.DateField(auto_now_add=True)
    element = models.ForeignKey(Element)
    vendor = models.ForeignKey(Company)
    category = models.ForeignKey(Category)  # 每个数据表元素对应一个产品类别

    def __str__(self):
        return str(self.pid) + "|" + self.category.name

    class Meta:
        ordering = ['pid']


# 价格表行
class PriceSheetElement(models.Model):
    pid = models.IntegerField(primary_key=True)
    element = models.ForeignKey(Element)
    vendor = models.ForeignKey(Company)


# ========================= DataSheetElement Addons ========================= #
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
    sequence = models.IntegerField(blank=True, null=True)
    data_sheet_element = models.ForeignKey(DataSheetElement)  # 每个元素有一个或多个数量

    def __str__(self):
        return str(self.value) + ' x ' + self.uom.name


# ========================= PriceSheetElement Addons ========================= #
# 计价条件
class PriceCondition(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    group = models.IntegerField(blank=True, null=True)  # 用于同意义但不同表述方式的价格条件，如：3MT可表达为3000KG
    low = models.FloatField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)
    uom = models.ForeignKey(UoM)  # 区间判定单位

    def __str__(self):
        return self.name + "@" + self.uom.name

    class Meta:
        ordering = ['pid']


# 价格
class Price(models.Model):
    pid = models.IntegerField(primary_key=True)  # 用于价格排序
    value = models.FloatField(blank=True, null=True)  # 价格值
    uom = models.ForeignKey(UoM)  # 计价单位
    currency = models.ForeignKey(Currency)
    category = models.ForeignKey(Category)
    price_conditions = models.ManyToManyField(PriceCondition)  # 计价条件，例，一个价格可以对应重量和体积双重条件
    price_sheet_element = models.ForeignKey(PriceSheetElement)

    class Meta:
        ordering = ['pid']


# ========================= Sheets ========================= #
# 数据表
class DataSheet(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)  # 数据表描述
    number_of_price_fields = models.IntegerField(blank=True, null=True)
    scheme = models.ForeignKey(Scheme)
    data_sheet_elements = models.ManyToManyField(DataSheetElement)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['pid']


# 价格表，每个供应商可以有多份价格表
class PriceSheet(models.Model):
    pid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)  # 价格表描述
    price_sheet_elements = models.ManyToManyField(PriceSheetElement)
    vendor = models.ForeignKey(Company)

    def __str__(self):
        return self.name


# ========================= Fields ========================= #
# 数据表显示字段
class DataSheetField(models.Model):
    data_sheet = models.ForeignKey(DataSheet)
    display_name = models.CharField(max_length=255, blank=False, null=False)
    field_type = models.CharField(max_length=30, blank=True, null=True)
    sequence = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['sequence']


# 价格表显示字段
class PriceSheetField(models.Model):
    price_sheet = models.ForeignKey(PriceSheet)
    display_name = models.CharField(max_length=255, blank=False, null=False)
    field_type = models.CharField(max_length=30, blank=True, null=True)
    sequence = models.IntegerField()
    price_conditions = models.ManyToManyField(PriceCondition)  # 计价条件，例，一个价格可以对应重量和体积双重条件

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['sequence']


# ========================= DataSheet Level Settings ========================= #
# 数据表设置
class DataSheetSetting(models.Model):
    pid = models.IntegerField(primary_key=True)
    setting = models.ForeignKey(Setting)
    data_sheet = models.ForeignKey(DataSheet)
    value = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.setting.name

    class Meta:
        ordering = ['pid']


# ========================= Cost ========================= #
# 成本
class Cost(models.Model):
    pid = models.IntegerField(primary_key=True)  # 前部与DataSheetElement的pid相同，后部为price condition的pid
    value = models.FloatField()
    total = models.BooleanField()
    data_sheet_element = models.ForeignKey(DataSheetElement)  # 一个数据表元素可有多个成本








