from django.urls import path
from .views import *

urlpatterns = [
    path('reportes/', cargar_reportes, name='cargar_reportes'),
    path('reportes/servicios/', reporte_servicios, name='reporte_servicios'),
    path('reportes/serviciosambulancias/', reporte_servicios_x_ambulancia, name='reporte_servicios_x_ambulancia'),
    path('reporte/serviciosambulancias/pdf/', imprimir_reporte_ambulancia_pdf, name='imprimir_reporte_ambulancia_pdf'),
    path('reportes/pacientesxbase/', reporte_servicios_x_tipo, name='reporte_servicios_x_tipo'),
    path('reportes/pacientesxbase/pdf', imprimir_reporte_tipo_servicio_pdf, name='imprimir_reporte_tipo_servicio_pdf'),
    path('reportes/serviciosconteo/', resumen_tipo_servicio, name='resumen_tipo_servicio'),
    path('reportes/serviciosconteo/pdf', imprimir_resumen_tipo_servicio_pdf, name='imprimir_resumen_tipo_servicio_pdf'),
    path('reportes/serviciossobresalientes/', reporte_sobresalientes, name='reporte_sobresalientes'),
    path('reportes/serviciossobresalientes/pdf', imprimir_reporte_sobresalientes_pdf, name='imprimir_reporte_sobresalientes_pdf'),
    path('reportes/serviciosparteinformativo/', reporte_parte_informativo, name='reporte_parte_informativo'),
    path('reportes/serviciosparteinformativo/pdf', reporte_parte_informativo_pdf, name='reporte_parte_informativo_pdf'),
    path('reportes/serviciosparamedico/', reporte_paramedico_base, name='reporte_paramedico_base'),
    path('reportes/serviciosparamedico/pdf', reporte_paramedico_base_pdf, name='reporte_paramedico_base_pdf'),
]