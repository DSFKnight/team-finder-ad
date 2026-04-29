from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns =[
    path('admin/', admin.site.urls),
    # Переадресация с корневого пути на список проектов (требование задания)
    path('', RedirectView.as_view(url='/projects/list/', permanent=False)),
    
    # Подключаем пути наших приложений
    path('users/', include('users.urls')),
    path('projects/', include('projects.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)