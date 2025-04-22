from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalogos/', include('apps.catalogos.urls')),
    path('procesos/', include('apps.procesos.urls')),
    path('', include('apps.login.urls')),
]
