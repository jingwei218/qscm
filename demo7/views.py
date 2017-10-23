from django.shortcuts import render
from django.http import HttpResponse
from qscm.settings import BASE_DIR
from .consumers import *
from .models import *
import json
import qrcode


# Create your views here.
def index(request):

    all_books = Book.objects.all()
    books = []
    for book in all_books:
        books.append({
            'name': book.name,
            'author': book.author,
            'publish_date': book.publish_date.isoformat(),
            'price': book.price
        })
    return render(request, 'demo7index.html',
                  {
                      'books': books,
                      'title': '7 Demos',
                  })


def multiupload(request):

    rec_files = request.FILES.getlist('fileuploads')
    for file in rec_files:
        file_path = BASE_DIR + '/demo7/uploads/' + file.name
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    return render(request, 'demo7index.html',
                  {
                      'title': '7 Demos',
                  })


def qrcgen(request):
    rec_json = json.loads(request.body.decode('utf-8'))
    url = rec_json['url']
    img = qrcode.make(url)
    img_path = BASE_DIR + '/demo7/uploads/qrcode.png'
    img.save(img_path)
    response_data = {'img_path': '/repo/qrcode.png'}
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )


def wspush(request):
    Channel('push-msg').send({'pushkey': 1})
    return HttpResponse('Complete')


def savetemplate(request):
    rec_json = json.loads(request.body.decode('utf-8'))
    ele_data = rec_json['printableElements']
    try:
        for data in ele_data:
            # 先查重

            printableElement = PrintableElement(name=data['name'],
                                                positionX=data['positionX'],
                                                positionY=data['positionY'],
                                                width=data['width'],
                                                height=data['height'])
            printableElement.save()
        response_data = {'save_message': 'Saved'}
    except:
        response_data = {'error_message': 'Error in saving printable elements'}

    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )
