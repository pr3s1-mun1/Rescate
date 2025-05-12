from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from apps.procesos.models import PacientexServicio, Servicio
from collections import defaultdict
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO

# Create your views here.
def cargar_reportes(request):
    # Aquí puedes implementar la lógica para generar el reporte diario
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