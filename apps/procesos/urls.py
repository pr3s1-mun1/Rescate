from django.urls import path
from .views import *

urlpatterns = [
    path('servicios/', vista_main, name='vista_main'),
    path('buscador/', formulario_buscar, name='formulario_buscar'),
    path('crear/', formulario_servicio, name='formulario_servicio'),
    path('crear_servicio/', crear_servicio, name='crear_servicio'),
    path('carga_modifica/<pk>/', carga_modifica, name='carga_modifica'),
    path('guardar_todo/<str:pk>', guardar_todo, name='guardar_todo'),
    path('reporte_servicio/<str:clave>/', reporte_servicio, name='reporte_servicio'),

]