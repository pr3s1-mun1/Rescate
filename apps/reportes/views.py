from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from apps.procesos.models import PacientexServicio, Servicio
from collections import defaultdict
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO
from collections import defaultdict
from django.db import connection
from datetime import date
def cargar_reportes(request):
    return render(request, 'main.html')

def reporte_servicios(request: HttpRequest):
    """
    Vista unificada para reporte de servicios que maneja:
    - GET sin parámetros: Muestra el formulario HTML
    - POST con fechas: Muestra el reporte en HTML
    - GET con parámetros fecha_inicio/fecha_fin: Genera PDF
    """
    fecha_inicio = request.POST.get('fecha_inicio') or request.GET.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin') or request.GET.get('fecha_fin')
    
    conteos = defaultdict(lambda: defaultdict(int))
    tipos_servicio = set()
    basees = set()

    if fecha_inicio and fecha_fin:
        servicios = Servicio.objects.filter(
            fecha__range=[fecha_inicio, fecha_fin]
        ).select_related()  

        for servicio in servicios:
            tipo = servicio.tipo_servicio_realizado
            tipos_servicio.add(tipo)
            
            pacientes = PacientexServicio.objects.filter(
                servicio=servicio
            ).select_related('base')
            
            for paciente in pacientes:
                base = str(paciente.base)
                basees.add(base)
                conteos[tipo][base] += 1

    context = {
        'conteos': dict(conteos),
        'tipos_servicio': sorted(tipos_servicio, key=lambda x: x.clave),
        'basees': sorted(basees),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'usar_landscape': len(basees) > 5
    }

    if request.method == 'GET' and fecha_inicio and fecha_fin:
        return generar_pdf_response(context)
    return render(request, 'reportes/reporte_servicio_base_fecha.html', context)

def generar_pdf_response(context: dict) -> HttpResponse:
    """Genera la respuesta PDF a partir del contexto"""
    template = get_template('plantillas/reporte_servicio.html')
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"reporte_servicios_{context['fecha_inicio']}_a_{context['fecha_fin']}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    return HttpResponse('Error al generar PDF', status=500)


def obtener_servicios_ambulancia(fecha_inicio, fecha_fin):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                S.fecha, 
                P.fecha_salida, 
                P.fecha_llegada, 
                P.fecha_retorno,
                CA.descripcion,
                TS.descripcion AS tipo_servicio,
                D.calle AS direccion,
                C.colonia AS colonia,
                S.calle_entre
            FROM 
                public.procesos_servicio AS S
            INNER JOIN 
                public.procesos_pacientexservicio AS P 
                ON S.clave = P.clave
            LEFT JOIN 
                public.catalogos_tiposservicio AS TS 
                ON S.tipo_servicio_realizado_id = TS.clave
            LEFT JOIN 
                public.catalogos_calle AS D 
                ON S.direccion_emergencia_id = D.clave
            LEFT JOIN 
                public.catalogos_colonia AS C 
                ON S.colonia_emergencia_id = C.clave
            LEFT JOIN
                public.catalogos_ambulancias AS CA 
                ON P.ambulancia_id = CA.clave
            WHERE 
                S.fecha BETWEEN %s AND %s
            ORDER BY 
                P.ambulancia_id, S.fecha
        """, [fecha_inicio, fecha_fin])

        columnas = [col[0] for col in cursor.description]
        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    
    return resultados



def reporte_servicios_x_ambulancia(request):
    fecha_inicio = request.POST.get('fecha_inicio') or request.GET.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin') or request.GET.get('fecha_fin')

    servicios_por_ambulancia = defaultdict(list)

    if fecha_inicio and fecha_fin:
        servicios = obtener_servicios_ambulancia(fecha_inicio, fecha_fin)
        for s in servicios:
            ambulancia = s['descripcion']
            servicios_por_ambulancia[ambulancia].append(s)

    context = {
        'servicios_por_ambulancia': dict(servicios_por_ambulancia),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    return render(request, 'reportes/reporte_ambulancia.html', context)

def imprimir_reporte_ambulancia_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    servicios_raw = []
    servicios_por_ambulancia = {}

    if fecha_inicio and fecha_fin:
        servicios_raw = obtener_servicios_ambulancia(fecha_inicio, fecha_fin)

        # Agrupar por ambulancia
        for s in servicios_raw:
            ambu = s['descripcion']
            if ambu not in servicios_por_ambulancia:
                servicios_por_ambulancia[ambu] = []
            servicios_por_ambulancia[ambu].append(s)

    template = get_template('plantillas/reporte_pdf_ambulancia.html')
    html = template.render({
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'servicios_por_ambulancia': servicios_por_ambulancia
    })

    response = HttpResponse(content_type='application/pdf')
    filename = f"reporte_ambulancias_{fecha_inicio}_a_{fecha_fin}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response, encoding='UTF-8')
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    return response

def obtener_servicios_por_tipo(fecha_inicio, fecha_fin):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                TS.descripcion AS tipo_servicio,
                P.base_id,
                COUNT(*) AS pacientes_count
            FROM 
                public.procesos_servicio AS S
            INNER JOIN 
                public.procesos_pacientexservicio AS P 
                ON S.clave = P.clave
            LEFT JOIN 
                public.catalogos_tiposservicio AS TS
                ON TS.clave = S.tipo_servicio_realizado_id
            WHERE 
                S.fecha BETWEEN %s AND %s
            GROUP BY 
                TS.descripcion, P.base_id
            ORDER BY 
                TS.descripcion, P.base_id
        """, [fecha_inicio, fecha_fin])

        columnas = [col[0] for col in cursor.description]
        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    
    return resultados

def reporte_servicios_x_tipo(request):
    from collections import defaultdict

    fecha_inicio = request.POST.get('fecha_inicio') or request.GET.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin') or request.GET.get('fecha_fin')

    tabla = defaultdict(dict)
    filas = set()
    columnas = set()

    if fecha_inicio and fecha_fin:
        datos = obtener_servicios_por_tipo(fecha_inicio, fecha_fin)

        for fila in datos:
            tipo = fila['tipo_servicio']
            base = fila['base_id']
            count = fila['pacientes_count']

            tabla[tipo][base] = count
            filas.add(tipo)
            columnas.add(base)

    context = {
        'tabla': tabla,
        'filas': sorted(filas),
        'columnas': sorted(columnas),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    return render(request, 'reportes/reporte_resumen_servicios.html', context)


def imprimir_reporte_tipo_servicio_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    tabla = defaultdict(dict)
    filas = set()
    columnas = set()

    if fecha_inicio and fecha_fin:
        datos = obtener_servicios_por_tipo(fecha_inicio, fecha_fin)

        for fila in datos:
            tipo = fila['tipo_servicio']
            base = fila['base_id']
            count = fila['pacientes_count']

            tabla[tipo][base] = count
            filas.add(tipo)
            columnas.add(base)

    template = get_template('plantillas/reporte_pdf_tipo_servicio.html')
    html = template.render({
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'tabla': tabla,
        'filas': sorted(filas),
        'columnas': sorted(columnas),
    })

    response = HttpResponse(content_type='application/pdf')
    filename = f"reporte_tipo_servicio_{fecha_inicio}_a_{fecha_fin}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response, encoding='UTF-8')
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    return response

def obtener_totales_por_tipo_servicio(fecha_inicio, fecha_fin):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                TS.descripcion AS tipo_servicio,
                COUNT(*) AS total
            FROM 
                public.procesos_servicio AS S
            LEFT JOIN 
                public.catalogos_tiposservicio AS TS
                ON TS.clave = S.tipo_servicio_realizado_id
            WHERE 
                S.fecha BETWEEN %s AND %s
            GROUP BY 
                TS.descripcion
            ORDER BY 
                TS.descripcion
        """, [fecha_inicio, fecha_fin])
        columnas = [col[0] for col in cursor.description]
        resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    return resultados


def resumen_tipo_servicio(request):
    fecha_inicio = request.GET.get('fecha_inicio') or request.POST.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin') or request.POST.get('fecha_fin')

    datos = []
    if fecha_inicio and fecha_fin:
        datos = obtener_totales_por_tipo_servicio(fecha_inicio, fecha_fin)

    context = {
        'datos': datos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    return render(request, 'reportes/resumen_conteo_servicio.html', context)


def imprimir_resumen_tipo_servicio_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    datos = []
    if fecha_inicio and fecha_fin:
        datos = obtener_totales_por_tipo_servicio(fecha_inicio, fecha_fin)

    template = get_template('plantillas/resumen_conteo_servicio_pdf.html')
    html = template.render({
        'datos': datos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })

    response = HttpResponse(content_type='application/pdf')
    filename = f"resumen_conteo_servicio_{fecha_inicio}_a_{fecha_fin}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response, encoding='UTF-8')
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)

    return response