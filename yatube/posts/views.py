from django.shortcuts import render


def index(request):
    template = 'posts/index.html'
    title = 'Yatube'
    context = {
        'title' : title,
        'text' : 'Это главная страница Yatube',
    }
    return render(request, template, context)


def group_posts(request):
    template = 'posts/<slag>:<slag>'
    title = 'Группы постов Yatube'
    context = {
        'title' : title,
        'text' : 'Здесь будет информация о группах проекта Yatube',
    }
    return render(request, template, context)


def group_list(request):
    template = 'posts/group_list.html'
    title = 'Лев Толстой – зеркало русской революции.'
    context = {
        'title' : title,
        'text' : 'TEXT_TEXT',
    }
    return render(request, template, context)
