from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django_ajax.decorators import ajax
from django.apps import apps
from django.views.decorators.csrf import csrf_protect
from .render import *
import json


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
            HorizonUser.objects.create_user(username=request.POST['username'], password=request.POST['password'])
            return HttpResponseRedirect('/' + platform_lower + '/login/')
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


# ========================= 项目 ========================= #
# 新建项目
def new_scheme(request):
    if request.user.is_authenticated():  # 用户已登录
        username = request.user.username
        settings = Setting.objects.filter(level=0)  # 设置项
        return render(request, 'newscheme.html',
        {
            'lang': 'en',
            'title': platform,
            'platform': platform,
            'username': username,
            'service': 'fusion',
            'settings': settings,
        })
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


# 保存新建项目
def save_n_create_scheme(request):
    if request.user.is_authenticated():  # 用户已登录
        rec_json = json.loads(request.body.decode('utf-8'))
        response_data = create_new_scheme(rec_json)
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


# 成本分析项目
def view_scheme(request, scheme_pid):
    if request.user.is_authenticated():  # 用户已登录
        username = request.user.username
        scheme = Scheme.objects.get(pid=scheme_pid)
        data_sheets = DataSheet.objects.filter(scheme=scheme)
        tables = render_data(data_sheets)

        return render(request, 'viewscheme.html',
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
def view_scheme_settings(request, scheme_pid):
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
def save_scheme_settings(request, scheme_pid):
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
