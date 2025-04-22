from django.shortcuts import render, redirect
from .models import *
from apps.catalogos.forms import *
from .forms import ParamedicosForm, ServicioForm, PacientesForm

def formulario_servicio(request):
    mensaje = None
    clave_generada = None

    # Servicio
    if request.method == 'POST' and 'submit_servicio' in request.POST:
        form_servicio = ServicioForm(request.POST)
        if form_servicio.is_valid():
            servicio = form_servicio.save()
            mensaje = 'Formulario de servicio enviado correctamente'
            clave_generada = servicio.clave
    else:
        ultimo_servicio = Servicio.objects.order_by('-clave').first()
        siguiente_numero = 1 if ultimo_servicio is None else ultimo_servicio.clave + 1
        form_servicio = ServicioForm(initial={'clave': siguiente_numero})
        

    # Paramédicos
    paramedicos = Paramedicos.objects.all()

    # Unidades
    unidades = TipoUnidad.objects.all()

    # Alergias
    alergias = Alergia.objects.all()

    # Pacientes
    pacientes = PacientexServicio.objects.all()
    form_paciente = PacientesForm()

    # Procedimientos
    procedimientos = Procedimiento.objects.all()

    # Material
    material = Material.objects.all()

    # Medicamentos
    medicamento = Medicamento.objects.all()

    # Equipo
    equipos = Equipo.objects.all()

    return render(request, 'create.html', {
        'form': form_servicio,
        'paramedicos': paramedicos,
        'unidades': unidades,
        'alergias': alergias,
        'materiales': material,
        'medicamentos': medicamento,
        'equipos': equipos,
        'form_paciente': form_paciente,
        'pacientes': pacientes,
        'mensaje': mensaje,
        'clave': clave_generada,
        'modo_crear': True,
        'procedimientos': procedimientos,  
    })

def formulario_buscar(request):
    servicios_filtrados = Servicio.objects.all()

    if request.method == 'POST':
        clave = request.POST.get('clave', '').strip()
        if clave:
            servicios_filtrados = Servicio.objects.filter(clave__icontains=clave)

    return render(request, 'buscador_servicios.html', {
        'servicios': servicios_filtrados
    })

