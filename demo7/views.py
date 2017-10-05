from django.shortcuts import render
from qscm.settings import BASE_DIR


# Create your views here.
def index(request):
    return render(request, 'demo7index.html',
                  {
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
