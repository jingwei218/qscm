from .calculation import *
from .lists import *
import re
import os


# 显示数据表、价格、成本数据
def render_data(datasheet):

    datatable = dict()  # 初始化数据表列表
    datatable['name'] = datasheet.name  # 数据表名
    datatable['id'] = datasheet.hash_pid  # 数据表hash_pid
    datatable['header'] = []  # 数据表列标题
    datatable['content'] = []  # 数据表内容
    datatable['locked'] = datasheet.data_locked
    datasheet_elements = datasheet.datasheet_elements.all()  # 数据表中所有行

    datasheet_fields = DataSheetField.objects.filter(datasheet=datasheet)
    number_of_data_fields = datasheet_fields.count()  # 数据字段个数
    number_of_data_rows = datasheet_elements.count()  # 数据行数
    data_matrix = [[0] * number_of_data_fields for x in range(0, number_of_data_rows)]
    quantity_vector = [0] * number_of_data_rows  # 用于储存所有用于分配的数量
    #number_of_price_fields = datasheet.number_of_price_fields  # 价格表字段个数
    #price_header_list = [0] * number_of_price_fields  # 初始化价格显示标题列表
    #price_matrix = [[0] * number_of_price_fields for x in range(0, number_of_data_rows)]  # 用于储存整张数据表的价格
    #quantity_header_list = [0] * number_of_price_fields  # 初始化数量分配标题列表
    #quantity_matrix_i = [[0] * number_of_price_fields for x in range(0, number_of_data_rows)]  # 用于储存分配后的数量
    #allocation_criteria = [[0, 0]] * number_of_price_fields  # 初始化数量分配条件列表，其中每一组分配条件的第一项为category，第二项为price_conditions

    # 添加数据表标题栏
    for datasheet_field in datasheet_fields:
        datatable['header'].append(datasheet_field.display_name)

    row = 0  # 初始化行号
    for datasheet_element in datasheet_elements:  # 遍历所有行

        #element = datasheet_element.element  # 获得数据行对应的element
        #vendor = datasheet_element.vendor  # 获得数据行对应的vendor
        #price_sheet_element = PriceSheetElement.objects.filter(element=element).filter(vendor=vendor)  # 检索出与当前行相关的价格

        for datasheet_field in datasheet_fields:  # 遍历所有数据列
            field_type = datasheet_field.field_type  # 获得字段类型
            datasheet_field_sequence = datasheet_field.sequence  # 获得字段在列表中的位置
            try:
                # 初始化单元格
                cell_value = None
                cell_id = None
                # 序列号
                if field_type == 'Serial':
                    cell_value = row + 1
                    cell_id = 0
                # 位置
                elif field_type == 'Location':
                    l = Location.objects.filter(datasheet_element=datasheet_element).get(sequence=datasheet_field_sequence)
                    cell_value = l.name
                    cell_id = l.hash_pid
                # 日期
                elif field_type == 'Date':
                    d = DataDate.objects.filter(datasheet_element=datasheet_element).get(sequence=datasheet_field_sequence)
                    cell_value = d.date
                    cell_id = d.hash_pid
                # 供应商
                elif field_type == 'Vendor':
                    v = datasheet_element.vendor
                    cell_value = v.name
                    cell_id = v.hash_pid
                # 数量
                elif field_type == 'Quantity':
                    quantities = Quantity.objects.filter(datasheet_element=datasheet_element)
                    q = quantities.get(sequence=datasheet_field_sequence)
                    cell_value = q.value
                    cell_id = q.hash_pid

                    chgu_q = quantities.filter(role='chgu')  # 已计算计费数量
                    sapc_q = quantities.filter(role='sapc')  # 与价格条件相同的计费单位的数量
                    mres_q = quantities.filter(role='mres')  # 多条件限定的计费数量

                    # 指定未分配量
                    if chgu_q:
                        u_qty = (chgu_q, 'chgu')
                    elif sapc_q:
                        u_qty = (sapc_q, 'sapc')
                    elif mres_q:
                        u_qty = (mres_q, 'mres')
                    quantity_vector[row] = u_qty  # 更新未分配的数量向量

            except ObjectDoesNotExist:
                cell_value = 0
            data_matrix[row][datasheet_field_sequence] = {'id': cell_id, 'value': cell_value}
        datatable['content'].append({'id': datasheet_element.hash_pid, 'values': data_matrix[row]})
        row += 1
    return datatable

        #if price_sheet_element:
        #    prices = Price.objects.filter(price_sheet_element=price_sheet_element)

            # 遍历每一个price_sheet_element的每一个价格
            #for price in prices:
            #    price_uom = price.uom.name
            #    price_currency = price.currency.name
            #    price_unit = price_currency + '/' + price_uom  # 显示的计价单位
            #    price_id = price.hash_pid

                # 查询价格限制条件的显示名称，并结合计价单位添加入价格条件列表
            #    price_conditions = price.price_conditions.all()
            #    price_header = price_conditions[0].display_name + ' (' + price_unit + ')'
            #    quantity_header = price_conditions[0].display_name
            #    cost_header = price_conditions[0].display_name + ' (' + price_currency + ')'

            #if price_header not in price_header_list:
            #        if price_conditions[0].group:
            #            price_conditions = PriceCondition.objects.filter(group=price_conditions[0].group)
            #        price_header_index = price_header_list.index(0)
            #        price_header_list[price_header_index] = price_header  # 在第一个0值处进行储存
            #        quantity_header_list[price_header_index] = quantity_header
            #        allocation_criteria[price_header_index] = [price.category, price_conditions]
            #    else:
            #        price_header_index = price_header_list.index(price_header)

            #    price_matrix[row][price_header_index] = {'id': price_id, 'value': price.value}  #

    #tables[-1]['table_header'] = data_header_list + price_header_list + quantity_header_list
    #quantity_matrix = allocate_quantity(quantity_vector, allocation_criteria, quantity_matrix_i)
    #for r in range(0, number_of_data_rows):
    #    tables[-1]['table_content'][r]['content'] = data_matrix[r] + price_matrix[r] + quantity_matrix[r]


# 根据前端传入Scheme级设置新建Scheme
def save_scheme_settings_to_json(rec_json):

    response_data = dict()
    scheme_settings = rec_json['scheme_settings']
    scheme_users = rec_json['scheme_users']
    mode = rec_json['mode']
    scheme_name = rec_json['scheme_name']
    r = re.compile(r'[A-Za-z0-9_.()\[\]\-]+')
    scheme_name = ''.join(r.findall(scheme_name))

    if mode == 'create':

        nbr_of_owners = 0

        try:
            scheme_pid = Scheme.objects.all().last().pid + 1
        except AttributeError:
            scheme_pid = 900000000  # 默认初始化Scheme的id
        scheme_hash_pid = hashed(scheme_pid)
        scheme_new = Scheme(pid=scheme_pid,
                            name=scheme_name,
                            setting_locked=False,
                            hash_pid=scheme_hash_pid)
        scheme_new.save()

        for scheme_setting in scheme_settings:
            scheme_setting_value = scheme_setting['scheme_setting_value']

            # 若项目设置有空值，则返回错误信息，删除已创建项目
            if scheme_setting_value == '':
                response_data['error_message'] = 'Setting value cannot be null.'
                SchemeSetting.objects.filter(scheme=scheme_new).delete()
                scheme_new.delete()
                return response_data

            setting_hash_pid = scheme_setting['setting_hash_pid']
            setting = Setting.objects.get(hash_pid=setting_hash_pid)

            try:
                scheme_setting_pid = SchemeSetting.objects.all().last().pid + 1
            except AttributeError:
                scheme_setting_pid = 4000

            scheme_setting_new = SchemeSetting(pid=scheme_setting_pid,
                                               value=scheme_setting_value,
                                               scheme=scheme_new,
                                               setting=setting,
                                               hash_pid=hashed(scheme_setting_pid))
            scheme_setting_new.save()

        for scheme_user in scheme_users:
            try:
                if scheme_user['user_selected']:
                    scheme_owner = HorizonUser.objects.get(hash_pid=scheme_user['user_hash_pid'])
                    scheme_new.owners.add(scheme_owner)
                    nbr_of_owners += 1
            except KeyError:  # 若无用户的hash_pid，有被篡改可能，删除已添加用户并返回错误信息
                owners = HorizonUser.objects.filter(scheme=scheme_new)
                for o in owners:
                    scheme_new.owners.remove(o)
                response_data['error_message'] = 'Owner does not match database.'
                scheme_new.delete()
                return response_data

        if nbr_of_owners == 0:  # 若无项目拥有者，则无法生成新项目
            response_data['error_message'] = 'Scheme must have at least 1 owner.'
            scheme_new.delete()
            return response_data

    elif mode == 'update':

        scheme_hash_pid = rec_json['scheme_hash_pid']
        scheme = Scheme.objects.get(hash_pid=scheme_hash_pid)

        for scheme_setting in scheme_settings:
            scheme_setting_value = scheme_setting['scheme_setting_value']
            # 若项目设置有空值，则返回错误信息
            if scheme_setting_value == '':
                response_data['error_message'] = 'Setting value cannot be null.'
                response_data['scheme_hash_pid'] = scheme_hash_pid
                return response_data

            setting_hash_pid = scheme_setting['setting_hash_pid']
            setting = Setting.objects.get(hash_pid=setting_hash_pid)

            scheme_setting_new = SchemeSetting.objects.filter(scheme=scheme).get(setting=setting)
            scheme_setting_new.value = scheme_setting_value
            scheme_setting_new.save()

        for scheme_user in scheme_users:
            scheme_owner = HorizonUser.objects.get(hash_pid=scheme_user['user_hash_pid'])
            if scheme_user['user_selected'] == 1 and scheme_user['user_status'] == 0:
                scheme.owners.add(scheme_owner)
            elif scheme_user['user_selected'] == 0 and scheme_user['user_status'] == 1:
                scheme.owners.remove(scheme_owner)

        nbr_of_owners = len(scheme.owners.all())
        if nbr_of_owners <= 0:
            response_data['error_message'] = 'Scheme must have at least 1 owner.'
            return response_data

        scheme.name = scheme_name
        scheme.save()

    response_data['scheme_hash_pid'] = scheme_hash_pid
    response_data['scheme_name'] = scheme_name

    return response_data


def get_scheme_settings_to_json(request, rec_json):

    response_data = dict()
    scheme_hash_pid = rec_json['scheme_hash_pid']

    scheme = Scheme.objects.get(hash_pid=scheme_hash_pid)
    scheme_setting_locked = scheme.setting_locked
    scheme_settings = SchemeSetting.objects.filter(scheme=scheme)
    scheme_owners = scheme.owners.all()

    username = request.user.username
    user_company = HorizonUser.objects.get(username=username).company
    users = HorizonUser.objects.filter(company=user_company)

    datasheets = DataSheet.objects.filter(scheme=scheme)

    response_data['scheme_name'] = scheme.name
    response_data['setting_locked'] = scheme_setting_locked
    response_data['scheme_settings'] = list()
    response_data['scheme_users'] = list()
    response_data['datasheets'] = list()


    owner_hashpid_list = list()
    for scheme_owner in scheme_owners:
        owner_hashpid_list.append(scheme_owner.hash_pid)

    for scheme_setting in scheme_settings:
        response_data['scheme_settings'].append({
            'setting_hash_pid': scheme_setting.setting.hash_pid,
            'scheme_setting_value': scheme_setting.value
        })

    for user in users:
        hash_pid = user.hash_pid
        if hash_pid in owner_hashpid_list:
            selected_owner = 1
        else:
            selected_owner = 0

        response_data['scheme_users'].append({
            'user_hash_pid': hash_pid,
            'user_username': user.username,
            'selected_owner': selected_owner
        })

    for data_sheet in datasheets:
        response_data['datasheets'].append({
            'datasheet_hash_pid': data_sheet.hash_pid,
            'datasheet_name': data_sheet.name,
            'number_of_price_fields': data_sheet.number_of_price_fields,
            'setting_locked': data_sheet.setting_locked
        })

    option_list['categories'] = list()
    categories = Category.objects.filter(level=1)
    for category in categories:
        option_list['categories'].append(category.name)
    response_data['option_list'] = option_list

    return response_data


def lock_scheme_settings_to_json(rec_json):

    response_data = dict()
    response_data['datasheets'] = list()

    scheme_hash_pid = rec_json['scheme_hash_pid']
    scheme_setting_locked = rec_json['scheme_setting_locked']

    scheme = Scheme.objects.get(hash_pid=scheme_hash_pid)
    scheme.setting_locked = scheme_setting_locked
    scheme.save()

    datasheets = DataSheet.objects.filter(scheme=scheme)
    for data_sheet in datasheets:
        response_data['datasheets'].append({
            'datasheet_hash_pid': data_sheet.hash_pid,
            'datasheet_name': data_sheet.name,
            'number_of_price_fields': data_sheet.number_of_price_fields,
            'setting_locked': data_sheet.setting_locked
        })

    option_list['categories'] = list()
    categories = Category.objects.filter(level=1)
    for category in categories:
        option_list['categories'].append(category.name)
    response_data['option_list'] = option_list

    return response_data


def save_datasheet_settings_to_json(rec_json):

    response_data = dict()
    scheme_hash_pid = rec_json['scheme_hash_pid']
    datasheet_category = rec_json['datasheet_category']
    datasheet_settings = rec_json['datasheet_settings']
    mode = rec_json['mode']
    datasheet_name = rec_json['datasheet_name']
    r = re.compile(r'[A-Za-z0-9_.()\[\]\-]+')
    datasheet_name = ''.join(r.findall(datasheet_name))  # 将文件名中的特殊符号去除

    scheme = Scheme.objects.get(hash_pid=scheme_hash_pid)
    category = Category.objects.get(name=datasheet_category)

    if mode == 'create':

        try:
            datasheet_pid = DataSheet.objects.all().last().pid + 1
        except AttributeError:
            datasheet_pid = 48000  # 默认初始化数据表的pid
        datasheet_hash_pid = hashed(datasheet_pid)
        datasheet_new = DataSheet(pid=datasheet_pid,
                                  name=datasheet_name,
                                  setting_locked=False,
                                  hash_pid=datasheet_hash_pid,
                                  category=category,
                                  scheme=scheme)
        datasheet_new.save()

        for datasheet_setting in datasheet_settings:
            datasheet_setting_value = datasheet_setting['datasheet_setting_value']

            # 若项目设置有空值，则返回错误信息，删除已创建项目
            if datasheet_setting_value == '':
                response_data['error_message'] = 'Setting value cannot be null.'
                DataSheetSetting.objects.filter(datasheet=datasheet_new).delete()
                datasheet_new.delete()
                return response_data

            setting_hash_pid = datasheet_setting['setting_hash_pid']
            setting = Setting.objects.get(hash_pid=setting_hash_pid)

            try:
                datasheet_setting_pid = DataSheetSetting.objects.all().last().pid + 1
            except AttributeError:
                datasheet_setting_pid = 40000

            datasheet_setting_new = DataSheetSetting(pid=datasheet_setting_pid,
                                                     value=datasheet_setting_value,
                                                     datasheet=datasheet_new,
                                                     setting=setting,
                                                     hash_pid=hashed(datasheet_setting_pid))
            datasheet_setting_new.save()

    elif mode == 'update':

        datasheet_hash_pid = rec_json['datasheet_hash_pid']
        datasheet = DataSheet.objects.get(hash_pid=datasheet_hash_pid)

        for datasheet_setting in datasheet_settings:
            datasheet_setting_value = datasheet_setting['datasheet_setting_value']
            # 若项目设置有空值，则返回错误信息
            if datasheet_setting_value == '':
                response_data['error_message'] = 'Setting value cannot be null.'
                response_data['datasheet_hash_pid'] = datasheet_hash_pid
                return response_data

            setting_hash_pid = datasheet_setting['setting_hash_pid']
            setting = Setting.objects.get(hash_pid=setting_hash_pid)

            datasheet_setting_new = DataSheetSetting.objects.filter(datasheet=datasheet).get(setting=setting)
            datasheet_setting_new.value = datasheet_setting_value
            datasheet_setting_new.save()

        datasheet.name = datasheet_name
        datasheet.category = category
        datasheet.save()

    response_data['datasheet_hash_pid'] = datasheet_hash_pid
    response_data['datasheet_name'] = datasheet_name

    return response_data


def get_datasheet_settings_to_json(rec_json):

    response_data = dict()
    datasheet_hash_pid = rec_json['datasheet_hash_pid']

    datasheet = DataSheet.objects.get(hash_pid=datasheet_hash_pid)
    datasheet_category = datasheet.category.name
    datasheet_setting_locked = datasheet.setting_locked
    datasheet_settings = DataSheetSetting.objects.filter(datasheet=datasheet)
    datasheet_fields = DataSheetField.objects.filter(datasheet=datasheet)

    response_data['datasheet_category'] = datasheet_category
    response_data['setting_locked'] = datasheet_setting_locked
    response_data['datasheet_settings'] = list()
    response_data['datasheet_fields'] = list()

    for datasheet_setting in datasheet_settings:
        response_data['datasheet_settings'].append({
            'setting_hash_pid': datasheet_setting.setting.hash_pid,
            'datasheet_setting_value': datasheet_setting.value,
        })

    for datasheet_field in datasheet_fields:
        response_data['datasheet_fields'].append({
            'field_name': datasheet_field.display_name,
            'field_sequence': datasheet_field.sequence,
            'field_type': datasheet_field.field_type
        })

    return response_data


def lock_datasheet_settings_to_json(rec_json):

    response_data = dict()
    response_data['datasheet_field_list'] = list()
    response_data['datasheet_fields'] = list()
    response_data['uoms'] = list()
    response_data['quantity_roles'] = quantity_roles

    datasheet_hash_pid = rec_json['datasheet_hash_pid']
    datasheet_setting_locked = rec_json['datasheet_setting_locked']

    datasheet = DataSheet.objects.get(hash_pid=datasheet_hash_pid)
    datasheet.setting_locked = datasheet_setting_locked
    datasheet.save()

    uoms = UoM.objects.all()
    for uom in uoms:
        response_data['uoms'].append({
            'name': uom.name,
            'uom_hash_pid': uom.hash_pid
        })

    if datasheet.datasheet_elements.count() > 0:
        response_data['datasheet_element_exists'] = True
    else:
        response_data['datasheet_element_exists'] = False

    datasheet_fields = DataSheetField.objects.filter(datasheet=datasheet)
    for datasheet_field in datasheet_fields:
        response_data['datasheet_fields'].append({
            'display_name': datasheet_field.display_name,
            'field_type': datasheet_field.field_type,
            'sequence': datasheet_field.sequence,
            'quantity_role': datasheet_field.quantity_role,
        })
        if datasheet_field.field_type == 'Quantity':
            try:
                response_data['datasheet_fields'][-1]['quantity_uom'] = datasheet_field.quantity_uom.name
            except AttributeError:
                response_data['datasheet_fields'][-1]['quantity_uom'] = datasheet_field.quantity_uom

    for field in datasheet_fields_set:
        response_data['datasheet_field_list'].append(field[0])

    response_data['xltemplate_file_name'] = datasheet.xltemplate_file_name

    return response_data


def save_datasheet_fields_to_json(rec_json):

    response_data = dict()
    datasheet_hash_pid = rec_json['datasheet_hash_pid']
    datasheet_template_fields = rec_json['datasheet_template_fields']

    datasheet = DataSheet.objects.get(hash_pid=datasheet_hash_pid)
    datasheet_fields = DataSheetField.objects.filter(datasheet=datasheet)
    datasheet_fields_count = datasheet_fields.count()

    wb_datasheet_template = Workbook()
    ws = wb_datasheet_template.active
    ws.title = datasheet.name

    for datasheet_template_field in datasheet_template_fields:

        display_name = datasheet_template_field['display_name']
        sequence = datasheet_template_field['sequence']
        field_type = datasheet_template_field['field_type']

        if display_name == '':
            response_data['error_message'] = 'Field cannot be null.'
            if datasheet_fields_count == 0:
                DataSheetField.objects.filter(datasheet=datasheet).delete()
            return response_data

        if field_type == 'Quantity':

            quantity_role = datasheet_template_field['quantity_role']
            quantity_uom = datasheet_template_field['quantity_uom']

            if quantity_uom == '':
                response_data['error_message'] = 'Quantity UoM cannot be null.'
                if datasheet_fields_count == 0:
                    DataSheetField.objects.filter(datasheet=datasheet).delete()
                return response_data

            # 查询是否有现成的UoM
            try:
                uom = UoM.objects.get(name=quantity_uom)
            except ObjectDoesNotExist:
                uom_pid = UoM.objects.all().last().pid + 1
                uom = UoM(pid=uom_pid, hash_pid=hashed(uom_pid), name=quantity_uom)
                uom.save()

            if datasheet_fields_count > 0:  # 更新字段名称
                datasheet_field = datasheet_fields.get(sequence=sequence)
                if datasheet.datasheet_elements.count() == 0:  # 当数据表中未有记录时可以调整字段类型和数量类型
                    datasheet_field.field_type = field_type
                    datasheet_field.display_name = display_name
                    datasheet_field.quantity_role = quantity_role
                    datasheet_field.quantity_uom = uom
            else:  # 新建
                datasheet_field = DataSheetField(sequence=sequence,
                                                 display_name=display_name,
                                                 field_type=field_type,
                                                 quantity_role=quantity_role,
                                                 quantity_uom=uom,
                                                 datasheet=datasheet)
        else:  # 非数量类型字段
            if datasheet_fields_count > 0:  # 更新字段名称
                datasheet_field = datasheet_fields.get(sequence=sequence)
                datasheet_field.display_name = display_name
                datasheet_field.quantity_role = None
                datasheet_field.quantity_uom = None
                if datasheet.datasheet_elements.count() == 0:  # 当数据表中未有记录时可以调整字段类型和数量类型
                    datasheet_field.field_type = field_type
            else:  # 新建
                datasheet_field = DataSheetField(sequence=sequence,
                                                 display_name=display_name,
                                                 field_type=field_type,
                                                 datasheet=datasheet)

        datasheet_field.save()

        ws.cell(row=1, column=sequence + 1, value=display_name)

    file_name = str(datasheet.pid) + '_' + datasheet.name
    file_name = file_name.replace(' ', '_')
    file_path = save_folders['datasheet_template']
    file_fullname = file_name + '.xlsx'
    file_fullpath = file_path + file_fullname
    wb_datasheet_template.save(file_fullpath)

    response_data['xltemplate_file_name'] = file_name
    datasheet.xltemplate_file_name = file_name
    datasheet.xltemplate_file_fullname = file_fullname
    datasheet.xltemplate_file_fullpath = file_fullpath
    datasheet.save()

    return response_data


def save_datasheet_upload(rec_file, file_path, datasheet):
    rec_file_name = rec_file.name
    r = re.compile(r'[A-Za-z0-9_.()\[\]\-]+')
    file_name = ''.join(r.findall(rec_file_name))
    if not os.path.exists(file_path):  # 不存在在目录时创建新目录
        os.makedirs(file_path)
    file_fullpath = file_path + file_name
    with open(file_fullpath, 'wb+') as destination:
        for chunk in rec_file.chunks():
            destination.write(chunk)
    clean_datasheet(datasheet)
    load_xl_datasheet(file_fullpath, datasheet)

    return file_name


def delete_datasheet(file_fullpath):
    os.remove(file_fullpath)
