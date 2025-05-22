from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalogos/', include('apps.catalogos.urls')),
    path('servicios/', include('apps.procesos.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('graficas/', include('apps.graficas.urls')),
    path('', include('apps.login.urls')),
]
