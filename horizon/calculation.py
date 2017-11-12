from django.core.exceptions import ObjectDoesNotExist
from openpyxl import *
from .models import *
import hashlib
import pandas as pd


def hashed(value):
    return hashlib.sha256(str(value).encode()).hexdigest()


def allocate_quantity(quantity_vector, criteria, quantity_matrix_i):
    """
    :param quantity_vector: 未分配数量的列表，每一项为(quantity, role, data_sheet_element category)
    :param criteria: 数量区间分配规则，每一项为[price category, price_conditions]
    :param quantity_matrix_i: 当前数据表的已分配的所有数量及其位置
    :param row: 当前行序号
    :return: quantity_matrix_i
    """

    number_of_criteria = len(criteria)

    # 自右向左遍历所有区间条件
    for i in range(number_of_criteria-1, -1, -1):
        price_category = criteria[i][0]  # 数量所对应分类，用于判断是否与数据行分类相同
        price_conditions = criteria[i][1]  # 价格条件，用于判断对应的数量是否位于区间内
        qty_range = dict()

        for price_condition in price_conditions:
            qty_range[price_condition.uom.name] = (price_condition.low, price_condition.high)

        row = 0
        for quantity_vector_element in quantity_vector:
            qty = quantity_vector_element[0]  # 数量对象
            qty_role = quantity_vector_element[1]  # 数量类型
            qty_category = quantity_vector_element[2]  # 业务类型
            if price_category == qty_category:
                if qty_role == 'chgu':  # 直接判断所处位置
                    qty_uom = qty[0].uom.name
                    try:
                        if qty_range[qty_uom][0] <= qty[0].value <= qty_range[qty_uom][1]:  # 找到uom对应的最低/最高限额，判断是否在区间内
                            quantity_matrix_i[row][i] = {'id': 0, 'value': qty[0].value}
                    except KeyError:
                        pass
                elif qty_role == 'sapc':
                    qty_uom = qty[0].uom
                    if qty_uom == price_conditions[0].uom:  # 直接对应uom
                        quantity_matrix_i[row][i] = {'id': 0, 'value': qty[0].value}
                elif qty_role == 'md':
                    q_in_range = [False] * len(qty)  # 判断值列表，当判断值列表中所有的元素为True，则判定在区间内
                    i_q = 0  # 初始化q的序号
                    for q in qty:
                        q_uom = q.uom.name
                        try:
                            if qty_range[q_uom][0] <= q.value <= qty_range[q_uom][1]:  # 找到uom对应的最低/最高限额，判断当前量是否在区间内
                                q_in_range[i_q] = True
                                i_q += 1
                            else:
                                break
                        except KeyError:
                            continue
                    try:
                        q_in_range.index(False)
                    except ValueError:
                        quantity_matrix_i[row][i] = {'id': 0, 'value': 1.0}

            row += 1
    return quantity_matrix_i


def chargeable_unit(base, conv, factor, compare):

    converted = conv * factor
    chargeable = converted
    return chargeable


def clean_datasheet(datasheet):

    # 清除location/quantity/datadate/datasheet_element
    datasheet_elements = DataSheetElement.objects.filter(datasheet=datasheet)
    for datasheet_element in datasheet_elements:
        datasheet_element.location_set.all().delete()
        datasheet_element.quantity_set.all().delete()
        datasheet_element.datadate_set.all().delete()
        datasheet_element.delete()


def load_xl_datasheet(file_fullpath, datasheet):

    # 通用参数
    category = datasheet.category
    category_pid = category.pid

    # 各类型字段
    # 必选字段
    datasheetfields = DataSheetField.objects.filter(datasheet=datasheet)
    serial_field = datasheetfields.get(field_type='Serial')
    vendor_field = datasheetfields.get(field_type='Vendor')
    # 可选字段
    quantity_fields = datasheetfields.filter(field_type='Quantity')
    location_fields = datasheetfields.filter(field_type='Location')
    date_fields = datasheetfields.filter(field_type='Date')

    # 排列参数
    location_cols = list()
    location_seqs = list()
    quantity_seqs = list()
    date_seqs = list()
    for field in location_fields:
        location_cols.append(field.display_name)  # 位置字段名称
        location_seqs.append(field.sequence)  # 位置字段序列
    for field in quantity_fields:
        quantity_seqs.append(field.sequence)  # 数量字段序列
    for field in date_fields:
        date_seqs.append(field.sequence)  # 日期字段序列
    serial_seq = serial_field.sequence  # 序号字段序列
    vendor_seq = vendor_field.sequence  # 供应商字段序列

    geo_checklist = dict()
    element_checklist = dict()
    vendor_checklist = dict()

    xl = pd.ExcelFile(file_fullpath)
    df = pd.read_excel(xl)

    last_location_pid = Location.objects.all().last().pid
    last_quantity_pid = Quantity.objects.all().last().pid

    for i, row in df.iterrows():  # 遍历每一行元素信息

        # element
        element_name = str(category_pid)  # 初始化元素名称
        for loc in row[location_cols]:  # 遍历每行中每一个位置信息
            if loc not in geo_checklist:  # 遍历记录
                # 查找地点信息，若找不到则新建地点信息。随后将找到或新建的地点信息pid号添加至元素名称中
                try:
                    geo = Geo.objects.get(name=loc)
                except ObjectDoesNotExist:
                    geo_pid = Geo.objects.all().last().pid + 1
                    geo = Geo(pid=geo_pid, hash_pid=hashed(geo_pid), name=loc)
                    geo.save()
                geo_checklist[loc] = geo
            else:
                geo = geo_checklist[loc]
            element_name += '-' + str(geo.pid)
        # 查找元素名称，若找不到则新建元素。
        if element_name not in element_checklist:
            try:
                element = Element.objects.filter(category=category).get(name=element_name)  # 确认是否已存在相同元素
            except ObjectDoesNotExist:
                element_pid = Element.objects.all().last().pid + 1  # 不存在相同元素时新建
                element = Element(pid=element_pid, hash_pid=hashed(element_pid), name=element_name, category=category)
                element.save()
            element_checklist[element_name] = element
        else:
            element = element_checklist[element_name]

        # vendor
        vendor_name = row[vendor_seq]
        if vendor_name not in vendor_checklist:
            try:
                vendor = Company.objects.get(name=vendor_name)  # 确认是否已存在相同公司名称
            except ObjectDoesNotExist:
                vendor_pid = Company.objects.all().last().pid + 1
                vendor = Company(pid=vendor_pid, hash_pid=hashed(vendor_pid), name=vendor_name)
                vendor.save()
            vendor_checklist[vendor_name] = vendor
        else:
            vendor = vendor_checklist[vendor_name]

        # datasheet element
        datasheet_element_pid = DataSheetElement.objects.all().last().pid + 1
        datasheet_element = DataSheetElement(pid=datasheet_element_pid, hash_pid=hashed(datasheet_element_pid),
                                             element=element, vendor=vendor)
        datasheet_element.save()

        # location
        for location_seq in location_seqs:
            location_name = row[location_seq]
            geo = geo_checklist[location_name]
            last_location_pid += 1
            location = Location(pid=last_location_pid, hash_pid=hashed(last_location_pid), sequence=location_seq,
                                datasheet_element=datasheet_element, name=location_name, geo=geo)
            location.save()

        # quantity
        for quantity_seq in quantity_seqs:
            quantity_value = row[quantity_seq]
            quantity_field = quantity_fields.get(sequence=quantity_seq)
            quantity_role = quantity_field.quantity_role
            quantity_uom = quantity_field.quantity_uom
            quantity_comparison = datasheet.datasheetsetting_set.get(setting=1033).value
            quantity_conv_factor = float(datasheet.datasheetsetting_set.get(setting=1032).value)
            last_quantity_pid += 1
            quantity = Quantity(pid=last_quantity_pid, hash_pid=hashed(last_quantity_pid), sequence=quantity_seq,
                                datasheet_element=datasheet_element, value=quantity_value, uom=quantity_uom,
                                role=quantity_role, converting_factor=quantity_conv_factor, comparison=quantity_comparison)
            quantity.save()

        # datasheet
        datasheet.datasheet_elements.add(datasheet_element)
