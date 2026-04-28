from django.urls import path
from . import views

app_name = 'projects'

urlpatterns =[
    # Список проектов
    path('list/', views.project_list_view, name='list'),
    
    # Создание проекта
    path('create-project/', views.project_create_view, name='create'),
    
    # Просмотр одного проекта
    path('<int:pk>/', views.project_detail_view, name='detail'),
    
    # Редактирование проекта
    path('<int:pk>/edit/', views.project_edit_view, name='edit'),
    
    # Завершить проект (AJAX POST)
    path('<int:pk>/complete/', views.project_complete_view, name='complete'),
    
    # Присоединиться / Отказаться (POST)
    path('<int:pk>/toggle-participate/', views.project_participate_view, name='participate'),
]