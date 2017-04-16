from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django_ajax.decorators import ajax
from django.apps import apps
from .models import *
from . import templates


appconfig = apps.get_app_config('horizon')


# 进入首页，包含登录链接
def index(request):
    return render(request, 'index.html',
                  {
                      'title': 'Quantum Horizon',
                  })


def userRegister(request):
    if 'username' in request.POST:
        hu = HorizonUser.objects.filter(username=request.POST['username'])
        if len(hu) == 1:  # 当用户名存在时，显示错误信息
            return render(request, 'register.html',
                          {
                              'title': 'Quantum Horizon Login',
                              'error_message': 'The username already exists.',
                          })
        else:
            # codes: register user
            return HttpResponseRedirect('/horizon/')
    else:  # 进入注册页面时，无usernanme等登录信息传入POST
        return render(request, 'register.html',
                      {
                          'title': 'Quantum Horizon Register',
                      })


# 用户登录页面
def userLogin(request):
    # 提交登录信息时
    if 'username' in request.POST:
        hu = HorizonUser.objects.filter(username=request.POST['username'])
        if list(hu) != []:
            u = authenticate(username=request.POST['username'], password=request.POST['password'])
        else:
            u = None
        if u is not None:
            login(request, u)
            return HttpResponseRedirect('/horizon/services/')
        else:
            # 当登录信息有误时，显示错误信息
            return render(request, 'login.html',
                          {
                              'title': 'Quantum Horizon Login',
                              'error_message': 'Incorrect username or password',
                          })
    else:  # 首次打开登录页面时，无usernanme等登录信息传入POST
        return render(request, 'login.html',
                      {
                          'title': 'Quantum Horizon Login',
                      })


# 用户登出
def userLogout(request):
    logout(request)
    return HttpResponseRedirect('/horizon/')


# 进入可用服务页面
def services(request):
    request.session.set_expiry(value=0)
    if request.user.is_authenticated():
        username = request.user.username
        services = Service.objects.filter(owners__username=username)
        return render(request, 'services.html',
                      {
                          'title': 'Quantum Horizon Services',
                          'username': username,
                          'services': services,
                      })
    else:
        return HttpResponseRedirect('/horizon/')


def dawn(request):

    if request.user.is_authenticated():
        username = request.user.username
        schemes = Scheme.objects.filter(owners__username=username)
        return render(request, 'dawn.html',
                      {
                          'lang': 'en',
                          'title': 'test',
                          'username': username,
                          'schemes': schemes,
                      })
    else:
        return HttpResponseRedirect('/horizon/')


def newScheme(request):
    return HttpResponseRedirect('/horizon/')


def viewScheme(request, scheme_pid):

    if request.user.is_authenticated():

        username = request.user.username
        scheme = Scheme.objects.get(pid=scheme_pid)
        data_sheets = DataSheet.objects.filter(scheme=scheme)
        data_sheet_tables = list()
        for data_sheet in data_sheets:  # 遍历所有数据表
            data_sheet_tables.append({'name': data_sheet.name,  # 数据表名
                                      'id': data_sheet.pid,  # 数据表pid
                                      'table_header': [],  # 数据表列标题
                                      'table_content': []  # 数据表内容
                                      })
            data_sheet_fields = data_sheet.datasheetfield_set.all()  # 数据表列标题
            for data_sheet_field in data_sheet_fields:
                data_sheet_tables[-1]['table_header'].append(data_sheet_field.data_field.display_name)

            data_sheet_elements = data_sheet.data_sheet_elements.all()  # 数据表每一行内容

            row = 1  # 初始化行号
            for data_sheet_element in data_sheet_elements:  # 遍历所有行
                data_sheet_tables[-1]['table_content'].append({'id': data_sheet_element.pid,
                                                               'content': []
                                                               })
                element = data_sheet_element.element  # 获得数据表每一行数据对应的element

                for data_sheet_field in data_sheet_fields:  # 遍历所有列
                    model_name = data_sheet_field.data_field.model_name
                    through = data_sheet_field.data_field.through
                    current_row = data_sheet_tables[-1]['table_content'][-1]['content']
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
                          'title': 'scheme',
                          'username': username,
                          'scheme': scheme,
                          'data_sheets': data_sheets,
                          'data_sheet_tables': data_sheet_tables,
                      })
    else:
        return HttpResponseRedirect('/horizon/')


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
                'unselected_fields': DataField.objects.exclude(display_name__in=selected_fields)
            })

        return render(request, 'dawn.html',
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
                    return HttpResponseRedirect('/horizon/')
            return HttpResponseRedirect('/horizon/dawn/scheme/' + '/setting/' + str(scheme_pid))
