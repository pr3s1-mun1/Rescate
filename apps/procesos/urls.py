from django.urls import path
from .views import *

urlpatterns = [
    path('servicios/', vista_main, name='vista_main'),
    path('buscador/', formulario_buscar, name='formulario_buscar'),
    path('crear/', formulario_servicio, name='formulario_servicio'),
    path('crear_servicio/', crear_servicio, name='crear_servicio'),
    path('modificar_servicio/<pk>/', modificar_servicio, name='modificar_servicio'),

]