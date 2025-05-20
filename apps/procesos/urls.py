from django.urls import path
from .views import *

urlpatterns = [
    path('servicios/', vista_principal, name='vista_main'),
    path('buscar/', formulario_buscar, name='formulario_buscar'),
    path('nuevo/', formulario_servicio, name='formulario_servicio'),
    path('creando/', crear_servicio, name='crear_servicio'),
    path('editar/<str:pk>/', carga_modifica, name='carga_modifica'),
    path('eliminar/<pk>/', eliminar_servicio, name='eliminar_servicio'),
    path('guardar_completo/<pk>/', guardar_todo, name='guardar_todo'),
    path('reporte/<str:clave>/', reporte_servicio, name='reporte_servicio'),


    path('exito/<str:pk>/', exito_guardado, name='exito_guardado'),
    path('fallo/', fallo_guardado, name='fallo_guardado'),
]