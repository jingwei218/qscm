from .calculation import *
from django.core.exceptions import ObjectDoesNotExist


# 显示数据表、价格、成本数据
def render_data(data_sheets):
    tables = list()  # 初始化数据表列表
    for data_sheet in data_sheets:  # 遍历所有数据表
        data_sheet_elements = data_sheet.data_sheet_elements.all()  # 数据表中所有行

        tables.append({'name': data_sheet.name,  # 数据表名
                       'id': data_sheet.pid,  # 数据表pid
                       'table_header': [],  # 数据表列标题
                       'table_content': [],  # 数据表内容
                       })

        data_sheet_fields = DataSheetField.objects.filter(data_sheet=data_sheet)
        number_of_data_fields = len(data_sheet_fields)  # 数据字段个数
        number_of_data_rows = len(data_sheet_elements)  # 数据行数
        number_of_price_fields = data_sheet.number_of_price_fields  # 价格表字段个数
        data_header_list = list()  # 初始化数据标题列表
        data_matrix = [[0] * number_of_data_fields for x in range(0, number_of_data_rows)]
        price_header_list = [0] * number_of_price_fields  # 初始化价格显示标题列表
        price_matrix = [[0] * number_of_price_fields for x in range(0, number_of_data_rows)]  # 用于储存整张数据表的价格
        quantity_header_list = [0] * number_of_price_fields  # 初始化数量分配标题列表
        quantity_vector = [0] * number_of_data_rows  # 用于储存所有用于分配的数量
        quantity_matrix_i = [[0] * number_of_price_fields for x in range(0, number_of_data_rows)]  # 用于储存分配后的数量
        allocation_criteria = [[0, 0]] * number_of_price_fields  # 初始化数量分配条件列表，其中每一组分配条件的第一项为category，第二项为price_conditions

        # 添加数据表标题栏
        for data_sheet_field in data_sheet_fields:
            data_header_list.append(data_sheet_field.display_name)

        row = 0  # 初始化行号
        for data_sheet_element in data_sheet_elements:  # 遍历所有行

            tables[-1]['table_content'].append({'id': data_sheet_element.pid, 'content': None})

            element = data_sheet_element.element  # 获得数据行对应的element
            vendor = data_sheet_element.vendor  # 获得数据行对应的vendor
            dse_category = data_sheet_element.category
            price_sheet_element = PriceSheetElement.objects.filter(element=element).filter(vendor=vendor)  # 检索出与当前行相关的价格

            for data_sheet_field in data_sheet_fields:  # 遍历所有数据列
                field_type = data_sheet_field.field_type
                data_sheet_field_index = data_sheet_field.sequence  #
                try:
                    cell_value = None
                    cell_id = None
                    if field_type == 'Increment':
                        cell_value = row + 1
                        cell_id = 0
                    elif field_type == 'Location':
                        l = Location.objects.filter(element=element).get(sequence=data_sheet_field_index)
                        cell_value = l.geo.name
                        cell_id = l.pid
                    elif field_type == 'Quantity':
                        quantities = Quantity.objects.filter(data_sheet_element=data_sheet_element)
                        q = quantities.get(sequence=data_sheet_field_index)
                        cell_value = q.value
                        cell_id = q.id

                        chgu_q = quantities.filter(role='chgu')  # 已计算计费数量
                        sapc_q = quantities.filter(role='sapc')  # 与价格条件相同的计费单位的数量
                        md_q = quantities.filter(role='md')  # 多维条件限定的计费数量
                        # 指定未分配量
                        if chgu_q:
                            u_qty = (chgu_q, 'chgu', dse_category)
                        elif sapc_q:
                            u_qty = (sapc_q, 'sapc', dse_category)
                        elif md_q:
                            u_qty = (md_q, 'md', dse_category)
                        quantity_vector[row] = u_qty
                    elif field_type == 'Vendor':
                        v = data_sheet_element.vendor
                        cell_value = v.name
                        cell_id = v.pid
                    elif field_type == 'Date':
                        d = data_sheet_element.start_date
                        cell_value = d
                    elif field_type == 'Category':
                        c = data_sheet_element.category
                        cell_value = c.name
                        cell_id = c.pid
                except ObjectDoesNotExist:
                    cell_value = 0
                data_matrix[row][data_sheet_field_index] = {'id': cell_id, 'value': cell_value}

            if price_sheet_element:
                prices = Price.objects.filter(price_sheet_element=price_sheet_element)

                # 遍历每一个price_sheet_element的每一个价格
                for price in prices:
                    price_uom = price.uom.name
                    price_currency = price.currency.name
                    price_unit = price_currency + '/' + price_uom  # 显示的计价单位
                    price_id = price.pid

                    # 查询价格限制条件的显示名称，并结合计价单位添加入价格条件列表
                    price_conditions = price.price_conditions.all()
                    price_header = price_conditions[0].display_name + ' (' + price_unit + ')'
                    quantity_header = price_conditions[0].display_name
                    cost_header = price_conditions[0].display_name + ' (' + price_currency + ')'

                    if price_header not in price_header_list:
                        if price_conditions[0].group:
                            price_conditions = PriceCondition.objects.filter(group=price_conditions[0].group)
                        price_header_index = price_header_list.index(0)
                        price_header_list[price_header_index] = price_header  # 在第一个0值处进行储存
                        quantity_header_list[price_header_index] = quantity_header
                        allocation_criteria[price_header_index] = [price.category, price_conditions]
                    else:
                        price_header_index = price_header_list.index(price_header)

                    price_matrix[row][price_header_index] = {'id': price_id, 'value': price.value}  #

            row += 1
        tables[-1]['table_header'] = data_header_list + price_header_list + quantity_header_list
        quantity_matrix = allocate_quantity(quantity_vector, allocation_criteria, quantity_matrix_i)
        for r in range(0, number_of_data_rows):
            tables[-1]['table_content'][r]['content'] = data_matrix[r] + price_matrix[r] + quantity_matrix[r]

    return tables


# 根据前端传入Scheme级设置新建Scheme
def create_new_scheme(rec_json):
    response_data = dict()
    scheme_name = rec_json['scheme_name']
    scheme_settings = rec_json['scheme_settings']
    mode = rec_json['mode']
    if mode == 'create':
        try:
            scheme_pid = Scheme.objects.all().last().pid + 1
        except AttributeError:
            scheme_pid = 900000000  # 默认初始化Scheme的id
        scheme_new = Scheme(pid=scheme_pid,
                            name=scheme_name,
                            setting_locked=False)
        scheme_new.save()
    elif mode == 'update':
        scheme_new = Scheme.objects.get(pid=scheme_pid)

    for scheme_setting in scheme_settings:
        setting_pid = int(scheme_setting['setting_pid'])
        scheme_setting_value = scheme_setting['scheme_setting_value']
        setting = Setting.objects.get(pid=setting_pid)
        # 若项目设置有空值，则返回错误信息，删除已创建项目
        if scheme_setting_value == '':
            response_data['error_message'] = 'Setting <' + setting.name + '> value cannot be null.'
            if mode == 'create':
                scheme_new.delete()
            return response_data
        try:
            scheme_setting_pid = SchemeSetting.objects.all().last().pid + 1
        except AttributeError:
            scheme_setting_pid = 4000
        scheme_setting_new = SchemeSetting(pid=scheme_setting_pid,
                                           value=scheme_setting_value,
                                           scheme=scheme_new,
                                           setting=setting)
        scheme_setting_new.save()
    
    response_data['scheme_pid'] = scheme_pid
    response_data['status'] = 'success'

    return response_data
