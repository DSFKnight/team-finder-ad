from django.urls import path

from . import views

app_name = 'users'

urlpatterns =[
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('list/', views.user_list_view, name='list'),
    path('edit-profile/', views.profile_edit_view, name='edit_profile'),
    
    # --- AJAX для навыков
    path('skills/', views.skill_autocomplete_view, name='skill_autocomplete'),
    path('<int:pk>/skills/add/', views.skill_add_view, name='skill_add'),
    path('<int:pk>/skills/<int:skill_id>/remove/', views.skill_remove_view, name='skill_remove'),

    path('change-password/', views.change_password_view, name='change_password'),
    
    path('<int:pk>/', views.user_detail_view, name='detail'),
]