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


def obtener_sobresalientes_por_fecha(fecha_inicio, fecha_fin):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.nombre_persona_reporta,
                s.clave,
                s.fecha,
                dc.calle AS direccion_emergencia,
                cc.colonia AS colonia_emergencia,
                s.calle_entre,
                t.descripcion,
                p.servicio_id as servicio,
                p.clave as Paciente,
                p.nombre,
                p.apellido_paterno,
                p.apellido_materno,
                p.sexo,
                p.edad,
                p.estatura,
                p.complexion,
                p.tez,
                p.pelo,
                p.ropa,
                p.sintoma,
                p.antecedente,
                p.base_id,
                p.ambulancia_id,
                dp.calle AS direccion_paciente,
                cp.colonia AS colonia_paciente,
                p.domicilio_numero
            FROM public.procesos_servicio AS s
            INNER JOIN public.procesos_pacientexservicio AS p ON s.clave = p.servicio_id
            INNER JOIN public.catalogos_tiposservicio AS t ON s.tipo_servicio_realizado_id = t.clave
            LEFT JOIN public.catalogos_calle AS dc ON s.direccion_emergencia_id = dc.clave
            LEFT JOIN public.catalogos_colonia AS cc ON s.colonia_emergencia_id = cc.clave
            LEFT JOIN public.catalogos_calle AS dp ON p.domicilio_id = dp.clave
            LEFT JOIN public.catalogos_colonia AS cp ON p.colonia_id = cp.clave
            WHERE t.sobresaliente = 'S'
              AND s.fecha BETWEEN %s AND %s
            ORDER BY s.fecha
        """, [fecha_inicio, fecha_fin])

        columnas = [col[0] for col in cursor.description]
        filas = cursor.fetchall()
        resultados = [dict(zip(columnas, fila)) for fila in filas]

    return resultados



palabras = {"sexo": {"1": "DESCONOCIDO", "2": "MASCULINO", "3": "FEMENINO"},
           "complexion": {"1": "CAQUEXIA", "2": "DELGADO", "3": "REGULAR", "4": "ROBUSTA", "5": "OBESA", "6": "OBESIDAD MÓRBIDA"},
           "tez": {"1": "BLANCO", "2": "MEDIO", "3": "MORENO", "4": "NEGRO"},
           "pelo": {"1": "NEGRO", "2": "CASTAÑO", "3": "RUBIO", "4": "PELIROJO", "5": "TEÑIDO", "6": "CANOSO", "7": "CALVO"},
           }

def reporte_sobresalientes(request):
    fecha_inicio = request.GET.get('fecha_inicio') or request.POST.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin') or request.POST.get('fecha_fin')

    textos = []

    if fecha_inicio and fecha_fin:
        resultados = obtener_sobresalientes_por_fecha(fecha_inicio, fecha_fin)

        def safe_upper(text):
            return text.upper() if text else ""

        for r in resultados:
            nombre_completo = f"{r['nombre']} {r['apellido_paterno']} {r['apellido_materno']}".strip()
            sexo = palabras["sexo"].get(str(r.get("sexo", "")), "NO ESPECIFICADO")
            complexion = palabras["complexion"].get(str(r.get("complexion", "")), "NO ESPECIFICADO")
            tez = palabras["tez"].get(str(r.get("tez", "")), "NO ESPECIFICADO")
            pelo = palabras["pelo"].get(str(r.get("pelo", "")), "NO ESPECIFICADO")

            texto = (
                f"POR COMISIÓN DE {safe_upper(r['nombre_persona_reporta'])}. DE LA BASE {safe_upper(r['base_id'])}, PARTIÓ LA AMBULANCIA #{safe_upper(r['ambulancia_id'])}\n"
                f"NOS ACERCAMOS A LA CALLES {safe_upper(r['direccion_emergencia'])} CRUCE CON {safe_upper(r['calle_entre'])} COLONIA {safe_upper(r['colonia_emergencia'])}.\n"
                f"SE REPORTA UN SERVICIO DE TIPO {safe_upper(r['descripcion'])}.\n"
                f"EL PACIENTE DE NOMBRE: {safe_upper(nombre_completo)} CON DIRECCIÓN {safe_upper(r['direccion_paciente'])} #{r['domicilio_numero']}. DE SEXO {safe_upper(sexo)} DE EDAD {r['edad']} AÑOS,\n"
                f"ESTATURA {r['estatura']} CM, COMPLEXIÓN {safe_upper(complexion)}, TEZ {safe_upper(tez)},\n"
                f"CABELLO {safe_upper(pelo)}, VESTÍA {safe_upper(r['ropa'])}.\n"
                f"SÍNTOMA: {safe_upper(r['sintoma'])}.\n"
                f"ANTECEDENTE: {safe_upper(r['antecedente'])}."
            )

            textos.append({
                'texto': texto,
                'servicio_id': r.get('servicio'),  # ID del servicio
                'paciente_id': r.get('paciente'),  # ID del paciente
                'fecha_servicio': r.get('fecha'),  # Fecha del servicio
            })

    context = {
        'textos': textos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    return render(request, 'reportes/reporte_sobresalientes.html', context)

def imprimir_reporte_sobresalientes_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio') or request.POST.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin') or request.POST.get('fecha_fin')

    textos = []

    if fecha_inicio and fecha_fin:
        resultados = obtener_sobresalientes_por_fecha(fecha_inicio, fecha_fin)

        def safe_upper(text):
            return text.upper() if text else ""

        for r in resultados:
            nombre_completo = f"{r['nombre']} {r['apellido_paterno']} {r['apellido_materno']}".strip()
            sexo = palabras["sexo"].get(str(r.get("sexo", "")), "NO ESPECIFICADO")
            complexion = palabras["complexion"].get(str(r.get("complexion", "")), "NO ESPECIFICADO")
            tez = palabras["tez"].get(str(r.get("tez", "")), "NO ESPECIFICADO")
            pelo = palabras["pelo"].get(str(r.get("pelo", "")), "NO ESPECIFICADO")

            texto = (
                f"POR COMISIÓN DE {safe_upper(r['nombre_persona_reporta'])}. DE LA BASE {safe_upper(r['base_id'])}, PARTIÓ LA AMBULANCIA #{safe_upper(r['ambulancia_id'])}<br>"
                f"NOS ACERCAMOS A LA CALLES {safe_upper(r['direccion_emergencia'])} CRUCE CON {safe_upper(r['calle_entre'])} COLONIA {safe_upper(r['colonia_emergencia'])}.<br>"
                f"SE REPORTA UN SERVICIO DE TIPO {safe_upper(r['descripcion'])}.<br>"
                f"EL PACIENTE DE NOMBRE: {safe_upper(nombre_completo)} CON DIRECCIÓN {safe_upper(r['direccion_paciente'])} #{r['domicilio_numero']}. DE SEXO {safe_upper(sexo)} DE EDAD {r['edad']} AÑOS,<br>"
                f"ESTATURA {r['estatura']} CM, COMPLEXIÓN {safe_upper(complexion)}, TEZ {safe_upper(tez)},<br>"
                f"CABELLO {safe_upper(pelo)}, VESTÍA {safe_upper(r['ropa'])}.<br>"
                f"SÍNTOMA: {safe_upper(r['sintoma'])}.<br>"
                f"ANTECEDENTE: {safe_upper(r['antecedente'])}."
            )

            textos.append({
                'texto': texto,
                'servicio_id': r.get('servicio'),
                'paciente_id': r.get('paciente'),
                'fecha_servicio': r.get('fecha'),
            })

    # Cargar plantilla
    template = get_template('plantillas/reporte_pdf_sobresalientes.html')
    html = template.render({
        'textos': textos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })

    # Generar PDF
    response = HttpResponse(content_type='application/pdf')
    filename = f"reporte_sobresalientes_{fecha_inicio}_a_{fecha_fin}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response, encoding='UTF-8')
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)

    return response


def obtener_resultados_parte_informativo(fecha_inicio, fecha_fin):
    resultados = []

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    s.fecha,
                    dc.calle AS direccion_emergencia,
                    cc.colonia AS colonia_emergencia,
                    s.calle_entre,
                    t.descripcion,
                    pxs.parte,
                    s.clave AS servicio,
                    CASE 
                        WHEN t.sobresaliente = 'S' THEN 'SI'
                        ELSE 'NO'
                    END AS es_sobresaliente
                FROM public.procesos_servicio AS s
                INNER JOIN public.catalogos_tiposservicio AS t ON s.tipo_servicio_realizado_id = t.clave
                INNER JOIN public.procesos_partexservico AS pxs ON s.clave = pxs.servicio_id
                LEFT JOIN public.catalogos_calle AS dc ON s.direccion_emergencia_id = dc.clave
                LEFT JOIN public.catalogos_colonia AS cc ON s.colonia_emergencia_id = cc.clave
                WHERE s.fecha BETWEEN %s AND %s
                ORDER BY s.fecha;
            """, [fecha_inicio, fecha_fin])

            columnas = [col[0] for col in cursor.description]
            resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    
    return resultados


def reporte_parte_informativo(request):
    fecha_inicio = request.GET.get('fecha_inicio') or request.POST.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin') or request.POST.get('fecha_fin')

    resultados = obtener_resultados_parte_informativo(fecha_inicio, fecha_fin)

    return render(request, 'reportes/reporte_parte_informativo.html', {
        'resultados': resultados,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })

def reporte_parte_informativo_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    resultados = obtener_resultados_parte_informativo(fecha_inicio, fecha_fin)

    template = get_template('plantillas/reporte_pdf_parte.html')
    context = {
        'resultados': resultados,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_sobresalientes.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    return response

def reporte_paramedico_base(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    datos_crudos = []

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    paramedicos.nombre, 
                    p.base_id
                FROM public.procesos_servicio AS s
                INNER JOIN public.procesos_pacientexservicio AS p ON s.clave = p.servicio_id
                INNER JOIN public.procesos_paramedicoxpaciente AS pp ON s.clave = pp.servicio_id
                INNER JOIN public.catalogos_paramedicos AS paramedicos ON paramedicos.clave = pp.paramedico_id
                WHERE s.fecha BETWEEN %s AND %s
            """, [fecha_inicio, fecha_fin])
            datos_crudos = cursor.fetchall()

    # Construir tabla dinámica: paramedico_nombre => base_id => conteo
    tabla = defaultdict(lambda: defaultdict(int))
    bases_detectadas = set()
    for paramedico_nombre, base_id in datos_crudos:
        tabla[paramedico_nombre][base_id] += 1
        bases_detectadas.add(base_id)

    # Ordenar bases
    bases_ordenadas = sorted(bases_detectadas)

    # Estructurar datos para el template
    total_por_base = defaultdict(int)
    resultados = []
    for paramedico_nombre in sorted(tabla.keys()):
        fila = {'paramedico_nombre': paramedico_nombre}
        total_paramedico = 0
        for base_id in bases_ordenadas:
            valor = tabla[paramedico_nombre].get(base_id, 0)
            fila[base_id] = valor
            total_paramedico += valor
        fila['total'] = total_paramedico  # ← total por paramédico
        resultados.append(fila)
    return render(request, 'reportes/reporte_paramedico_base.html', {
        'resultados': resultados,
        'bases': bases_ordenadas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total': total_paramedico
    })

def reporte_paramedico_base_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    datos_crudos = []

    if fecha_inicio and fecha_fin:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    paramedicos.nombre, 
                    p.base_id
                FROM public.procesos_servicio AS s
                INNER JOIN public.procesos_pacientexservicio AS p ON s.clave = p.servicio_id
                INNER JOIN public.procesos_paramedicoxpaciente AS pp ON s.clave = pp.servicio_id
                INNER JOIN public.catalogos_paramedicos AS paramedicos ON paramedicos.clave = pp.paramedico_id
                WHERE s.fecha BETWEEN %s AND %s
            """, [fecha_inicio, fecha_fin])
            datos_crudos = cursor.fetchall()

    tabla = defaultdict(lambda: defaultdict(int))
    bases_detectadas = set()
    for paramedico_nombre, base_id in datos_crudos:
        tabla[paramedico_nombre][base_id] += 1
        bases_detectadas.add(base_id)

    bases_ordenadas = sorted(bases_detectadas)

    resultados = []
    for paramedico_nombre in sorted(tabla.keys()):
        fila = {'paramedico_nombre': paramedico_nombre}
        total_paramedico = 0
        for base_id in bases_ordenadas:
            valor = tabla[paramedico_nombre].get(base_id, 0)
            fila[base_id] = valor
            total_paramedico += valor
        fila['total'] = total_paramedico
        resultados.append(fila)

    template = get_template("plantillas/reporte_pdf_paramedicos.html")
    html = template.render({
        'resultados': resultados,
        'bases': bases_ordenadas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_paramedico_base.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response, encoding='utf-8')
    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)
    return response