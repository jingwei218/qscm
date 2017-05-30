from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django_ajax.decorators import ajax
from django.apps import apps
from .models import *


appconfig = apps.get_app_config('horizon')
platform = HorizonSetting.objects.get(name='platform').value
platform_lower = platform.lower()


# 进入首页，包含登录链接
def index(request):
    return render(request, 'index.html',
                  {
                      'title': platform,
                      'platform': platform,
                  })


# ========================= 用户相关 ========================= #
# 用户注册
def user_register(request):
    if 'username' in request.POST:
        hu = HorizonUser.objects.filter(username=request.POST['username'])
        if len(hu) == 1:  # 当用户名存在时，显示错误信息
            return render(request, 'register.html',
                          {
                              'title': platform,
                              'error_message': 'The username already exists.',
                          })
        else:
            # codes: register user
            return HttpResponseRedirect('/' + platform_lower + '/')
    else:  # 进入注册页面时，无usernanme等登录信息传入POST
        return render(request, 'register.html',
                      {
                          'title': platform,
                      })


# 用户登录
def user_login(request):
    # 提交登录信息时
    if 'username' in request.POST:
        hu = HorizonUser.objects.filter(username=request.POST['username'])
        if hu:  # 找到用户名
            u = authenticate(username=request.POST['username'], password=request.POST['password'])
            if u:
                login(request, u)
                return HttpResponseRedirect('/' + platform_lower + '/services/')
            else:
                # 当登录信息有误时，显示错误信息
                return render(request, 'login.html',
                              {
                                  'title': platform,
                                  'platform': platform,
                                  'error_message': 'Incorrect password',
                              })
        else:  # 用户名未找到
            return render(request, 'login.html',
                          {
                              'title': platform,
                              'platform': platform,
                              'error_message': 'Incorrect username',
                          })
    else:  # 首次打开登录页面时，无usernanme等登录信息传入POST
        return render(request, 'login.html',
                      {
                          'title': platform,
                          'platform': platform,
                      })


# 用户登出
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/' + platform_lower + '/')


# 进入可用服务页面
def view_services(request):
    request.session.set_expiry(value=0)
    if request.user.is_authenticated():
        username = request.user.username
        services = Service.objects.filter(owners__username=username)
        return render(request, 'services.html',
                      {
                          'title': platform,
                          'username': username,
                          'services': services,
                          'platform': platform,
                      })
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


# ========================= 服务 ========================= #
# 采购成本分析
def service_fusion(request):
    if request.user.is_authenticated():
        username = request.user.username
        schemes = Scheme.objects.filter(owners__username=username)
        return render(request, 'fusion.html',
                      {
                          'lang': 'en',
                          'title': platform,
                          'platform': platform,
                          'username': username,
                          'service': 'fusion',
                          'schemes': schemes,
                      })
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


# 对账
def service_fission(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/' + platform_lower + '/')
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


# ========================= 服务 ========================= #
# 新建项目
def new_scheme(request):
    return HttpResponseRedirect('/' + platform_lower + '/')


# 成本分析项目
def view_scheme(request, scheme_pid):
    if request.user.is_authenticated():  # 用户已登录
        username = request.user.username
        scheme = Scheme.objects.get(pid=scheme_pid)
        data_sheets = DataSheet.objects.filter(scheme=scheme)
        tables = list()
        for data_sheet in data_sheets:  # 遍历所有数据表
            tables.append({'name': data_sheet.name,  # 数据表名
                           'id': data_sheet.pid,  # 数据表pid
                           'table_header': [],  # 数据表列标题
                           'table_content': []  # 数据表内容
                           })
            data_sheet_fields = data_sheet.datasheetfield_set.all()  # 数据表列标题
            for data_sheet_field in data_sheet_fields:
                tables[-1]['table_header'].append(data_sheet_field.data_field.display_name)

            data_sheet_elements = data_sheet.data_sheet_elements.all()  # 数据表每一行内容

            row = 1  # 初始化行号
            for data_sheet_element in data_sheet_elements:  # 遍历所有行
                tables[-1]['table_content'].append({'id': data_sheet_element.pid,
                                                    'content': []
                                                    })
                element = data_sheet_element.element  # 获得数据表每一行数据对应的element

                for data_sheet_field in data_sheet_fields:  # 遍历所有列
                    model_name = data_sheet_field.data_field.model_name
                    through = data_sheet_field.data_field.through
                    current_row = tables[-1]['table_content'][-1]['content']
                    if model_name is None:  # 没有model_name则显示行号
                        current_row.append(row)
                    else:  #
                        model = appconfig.get_model(model_name)  # 按model名称获得对象
                        attr_name = data_sheet_field.data_field.display_name_through_attribute  # 属性名称
                        try:
                            if through == 'Element':
                                query = model.objects.get(element=element)
                                current_row.append(getattr(query, attr_name))
                            elif through == 'Location':
                                query = model.objects.filter(element=element).filter(
                                    type=data_sheet_field.data_field.display_name)
                                location = []
                                for loc in query:
                                    location.append(getattr(loc.geo, attr_name))
                                location = "|".join(location)
                                if location != '':
                                    current_row.append(location)
                                else:
                                    raise ObjectDoesNotExist
                            elif through == 'Quantity':
                                uom = UoM.objects.get(name=data_sheet_field.data_field.display_name)
                                query = model.objects.filter(data_sheet_element=data_sheet_element).get(uom=uom)
                                current_row.append(getattr(query, attr_name))
                        except ObjectDoesNotExist:
                            current_row.append('N/A')
                row += 1

        return render(request, 'scheme.html',
                      {
                          'lang': 'en',
                          'title': scheme.name,
                          'platform': platform,
                          'username': username,
                          'service': 'fusion',
                          'scheme': scheme,
                          'data_sheets': data_sheets,
                          'tables': tables,
                      })
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


# Scheme和DataSheet的设置
def viewSchemeSetting(request, scheme_pid):
    if request.user.is_authenticated():
        username = request.user.username  # 用户名
        schemes = Scheme.objects.filter(owners__username=username)  # 筛选出用户名下的scheme集合
        scheme = Scheme.objects.get(pid=scheme_pid)  # 筛选出指定scheme
        scheme_name = scheme.name  # scheme的名称
        scheme_settings = SchemeSetting.objects.filter(scheme=scheme)  # scheme的所有设置项
        data_sheets = DataSheet.objects.filter(scheme=scheme)  # scheme对应的数据表集合
        data_sheet_settings_group = list()
        for data_sheet in data_sheets:
            selected_fields = list()
            data_sheet_fields = DataSheetField.objects.filter(data_sheet=data_sheet)
            for data_sheet_field in data_sheet_fields:
                selected_fields.append(data_sheet_field.data_field.display_name)
            data_sheet_settings_group.append({
                'id': data_sheet.pid,
                'name': data_sheet.name,
                'data_sheet_settings': DataSheetSetting.objects.filter(data_sheet=data_sheet),
                'data_sheet_fields': data_sheet_fields,
                'unselected_fields': DisplayField.objects.exclude(display_name__in=selected_fields)
            })

        return render(request, 'fusion.html',
                      {
                          'lang': 'en',
                          'title': 'Scheme Setting',
                          'username': username,
                          'schemes': schemes,
                          'scheme_settings': scheme_settings,
                          'scheme_name': scheme_name,
                          'data_sheets': data_sheets,
                          'data_sheet_settings_group': data_sheet_settings_group,
                      })


@ajax
def saveSchemeSetting(request, scheme_pid):
    scheme = Scheme.objects.get(pid=scheme_pid)
    setting_locked = scheme.setting_locked
    if request.user.is_authenticated() and not setting_locked:
        if request.POST:
            for setting_id in request.POST:
                try:
                    if setting_id[0] == 's':
                        setting = SchemeSetting.objects.get(pid=int(setting_id[1:]))
                    elif setting_id[0] == 'd':
                        setting = DataSheetSetting.objects.get(pid=int(setting_id[1:]))
                    setting.value = request.POST[setting_id]
                    setting.save()
                except:
                    return HttpResponseRedirect('/' + platform_lower + '/')
            return HttpResponseRedirect('/' + platform_lower + '/' + 'fusion/scheme/' + '/setting/' + str(scheme_pid))
