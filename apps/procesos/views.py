from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from django.db.models import Max, Q, OuterRef, Exists

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


@requiere_tipo_paramedico(2, 3, 4, 5)
def formulario_buscar(request):
    if request.method == 'POST':
        filtros = request.POST.dict()
        # Obtener la consulta base de pacientexservicio filtrada
        pacientes_servicios_query = buscar_servicios_filtrados(filtros)
    else:
        # Caso sin filtros
        pacientes_servicios_query = PacientexServicio.objects.all().order_by('-servicio__clave').select_related('servicio')

    # Paginación para servicios CON pacientes (manteniendo nombre original)
    paginator_con = Paginator(pacientes_servicios_query, 9)
    page_number_con = request.GET.get('page_con')
    pacientes_servicios = paginator_con.get_page(page_number_con)

    # Obtener servicios SIN pacientes (optimizado)
    servicios_con_paciente_claves = pacientes_servicios_query.values_list('servicio__clave', flat=True).distinct()
    
    # Aplicar los mismos filtros a servicios sin pacientes si hay filtros activos
    if request.method == 'POST':
        servicios_sin_paciente = buscar_servicios_sin_pacientes(filtros).exclude(
            clave__in=servicios_con_paciente_claves
        )
    else:
        servicios_sin_paciente = Servicio.objects.exclude(
            clave__in=servicios_con_paciente_claves
        ).order_by('-clave')

    # Paginación para servicios SIN pacientes (manteniendo nombre original)
    paginator_sin = Paginator(servicios_sin_paciente, 9)
    page_number_sin = request.GET.get('page_sin')
    servicios_sin_paciente_page = paginator_sin.get_page(page_number_sin)

    return render(request, 'buscador_servicios.html', {
        'pacientes_servicios': pacientes_servicios,
        'servicios_sin_paciente': servicios_sin_paciente_page,
        'filtros': filtros if request.method == 'POST' else {},
    })

@requiere_tipo_paramedico(2, 3, 4, 5)
def buscar_servicios_sin_pacientes(filtros):
    """Función auxiliar para aplicar los mismos filtros a servicios sin pacientes"""
    
    servicios = Servicio.objects.all()
    
    # Aplicar los mismos filtros que en buscar_servicios_filtrados
    clave = filtros.get('clave')
    if clave:
        servicios = servicios.filter(clave__icontains=clave)

    fecha_inicio = filtros.get('fecha_inicio')
    fecha_fin = filtros.get('fecha_fin')
    if fecha_inicio:
        servicios = servicios.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        servicios = servicios.filter(fecha__lte=fecha_fin)

    base = filtros.get('base')
    if base:
        servicios = servicios.filter(base__icontains=base)

    direccion = filtros.get('direccion')
    if direccion:
        servicios = servicios.filter(direccion_emergencia__calle__icontains=direccion)
    
    return servicios

@requiere_tipo_paramedico(2, 3, 4, 5)
def buscar_servicios_filtrados(filtros):
    """
    Versión optimizada pero manteniendo la estructura original
    """

    # Base query ahora es sobre PacientexServicio (como en tu versión original)
    pacientes_qs = PacientexServicio.objects.all().select_related('servicio')

    # Filtros en campos del servicio (a través de la relación)
    clave = filtros.get('clave')
    if clave:
        pacientes_qs = pacientes_qs.filter(servicio__clave__icontains=clave)

    fecha_inicio = filtros.get('fecha_inicio')
    fecha_fin = filtros.get('fecha_fin')
    if fecha_inicio:
        pacientes_qs = pacientes_qs.filter(servicio__fecha__gte=fecha_inicio)
    if fecha_fin:
        pacientes_qs = pacientes_qs.filter(servicio__fecha__lte=fecha_fin)

    base = filtros.get('base')
    if base:
        pacientes_qs = pacientes_qs.filter(servicio__base__icontains=base)

    direccion = filtros.get('direccion')
    if direccion:
        pacientes_qs = pacientes_qs.filter(servicio__direccion_emergencia__calle__icontains=direccion)

    # Filtros en campos del paciente (manteniendo tu lógica original)
    paciente = filtros.get('paciente')
    if paciente:
        paciente = paciente.strip()
        if paciente.isdigit():
            pacientes_qs = pacientes_qs.filter(clave=int(paciente))
        else:
            palabras = paciente.split()
            filtros_q = Q()
            for palabra in palabras:
                filtros_q |= (
                    Q(nombre__icontains=palabra) |
                    Q(apellido_paterno__icontains=palabra) |
                    Q(apellido_materno__icontains=palabra)
                )
            pacientes_qs = pacientes_qs.filter(filtros_q)

    # Resto de filtros (manteniendo tus nombres originales)
    campos_filtro = [
        'ropa', 'sintoma', 'antecedente', 'placas', 'sexo',
        'servicio_realizado', 'enfermedad', 'hospital', 'ambulancia'
    ]
    
    for campo in campos_filtro:
        valor = filtros.get(campo)
        if valor:
            pacientes_qs = pacientes_qs.filter(**{f"{campo}__icontains": valor})

    return pacientes_qs.order_by('-servicio__clave')

#Función para cargar formulario y pestañas de creación (Primera Parte)
def formulario_servicio(request):    
    context = {
        'form': ServicioForm(initial={'clave': Servicio.obtener_siguiente_numero()}),
        'paramedicos': Paramedicos.objects.filter(estatus='A').exclude(clave=16).order_by('nombre'),
        'unidades': TipoUnidad.objects.all(),
        }
    
    return render(request, 'create.html', context)

#Función para mostrar conteos de hojas de servicio además de los botones de selección
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
        servicio_form = ServicioForm(request.POST)

        try:
            if servicio_form.is_valid():
                with transaction.atomic():
                    servicio = servicio_form.save()

                    # Procesar unidades
                    unidades = json.loads(request.POST.get('unidades', '[]'))
                    for u in unidades:
                        try:
                            if u.get('clave') and u.get('id_unidad'):
                                UnidadxServicio.objects.create(
                                    servicio=servicio,
                                    unidad=TipoUnidad.objects.get(clave=u['clave']),
                                    numero_unidad=u['id_unidad'],
                                    agente_nombre=u.get('agente', '')
                                )
                        except Exception as e:
                            print(f"Error al registrar unidad: {e}")
                            Logs_Sistema.objects.create(
                                usuario=request.session.get("user", "Desconocido"),
                                accion=f"Error al registrar unidad para servicio {servicio.clave}: {e}"
                            )

                    # Procesar paramédicos
                    paramedicos = json.loads(request.POST.get('paramedicos', '[]'))
                    for item in paramedicos:
                        try:
                            clave = item.get("clave")
                            paramedico = Paramedicos.objects.get(clave=clave)
                            ParamedicoxPaciente.objects.create(servicio=servicio, paramedico=paramedico)
                        except Exception as e:
                            print(f"Error al registrar paramédico: {e}")
                            Logs_Sistema.objects.create(
                                usuario=request.session.get("user", "Desconocido"),
                                accion=f"Error al registrar paramédico para servicio {servicio.clave}: {e}"
                            )

                    # Registro de log por creación exitosa
                    Logs_Sistema.objects.create(
                        usuario=request.session.get("user", "Desconocido"),
                        accion=f"Creó servicio con clave {servicio.clave}"
                    )

                    print(f"Servicio creado con éxito: {servicio.clave}")
                    return redirect('carga_modifica_n', pk=servicio.clave)

            else:
                # Formulario inválido
                print("Formulario inválido:", servicio_form.errors)
                Logs_Sistema.objects.create(
                    usuario=request.session.get("user", "Desconocido"),
                    accion=f"Error al crear servicio: formulario inválido: {servicio_form.errors.as_json()}"
                )

                context = {
                    'servicio_form': servicio_form,
                    'unidades': TipoUnidad.objects.all(),
                    'paramedicos': Paramedicos.objects.all(),
                    'errores': servicio_form.errors,
                }
                return render(request, 'modificar_servicio.html', context)

        except Exception as e:
            # Error inesperado
            print(f"Error inesperado al crear servicio: {e}")
            Logs_Sistema.objects.create(
                usuario=request.session.get("user", "Desconocido"),
                accion=f"Error inesperado al crear servicio: {e}"
            )

            context = {
                'servicio_form': servicio_form,
                'unidades': TipoUnidad.objects.all(),
                'paramedicos': Paramedicos.objects.filter(estatus='A', tipo='P').exclude(clave=16),
                'error_general': 'Ocurrió un error inesperado al crear el servicio.'
            }
            return render(request, 'modificar_servicio.html', context)

    else:
        servicio_form = ServicioForm()
    context = {
        'servicio_form': servicio_form,
        'unidades': TipoUnidad.objects.all(),
        'paramedicos': Paramedicos.objects.exclude(clave=16).filter(estatus='A', tipo='P'),
    }

    return render(request, 'modificar_servicio.html', context)

def carga_modifica(request, pk, ps):
    try:
        servicio = get_object_or_404(Servicio, pk=pk)
        form_servicio = ServicioForm(instance=servicio)

        paciente = None
        if ps is not None:
            try:
                paciente = PacientexServicio.objects.get(clave=ps, servicio=servicio)
            except PacientexServicio.DoesNotExist:
                print(f"Paciente con clave {ps} no encontrado para el servicio {pk}")

        permisos = request.session.get("permisos", 1)  # por defecto 1 si no se encuentra
        formularios_editables = permisos != 1
        print(formularios_editables)

        es_paciente_nuevo = False

        if paciente:
            form_paciente = PacientesForm(instance=paciente)
            if permisos == 1:
                es_paciente_nuevo = False  # usuario 1 no puede editar
            else:
                es_paciente_nuevo = True   # usuario 2 sí puede editar
        else:
            form_paciente = PacientesForm(initial={'clave': PacientexServicio.obtener_siguiente_numero()})
            es_paciente_nuevo = True  # ambos pueden crear


        # Embarazo relacionado
        embarazo_instancia = EmbarazoxPaciente.objects.filter(paciente=paciente).first()
        if embarazo_instancia:
            form_embarazo = EmbarazoAsignadoForm(instance=embarazo_instancia)
        else:
            max_secuencia = EmbarazoxPaciente.objects.aggregate(max_seq=Max('secuencia'))['max_seq'] or 0
            siguiente_secuencia = max_secuencia + 1
            form_embarazo = EmbarazoAsignadoForm(initial={'secuencia': siguiente_secuencia})

        # Parte
        parte_instancia = PartexServico.objects.filter(servicio=servicio).first()
        form_partes = PartesAsignadoForm(instance=parte_instancia)

        # Log de acceso exitoso
        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Accedió a modificar servicio con clave {pk} y paciente {ps if ps else 'nuevo'}"
        )
        print(f"Se ejecuta esta funcion")

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
            'quemaduras_asignados': QuemaduraxPaciente.objects.filter(paciente__servicio=servicio),
            'impactos_asignados': ImpactoxVehiculo.objects.filter(paciente__servicio=servicio),
            'testigos_asignados': TestigoxPaciente.objects.filter(paciente__servicio=servicio),
            'paramedicos': Paramedicos.objects.filter(estatus='A', tipo='P'),
            'unidades': TipoUnidad.objects.all(),
            'alergias': Alergia.objects.all(),
            'materiales': Material.objects.all(),
            'medicamentos': Medicamento.objects.all(),
            'equipos': Equipo.objects.all(),
            'procedimientos': Procedimiento.objects.all().order_by('protocolo'),
            'paciente_nuevo' : es_paciente_nuevo,
            'formularios_editables': formularios_editables,
        }

        return render(request, 'modificar_servicio.html', context)

    except Exception as e:
        print(f"Error en carga_modifica: {e}")
        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Error en carga_modifica para servicio {pk}: {e}"
        )
        return render(request, '404.html', {'mensaje': 'Ocurrió un error al cargar el servicio.'})

def carga_modifica_n(request, pk):
    try:
        permisos = request.session.get("permisos", 1)  # por defecto 1
        formularios_editables = permisos != 1
        es_paciente_nuevo = True
        print(es_paciente_nuevo)
        print(formularios_editables)
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

        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Accedió a carga_modifica_n para crear paciente nuevo en servicio {pk}"
        )
        print(f"Acceso a carga_modifica_n para servicio {pk} con paciente nuevo")

        context = {
            'form': form_servicio,
            'form_paciente': form_paciente,
            'form_embarazo': form_embarazo,
            'form_partes': form_partes,
            'editar': True,
            'servicio': servicio,
            'paciente_clave': '',  # aún no existe
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
            'quemaduras_asignados': QuemaduraxPaciente.objects.filter(paciente__servicio=servicio),
            'impactos_asignados': ImpactoxVehiculo.objects.filter(paciente__servicio=servicio),
            'testigos_asignados': TestigoxPaciente.objects.filter(paciente__servicio=servicio),
            'paramedicos': Paramedicos.objects.filter(estatus='A', tipo='P'),
            'unidades': TipoUnidad.objects.all(),
            'alergias': Alergia.objects.all().order_by('descripcion'),
            'materiales': Material.objects.all().order_by('descripcion'),
            'medicamentos': Medicamento.objects.all().order_by('descripcion'),
            'equipos': Equipo.objects.all().order_by('descripcion'),
            'procedimientos': Procedimiento.objects.all().order_by('protocolo', 'descripcion'),
            'paciente_nuevo': es_paciente_nuevo,
            'formularios_editables': formularios_editables,
        }

        return render(request, 'modificar_servicio.html', context)

    except Exception as e:
        print(f"Error en carga_modifica_n: {e}")
        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Error en carga_modifica_n para servicio {pk}: {e}"
        )
        return render(request, '404.html', {'mensaje': 'Ocurrió un error al preparar el formulario para un nuevo paciente.'})



@requiere_sesion
@requiere_tipo_paramedico(4, 5)
def eliminar_servicio(request, pk):
    print("Eliminando servicio con pk:", pk)
    servicio = get_object_or_404(Servicio, pk=pk)
    servicio.delete()
    return redirect('formulario_buscar')



def guardar_todo(request, pk, ps):
    try:
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

        # POST request
        form_servicio = ServicioForm(request.POST, instance=servicio)
        pacientes_form = PacientesForm(request.POST, instance=paciente)
        # Buscar si ya existe un PartexServico relacionado con ese servicio
        parte_instancia = PartexServico.objects.filter(servicio=servicio).first()

        # Crear el formulario con la instancia si existe, o sin instancia si es nuevo
        partes_form = PartesAsignadoForm(request.POST or None, instance=parte_instancia)

        if not (form_servicio.is_valid() and pacientes_form.is_valid() and partes_form.is_valid()):
            print("Errores en los formularios:")
            print("Servicio:", form_servicio.errors)
            print("Paciente:", pacientes_form.errors)
            print("Partes:", partes_form.errors)

            return render(request, 'modificar_servicio.html', {
                'form_servicio': form_servicio,
                'pacientes_form': pacientes_form,
                'servicio': servicio,
                'paciente': paciente,
                'editar': True,
                'errores_partes': partes_form.errors
            })

        servicio = form_servicio.save(commit=False)
        servicio.clave = pk  # Asegura que la clave no cambie
        servicio.save()

        paciente = pacientes_form.save(commit=False)
        parte = partes_form.save(commit=False)

        # Si es nuevo, generar clave manualmente
        if paciente.clave is None:
            paciente.clave = PacientexServicio.obtener_siguiente_numero()
        
        paciente.servicio = servicio
        paciente.save()

        parte.servicio = servicio
        parte.save()



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
        guardar_quemaduras(request, paciente)
        guardar_impactos(request, paciente)
        guardar_testigos(request, paciente)

        # Guardado de embarazo (si aplica)
        embarazo = request.POST.get('embarazo') == 'true'
        if embarazo:
            # Buscar si ya existe un embarazo del paciente
            embarazo_existente = EmbarazoxPaciente.objects.filter(paciente=paciente).first()

            if embarazo_existente:
                # Si existe, pasar como 'instance' para actualizar
                form_embarazo = EmbarazoAsignadoForm(request.POST, instance=embarazo_existente)
            else:
                # Si no, crear nuevo
                form_embarazo = EmbarazoAsignadoForm(request.POST)

            if form_embarazo.is_valid():
                embarazo_obj = form_embarazo.save(commit=False)
                embarazo_obj.paciente = paciente

                # Si es nuevo, asignar secuencia
                if not embarazo_existente:
                    ultima_secuencia = EmbarazoxPaciente.objects.aggregate(Max('secuencia'))['secuencia__max'] or 0
                    embarazo_obj.secuencia = ultima_secuencia + 1

                embarazo_obj.save()
            else:
                print('Error en formulario de embarazo:')
                print(form_embarazo.errors)

        # Log de éxito
        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Actualizó servicio con clave {servicio.clave} y paciente con clave {paciente.clave}"
        )
        print(f"Guardado exitoso del servicio {servicio.clave} y paciente {paciente.clave}")
        return redirect('exito_guardado', pk=servicio.clave, ps=paciente.clave)

    except Exception as e:
        print(f"Error general en guardar_todo: {e}")
        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Error general en guardar_todo para servicio {pk}: {e}"
        )
        base_url = reverse('fallo_guardado')
        query_string = urlencode({'error': str(e)})
        url = f"{base_url}?{query_string}"
        return redirect(url)



def guardar_todo_n(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    paciente = None  # Siempre será nuevo

    if request.method != 'POST':
        siguiente_clave = PacientexServicio.obtener_siguiente_numero()
        pacientes_form = PacientesForm(initial={'clave': siguiente_clave})
        return render(request, 'modificar_servicio.html', {
            'form_servicio': ServicioForm(instance=servicio),
            'pacientes_form': pacientes_form,
            'servicio': servicio,
            'paciente': paciente,
            'editar': True
        })

    form_servicio = ServicioForm(request.POST, instance=servicio)
    pacientes_form = PacientesForm(request.POST)

    if not form_servicio.is_valid():
        print("Formulario de servicio inválido")
        print(form_servicio.errors)

    if not pacientes_form.is_valid():
        print("Formulario de paciente inválido")
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
        servicio = form_servicio.save(commit=False)
        servicio.clave = pk
        servicio.save()

        paciente = pacientes_form.save(commit=False)
        clave_generada = PacientexServicio.obtener_siguiente_numero()
        paciente.clave = clave_generada
        paciente.servicio = servicio
        paciente.save()

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

        if request.POST.get('embarazo') == 'true':
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
                    accion=f"Error en formulario de embarazo para paciente {paciente.clave}: {form_embarazo.errors}"
                )

        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Guardó nuevo paciente con clave {paciente.clave} en servicio {servicio.clave}"
        )
        return redirect('exito_guardado', pk=servicio.clave, ps=paciente.clave)

    except Exception as e:
        print(f"Error general en guardar_todo_n: {e}")
        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Error general en guardar_todo_n para servicio {pk}: {e}"
        )
        return redirect('fallo_guardado', error=str(e))



def exito_guardado(request, pk, ps):
    return render(request, 'resp/exito_guardado.html', {'clave': pk, 'paciente' : ps})

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
        

        print(f"Guardando testigo: {nombre}, Edad: {edad}, Dirección: {direccion}, Teléfono: {telefono}")
        # Crear y guardar cada testigo
        TestigoxPaciente.objects.create(
            paciente=paciente,
            nombre=nombre,
            edad=edad,
            domicilio=direccion,
            telefono=telefono
        )

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



def agregar_paciente(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)

    permisos = request.session.get("permisos", 1)  # por defecto 1
    formularios_editables = permisos != 1
    es_paciente_nuevo = True
    print(es_paciente_nuevo)
    print(formularios_editables)
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
        'paramedicos': Paramedicos.objects.filter(estatus='A', tipo='P'),
        'unidades': TipoUnidad.objects.all(),
        'alergias': Alergia.objects.all(),
        'materiales': Material.objects.all(),
        'medicamentos': Medicamento.objects.all(),
        'equipos': Equipo.objects.all(),
        'procedimientos': Procedimiento.objects.all(),
        'editar': False,
        'paciente_nuevo' : es_paciente_nuevo,
        'formularios_editables': formularios_editables,
    }

    return render(request, 'agregar_paciente.html', context)


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
    alerta_fecha_futura = False
    hoy = timezone.now().date()

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('estatus_'):
                try:
                    paramedico_id = int(key.replace('estatus_', ''))
                    estatus = value
                    observacion = request.POST.get(f'observacion_{paramedico_id}', '').strip()
                    fecha_actual = timezone.now()

                    ya_existe = Reloj.objects.filter(
                        paramedico_id=paramedico_id,
                        fecha__date=fecha_actual.date()
                    ).exists()

                    if not ya_existe:
                        Reloj.objects.create(
                            paramedico_id=paramedico_id,
                            fecha=fecha_actual,
                            estatus=estatus,
                            observacion=observacion
                        )

                        Logs_Sistema.objects.create(
                            usuario=request.session.get("user", "Desconocido"),
                            accion=f"Registró asistencia de paramédico ID {paramedico_id} con estatus {estatus} el {fecha_actual}"
                        )

                        print(f"✅ Registrado paramédico {paramedico_id} con estatus {estatus}")
                    else:
                        print(f"⚠️ Ya existe asistencia para el paramédico {paramedico_id} hoy")

                except Exception as e:
                    print(f"❌ Error registrando asistencia de paramédico {paramedico_id}: {e}")
                    Logs_Sistema.objects.create(
                        usuario=request.session.get("user", "Desconocido"),
                        accion=f"Error registrando asistencia de paramédico {paramedico_id}: {e}"
                    )

        return redirect('ver_reloj')

    # Procesar filtro de fecha
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha_filtrada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_filtrada = hoy
    else:
        fecha_filtrada = hoy

    if fecha_filtrada > hoy:
        alerta_fecha_futura = True
        paramedicos = []
    else:
        # Solo paramédicos con registros ese día (exacto o hasta hoy si es hoy)
        if fecha_filtrada == hoy:
            relojes = Reloj.objects.filter(
                paramedico=OuterRef('pk'),
                fecha__date__lte=fecha_filtrada
            )
        else:
            relojes = Reloj.objects.filter(
                paramedico=OuterRef('pk'),
                fecha__date=fecha_filtrada
            )

        paramedicos = Paramedicos.objects.filter(
            Q(estatus='A') & (Q(tipo='P') | Q(tipo='A') | Q(tipo='S')),
            Exists(relojes)
        ).exclude(clave=16).order_by('nombre')

        for p in paramedicos:
            if fecha_filtrada == hoy:
                ultimo = Reloj.objects.filter(
                    paramedico=p,
                    fecha__date__lte=fecha_filtrada
                ).order_by('-fecha').first()
            else:
                ultimo = Reloj.objects.filter(
                    paramedico=p,
                    fecha__date=fecha_filtrada
                ).order_by('-fecha').first()

            p.ultimo_estatus = ultimo.estatus if ultimo else ''
            p.ultima_observacion = ultimo.observacion if ultimo else ''

    print(paramedicos)
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
