from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from apps.catalogos.forms import *
from apps.catalogos.views import requiere_tipo_paramedico
from .forms import ServicioForm, PacientesForm, EmbarazoAsignadoForm, PartesAsignadoForm
from django.http import HttpResponse
from collections import defaultdict
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime
import json


def formulario_buscar(request):
    clave = request.POST.get('clave', '').strip() if request.method == 'POST' else ''
    servicios = Servicio.objects.filter(clave__icontains=clave) if clave else Servicio.objects.all()
    servicios = servicios.order_by('clave')

    pacientes = PacientexServicio.objects.filter(servicio__in=servicios)

    return render(request, 'buscador_servicios.html', {
        'servicios': servicios,
        'pacientes': pacientes
    })



#Función para cargar formulario y pestañas de creación (Primera Parte)
@requiere_tipo_paramedico('P', 'A')
def formulario_servicio(request):    
    context = {
        'form': ServicioForm(initial={'clave': Servicio.obtener_siguiente_numero()}),
        'paramedicos': Paramedicos.objects.all(),
        'unidades': TipoUnidad.objects.all(),
        }
    
    return render(request, 'create.html', context)

#Función para mostrar conteos de hojas de servicio además de los botones de selección
def vista_principal(request):
    total_servicios = Servicio.objects.count()
    servicios_activos = Servicio.objects.filter(estatus='P').count()
    hojas_hoy = Servicio.objects.filter(fecha=datetime.date.today()).count()
    pendientes = Servicio.objects.count()

    return render(request, 'serv_principal.html', {
        'total_servicios': total_servicios,
        'servicios_activos': servicios_activos,
        'hojas_hoy': hojas_hoy,
        'pendientes': pendientes,
    })

#Función para guardar formulario y pestañas de creación (Primera Parte)
from django.shortcuts import redirect

def crear_servicio(request):
    if request.method == 'POST':
        servicio_form = ServicioForm(request.POST)

        if servicio_form.is_valid():
            servicio = servicio_form.save()

            unidades = json.loads(request.POST.get('unidades', '[]'))
            for u in unidades:
                if u.get('clave') and u.get('id_unidad'):
                    UnidadxServicio.objects.create(
                        servicio=servicio,
                        unidad=TipoUnidad.objects.get(clave=u['clave']),
                        numero_unidad=u['id_unidad'],
                        agente_nombre=u.get('agente', '')
                    )

            paramedicos = json.loads(request.POST.get('paramedicos', '[]'))
            for item in paramedicos:
                clave = item.get("clave")
                paramedico = Paramedicos.objects.get(clave=clave)
                ParamedicoxPaciente.objects.create(servicio=servicio, paramedico=paramedico)

            print("Servicio creado con éxito:", servicio.clave)
            return redirect('carga_modifica', pk=servicio.clave)  # redirige a otra vista

        else:
            context = {
                'servicio_form': servicio_form,
                'unidades': TipoUnidad.objects.all(),
                'paramedicos': Paramedicos.objects.all(),
                'errores': servicio_form.errors,
            }
            return render(request, 'modificar_servicio.html', context)

    else:
        servicio_form = ServicioForm()

    context = {
        'servicio_form': servicio_form,
        'unidades': TipoUnidad.objects.all(),
        'paramedicos': Paramedicos.objects.all(),
    }

    return render(request, 'modificar_servicio.html', context)


@requiere_tipo_paramedico('P', 'A')
def carga_modifica(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    form_servicio = ServicioForm(instance=servicio)

    paciente = PacientexServicio.objects.filter(servicio=servicio).first()
    if paciente:
        form_paciente = PacientesForm(instance=paciente)
    else:
        form_paciente = PacientesForm(initial={'clave': PacientexServicio.obtener_siguiente_numero()})


    form_embarazo = EmbarazoAsignadoForm()
    parte_instancia = PartexServico.objects.filter(servicio=servicio).first()
    form_partes = PartesAsignadoForm(instance=parte_instancia)

    context = {
        'form': form_servicio,
        'form_paciente': form_paciente,
        'form_embarazo': form_embarazo,
        'form_partes': form_partes,
        'editar': True,
        'servicio': servicio,
        'pacientes': PacientexServicio.objects.filter(servicio=servicio),
        'form_partes': PartesAsignadoForm(instance=parte_instancia),
        
        # Datos relacionados asignados
        'paramedicos_asignados': ParamedicoxPaciente.objects.filter(servicio=servicio),
        'unidades_asignadas': UnidadxServicio.objects.filter(servicio=servicio),
        'procedimientos_asignados': ProcedimientoxPaciente.objects.filter(paciente__servicio=servicio),
        'alergias_asignados': AlergiaxPaciente.objects.filter(paciente__servicio=servicio),
        'materiales_asignados': MaterialxPaciente.objects.filter(paciente__servicio=servicio),
        'ingeridos_asignados': MedIngeridoxPaciente.objects.filter(paciente__servicio=servicio),
        'administrados_asignados': MedAdministradoxPaciente.objects.filter(paciente__servicio=servicio),
        'equipos_asignados': EquipoxPaciente.objects.filter(paciente__servicio=servicio),
        'lesiones_asignados': LesionxPaciente.objects.filter(paciente__servicio=servicio),
        'impactos_asignados': ImpactoxVehiculo.objects.filter(paciente__servicio=servicio),
        'testigos_asignados': TestigoxPaciente.objects.filter(paciente__servicio=servicio),

        # Catálogos
        'paramedicos': Paramedicos.objects.all(),
        'unidades': TipoUnidad.objects.all(),
        'alergias': Alergia.objects.all(),
        'materiales': Material.objects.all(),
        'medicamentos': Medicamento.objects.all(),
        'equipos': Equipo.objects.all(),
        'procedimientos': Procedimiento.objects.all(),
    }

    return render(request, 'modificar_servicio.html', context)

@requiere_tipo_paramedico('P', 'A')
def eliminar_servicio(request, pk):
    print("Eliminando servicio con pk:", pk)
    servicio = get_object_or_404(Servicio, pk=pk)
    servicio.delete()
    return redirect('formulario_buscar')

def guardar_todo(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)

    if request.method != 'POST':
        return render(request, 'modificar_servicio.html', {
            'form_servicio': ServicioForm(instance=servicio),
            'pacientes_form': PacientesForm(),
            'servicio': servicio,
            'editar': True
        })

    form_servicio = ServicioForm(request.POST, instance=servicio)
    paciente_clave = request.POST.get('clave')
    paciente = PacientexServicio.objects.filter(clave=paciente_clave).first()
    pacientes_form = PacientesForm(request.POST, instance=paciente)

    if not (form_servicio.is_valid() and pacientes_form.is_valid()):
        print("Errores de validación:")
        print("- Servicio:", form_servicio.errors)
        print("- Paciente:", pacientes_form.errors)
        return render(request, 'modificar_servicio.html', {
            'form_servicio': form_servicio,
            'pacientes_form': pacientes_form,
            'servicio': servicio,
            'editar': True
        })

    try:
        servicio = form_servicio.save()
        paciente = pacientes_form.save(commit=False)
        paciente.servicio = servicio
        paciente.save()

        guardar_unidades(request, servicio)
        guardar_paramedicos(request, servicio)
        guardar_procedimientos(request, paciente)
        guardar_alergias(request, paciente)
        guardar_materiales(request, paciente)
        guardar_ingeridos(request, paciente)
        guardar_administrados(request, paciente)
        guardar_equipos(request, paciente)
        guardar_lesiones(request, paciente)
        guardar_impactos(request, paciente)
        guardar_testigos(request, paciente)

        embarazo = request.POST.get('embarazo') == 'true'

        if embarazo:
            form_embarazo = EmbarazoAsignadoForm(request.POST)
            if form_embarazo.is_valid():
                form_embarazo.save(commit=False)
                form_embarazo.paciente = paciente
                form_embarazo.save()



        form_partes = PartesAsignadoForm(request.POST)
        if form_partes.is_valid():
            PartexServico.objects.filter(servicio=servicio).delete()
            parte = form_partes.save(commit=False)
            parte.servicio = servicio 
            parte.save()


        return redirect('exito_guardado', pk=servicio.clave)

    except Exception as e:
        print(f"Error general: {e}")
        return redirect('fallo_guardado', error=str(e))

def exito_guardado(request, pk):
    return render(request, 'resp/exito_guardado.html', {'clave': pk})

def fallo_guardado(request):
    error = request.GET.get('error', 'Ocurrió un error inesperado.')
    return render(request, 'resp/fallo_guardado.html', {'error': error})


def guardar_unidades(request, servicio):
    UnidadxServicio.objects.filter(servicio=servicio).delete()
    unidades = json.loads(request.POST.get('unidades', '[]'))
    for u in unidades:
        if u.get('clave') and u.get('id_unidad'):
            UnidadxServicio.objects.create(
                servicio=servicio,
                unidad=TipoUnidad.objects.get(clave=u['clave']),
                numero_unidad=u['id_unidad'],
                agente_nombre=u.get('agente', '')
            )

def guardar_paramedicos(request, servicio):
    ParamedicoxPaciente.objects.filter(servicio=servicio).delete()
    paramedicos = json.loads(request.POST.get('paramedicos', '[]'))
    for item in paramedicos:
        clave = item.get("clave")
        paramedico = Paramedicos.objects.get(clave=clave)
        ParamedicoxPaciente.objects.create(servicio=servicio, paramedico=paramedico)

def guardar_procedimientos(request, paciente):
        ProcedimientoxPaciente.objects.filter(paciente=paciente).delete()
        procedimientos = json.loads(request.POST.get('procedimientos', '[]'))
        for i in procedimientos:
            clave = i.get("clave")
            procedimiento = Procedimiento.objects.get(clave=clave)
            ProcedimientoxPaciente.objects.create(procedimiento=procedimiento, paciente=paciente)

def guardar_alergias(request, paciente):
    AlergiaxPaciente.objects.filter(paciente=paciente).delete()
    alergias = json.loads(request.POST.get('alergias', '[]'))
    for i in alergias:
        clave = i.get('clave')
        alergia = Alergia.objects.get(clave=clave)
        AlergiaxPaciente.objects.create(alergia=alergia, paciente=paciente)

def guardar_materiales(request, paciente):
    MaterialxPaciente.objects.filter(paciente=paciente).delete()
    materiales = json.loads(request.POST.get('materiales', '[]'))
    for i in materiales:
        clave = i.get('clave')
        cantidad = i.get('cantidad')
        material = Material.objects.get(clave=clave)
        MaterialxPaciente.objects.create(paciente=paciente, material=material, cantidad=cantidad, costo=0)

def guardar_ingeridos(request, paciente):
    MedIngeridoxPaciente.objects.filter(paciente=paciente).delete()
    ingeridos = json.loads(request.POST.get('ingeridos', '[]'))
    for i in ingeridos:
        clave = i.get('clave')
        cantidad = i.get('cantidad')
        ingerido = Medicamento.objects.get(clave=clave)
        MedIngeridoxPaciente.objects.create(paciente=paciente, medicamento=ingerido, cantidad=cantidad)

def guardar_administrados(request, paciente):
    MedAdministradoxPaciente.objects.filter(paciente=paciente).delete()
    administrados = json.loads(request.POST.get('administrado', '[]'))
    for i in administrados:
        clave = i.get('clave')
        cantidad = i.get('cantidad')
        administrado = Medicamento.objects.get(clave=clave)
        MedAdministradoxPaciente.objects.create(paciente=paciente, medicamento=administrado, cantidad=cantidad, costo=0)

def guardar_equipos(request, paciente):
    EquipoxPaciente.objects.filter(paciente=paciente).delete()
    equipos = json.loads(request.POST.get('equipo', '[]'))
    for i in equipos:
        clave = i.get('clave')
        cantidad = i.get('cantidad')
        equipo = Equipo.objects.get(clave=clave)
        EquipoxPaciente.objects.create(paciente=paciente, equipo=equipo, cantidad=cantidad)

def guardar_lesiones(request, paciente):
    LesionxPaciente.objects.filter(paciente=paciente).delete()
    lesiones = json.loads(request.POST.get('lesiones', '[]'))
    for i in lesiones:
        descripcion = i.get('descripcion')
        cantidad = i.get('valor') or '0'
        val_formato = float(cantidad.replace(',', '.'))
        LesionxPaciente.objects.create(paciente=paciente, lesion=descripcion, valor=val_formato)

def guardar_impactos(request, paciente):
    ImpactoxVehiculo.objects.filter(paciente=paciente).delete()
    impactos = json.loads(request.POST.get('impacto', '[]'))
    for i in impactos:
        descripcion = i.get('descripcion')
        ImpactoxVehiculo.objects.create(paciente=paciente, impacto=descripcion)

def guardar_testigos(request, paciente):
    TestigoxPaciente.objects.filter(paciente=paciente).delete()
    try:
        testigos = json.loads(request.POST.get('testigos', '[]'))
    except json.JSONDecodeError:
        testigos = []
    for i in testigos:
        nombre = i.get('nombre')
        edad = i.get('edad')
        direccion = i.get('direccion')
        telefono = i.get('telefono')
        TestigoxPaciente.objects.create(paciente=paciente, nombre=nombre, edad=edad, domicilio=direccion, telefono=telefono)

def reporte_servicio(request, clave):
    servicio = get_object_or_404(Servicio, clave=clave)
    paciente = PacientexServicio.objects.filter(servicio=servicio).first()

    template = get_template("reporte/reporte_servicio.html")
    context = {
        "servicio": servicio,
        "paciente": paciente,
        "paramedicos_asignados": ParamedicoxPaciente.objects.filter(servicio=servicio),
        "unidades_asignadas": UnidadxServicio.objects.filter(servicio=servicio),
        "procedimientos_asignados": ProcedimientoxPaciente.objects.filter(paciente__servicio=servicio),
        "alergias_asignados": AlergiaxPaciente.objects.filter(paciente__servicio=servicio),
        "materiales_asignados": MaterialxPaciente.objects.filter(paciente__servicio=servicio),
        "ingeridos_asignados": MedIngeridoxPaciente.objects.filter(paciente__servicio=servicio),
        "administrados_asignados": MedAdministradoxPaciente.objects.filter(paciente__servicio=servicio),
        "equipos_asignados": EquipoxPaciente.objects.filter(paciente__servicio=servicio),
        "lesiones_asignados": LesionxPaciente.objects.filter(paciente__servicio=servicio),
        "impactos_asignados": ImpactoxVehiculo.objects.filter(paciente__servicio=servicio),
        "testigos_asignados": TestigoxPaciente.objects.filter(paciente__servicio=servicio),
    }

    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="reporte_servicio_{clave}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)
    return response
