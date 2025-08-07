import matplotlib
matplotlib.use('Agg')  # <-- ESTO ES LO IMPORTANTE
import matplotlib.pyplot as plt
from django.shortcuts import render
from apps.procesos.models import Servicio
from apps.catalogos.views import requiere_tipo_paramedico
from collections import Counter
from io import BytesIO
from django.http import HttpResponse, HttpResponseBadRequest
from django.db import connection
import base64
import numpy as np
from matplotlib.ticker import MaxNLocator, MultipleLocator
from matplotlib.patches import Patch

@requiere_tipo_paramedico(2)
def cargar_graficas(request):
    return render(request, 'maingraficos.html')

@requiere_tipo_paramedico(2)
def traslados(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT h.nombre, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN catalogos_hospitales as h ON h.clave = p.hospital_id
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                WHERE p.hospital_id in (12, 70) AND s.fecha BETWEEN %s AND %s
                GROUP BY h.nombre
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        nombres = [r[0] for r in resultados]
        totales = [r[1] for r in resultados]

        colores = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray']
        colores = (colores * (len(nombres)//len(colores) + 1))[:len(nombres)]

        etiquetas = nombres

        fig, ax = plt.subplots(figsize=(10, 8))
        barras = ax.bar(nombres, totales, color=colores)

        ax.set_ylabel('Total Pacientes')
        ax.set_xlabel('Hospital')
        ax.set_title(f'Traslados por Hospital del {fecha_inicio} al {fecha_fin}')

        legend_patches = [Patch(color=col, label=label) for col, label in zip(colores, etiquetas)]
        ax.legend(handles=legend_patches, title='Hospital')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/traslados_municipio.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })

@requiere_tipo_paramedico(2)
def traslados_hospitalarios(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT h.nombre, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN catalogos_hospitales as h ON h.clave = p.hospital_id
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                WHERE s.fecha BETWEEN %s AND %s
                GROUP BY h.nombre
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        nombres = [r[0] for r in resultados]
        totales = [r[1] for r in resultados]

        colores = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray']
        colores = (colores * (len(nombres)//len(colores) + 1))[:len(nombres)]

        etiquetas = nombres

        fig, ax = plt.subplots(figsize=(10, 8))
        barras = ax.bar(nombres, totales, color=colores)

        ax.set_ylabel('Total Pacientes')
        ax.set_xlabel('Hospital')
        ax.set_title(f'Traslados por Hospital del {fecha_inicio} al {fecha_fin}')

        legend_patches = [Patch(color=col, label=label) for col, label in zip(colores, etiquetas)]
        ax.legend(handles=legend_patches, title='Hospital')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/traslados_hospitalarios.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })

@requiere_tipo_paramedico(2)
def pacientes_sector(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT base_id, h.estacion, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN catalogos_bases as h ON h.clave = p.base_id
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                WHERE s.fecha BETWEEN %s AND %s
                GROUP BY base_id, h.estacion
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        nombres = [f"{r[0]} - {r[1]}" for r in resultados]
        totales = [r[2] for r in resultados]

        # Colores para las barras
        colores = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple',
                   'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
        bar_colors = [colores[i % len(colores)] for i in range(len(resultados))]

        fig, ax = plt.subplots(figsize=(12, 8))
        barras = ax.bar(nombres, totales, color=bar_colors)

        ax.set_title(f'Traslados por Base del {fecha_inicio} al {fecha_fin}')
        ax.set_xlabel('Base - Estación')
        ax.set_ylabel('Total Pacientes')

        # Mostrar solo enteros en eje Y
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Rotar etiquetas eje X para mejor lectura
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        # Leyenda con nombre de estación sin repetir colores
        estaciones = list(dict.fromkeys([r[1] for r in resultados]))  # Unicos manteniendo orden
        estaciones_colores = {est: colores[i % len(colores)] for i, est in enumerate(estaciones)}
        handles = [plt.Rectangle((0,0),1,1, color=estaciones_colores[est]) for est in estaciones]
        ax.legend(handles, estaciones, title='Estación', bbox_to_anchor=(1.05, 1), loc='upper left')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/pacientes_sector.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })

@requiere_tipo_paramedico(2)
def pacientes_sector_m(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT base_id, h.estacion, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN catalogos_bases as h ON h.clave = p.base_id
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                WHERE p.sexo = '2' and s.fecha BETWEEN %s AND %s
                GROUP BY base_id, h.estacion
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        nombres = [f"{r[0]} - {r[1]}" for r in resultados]
        totales = [r[2] for r in resultados]

        # Colores para las barras
        colores = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple',
                   'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
        bar_colors = [colores[i % len(colores)] for i in range(len(resultados))]

        fig, ax = plt.subplots(figsize=(12, 8))
        barras = ax.bar(nombres, totales, color=bar_colors)

        ax.set_title(f'Traslados por Base del {fecha_inicio} al {fecha_fin}')
        ax.set_xlabel('Base - Estación')
        ax.set_ylabel('Total Pacientes')

        # Mostrar solo enteros en eje Y
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Rotar etiquetas eje X para mejor lectura
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        # Leyenda con nombre de estación sin repetir colores
        estaciones = list(dict.fromkeys([r[1] for r in resultados]))  # Unicos manteniendo orden
        estaciones_colores = {est: colores[i % len(colores)] for i, est in enumerate(estaciones)}
        handles = [plt.Rectangle((0,0),1,1, color=estaciones_colores[est]) for est in estaciones]
        ax.legend(handles, estaciones, title='Estación', bbox_to_anchor=(1.05, 1), loc='upper left')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/pacientes_sector.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })

@requiere_tipo_paramedico(2)
def pacientes_sector_f(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT base_id, h.estacion, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN catalogos_bases as h ON h.clave = p.base_id
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                WHERE p.sexo = '3' and s.fecha BETWEEN %s AND %s
                GROUP BY base_id, h.estacion
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        nombres = [f"{r[0]} - {r[1]}" for r in resultados]
        totales = [r[2] for r in resultados]

        # Colores para las barras
        colores = ['tab:red', 'tab:blue', 'tab:green', 'tab:orange', 'tab:purple',
                   'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
        bar_colors = [colores[i % len(colores)] for i in range(len(resultados))]

        fig, ax = plt.subplots(figsize=(12, 8))
        barras = ax.bar(nombres, totales, color=bar_colors)

        ax.set_title(f'Traslados por Base del {fecha_inicio} al {fecha_fin}')
        ax.set_xlabel('Base - Estación')
        ax.set_ylabel('Total Pacientes')

        # Mostrar solo enteros en eje Y
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Rotar etiquetas eje X para mejor lectura
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        # Leyenda con nombre de estación sin repetir colores
        estaciones = list(dict.fromkeys([r[1] for r in resultados]))  # Unicos manteniendo orden
        estaciones_colores = {est: colores[i % len(colores)] for i, est in enumerate(estaciones)}
        handles = [plt.Rectangle((0,0),1,1, color=estaciones_colores[est]) for est in estaciones]
        ax.legend(handles, estaciones, title='Estación', bbox_to_anchor=(1.05, 1), loc='upper left')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/pacientes_sector.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })

@requiere_tipo_paramedico(2)
def intoxicaciones(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT h.nombre, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN catalogos_enfermedad as h ON h.clave = p.enfermedad_id
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                WHERE h.grupoenfermedad_id = '17' 
                  AND s.fecha BETWEEN %s AND %s
                GROUP BY h.nombre
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        nombres = [r[0] for r in resultados]
        totales = [r[1] for r in resultados]

        colores = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray']
        colores = (colores * (len(nombres)//len(colores) + 1))[:len(nombres)]

        fig, ax = plt.subplots(figsize=(max(10, len(nombres) * 0.5), 8))
        barras = ax.bar(nombres, totales, color=colores)

        ax.set_ylabel('Total Casos')
        ax.set_xlabel('Enfermedad')
        ax.set_title(f'Intoxicaciones del {fecha_inicio} al {fecha_fin}')

        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.set_ylim(0, max(totales) + 1)

        legend_patches = [Patch(color=col, label=label) for col, label in zip(colores, nombres)]
        ax.legend(handles=legend_patches, title='Enfermedad')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/intoxicaciones.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })

@requiere_tipo_paramedico(2)
def pacientes_por_colonia(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.colonia_id, c.colonia, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                JOIN catalogos_colonia as c ON p.colonia_id = c.clave
                WHERE s.fecha BETWEEN %s AND %s
                GROUP BY p.colonia_id, c.colonia
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        colonias = [r[1] for r in resultados]  # Nombre de la colonia
        totales = [r[2] for r in resultados]   # Total de pacientes

        colores = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray']
        colores = (colores * (len(colonias)//len(colores) + 1))[:len(colonias)]

        fig, ax = plt.subplots(figsize=(max(10, len(colonias) * 0.4), 8))
        barras = ax.bar(colonias, totales, color=colores)

        ax.set_ylabel('Total de Pacientes')
        ax.set_xlabel('Colonia')
        ax.set_title(f'Pacientes por Colonia del {fecha_inicio} al {fecha_fin}')
        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.set_ylim(0, max(totales) + 1)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/pacientes_por_colonia.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })

@requiere_tipo_paramedico(2)
def defunciones(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT h.nombre, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN catalogos_enfermedad as h ON h.clave = p.enfermedad_id
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                WHERE h.grupoenfermedad_id = '26' 
                  AND s.fecha BETWEEN %s AND %s
                GROUP BY h.nombre
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        nombres = [r[0] for r in resultados]
        totales = [r[1] for r in resultados]

        colores = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray']
        colores = (colores * (len(nombres)//len(colores) + 1))[:len(nombres)]

        fig, ax = plt.subplots(figsize=(max(10, len(nombres) * 0.5), 8))
        barras = ax.bar(nombres, totales, color=colores)

        ax.set_ylabel('Total Casos')
        ax.set_xlabel('Defunciones')
        ax.set_title(f'Defunciones del {fecha_inicio} al {fecha_fin}')

        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.set_ylim(0, max(totales) + 1)

        legend_patches = [Patch(color=col, label=label) for col, label in zip(colores, nombres)]
        ax.legend(handles=legend_patches, title='Defunciones')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/defunciones.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })

@requiere_tipo_paramedico(2)
def lesiones(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    resultados = []
    grafica_base64 = None

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT h.nombre, COUNT(*) as total
                FROM procesos_pacientexservicio as p
                JOIN catalogos_enfermedad as h ON h.clave = p.enfermedad_id
                JOIN procesos_servicio as s ON p.servicio_id = s.clave
                WHERE h.grupoenfermedad_id = '18' 
                  AND s.fecha BETWEEN %s AND %s
                GROUP BY h.nombre
                ORDER BY total DESC;
            """, [fecha_inicio, fecha_fin])
            resultados = cursor.fetchall()

        nombres = [r[0] for r in resultados]
        totales = [r[1] for r in resultados]

        colores = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray']
        colores = (colores * (len(nombres)//len(colores) + 1))[:len(nombres)]

        fig, ax = plt.subplots(figsize=(max(10, len(nombres) * 0.5), 8))
        barras = ax.bar(nombres, totales, color=colores)

        ax.set_ylabel('Total Casos')
        ax.set_xlabel('Lesiones')
        ax.set_title(f'Lesiones del {fecha_inicio} al {fecha_fin}')

        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.set_ylim(0, max(totales) + 1)

        legend_patches = [Patch(color=col, label=label) for col, label in zip(colores, nombres)]
        ax.legend(handles=legend_patches, title='Lesiones')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        grafica_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "reportes/lesiones.html", {
        "resultados": resultados,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_base64": grafica_base64,
    })