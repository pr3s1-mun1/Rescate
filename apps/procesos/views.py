from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from apps.catalogos.forms import *
from apps.catalogos.views import requiere_tipo_paramedico, Logs_Sistema
from .forms import ServicioForm, PacientesForm, EmbarazoAsignadoForm, PartesAsignadoForm
from django.http import HttpResponse
from collections import defaultdict
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Max
from django.http import JsonResponse
from django.core.paginator import Paginator


import datetime
import json


def formulario_buscar(request):
    if request.method == 'POST':
        filtros = request.POST.dict()
        pacientes_servicios_query = buscar_servicios_filtrados(filtros)
    else:
        pacientes_servicios_query = PacientexServicio.objects.all().order_by('-clave').select_related('servicio')

    paginator_con = Paginator(pacientes_servicios_query, 8)
    page_number_con = request.GET.get('page_con')
    pacientes_servicios = paginator_con.get_page(page_number_con)

    # Servicios sin pacientes (opcional, puedes agregar lógica similar)
    servicios_con_paciente_claves = pacientes_servicios_query.values_list('servicio__clave', flat=True).distinct()
    servicios_sin_paciente = Servicio.objects.exclude(clave__in=servicios_con_paciente_claves)

    paginator_sin = Paginator(servicios_sin_paciente, 8)
    page_number_sin = request.GET.get('page_sin')
    servicios_sin_paciente_page = paginator_sin.get_page(page_number_sin)

    return render(request, 'buscador_servicios.html', {
        'pacientes_servicios': pacientes_servicios,
        'servicios_sin_paciente': servicios_sin_paciente_page,
        'filtros': filtros if request.method == 'POST' else {},
    })


def buscar_servicios_filtrados(filtros):
    """
    filtros: dict con las claves de filtro y sus valores, por ejemplo:
    {
        'clave': 'abc',
        'fecha_inicio': '2025-01-01',
        'fecha_fin': '2025-01-31',
        'base': 'Base 1',
        'direccion': 'Calle 123',
        'paciente': 'Juan',
        'ropa': 'Azul',
        'sintoma': 'Dolor',
        'antecedente': 'Ninguno',
        'placas': 'XYZ123',
        'sexo': 'M',
        'servicio_realizado': 'Traslado',
        'enfermedad': 'Diabetes',
        'hospital': 'Hospital Central',
        'ambulancia': 'Ambulancia 1'
    }
    """
    from django.db.models import Q

    servicios = Servicio.objects.all()

    # Filtro por clave (en Servicio)
    clave = filtros.get('clave')
    if clave:
        servicios = servicios.filter(clave__icontains=clave)

    # Filtro fechas (en Servicio.fecha)
    fecha_inicio = filtros.get('fecha_inicio')
    fecha_fin = filtros.get('fecha_fin')
    if fecha_inicio:
        servicios = servicios.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        servicios = servicios.filter(fecha__lte=fecha_fin)

    # Filtro base (asumiendo que es un campo en Servicio)
    base = filtros.get('base')
    if base:
        servicios = servicios.filter(base__icontains=base)

    # Filtro dirección (en Servicio.direccion_emergencia.calle)
    direccion = filtros.get('direccion')
    if direccion:
        servicios = servicios.filter(direccion_emergencia__calle__icontains=direccion)

    # Ahora, para los filtros que involucran a pacientes o detalles de PacientexServicio:
    pacientes_qs = PacientexServicio.objects.filter(servicio__in=servicios)

    paciente = filtros.get('paciente')
    if paciente:
        pacientes_qs = pacientes_qs.filter(
            Q(nombre__icontains=paciente) | Q(apellido_paterno__icontains=paciente) | Q(apellido_materno__icontains=paciente)
        )

    ropa = filtros.get('ropa')
    if ropa:
        pacientes_qs = pacientes_qs.filter(ropa__icontains=ropa)

    sintoma = filtros.get('sintoma')
    if sintoma:
        pacientes_qs = pacientes_qs.filter(sintomas__icontains=sintoma)

    antecedente = filtros.get('antecedente')
    if antecedente:
        pacientes_qs = pacientes_qs.filter(antecedentes__icontains=antecedente)

    placas = filtros.get('placas')
    if placas:
        pacientes_qs = pacientes_qs.filter(placas__icontains=placas)

    sexo = filtros.get('sexo')
    if sexo:
        pacientes_qs = pacientes_qs.filter(sexo=sexo)

    servicio_realizado = filtros.get('servicio_realizado')
    if servicio_realizado:
        pacientes_qs = pacientes_qs.filter(servicio_realizado__icontains=servicio_realizado)

    enfermedad = filtros.get('enfermedad')
    if enfermedad:
        pacientes_qs = pacientes_qs.filter(enfermedad__icontains=enfermedad)

    hospital = filtros.get('hospital')
    if hospital:
        pacientes_qs = pacientes_qs.filter(hospital__icontains=hospital)

    ambulancia = filtros.get('ambulancia')
    if ambulancia:
        pacientes_qs = pacientes_qs.filter(ambulancia__icontains=ambulancia)

    # Devuelve la queryset filtrada (puedes usar .select_related si quieres optimizar)
    return pacientes_qs.select_related('servicio')


#Función para cargar formulario y pestañas de creación (Primera Parte)
@requiere_tipo_paramedico('P', 'A')
def formulario_servicio(request):    
    context = {
        'form': ServicioForm(initial={'clave': Servicio.obtener_siguiente_numero()}),
        'paramedicos': Paramedicos.objects.filter(estatus='A').order_by('nombre'),
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

            # Registro de log
            Logs_Sistema.objects.create(
                usuario=request.session.get("user", "Desconocido"),
                accion=f"Creó servicio con clave {servicio.clave}"
            )

            print("Servicio creado con éxito:", servicio.clave)
            return redirect('carga_modifica_n', pk=servicio.clave)

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
def carga_modifica(request, pk, ps):
    servicio = get_object_or_404(Servicio, pk=pk)
    form_servicio = ServicioForm(instance=servicio)

    paciente = None
    if ps is not None:
        try:
            paciente = PacientexServicio.objects.get(clave=ps, servicio=servicio)
        except PacientexServicio.DoesNotExist:
            paciente = None

    if paciente:
        form_paciente = PacientesForm(instance=paciente)
    else:
        form_paciente = PacientesForm(initial={'clave': PacientexServicio.obtener_siguiente_numero()})
 

    # 💡 Aquí obtenemos el Embarazo relacionado (si existe)
    embarazo_instancia = EmbarazoxPaciente.objects.filter(paciente=paciente).first()

    if embarazo_instancia:
        # Si ya existe, se carga en modo edición
        form_embarazo = EmbarazoAsignadoForm(instance=embarazo_instancia)
    else:
        # Si no existe, se calcula la siguiente secuencia y se carga como valor inicial
        max_secuencia = EmbarazoxPaciente.objects.aggregate(max_seq=Max('secuencia'))['max_seq'] or 0
        siguiente_secuencia = max_secuencia + 1
        form_embarazo = EmbarazoAsignadoForm(initial={'secuencia': siguiente_secuencia})

    parte_instancia = PartexServico.objects.filter(servicio=servicio).first()
    form_partes = PartesAsignadoForm(instance=parte_instancia)

    context = {
        'form': form_servicio,
        'form_paciente': form_paciente,
        'form_embarazo': form_embarazo,
        'form_partes': form_partes,
        'editar': True,
        'servicio': servicio,
        'paciente_clave': ps,
        'pacientes': PacientexServicio.objects.filter(servicio=servicio),
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
        'paramedicos': Paramedicos.objects.all(),
        'unidades': TipoUnidad.objects.all(),
        'alergias': Alergia.objects.all(),
        'materiales': Material.objects.all(),
        'medicamentos': Medicamento.objects.all(),
        'equipos': Equipo.objects.all(),
        'procedimientos': Procedimiento.objects.all().order_by('protocolo'),
    }

    return render(request, 'modificar_servicio.html', context)

@requiere_tipo_paramedico('P', 'A')
def carga_modifica_n(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    form_servicio = ServicioForm(instance=servicio)

    # Paciente nuevo: formulario sin instancia, pero con clave generada
    siguiente_clave = PacientexServicio.obtener_siguiente_numero()
    form_paciente = PacientesForm(initial={'clave': siguiente_clave})

    # El paciente aún no existe, así que no tiene embarazos asociados
    max_secuencia = EmbarazoxPaciente.objects.aggregate(max_seq=Max('secuencia'))['max_seq'] or 0
    siguiente_secuencia = max_secuencia + 1
    form_embarazo = EmbarazoAsignadoForm(initial={'secuencia': siguiente_secuencia})

    # Se puede cargar partes si ya existen por servicio
    parte_instancia = PartexServico.objects.filter(servicio=servicio).first()
    form_partes = PartesAsignadoForm(instance=parte_instancia)

    context = {
        'form': form_servicio,
        'form_paciente': form_paciente,
        'form_embarazo': form_embarazo,
        'form_partes': form_partes,
        'editar': True,
        'servicio': servicio,
        'paciente_clave': '',  # o None, ya que no existe aún
        'pacientes': PacientexServicio.objects.filter(servicio=servicio),
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
        'paramedicos': Paramedicos.objects.filter(estatus='A').order_by('nombre'),
        'unidades': TipoUnidad.objects.all(),
        'alergias': Alergia.objects.all().order_by('descripcion'),
        'materiales': Material.objects.all().order_by('descripcion'),
        'medicamentos': Medicamento.objects.all().order_by('descripcion'),
        'equipos': Equipo.objects.all().order_by('descripcion'),
        'procedimientos': Procedimiento.objects.all().order_by('protocolo', 'descripcion')
    }

    return render(request, 'modificar_servicio.html', context)


@requiere_tipo_paramedico('P', 'A')
def eliminar_servicio(request, pk):
    print("Eliminando servicio con pk:", pk)
    servicio = get_object_or_404(Servicio, pk=pk)
    servicio.delete()
    return redirect('formulario_buscar')

def guardar_todo(request, pk, ps):
    servicio = get_object_or_404(Servicio, pk=pk)

    paciente = None
    if ps and ps != 'None':
        try:
            paciente = PacientexServicio.objects.get(clave=ps, servicio=servicio)
        except PacientexServicio.DoesNotExist:
            paciente = None

    if request.method != 'POST':
        pacientes_form = PacientesForm(instance=paciente) if paciente else PacientesForm(
            initial={'clave': PacientexServicio.obtener_siguiente_numero()}
        )
        return render(request, 'modificar_servicio.html', {
            'form_servicio': ServicioForm(instance=servicio),
            'pacientes_form': pacientes_form,
            'servicio': servicio,
            'paciente': paciente,
            'editar': True
        })

    form_servicio = ServicioForm(request.POST, instance=servicio)
    pacientes_form = PacientesForm(request.POST, instance=paciente)
    partes_form = PartesAsignadoForm(request.POST, instance=servicio)

    if not (form_servicio.is_valid() and pacientes_form.is_valid() and partes_form.is_valid()):
        return render(request, 'modificar_servicio.html', {
            'form_servicio': form_servicio,
            'pacientes_form': pacientes_form,
            'servicio': servicio,
            'paciente': paciente,
            'editar': True,
            'errores_partes': partes_form.errors
        })
    if partes_form.is_valid():
        print("SISTABNNN")

    try:
        servicio = form_servicio.save(commit=False)
        servicio.clave = pk  # Se asegura que la clave no cambie
        servicio.save()

        paciente = pacientes_form.save(commit=False)
        parte = partes_form.save(commit=False)

        # Si es nuevo, generar clave manualmente
        if paciente.clave is None:
            paciente.clave = PacientexServicio.obtener_siguiente_numero()
        
        paciente.servicio = servicio
        paciente.save()

        parte.servicio = servicio
        try:
            parte.save()
        except Exception as e:
            print(e)


        # Guardado auxiliar
        guardar_unidades(request, servicio)
        guardar_paramedicos(request, servicio, paciente)
        guardar_procedimientos(request, paciente)
        guardar_alergias(request, paciente)
        guardar_materiales(request, paciente)
        guardar_ingeridos(request, paciente)
        guardar_administrados(request, paciente)
        guardar_equipos(request, paciente)
        guardar_lesiones(request, paciente)
        guardar_impactos(request, paciente)
        guardar_testigos(request, paciente)

        # Guardado de embarazo (si aplica)
        embarazo = request.POST.get('embarazo') == 'true'
        if embarazo:
            form_embarazo = EmbarazoAsignadoForm(request.POST)
            if form_embarazo.is_valid():
                embarazo_obj = form_embarazo.save(commit=False)
                embarazo_obj.paciente = paciente
                embarazo_obj.save()
            else:
                print('Error en formulario de embarazo:')
                print(form_embarazo.errors)


        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Actualizó servicio con clave {servicio.clave} y paciente con clave {paciente.clave if paciente else 'N/A'}"
        )
        return redirect('exito_guardado', pk=servicio.clave, ps=paciente.clave)

    except Exception as e:
        print(f"Error general: {e}")
        return redirect('fallo_guardado', error=str(e))


def guardar_todo_n(request, pk):
    print("🔍 Iniciando guardar_todo_n")
    servicio = get_object_or_404(Servicio, pk=pk)
    print(f"📦 Servicio encontrado: {servicio}")

    paciente = None  # ← Siempre será nuevo

    if request.method != 'POST':
        print("📄 GET recibido, preparando formulario con clave nueva de paciente")
        siguiente_clave = PacientexServicio.obtener_siguiente_numero()
        print(f"🆕 Clave generada para nuevo paciente: {siguiente_clave}")
        pacientes_form = PacientesForm(initial={'clave': siguiente_clave})
        return render(request, 'modificar_servicio.html', {
            'form_servicio': ServicioForm(instance=servicio),
            'pacientes_form': pacientes_form,
            'servicio': servicio,
            'paciente': paciente,
            'editar': True
        })

    print("📨 POST recibido, procesando formularios")
    form_servicio = ServicioForm(request.POST, instance=servicio)
    pacientes_form = PacientesForm(request.POST)

    if not form_servicio.is_valid():
        print("❌ Formulario de servicio inválido")
        print(form_servicio.errors)
    if not pacientes_form.is_valid():
        print("❌ Formulario de paciente inválido")
        print(pacientes_form.errors)

    if not (form_servicio.is_valid() and pacientes_form.is_valid()):
        return render(request, 'modificar_servicio.html', {
            'form_servicio': form_servicio,
            'pacientes_form': pacientes_form,
            'servicio': servicio,
            'paciente': paciente,
            'editar': True
        })

    try:
        # Guardar servicio
        servicio = form_servicio.save(commit=False)
        servicio.clave = pk  # Asegura clave original
        servicio.save()
        print(f"✅ Servicio guardado: {servicio}")

        # Guardar paciente nuevo
        paciente = pacientes_form.save(commit=False)
        clave_generada = PacientexServicio.obtener_siguiente_numero()
        paciente.clave = clave_generada
        paciente.servicio = servicio
        paciente.save()
        print(f"✅ Paciente guardado con clave {paciente.clave}")

        # Guardado auxiliar
        print("💾 Guardando auxiliares")
        guardar_unidades(request, servicio)
        guardar_paramedicos(request, servicio, paciente)
        guardar_procedimientos(request, paciente)
        guardar_alergias(request, paciente)
        guardar_materiales(request, paciente)
        guardar_ingeridos(request, paciente)
        guardar_administrados(request, paciente)
        guardar_equipos(request, paciente)
        guardar_lesiones(request, paciente)
        guardar_impactos(request, paciente)
        guardar_testigos(request, paciente)
        print("✅ Todos los datos auxiliares guardados")

        # Guardar embarazo si aplica
        if request.POST.get('embarazo') == 'true':
            print("🤰 Embarazo marcado como verdadero, procesando formulario")
            form_embarazo = EmbarazoAsignadoForm(request.POST)
            if form_embarazo.is_valid():
                embarazo_obj = form_embarazo.save(commit=False)
                embarazo_obj.paciente = paciente
                embarazo_obj.save()
                print("✅ Embarazo guardado correctamente")
            else:
                print('❌ Error en formulario de embarazo:', form_embarazo.errors)

        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Actualizó servicio con clave {servicio.clave} y paciente con clave {paciente.clave if paciente else 'N/A'}"
        )
        return redirect('exito_guardado', pk=servicio.clave, ps=paciente.clave)

    except Exception as e:
        print(f"❌ Error general en guardar_todo_n: {e}")
        return redirect('fallo_guardado', error=str(e))


def exito_guardado(request, pk, ps):
    return render(request, 'resp/exito_guardado.html', {'clave': pk, 'paciente' : ps})

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

def obtener_calles_por_colonia(request):
    colonia_id = request.GET.get('colonia_id')
    calles = Calle_Colonia.objects.filter(colonia_id=colonia_id).select_related('calle').order_by('calle__calle')
    data = [{'id': c.calle.clave, 'nombre': c.calle.calle} for c in calles]
    return JsonResponse(data, safe=False)
from django.db import transaction

@requiere_tipo_paramedico('P', 'A')

def agregar_paciente(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)

    if request.method == 'POST':
        form_paciente = PacientesForm(request.POST)
        form_embarazo = EmbarazoAsignadoForm(request.POST)
        form_partes = PartesAsignadoForm(request.POST)

        if form_paciente.is_valid():
            try:
                with transaction.atomic():
                    paciente = form_paciente.save(commit=False)

                    if paciente.clave is None:
                        paciente.clave = PacientexServicio.obtener_siguiente_numero()

                    paciente.servicio = servicio
                    paciente.save()

                    if form_embarazo.is_valid() and request.POST.get('embarazo') == 'true':
                        embarazo = form_embarazo.save(commit=False)
                        embarazo.paciente = paciente
                        embarazo.save()

                    if form_partes.is_valid():
                        parte = form_partes.save(commit=False)
                        parte.servicio = servicio
                        parte.save()

                    return redirect('carga_modifica_n', pk=servicio.pk)

            except Exception as e:
                print(f"Error al guardar el paciente: {e}")

        siguiente_clave = request.POST.get('clave')

    else:
        siguiente_clave = PacientexServicio.obtener_siguiente_numero()
        form_paciente = PacientesForm(initial={'clave': siguiente_clave})

        max_secuencia = EmbarazoxPaciente.objects.aggregate(max_seq=Max('secuencia'))['max_seq'] or 0
        siguiente_secuencia = max_secuencia + 1
        form_embarazo = EmbarazoAsignadoForm(initial={'secuencia': siguiente_secuencia})

        form_partes = PartesAsignadoForm()

    form_servicio = ServicioForm(instance=servicio)

    context = {
        'form': form_servicio,
        'form_paciente': form_paciente,
        'form_embarazo': form_embarazo,
        'form_partes': form_partes,
        'servicio': servicio,
        'siguiente_clave': siguiente_clave,  # <- Aquí se agrega
        'paramedicos_asignados': ParamedicoxPaciente.objects.filter(servicio=servicio),
        'unidades_asignadas': UnidadxServicio.objects.filter(servicio=servicio),
        'paramedicos': Paramedicos.objects.all(),
        'unidades': TipoUnidad.objects.all(),
        'alergias': Alergia.objects.all(),
        'materiales': Material.objects.all(),
        'medicamentos': Medicamento.objects.all(),
        'equipos': Equipo.objects.all(),
        'procedimientos': Procedimiento.objects.all(),
        'editar': False,
    }

    return render(request, 'agregar_paciente.html', context)

