from django.conf import settings
from django.core.paginator import Paginator


def get_posts_paginator(queryset, request):
    paginator = Paginator(queryset, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
