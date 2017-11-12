from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .render import *
import json

# platform = HorizonSetting.objects.get(name='platform').value
# platform_lower = platform.lower()
platform = 'Horizon'
platform_lower = 'horizon'


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
        user_company = HorizonUser.objects.get(username=username).company
        users = HorizonUser.objects.filter(company=user_company)
        schemes = Scheme.objects.filter(owners__username=username)
        scheme_settings = Setting.objects.filter(level=0)  # 项目设置项
        datasheet_settings = Setting.objects.filter(level=1)  # 数据表设置项
        return render(request, 'fusion.html',
                      {
                          'lang': 'en',
                          'title': platform,
                          'platform': platform,
                          'username': username,
                          'service': 'fusion',
                          'schemes': schemes,
                          'scheme_settings': scheme_settings,
                          'datasheet_settings': datasheet_settings,
                          'users': users,
                          'company': user_company.name,
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
# 保存新建项目
def save_scheme_settings(request):

    if request.user.is_authenticated():  # 用户已登录
        rec_json = json.loads(request.body.decode('utf-8'))  # 前端发送来的json
        response_data = save_scheme_settings_to_json(rec_json)  # 解析json，并创建新的项目，生成返回信息
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


def get_scheme_settings(request):

    if request.user.is_authenticated():  # 用户已登录
        rec_json = json.loads(request.body.decode('utf-8'))  # 前端发送来的json
        response_data = get_scheme_settings_to_json(request, rec_json)  # 解析json，并创建新的项目，生成返回信息
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


def lock_scheme_settings(request):

    if request.user.is_authenticated():
        rec_json = json.loads(request.body.decode('utf-8'))  # 前端发送来的json
        response_data = lock_scheme_settings_to_json(rec_json)  # 解析json，并创建新的项目，生成返回信息
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


def save_datasheet_settings(request):

    if request.user.is_authenticated():  # 用户已登录
        rec_json = json.loads(request.body.decode('utf-8'))  # 前端发送来的json
        response_data = save_datasheet_settings_to_json(rec_json)  # 解析json，并创建新的项目，生成返回信息
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


def get_datasheet_settings(request):

    if request.user.is_authenticated():
        rec_json = json.loads(request.body.decode('utf-8'))
        response_data = get_datasheet_settings_to_json(rec_json)
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )


def lock_datasheet_settings(request):

    if request.user.is_authenticated():
        rec_json = json.loads(request.body.decode('utf-8'))  # 前端发送来的json
        response_data = lock_datasheet_settings_to_json(rec_json)  # 解析json，并创建新的项目，生成返回信息
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


def save_datasheet_fields(request):

    if request.user.is_authenticated():
        rec_json = json.loads(request.body.decode('utf-8'))  # 前端发送来的json
        response_data = save_datasheet_fields_to_json(rec_json)  # 解析json，并创建新的项目，生成返回信息
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


def get_datasheet_template(request, datasheet_hash_pid):

    if request.user.is_authenticated():

        datasheet = DataSheet.objects.get(hash_pid=datasheet_hash_pid)
        file_fullpath = datasheet.xltemplate_file_fullpath
        file_fullname = datasheet.xltemplate_file_fullname

        with open(file_fullpath, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/vnd.ms-excel")  # application/force-download
            response['Content-Disposition'] = 'inline; filename={0}'.format(file_fullname)
            return response

    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


def upload_datasheet_file(request):

    if request.user.is_authenticated():

        response_data = dict()
        try:
            datasheet_hash_pid = request.POST['datasheet_hash_pid']
            datasheet = DataSheet.objects.get(hash_pid=datasheet_hash_pid)
            datasheet_pid = datasheet.pid
            rec_file = request.FILES["datasheet_file"]  # 前端发送来的文件
            file_path = save_folders['datasheet_file'] + str(datasheet_pid) + '/'  # 每个数据表创建单独的目录
            file_name = save_datasheet_upload(rec_file, file_path, datasheet)
            datasheet.xldatasheet_file_name = file_name
            datasheet.save()
            response_data['xldatasheet_file_name'] = file_name

        except KeyError:
            response_data = {'error_message': 'No file was selected.'}

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')


# 成本分析项目
def get_datasheets(request, scheme_hash_pid):

    if request.user.is_authenticated():  # 用户已登录
        username = request.user.username
        scheme = Scheme.objects.get(hash_pid=scheme_hash_pid)
        datasheets = DataSheet.objects.filter(scheme=scheme)
        datatables = list()

        for datasheet in datasheets:
            datatable = render_data(datasheet)
            datatables.append(datatable)

        return render(request, 'datasheets.html',
                      {
                          'lang': 'en',
                          'title': scheme.name,
                          'platform': platform,
                          'username': username,
                          'service': 'fusion',
                          'scheme': scheme,
                          'datatables': datatables,

                      })
    else:
        return HttpResponseRedirect('/' + platform_lower + '/')
