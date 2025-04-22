from django.urls import path
from .views import *

urlpatterns = [
    path('buscador/', formulario_buscar, name='formulario_buscar'),
    path('servicio/', formulario_servicio, name='formulario_servicio'),
]