from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('Главная страница проекта')

def group_posts(request):
    return HttpResponse('Страница с группированными постами')