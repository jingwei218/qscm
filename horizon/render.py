from .calculation import *
from django.core.exceptions import ObjectDoesNotExist


def render_data(data_sheets):
    tables = list()
    quantity_tables = list()
    for data_sheet in data_sheets:  # 遍历所有数据表

        data_sheet_elements = data_sheet.data_sheet_elements.all()  # 数据表中所有行

        tables.append({'name': data_sheet.name,  # 数据表名
                       'id': data_sheet.pid,  # 数据表pid
                       'table_header': [],  # 数据表列标题
                       'table_content': []  # 数据表内容
                       })

        data_sheet_fields = DataSheetField.objects.filter(data_sheet=data_sheet)
        number_of_data_fields = len(data_sheet_fields)
        number_of_price_fields = data_sheet.number_of_price_fields
        number_of_data_rows = len(data_sheet_elements)

        # 添加数据表标题栏
        for data_sheet_field in data_sheet_fields:
            tables[-1]['table_header'].append(data_sheet_field.display_name)

        row = 0  # 初始化行号
        price_header_list = [0] * number_of_price_fields  # 初始化价格显示标题列表
        price_matrix = [[0] * number_of_price_fields for x in range(0, number_of_data_rows)]  # 用于储存整张数据表的价格
        quantity_vector = [0] * number_of_data_rows  # 用于储存所有用于分配的数量
        quantity_matrix = [[0] * number_of_price_fields for x in range(0, number_of_data_rows)]  # 用于储存分配后的数量
        allocation_criteria = [[0, 0]] * number_of_price_fields  # 初始化数量分配条件列表，其中每一组分配条件的第一项为category，第二项为price_conditions

        for data_sheet_element in data_sheet_elements:  # 遍历所有行
            tables[-1]['table_content'].append({'id': data_sheet_element.pid,
                                                'row_content': [0] * number_of_data_fields
                                                })
            element = data_sheet_element.element  # 获得数据行对应的element
            vendor = data_sheet_element.vendor  # 获得数据行对应的vendor
            dse_category = data_sheet_element.category

            price_sheet_element = PriceSheetElement.objects.filter(element=element).filter(vendor=vendor)  # 检索出与当前行相关的价格
            if price_sheet_element:
                prices = Price.objects.filter(price_sheet_element=price_sheet_element)
                price_list_current_row = [0] * number_of_price_fields
                cost_list_current_row = [0] * number_of_price_fields

                # 遍历每一个price_sheet_element的每一个价格
                for price in prices:
                    price_uom = price.uom.name
                    price_currency = price.currency.name
                    price_unit = price_currency + '/' + price_uom  # 显示的计价单位
                    price_category = price.category

                    # 查询价格限制条件的显示名称，并结合计价单位添加入价格条件列表
                    price_conditions = price.price_conditions.all()
                    price_header = price_conditions[0].display_name + ' (' + price_unit + ')'
                    cost_header = price_conditions[0].display_name + ' (' + price_currency + ')'

                    if price_header not in price_header_list:
                        if price_conditions[0].group:
                            price_conditions = PriceCondition.objects.filter(group=price_conditions[0].group)
                        price_header_index = price_header_list.index(0)
                        price_header_list[price_header_index] = price_header  # 在第一个0值处进行储存
                        allocation_criteria[price_header_index] = [price.category, price_conditions]
                    else:
                        price_header_index = price_header_list.index(price_header)

                    price_list_current_row[price_header_index] = price.value  # 用于显示
                    price_matrix[row][price_header_index] = price.value  # 用于计算

            for data_sheet_field in data_sheet_fields:  # 遍历所有数据列
                field_type = data_sheet_field.field_type
                current_row = tables[-1]['table_content'][-1]['row_content']  # 最后一个数据表的最后一行
                data_sheet_field_index = data_sheet_field.sequence  #
                try:
                    row_value = None
                    if field_type == 'Increment':
                        row_value = row + 1
                    elif field_type == 'Location':
                        l = Location.objects.filter(element=element).get(sequence=data_sheet_field_index)
                        row_value = l.geo.name
                    elif field_type == 'Quantity':
                        quantities = Quantity.objects.filter(data_sheet_element=data_sheet_element)
                        q = quantities.get(sequence=data_sheet_field_index)
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
                        row_value = q.value
                        quantity_vector[row] = u_qty
                    elif field_type == 'Vendor':
                        v = data_sheet_element.vendor.name
                        row_value = v
                    elif field_type == 'Date':
                        d = data_sheet_element.start_date
                        row_value = d
                    elif field_type == 'Category':
                        c = data_sheet_element.category.name
                        row_value = c
                except ObjectDoesNotExist:
                    row_value = 0
                current_row[data_sheet_field_index] = row_value
            if price_list_current_row:
                current_row += price_list_current_row
            row += 1
        tables[-1]['table_header'] += price_header_list * 2
        q_matrix = allocate_quantity(quantity_vector, allocation_criteria, quantity_matrix)
        quantity_tables += q_matrix
    return tables, quantity_tables
