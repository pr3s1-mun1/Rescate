from django.urls import path
from .views import *

urlpatterns = [
    path('servicios/', vista_principal, name='vista_main'),
    path('buscar/', formulario_buscar, name='formulario_buscar'),
    path('nuevo/', formulario_servicio, name='formulario_servicio'),
    path('creando/', crear_servicio, name='crear_servicio'),
    path('editar/<pk>/', carga_modifica, name='carga_modifica'),
    path('guardar_completo/<str:pk>', guardar_todo, name='guardar_todo'),
    path('reporte/<str:clave>/', reporte_servicio, name='reporte_servicio'),

]