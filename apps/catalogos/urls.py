from django.urls import path
from .views import *

urlpatterns = [
    path('relacionar-calle-colonia/', relacionar_calle_colonia, name='relacionar_calle_colonia'),

    #Vistas de formularios
    path('<str:tipo>/', catalogo_general, name='catalogo_general'),

    #Edición de formularios
    path('update/<str:tipo>/<str:clave>/', update_catalogo, name='update_catalogo'),

    #Eliminación de formularios
    path('delete/<str:tipo>/<str:clave>/', delete_catalogo, name='delete_catalogo'),

    path('agregar/<str:tipo>/', add_catalogo, name='add_catalogo'),

]
