from django.urls import path
from .views import *

urlpatterns = [
    path('servicios/', vista_principal, name='vista_main'),
    path('buscar/', formulario_buscar, name='formulario_buscar'),
    path('nuevo/', formulario_servicio, name='formulario_servicio'),
    path('creando/', crear_servicio, name='crear_servicio'),
    path('editar/<str:pk>/', carga_modifica_v2, name='carga_modifica_v2'),
    path('editar/<str:pk>/<str:ps>/', carga_modifica_v2, name='carga_modifica_v2_ps'),

    path('guardando/<str:pk>/', guardar_sin_paciente, name='guardar_sin_paciente'),

    path('eliminar/<pk>/', eliminar_servicio, name='eliminar_servicio'),
    path('eliminar_paciente/<pk>/<servicio>/', eliminar_paciente, name='eliminar_paciente'),
    path('agregar-paciente/<int:pk>/', agregar_paciente, name='agregar_paciente'),
    path('reporte/<str:clave>/', reporte_servicio, name='reporte_servicio'),

    path('fallo/', fallo_guardado, name='fallo_guardado'),
    path('ajax/calles_por_colonia/', obtener_colonias_por_calle, name='ajax_colonias_por_calle'),
    path('ajax/calles_por_calle/', obtener_calles_por_calle, name='ajax_calles_por_calle'),
    path('combustible/', lista_combustible, name='lista_combustible'),
    path('combustible/nuevo/', crear_combustible, name='crear_combustible'),
    path('combustible/editar/<int:clave>/', editar_combustible, name='editar_combustible'),
    path('reloj/', ver_reloj, name='ver_reloj'),
    path('reloj/imprimir/', imprimir_reporte, name='imprimir_reporte'),



]