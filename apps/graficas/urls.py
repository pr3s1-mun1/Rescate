from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('graficas/', cargar_graficas, name='cargar_graficas'),
    path('trasladosmunicipales/', traslados, name='traslados'),
    path('trasladoshospitalarios/', traslados_hospitalarios, name='traslados_hospitalarios'),
    path('pacientesector/', pacientes_sector, name='pacientes_sector'),
    path('pacientesectorm/', pacientes_sector_m, name='pacientes_sector_m'),
    path('pacientesectorf/', pacientes_sector_f, name='pacientes_sector_f'),
    path('pacientesmenores/', pacientes_menores, name='pacientes_menores'),
    path('intoxicaciones/', intoxicaciones, name='intoxicaciones'),
    path('pacienteporcolonia/', pacientes_por_colonia, name='pacientes_por_colonia'),
    path('defunciones/', defunciones, name='defunciones'),
    path('lesiones/', lesiones, name='lesiones'),

    path('trasladosmunicipalespdf/', generar_pdf_grafica, name='generar_pdf_grafica'),
]
