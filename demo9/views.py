from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from qscm.settings import BASE_DIR
from .consumers import *
from .models import *
import json
import qrcode
import string
import random
import os

demo9 = apps.get_app_config('demo9')


# Create your views here.
def index(request):

    books = Book.objects.all()
    return render(request, 'demo9index.html',
                  {
                      'books': books,
                      'title': 'Demo9',
                  })


def multiupload(request):

    rec_files = request.FILES.getlist('fileuploads')
    for file in rec_files:
        file_path = BASE_DIR + '/demo9/uploads/' + file.name
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    return HttpResponseRedirect('/demo9')


def qrcgen(request):
    rec_json = json.loads(request.body.decode('utf-8'))
    qrc_content = dict()
    qrc_content['url'] = rec_json['url']

    s = string.ascii_letters + '_'
    while True:
        random_code = ''.join(random.choice(s) for i in range(16))
        file_path = BASE_DIR + '/demo9/uploads/' + random_code + '/'
        if not os.path.exists(file_path):  # 不存在在目录时创建新目录
            os.makedirs(file_path)
            break
    qrc_content['path_token'] = random_code
    qrcode_img = qrcode.make(qrc_content['url'])
    qrcode_img_storage_path = file_path + 'qrcode.png'
    qrcode_img.save(qrcode_img_storage_path)

    response_data = {
        'img_path': '/demo9repo/' + random_code + '/qrcode.png',
    }
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )


def wspush(request):
    Channel('push-msg').send({'pushkey': 1})
    return HttpResponse('Complete')


def addelement(request):
    rec_json = json.loads(request.body.decode('utf-8'))
    node = rec_json['node']
    response_data = dict()

    if node != 'label':
        # get model
        model_name = rec_json['model_name']
        filter_conditon_string = rec_json['filter_condition_string']
        col_string = rec_json['col_string']
        html = None
        try:
            model = demo9.get_model(model_name)
        except LookupError:
            response_data['error_message'] = 'No model'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        # filter
        queryset, response_data = getqueryset(model, filter_conditon_string, response_data)
        if 'error_message' in response_data:
            return HttpResponse(json.dumps(response_data), content_type="application/json")
        # get response each column
        response_data = getresponse(node, queryset, col_string, response_data)
        if 'error_message' in response_data:
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        model_name = None
        filter_conditon_string = None
        col_string = None
        html = rec_json['label_text']
        if html == '':
            response_data['error_message'] = 'No text'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    try:
        node_id = TemplateElement.objects.last().node_id + 1
    except AttributeError:
        node_id = 1

    template_name = rec_json['template_name']
    tpl, response_data = gettemplate(template_name, response_data)
    if 'error_message' in response_data:
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    template_element = TemplateElement(node=node, node_id=node_id, status='new',
                                       modelName=model_name,
                                       filterConditions=filter_conditon_string,
                                       columns=col_string,
                                       html=html,
                                       reportTemplate=tpl)
    template_element.save()
    response_data.update({'node_eid': node + '-' + str(node_id)})
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def savetemplate(request):
    rec_json = json.loads(request.body.decode('utf-8'))
    template_elements = rec_json['templateElements']
    response_data = dict()

    if len(template_elements) == 0:
        response_data['error_message'] = 'No element found'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    for template_element in template_elements:
        node_id = template_element['node_id']
        te = TemplateElement.objects.get(node_id=node_id)
        te.positionX = template_element['positionX']
        te.positionY = template_element['positionY']
        te.width = template_element['width']
        te.height = template_element['height']
        te.status = 'saved'
        te.save()
    response_data['message'] = 'Template elements are saved'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def loadtemplate(request):
    rec_json = json.loads(request.body.decode('utf-8'))
    template_name = rec_json['template_name']
    response_data = dict()

    try:
        report_template = ReportTemplate.objects.get(name=template_name.upper())
    except ObjectDoesNotExist:
        response_data.update({'error_message': 'Template does not exist'})
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    tes = TemplateElement.objects.filter(reportTemplate=report_template).filter(status='saved')
    if len(tes) == 0:
        response_data.update({'error_message': 'No element found'})
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    response_data.update({'templateElements': dict()})
    for te in tes:
        node = te.node
        node_id = te.node_id
        node_eid = node + '-' + str(node_id)
        modelName = te.modelName
        filterConditions = te.filterConditions
        columns = te.columns
        html = te.html
        response_data_temp = dict()

        if node != 'label':
            model = demo9.get_model(modelName)
            queryset, response_data_temp = getqueryset(model, filterConditions, response_data_temp)
            if 'error_message' in response_data:
                return HttpResponse(json.dumps(response_data_temp), content_type="application/json")
            # get response each column
            response_data_temp = getresponse(node, queryset, columns, response_data_temp)
            if 'error_message' in response_data:
                return HttpResponse(json.dumps(response_data_temp), content_type="application/json")
            context = response_data_temp['context']
        else:
            context = te.html

        response_data['templateElements'].update({
            node_eid: {
                'node': node,
                'node_eid': node_eid,
                'context': context,
                'modelName': modelName,
                'filterConditions': filterConditions,
                'columns': columns,
                'positionX': te.positionX,
                'positionY': te.positionY,
                'width': te.width,
                'height': te.height,
                'message': 'Loaded'
            }
        })

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def getqueryset(model, filter_conditon_string, response_data):
    if filter_conditon_string != '':
        queryset = model.objects
        filter_conditions = filter_conditon_string.split(',')
        try:
            for filter_condition in filter_conditions:
                condition_components = filter_condition.split(':')
                lhs = condition_components[0]
                rhs = condition_components[1]
                queryset = queryset.filter(**{lhs: rhs})
        except:
            response_data.update({'error_message': 'Filter condition error: ' + filter_conditon_string})
            queryset = None
    else:
        queryset = model.objects.all()
    return queryset, response_data


def getresponse(node, queryset, col_string, response_data):
    table = dict()
    try:
        if node == 'table':
            i = 0
            cols = col_string.split(',')
            for query in queryset:
                table[i] = dict()
                for col in cols:
                    table[i][col] = str(getattr(query, col))
                i += 1
            response_data.update({'context': table})
        elif node == 'field':
            col = col_string
            query = queryset[0]
            field = str(getattr(query, col))
            response_data.update({'context': field})
    except AttributeError:
        response_data.update({'error_message': 'Field(s) incorrect'})
    return response_data


def gettemplate(template_name, response_data):
    if template_name == '':
        response_data['error_message'] = 'No template name'
        tpl = None
    else:
        template_name_uc = template_name.upper()
        tpl = ReportTemplate.objects.filter(name=template_name_uc)
        if len(tpl) == 0:
            try:
                tid = ReportTemplate.objects.last().tid + 1
            except AttributeError:
                tid = 1
            tpl = ReportTemplate(tid=tid, name=template_name_uc)
            tpl.save()
            response_data['message'] = template_name + ' is created.'
        else:
            tpl = tpl[0]
            response_data['message'] = template_name + ' is retrieved.'
    return tpl, response_data
