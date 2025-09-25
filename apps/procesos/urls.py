from django.urls import path
from .views import *

urlpatterns = [
    path('servicios/', vista_principal, name='vista_main'),
    path('buscar/', formulario_buscar, name='formulario_buscar'),
    path('nuevo/', formulario_servicio, name='formulario_servicio'),
    path('creando/', crear_servicio, name='crear_servicio'),
    path('editar/<str:pk>/', carga_modifica_n, name='carga_modifica_n'),
    path('editar/<str:pk>/<str:ps>/', carga_modifica, name='carga_modifica'),
    path('eliminar/<pk>/', eliminar_servicio, name='eliminar_servicio'),
    path('servicio/<int:pk>/agregar-paciente/', agregar_paciente, name='agregar_paciente'),
    path('guardar_completo/<int:pk>/', guardar_todo_n, name='guardar_todo_n'),
    path('guardar_completo/<int:pk>/<int:ps>/', guardar_todo, name='guardar_todo'),
    path('reporte/<str:clave>/', reporte_servicio, name='reporte_servicio'),
    path('exito/<str:pk>/<str:ps>/', exito_guardado, name='exito_guardado'),
    path('exito/<str:pk>/', exito_guardado_2, name='exito_guardado_2'),
    path('fallo/', fallo_guardado, name='fallo_guardado'),
    path('ajax/calles_por_colonia/', obtener_colonias_por_calle, name='ajax_colonias_por_calle'),
    path('ajax/calles_por_calle/', obtener_calles_por_calle, name='ajax_calles_por_calle'),
    path('combustible/', lista_combustible, name='lista_combustible'),
    path('combustible/nuevo/', crear_combustible, name='crear_combustible'),
    path('combustible/editar/<int:clave>/', editar_combustible, name='editar_combustible'),
    path('reloj/', ver_reloj, name='ver_reloj'),
    path('reloj/imprimir/', imprimir_reporte, name='imprimir_reporte'),



]