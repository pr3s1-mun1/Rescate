from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from django.db.models import Max, Q, OuterRef, Exists, Value, Subquery
from django.db.models.functions import Concat
from django.contrib import messages
from urllib.parse import urlencode

from urllib.parse import urlencode
from datetime import datetime, timedelta
from collections import defaultdict
import json
import io

from xhtml2pdf import pisa

from .models import *
from .forms import ServicioForm, PacientesForm, EmbarazoAsignadoForm, PartesAsignadoForm, CombustibleForm
from apps.catalogos.forms import *
from apps.catalogos.views import requiere_tipo_paramedico, requiere_sesion, Logs_Sistema


def paginar_queryset(qs, request, param='page', per_page=9):
    """Paginación genérica para cualquier queryset."""
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get(param)
    return paginator.get_page(page_number)

def buscar_servicios_filtrados(filtros):
    """
    Filtra PacientexServicio considerando campos simples y ForeignKeys
    a través de la relación Servicio.
    """
    qs = PacientexServicio.objects.all().select_related('servicio')

    # Filtros sobre Servicio
    if filtros.get('clave'):
        qs = qs.filter(servicio__clave__icontains=filtros['clave'])
    if filtros.get('fecha_inicio'):
        qs = qs.filter(servicio__fecha__date__gte=filtros['fecha_inicio'])
    if filtros.get('fecha_fin'):
        qs = qs.filter(servicio__fecha__date__lte=filtros['fecha_fin'])
    if filtros.get('direccion'):
        qs = qs.filter(servicio__direccion_emergencia__calle__icontains=filtros['direccion'])

    # Filtro por paciente
    paciente = filtros.get('paciente')
    if paciente:
        paciente = paciente.strip()
        if paciente.isdigit():
            qs = qs.filter(clave=int(paciente))
        else:
            qs = qs.annotate(
                nombre_completo=Concat(
                    'nombre', Value(' '),
                    'apellido_paterno', Value(' '),
                    'apellido_materno'
                )
            ).filter(nombre_completo__icontains=paciente)

    # Campos simples
    campos_simples = ['ropa', 'sintoma', 'antecedente', 'placas', 'sexo']
    for campo in campos_simples:
        valor = filtros.get(campo)
        if valor:
            qs = qs.filter(**{f"{campo}__icontains": valor})

    # ForeignKey en Servicio
    if filtros.get('servicio_realizado'):
        qs = qs.filter(
            servicio__tipo_servicio_realizado__descripcion__icontains=filtros['servicio_realizado']
        )


    # ForeignKeys en PacientexServicio
    if filtros.get('enfermedad'):
        qs = qs.filter(enfermedad__nombre__icontains=filtros['enfermedad'])
    if filtros.get('hospital'):
        qs = qs.filter(hospital__nombre__icontains=filtros['hospital'])
    if filtros.get('ambulancia'):
        qs = qs.filter(ambulancia__descripcion__icontains=filtros['ambulancia'])
    if filtros.get('base'):
        qs = qs.filter(base__clave__icontains=filtros['base'])

    return qs.order_by('-servicio__clave')



def buscar_servicios_sin_pacientes(filtros):
    """Aplica filtros sobre Servicios sin pacientes."""
    qs = Servicio.objects.all()
    if filtros.get('clave'):
        qs = qs.filter(clave__icontains=filtros['clave'])
    if filtros.get('fecha_inicio'):
        qs = qs.filter(fecha__gte=filtros['fecha_inicio'])
    if filtros.get('fecha_fin'):
        qs = qs.filter(fecha__lte=filtros['fecha_fin'])
    if filtros.get('direccion'):
        qs = qs.filter(direccion_emergencia__calle__icontains=filtros['direccion'])
    return qs


from urllib.parse import urlencode

@requiere_sesion
@requiere_tipo_paramedico(2, 3, 4, 5)
def formulario_buscar(request):
    filtros = request.GET.dict()

    # Pacientes con servicios existentes
    if filtros:
        pacientes_servicios_query = buscar_servicios_filtrados(filtros).filter(servicio__isnull=False)
    else:
        pacientes_servicios_query = (
            PacientexServicio.objects
            .filter(servicio__isnull=False)
            .select_related('servicio')
            .order_by('-servicio__clave')
        )

    pacientes_servicios = paginar_queryset(pacientes_servicios_query, request, 'page_con')

    # Claves de servicios con paciente
    claves_con_paciente = pacientes_servicios_query.values_list('servicio__clave', flat=True).distinct()

    # Servicios sin pacientes asociados
    if filtros:
        servicios_sin_paciente_query = (
            buscar_servicios_sin_pacientes(filtros)
            .exclude(clave__in=claves_con_paciente)
        )
    else:
        servicios_sin_paciente_query = (
            Servicio.objects
            .exclude(clave__in=claves_con_paciente)
            .order_by('-clave')
        )

    servicios_sin_paciente = paginar_queryset(servicios_sin_paciente_query, request, 'page_sin')

    # Reconstruir query string sin parámetros de paginación
    filtros_sin_paginacion = {k: v for k, v in filtros.items() if k not in ['page_con', 'page_sin']}
    query_string = urlencode(filtros_sin_paginacion)

    context = {
        'pacientes_servicios': pacientes_servicios,
        'servicios_sin_paciente': servicios_sin_paciente,
        'filtros': filtros,
        'query_string': query_string,
    }
    return render(request, 'buscador_servicios.html', context)


#Función para cargar formulario y pestañas de creación (Primera Parte)
def formulario_servicio(request):    
    context = {
        'form': ServicioForm(),
        'paramedicos': Paramedicos.objects.filter(estatus='A').exclude(clave=16).order_by('nombre'),
        'unidades': TipoUnidad.objects.all(),
        'no_mostrar_pacientes': True,
        }
    
    return render(request, 'create.html', context)

#Función para mostrar conteos de hojas de servicio además de los botones de selección
@requiere_sesion
def vista_principal(request):
    hoy = timezone.now().date()

    # Servicios realizados hoy
    servicios_hoy = Servicio.objects.filter(fecha=hoy).count()

    # Servicios en total
    servicios_tot = Servicio.objects.count()

    # Pacientes únicos hoy (por nombre + apellidos) — como no hay FK a paciente
    pacientes_hoy = PacientexServicio.objects.filter(
        servicio__fecha=hoy
    ).values('nombre', 'apellido_paterno', 'apellido_materno').distinct().count()

    # Servicios del mes actual
    servicios_mes = Servicio.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).count()

    # Pacientes únicos del mes
    pacientes_mes = PacientexServicio.objects.filter(
        servicio__fecha__year=hoy.year,
        servicio__fecha__month=hoy.month
    ).values('nombre', 'apellido_paterno', 'apellido_materno').distinct().count()

    # Últimos 3 servicios ordenados por fecha y hora descendente
    ultimos_servicios = Servicio.objects.order_by('-clave')[:10]

    # Obtener pacientes asociados a esos servicios y preparar datos para la plantilla
    ultimos_servicios_con_pacientes = []
    for servicio in ultimos_servicios:
        pacientes = PacientexServicio.objects.filter(servicio=servicio)
        for pxservicio in pacientes:
            nombre_completo = f"{pxservicio.nombre} {pxservicio.apellido_paterno} {pxservicio.apellido_materno}".strip()
            paciente = pxservicio.clave
            ultimos_servicios_con_pacientes.append({
                'servicio': servicio,
                'paciente_nombre': nombre_completo,
                'registro': pxservicio,
                'domicilio': pxservicio.domicilio,
                'colonia': pxservicio.colonia,
                'clavepaciente': paciente,
            })

    # Limitar a 3 registros para no saturar la vista
    ultimos_servicios_con_pacientes = ultimos_servicios_con_pacientes[:10]


    hace_24_horas = timezone.now() - timedelta(hours=24)
    ult_24_horas = Servicio.objects.filter(fecha__gte=hace_24_horas).count()

    context = {
        'servicios_hoy': servicios_hoy,
        'pacientes_hoy': pacientes_hoy,
        'servicios_mes': servicios_mes,
        'pacientes_mes': pacientes_mes,
        'ultimos_servicios_pacientes': ultimos_servicios_con_pacientes,
        'total_servicios': servicios_tot,
        'conteo_ultimos': ult_24_horas,
        'hoy': hoy,  # Por si quieres usar en plantilla para fechas u otras referencias
    }

    return render(request, 'serv_principal.html', context)


def crear_servicio(request):
    if request.method == 'POST':
        servicio_guardado = guardar_servicio(request)
        if servicio_guardado:
            # redirige a la vista de agregar paciente del servicio recién creado
            messages.success(request, "Servicio guardado exitosamente")
            return redirect('agregar_paciente', pk=servicio_guardado.pk)
        else:
            # si falla guardar_servicio, recarga la misma página
            messages.error(request, "Error al guardar el servicio. Por favor, inténtelo de nuevo.")
            return redirect('crear_servicio', )  


@requiere_sesion
@requiere_tipo_paramedico(4, 5)
def eliminar_servicio(request, pk):
    print("Eliminando servicio con pk:", pk)
    servicio = get_object_or_404(Servicio, pk=pk)
    servicio.delete()
    Logs_Sistema.objects.create(
        usuario=request.session.get('user', 'desconocido'),
        accion=f"Eliminó servicio {pk}"
    ) 
    return redirect('formulario_buscar')

#279362

def guardar_auxiliares(request, servicio, paciente):
        guardar_unidades(request, servicio)
        guardar_paramedicos(request, servicio, paciente)
        guardar_procedimientos(request, paciente)
        guardar_alergias(request, paciente)
        guardar_materiales(request, paciente)
        guardar_ingeridos(request, paciente)
        guardar_administrados(request, paciente)
        guardar_equipos(request, paciente)
        guardar_lesiones(request, paciente)
        guardar_quemaduras(request, paciente)
        guardar_impactos(request, paciente)
        guardar_testigos(request, paciente)


def fallo_guardado(request):
    error = request.GET.get('error', 'Error desconocido')
    return render(request, 'fallo_guardado.html', {'error': error})


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

def guardar_paramedicos(request, servicio, paciente):
    ParamedicoxPaciente.objects.filter(servicio=servicio).delete()
    paramedicos = json.loads(request.POST.get('paramedicos', '[]'))
    for item in paramedicos:
        clave = item.get("clave")
        paramedico = Paramedicos.objects.get(clave=clave)
        ParamedicoxPaciente.objects.create(servicio=servicio, paramedico=paramedico, paciente=paciente)

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

def guardar_quemaduras(request, paciente):
    QuemaduraxPaciente.objects.filter(paciente=paciente).delete()
    quemaduras = json.loads(request.POST.get('quemaduras', '[]'))
    for i in quemaduras:
        descripcion = i.get('descripcion')
        cantidad = i.get('valor') or '0'
        val_formato = float(cantidad.replace(',', '.'))
        QuemaduraxPaciente.objects.create(paciente=paciente, quemadura=descripcion, valor=val_formato)

def guardar_impactos(request, paciente):
    ImpactoxVehiculo.objects.filter(paciente=paciente).delete()
    impactos = json.loads(request.POST.get('impacto', '[]'))
    for i in impactos:
        descripcion = i.get('descripcion')
        ImpactoxVehiculo.objects.create(paciente=paciente, impacto=descripcion)

def guardar_testigos(request, paciente):
    # Borra los testigos previos asociados al paciente
    TestigoxPaciente.objects.filter(paciente=paciente).delete()
    
    try:
        testigos = json.loads(request.POST.get('testigos', '[]'))
    except json.JSONDecodeError:
        testigos = []
    
    for testigo_data in testigos:
        nombre = testigo_data.get('nombre')
        edad = testigo_data.get('edad')
        direccion = testigo_data.get('direccion')
        telefono = testigo_data.get('telefono')
        parentesco = testigo_data.get('parentesco')
        
        # Crear y guardar cada testigo
        TestigoxPaciente.objects.create(
            paciente=paciente,
            nombre=nombre,
            edad=edad,
            domicilio=direccion,
            telefono=telefono,
            parentesco=parentesco
        )

@requiere_tipo_paramedico(3, 4, 5)
def reporte_servicio(request, clave):
    servicio = get_object_or_404(Servicio, clave=clave)
    paciente = PacientexServicio.objects.filter(servicio=servicio).first()

    template = get_template("reporte/reporte_servicio.html")
    context = {
        "servicio": servicio,
        "paciente": paciente,
        "paramedicos_asignados": ParamedicoxPaciente.objects.filter(servicio=servicio),
        "unidades_asignadas": UnidadxServicio.objects.filter(servicio=servicio),
        "parte": PartexServico.objects.filter(servicio=servicio),
        "procedimientos_asignados": ProcedimientoxPaciente.objects.filter(paciente__servicio=servicio),
        "alergias_asignados": AlergiaxPaciente.objects.filter(paciente__servicio=servicio),
        "materiales_asignados": MaterialxPaciente.objects.filter(paciente__servicio=servicio),
        "ingeridos_asignados": MedIngeridoxPaciente.objects.filter(paciente__servicio=servicio),
        "administrados_asignados": MedAdministradoxPaciente.objects.filter(paciente__servicio=servicio),
        "equipos_asignados": EquipoxPaciente.objects.filter(paciente__servicio=servicio),
        "lesiones_asignados": LesionxPaciente.objects.filter(paciente__servicio=servicio),
        "impactos_asignados": ImpactoxVehiculo.objects.filter(paciente__servicio=servicio),
        "testigos_asignados": TestigoxPaciente.objects.filter(paciente__servicio=servicio),
        "paramedico_asignados": ParamedicoxPaciente.objects.filter(paciente__servicio=servicio),
    }

    print(context['parte'])
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="reporte_servicio_{clave}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)
    return response

def obtener_colonias_por_calle(request):
    calle_id = request.GET.get('calle_id')
    colonias = Calle_Colonia.objects.filter(calle_id=calle_id).select_related('colonia').order_by('colonia__colonia')
    data = [{'id': c.colonia.clave, 'nombre': c.colonia.colonia} for c in colonias]
    return JsonResponse(data, safe=False)

def obtener_calles_por_calle(request):
    calle_id = request.GET.get('calle_id')  
    if not calle_id:
        return JsonResponse([], safe=False)

    colonias_ids = Calle_Colonia.objects.filter(
        calle=calle_id
    ).values_list('colonia', flat=True).distinct()

    calles = Calle_Colonia.objects.filter(
        colonia__in=colonias_ids
    ).select_related('calle').values(
        'calle', 'calle__calle'
    ).distinct().order_by('calle__calle')

    data = [{'id': c['calle'], 'nombre': c['calle__calle']} for c in calles]
    return JsonResponse(data, safe=False)



salidas_enfalso = ['34', '35', '213']

def agregar_paciente(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)

    if request.method == 'POST':
        tipo_servicio_realizado = request.POST.get('tipo_servicio_realizado', '')

        if tipo_servicio_realizado in salidas_enfalso:
            # Solo guardamos servicio
            servicio_guardado = guardar_servicio(request, servicio)
            if not servicio_guardado:
                return render(request, 'agregar_paciente.html', {'form': ServicioForm(instance=servicio)})
            messages.success(request, "Servicio guardado exitosamente")
            return redirect('carga_modifica_v2', pk=servicio_guardado.pk)
        else:
            # Flujo completo: servicio → paciente → embarazo/partes
            try:
                #Guardar parte
                form_partes = PartesAsignadoForm(request.POST)
                if form_partes.is_valid():
                    parte = form_partes.save(commit=False)
                    parte.servicio = servicio
                    parte.save()

                # Guardar el servicio
                servicio_guardado = guardar_servicio(request, servicio)
                if not servicio_guardado:
                    return render(request, 'agregar_paciente.html', {'form': ServicioForm(instance=servicio)})

                # Guardar paciente → aquí se genera la clave automáticamente
                paciente = guardar_paciente(servicio_guardado, request)
                guardar_servicio(request, servicio_guardado, paciente)

                # Guardar embarazo y partes
                guardar_embarazo_partes(paciente, servicio_guardado, request)

                # Redirigir usando la clave generada
                messages.success(request, "Paciente y servicio guardados exitosamente")
                return redirect('carga_modifica_v2_ps', pk=servicio_guardado.pk, ps=paciente.clave)

            except Exception as e:
                messages.error(request, "Error al guardar datos")
                print(f"Error al guardar datos: {e}")


    else:
        form_servicio = ServicioForm(instance=servicio)
        form_paciente = PacientesForm()
        form_embarazo = EmbarazoAsignadoForm()

        parte_instancia = PartexServico.objects.filter(servicio=servicio).first()
        form_partes = PartesAsignadoForm(instance=parte_instancia)

    context = {
        'form': form_servicio,
        'form_paciente': form_paciente,
        'form_embarazo': form_embarazo,
        'form_partes': form_partes,
        'servicio': servicio,
        'no_mostrar_pacientes': True,
        "paramedicos_asignados": ParamedicoxPaciente.objects.filter(servicio=servicio),
        "unidades_asignadas": UnidadxServicio.objects.filter(servicio=servicio),
    }

    context.update(carga_relacionados(servicio))
    return render(request, 'agregar_paciente.html', context)

@requiere_sesion
def carga_modifica_v2(request, pk, ps=None):
    servicio = get_object_or_404(Servicio, pk=pk)
    paciente = None
    formularios_editables = True
    usuario = request.session.get("permisos", 1)
    formularios_editables = usuario in [2, 3, 4, 5]

    if ps:
        paciente = get_object_or_404(PacientexServicio, clave=ps, servicio=servicio)

    if request.method == 'POST':
        # Instancia
        guardar_servicio(request, servicio, paciente=paciente)
        messages.success(request, "Servicio actualizado exitosamente")

        if paciente:
            paciente = guardar_paciente(servicio, request, paciente_existente=paciente)
            messages.success(request, "Servicio y paciente actualizados exitosamente")
            return redirect('carga_modifica_v2_ps', pk=pk, ps=paciente.clave)

        
        return redirect('carga_modifica_v2', pk=pk)

    # Formulario del servicio
    form_servicio = ServicioForm(instance=servicio)

    # Partes 
    parte_instancia = PartexServico.objects.filter(servicio=servicio).first()
    form_partes = PartesAsignadoForm(instance=parte_instancia)

    # Paciente
    if paciente:
        form_paciente = PacientesForm(instance=paciente)
        embarazo_instancia = EmbarazoxPaciente.objects.filter(paciente=paciente).first()
        form_embarazo = EmbarazoAsignadoForm(instance=embarazo_instancia)
        hay_paciente = True
    else:
        form_paciente = None
        form_embarazo = None
        hay_paciente = False

    context = {
        'form': form_servicio,
        'form_paciente': form_paciente,
        'form_embarazo': form_embarazo,
        'form_partes': form_partes,
        'paciente_clave': ps,
        'servicio': servicio,
        'hay_paciente': hay_paciente,
        'formularios_editables': formularios_editables,
    }

    context.update(carga_relacionados(servicio, paciente))

    return render(request, 'modificar_servicio.html', context)




def carga_relacionados(servicio, paciente=None):
    """
    Retorna un diccionario con todos los objetos relacionados a un paciente y servicio.
    Si paciente es None, solo devuelve los datos de servicio.
    """
    context = {
        'paramedicos_asignados': ParamedicoxPaciente.objects.filter(servicio=servicio),
        'unidades_asignadas': UnidadxServicio.objects.filter(servicio=servicio),
        'paramedicos': Paramedicos.objects.filter(estatus='A', tipo='P'),
        'unidades': TipoUnidad.objects.all(),
        'alergias': Alergia.objects.all().order_by('descripcion'),
        'materiales': Material.objects.all().order_by('descripcion'),
        'medicamentos': Medicamento.objects.all().order_by('descripcion'),
        'equipos': Equipo.objects.all().order_by('descripcion'),
        'procedimientos': Procedimiento.objects.all().order_by('protocolo', 'descripcion'),
    }

    if paciente:
        context.update({
            'pacientes': PacientexServicio.objects.filter(servicio=servicio),
            'procedimientos_asignados': ProcedimientoxPaciente.objects.filter(paciente=paciente),
            'alergias_asignados': AlergiaxPaciente.objects.filter(paciente=paciente),
            'materiales_asignados': MaterialxPaciente.objects.filter(paciente=paciente),
            'ingeridos_asignados': MedIngeridoxPaciente.objects.filter(paciente=paciente),
            'administrados_asignados': MedAdministradoxPaciente.objects.filter(paciente=paciente),
            'equipos_asignados': EquipoxPaciente.objects.filter(paciente=paciente),
            'lesiones_asignados': LesionxPaciente.objects.filter(paciente=paciente),
            'quemaduras_asignados': QuemaduraxPaciente.objects.filter(paciente=paciente),
            'impactos_asignados': ImpactoxVehiculo.objects.filter(paciente=paciente),
            'testigos_asignados': TestigoxPaciente.objects.filter(paciente=paciente),
        })

    return context

    


def guardar_servicio(request, servicio=None, paciente=None):
    """
    Guarda o actualiza un servicio.
    También guarda sus unidades, paramédicos y parte asociada.
    Retorna el servicio guardado o None si hay errores.
    """
    # Crear o actualizar servicio
    form_servicio = ServicioForm(request.POST, instance=servicio) if servicio else ServicioForm(request.POST)

    if not form_servicio.is_valid():
        print("❌ Errores en formulario de servicioooo:", form_servicio.errors)
        messages.error(request, "Error al guardar el servicio. Por favor, revise los datos e intente nuevamente.")
        return None, form_servicio.errors

    servicio = form_servicio.save()

    # Guardar unidades y paramédicos
    guardar_unidades(request, servicio)
    guardar_paramedicos(request, servicio, paciente=paciente)

    # Guardar o actualizar parte asociada al servicio
    parte_instancia = PartexServico.objects.filter(servicio=servicio).first()
    form_partes = PartesAsignadoForm(request.POST, instance=parte_instancia)

    if form_partes.is_valid():
        parte = form_partes.save(commit=False)
        parte.servicio = servicio
        parte.save()
    else:
        print("⚠️ Errores en formulario de partes:", form_partes.errors)

    # Log del sistema
    Logs_Sistema.objects.create(
        usuario=request.session.get("user", "Desconocido"),
        accion=f"Servicio guardado con clave {servicio.clave}"
    )

    return servicio



def guardar_paciente(servicio, request, paciente_existente=None):
    """
    Crea o actualiza un paciente asociado a un servicio.
    También guarda todos los datos dependientes (procedimientos, alergias, etc.)
    Retorna la instancia del paciente guardado.
    """
    form_paciente = PacientesForm(request.POST, instance=paciente_existente)

    if form_paciente.is_valid():
        paciente = form_paciente.save(commit=False)
        paciente.servicio = servicio
        paciente.save()

        # Guardar datos relacionados del paciente
        guardar_procedimientos(request, paciente)
        guardar_alergias(request, paciente)
        guardar_materiales(request, paciente)
        guardar_ingeridos(request, paciente)
        guardar_administrados(request, paciente)
        guardar_equipos(request, paciente)
        guardar_lesiones(request, paciente)
        guardar_quemaduras(request, paciente)
        guardar_impactos(request, paciente)
        guardar_testigos(request, paciente)

        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Paciente guardado con clave {paciente.clave} en servicio {servicio.clave}"
        )

        embarazo = request.POST.get('embarazo')
        

        return paciente

    else:
        print("❌ Errores en formulario de paciente:", form_paciente.errors)
        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Error al guardar paciente en servicio {servicio.clave}: {form_paciente.errors}"
        )
        return paciente_existente





@requiere_sesion
@requiere_tipo_paramedico(3, 4, 5)
def lista_combustible(request):
    combustibles = Combustible.objects.all().order_by('-fecha')

    # Filtros
    fecha = request.GET.get('fecha')
    factura = request.GET.get('factura')
    remision = request.GET.get('remision')

    if fecha:
        combustibles = combustibles.filter(fecha__date=fecha)
    if factura:
        combustibles = combustibles.filter(factura__icontains=factura)
    if remision:
        combustibles = combustibles.filter(remision__icontains=remision)

    # Paginación
    paginator = Paginator(combustibles, 10)  # 10 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'combustible/gasolina.html', {
        'page_obj': page_obj,
        'fecha': fecha,
        'factura': factura,
        'remision': remision,
    })

@requiere_sesion
@requiere_tipo_paramedico(3, 4, 5)
def crear_combustible(request):
    if request.method == 'POST':
        form = CombustibleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_combustible')
    else:
        form = CombustibleForm()
    return render(request, 'combustible/formulario.html', {'form': form, 'accion': 'Crear'})

@requiere_sesion
@requiere_tipo_paramedico(3, 4, 5)
def editar_combustible(request, clave):
    combustible = get_object_or_404(Combustible, clave=clave)
    if request.method == 'POST':
        form = CombustibleForm(request.POST, instance=combustible)
        if form.is_valid():
            form.save()
            return redirect('lista_combustible')
    else:
        form = CombustibleForm(instance=combustible)
    return render(request, 'combustible/formulario.html', {'form': form, 'accion': 'Editar'})



@requiere_sesion
@requiere_tipo_paramedico(3, 4, 5)
def ver_reloj(request):
    hoy = timezone.now().date()
    alerta_fecha_futura = False
    fecha_str = request.GET.get('fecha')

    # Procesar fecha filtrada
    try:
        fecha_filtrada = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else hoy
    except ValueError:
        fecha_filtrada = hoy

    if fecha_filtrada > hoy:
        alerta_fecha_futura = True

    # POST: registrar o actualizar estatus
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('estatus_'):
                try:
                    # key = estatus_{paramedico_id}
                    paramedico_id = int(key.replace('estatus_', ''))
                    observacion = request.POST.get(f'observacion_{paramedico_id}', '').strip()

                    # Tomar fecha enviada en el formulario, si existe
                    fecha_input_str = request.POST.get(f'fecha_{paramedico_id}', fecha_filtrada.strftime('%Y-%m-%d'))
                    try:
                        fecha_input = datetime.strptime(fecha_input_str, '%Y-%m-%d').date()
                    except ValueError:
                        fecha_input = hoy

                    # Buscar o crear registro para esa fecha
                    obj, created = Reloj.objects.get_or_create(
                        paramedico_id=paramedico_id,
                        fecha__date=fecha_input,
                        defaults={'estatus': value, 'observacion': observacion, 'fecha': datetime.combine(fecha_input, datetime.min.time())}
                    )

                    if not created:
                        obj.estatus = value
                        obj.observacion = observacion
                        obj.save()

                except Exception as e:
                    print(f"❌ Error registrando asistencia: {e}")

        return redirect(f'{request.path}?fecha={fecha_filtrada.strftime("%Y-%m-%d")}')

    # Obtener paramédicos con último estatus de la fecha filtrada
    if not alerta_fecha_futura:
        relojes = Reloj.objects.filter(
            paramedico=OuterRef('pk'),
            fecha__date__lte=fecha_filtrada
        ).order_by('-fecha')

        paramedicos = Paramedicos.objects.filter(
            Q(estatus='A') & Q(tipo__in=['P', 'A', 'S'])
        ).exclude(clave=16).annotate(
            ultimo_estatus=Subquery(relojes.values('estatus')[:1]),
            ultima_observacion=Subquery(relojes.values('observacion')[:1])
        ).order_by('nombre')
    else:
        paramedicos = []

    status_options = [
        ('A', 'ACTIVO'), ('F', 'BAJA'), ('D', 'DESCANSO'), ('E', 'DESCANSO ADICIONAL'),
        ('N', 'FALTA INJUSTIFICADA'), ('J', 'FALTA JUSTIFICADA'), ('I', 'INCAPACIDAD'),
        ('P', 'PERMISO'), ('S', 'SUSPENSION'), ('V', 'VACACIONES')
    ]

    return render(request, 'reloj/reloj.html', {
        'paramedicos': paramedicos,
        'status_options': status_options,
        'fecha_filtrada': fecha_filtrada.strftime('%Y-%m-%d'),
        'alerta_fecha_futura': alerta_fecha_futura,
    })


@requiere_sesion
@requiere_tipo_paramedico(3, 4, 5)
def imprimir_reporte(request):


    fecha_str = request.GET.get('fecha')
    fecha = timezone.now().date()
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    paramedicos = Paramedicos.objects.filter(
        Q(estatus='A') & (Q(tipo='P') | Q(tipo='A') | Q(tipo='S'))
    ).exclude(clave=16).order_by('nombre')

    for p in paramedicos:
        ultimo = Reloj.objects.filter(
            paramedico=p,
            fecha__date=fecha
        ).order_by('-fecha').first()

        p.ultimo_estatus = ultimo.estatus if ultimo else ''
        p.ultima_observacion = ultimo.observacion if ultimo else ''

    # Renderizar template a HTML string
    template = get_template('reloj/reporte_imprimible.html')
    html = template.render({
        'paramedicos': paramedicos,
        'fecha': fecha.strftime('%Y-%m-%d'),
        'request': request,  # Para resolver static en el template
    })

    print(paramedicos)

    # Crear PDF en memoria
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="reporte_asistencia.pdf"'

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode('UTF-8')), result)

    if not pdf.err:
        response.write(result.getvalue())
        return response
    else:
        return HttpResponse('Error al generar PDF', status=500)



def guardar_embarazo_partes(paciente, servicio, request):
    """
    Guarda embarazo y partes solo si existen y son válidos.
    """
    form_embarazo = EmbarazoAsignadoForm(request.POST)
    form_partes = PartesAsignadoForm(request.POST)

    if paciente and form_embarazo.is_valid() and request.POST.get('embarazo') == 'true':
        embarazo = form_embarazo.save(commit=False)
        embarazo.paciente = paciente
        embarazo.save()

    if form_partes.is_valid():
        parte = form_partes.save(commit=False)
        parte.servicio = servicio
        parte.save()



def guardar_sin_paciente(request, pk):
    """
    Guarda un servicio sin paciente asociado.
    Redirige a la vista de modificación si se guarda correctamente.
    """
    print("Guardando servicio sin paciente para pk:", pk)
    try:
        # Verifica que el servicio exista
        servicio = get_object_or_404(Servicio, pk=pk)

        # Llama a la función que guarda los datos
        servicio_guardado = guardar_servicio(request, servicio=servicio)

        if servicio_guardado:
            messages.success(request, "Servicio guardado exitosamente (sin paciente).")
            return redirect('carga_modifica_v2', pk=servicio_guardado.pk)
        else:
            messages.error(request, "No se pudo guardar el servicio. Intenta nuevamente.")
            return redirect('agregar_paciente', pk=pk)

    except Exception as e:
        print(f"⚠️ Error al guardar sin paciente: {e}")
        messages.error(request, f"Ocurrió un error inesperado: {str(e)}")
        return redirect('carga_modifica_v2', pk=pk)