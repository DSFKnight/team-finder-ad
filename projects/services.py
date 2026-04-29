from django.core.paginator import Paginator

from .constants import PROJECTS_PER_PAGE

def get_paginated_page(request, queryset, per_page=PROJECTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
