from django.urls import path
from .views import *

urlpatterns = [
    path('reportes/', cargar_reportes, name='cargar_reportes'),
    path('reportes/servicios/', reporte_servicios, name='reporte_servicios'),

]