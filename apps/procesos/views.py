from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from apps.catalogos.forms import *
from .forms import ParamedicosForm, ServicioForm, PacientesForm, UnidadAsignadoForm, ParamedicoAsignadoForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime
import json


def formulario_buscar(request):
    clave = request.POST.get('clave', '').strip() if request.method == 'POST' else ''
    servicios = Servicio.objects.filter(clave__icontains=clave) if clave else Servicio.objects.all()
    servicios = servicios.order_by('clave')  # ← Aquí aplicamos el orden

    pacientes = PacientexServicio.objects.filter(servicio__in=servicios)

    return render(request, 'buscador_servicios.html', {
        'servicios': servicios,
        'pacientes': pacientes
    })



#Función para cargar formulario y pestañas de creación (Primera Parte)
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
from django.shortcuts import render, redirect
from django.http import Http404
import json
from .forms import ServicioForm
from .models import Servicio, TipoUnidad, Paramedicos, UnidadxServicio, ParamedicoxPaciente

def crear_servicio(request):
    servicio = None
    if request.method == 'POST':
        servicio_form = ServicioForm(request.POST)

        if servicio_form.is_valid():
            servicio = servicio_form.save()

            # Manejo de unidades asignadas
            unidades = json.loads(request.POST.get('unidades', '[]'))
            for u in unidades:
                if u.get('clave') and u.get('id_unidad'):
                    try:
                        unidad = TipoUnidad.objects.get(clave=u['clave'])
                        UnidadxServicio.objects.create(
                            servicio=servicio,
                            unidad=unidad,
                            numero_unidad=u['id_unidad'],
                            agente_nombre=u.get('agente', '')
                        )
                    except TipoUnidad.DoesNotExist:
                        print(f"Unidad con clave {u['clave']} no encontrada.")
            
            # Manejo de paramédicos asignados
            paramedicos = json.loads(request.POST.get('paramedicos', '[]'))
            for item in paramedicos:
                clave = item.get("clave")
                try:
                    paramedico = Paramedicos.objects.get(clave=clave)
                    ParamedicoxPaciente.objects.create(servicio=servicio, paramedico=paramedico)
                except Paramedicos.DoesNotExist:
                    print(f"Paramédico con clave {clave} no encontrado.")
            
            return redirect('carga_modifica', pk=servicio.pk)

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





def carga_modifica(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    form_servicio = ServicioForm(instance=servicio)

    paciente = PacientexServicio.objects.filter(servicio=servicio).first()
    if paciente:
        form_paciente = PacientesForm(instance=paciente)
    else:
        form_paciente = PacientesForm(initial={'clave': PacientexServicio.obtener_siguiente_numero()})

    context = {
        'form': form_servicio,
        'form_paciente': form_paciente,
        'editar': True,
        'servicio': servicio,
        'pacientes': PacientexServicio.objects.filter(servicio=servicio),

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

        return redirect('carga_modifica', pk)

    except Exception as e:
        print(f"Error general: {e}")
        return render(request, 'modificar_servicio.html', {
            'form_servicio': form_servicio,
            'pacientes_form': pacientes_form,
            'servicio': servicio,
            'editar': True
        })

def guardar_unidades(request, servicio):
    UnidadxServicio.objects.filter(servicio=servicio).delete()
    unidades = json.loads(request.POST.get('unidades', '[]'))
    print(unidades)
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
    print(paramedicos)
    for item in paramedicos:
        clave = item.get("clave")
        paramedico = Paramedicos.objects.get(clave=clave)
        ParamedicoxPaciente.objects.create(servicio=servicio, paramedico=paramedico)

def guardar_procedimientos(request, paciente):
        ProcedimientoxPaciente.objects.filter(paciente=paciente).delete()
        procedimientos = json.loads(request.POST.get('procedimientos', '[]'))
        print(procedimientos)
        for i in procedimientos:
            clave = i.get("clave")
            procedimiento = Procedimiento.objects.get(clave=clave)
            ProcedimientoxPaciente.objects.create(procedimiento=procedimiento, paciente=paciente)

def guardar_alergias(request, paciente):
    AlergiaxPaciente.objects.filter(paciente=paciente).delete()
    alergias = json.loads(request.POST.get('alergias', '[]'))
    print(alergias)
    for i in alergias:
        clave = i.get('clave')
        alergia = Alergia.objects.get(clave=clave)
        AlergiaxPaciente.objects.create(alergia=alergia, paciente=paciente)

def guardar_materiales(request, paciente):
    MaterialxPaciente.objects.filter(paciente=paciente).delete()
    materiales = json.loads(request.POST.get('materiales', '[]'))
    print(materiales)
    for i in materiales:
        clave = i.get('clave')
        cantidad = i.get('cantidad')
        material = Material.objects.get(clave=clave)
        MaterialxPaciente.objects.create(paciente=paciente, material=material, cantidad=cantidad, costo=0)

def guardar_ingeridos(request, paciente):
    MedIngeridoxPaciente.objects.filter(paciente=paciente).delete()
    ingeridos = json.loads(request.POST.get('ingeridos', '[]'))
    print(ingeridos)
    for i in ingeridos:
        clave = i.get('clave')
        cantidad = i.get('cantidad')
        ingerido = Medicamento.objects.get(clave=clave)
        MedIngeridoxPaciente.objects.create(paciente=paciente, medicamento=ingerido, cantidad=cantidad)

def guardar_administrados(request, paciente):
    MedAdministradoxPaciente.objects.filter(paciente=paciente).delete()
    administrados = json.loads(request.POST.get('administrado', '[]'))
    print(administrados)
    for i in administrados:
        clave = i.get('clave')
        cantidad = i.get('cantidad')
        administrado = Medicamento.objects.get(clave=clave)
        MedAdministradoxPaciente.objects.create(paciente=paciente, medicamento=administrado, cantidad=cantidad, costo=0)

def guardar_equipos(request, paciente):
    equipos_data = {}
    for clave in request.POST:
        if clave.startswith('equipos[') and '][cantidad]' in clave:
            clave_equipos = clave.split('[')[1].split(']')[0]
            cantidad = request.POST.get(clave)
            if cantidad is not None and cantidad.strip() != '':
                equipos_data[clave_equipos] = cantidad
    for clave_equipos, cantidad in equipos_data.items():
        try:
            equipo = Equipo.objects.get(clave=clave_equipos)
            EquipoxPaciente.objects.create(
                paciente=paciente, 
                equipo=equipo, 
                cantidad=cantidad
            )
        except Equipo.DoesNotExist:
            print(f"Error: Equipo con clave {clave_equipos} no encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al asignar el equipos: {str(e)}")

def guardar_lesiones(request, paciente):
    LesionxPaciente.objects.filter(paciente=paciente).delete()

    # Obtener el JSON de lesiones desde el POST
    lesiones_json = request.POST.get('lesiones', '[]')
    print("JSON recibido:", lesiones_json)  # Debug

    try:
        lesiones = json.loads(lesiones_json)
    except json.JSONDecodeError as e:
        print("Error al decodificar JSON:", e)
        lesiones = []

    if not isinstance(lesiones, list):
        print("El JSON no es una lista de objetos.")
        return
    
    # Guardar cada lesión
    for lesion_data in lesiones:
        if not isinstance(lesion_data, dict):
            print("Formato inválido para lesión:", lesion_data)
            continue

        descripcion = lesion_data.get('descripcion', '').strip()
        valor_raw = lesion_data.get('valor', 0)

        try:
            valor = float(valor_raw)
        except (TypeError, ValueError):
            print(f"Valor inválido para la lesión '{descripcion}':", valor_raw)
            valor = 0

        if descripcion:
            print(f"Guardando lesión: {descripcion} | Valor: {valor}")
            LesionxPaciente.objects.create(
                paciente=paciente,
                lesion=descripcion,
                valor=valor
            )
        else:
            print("Descripción vacía, no se guarda esta lesión.")

def guardar_impactos(request, paciente):
    ImpactoxVehiculo.objects.filter(paciente=paciente).delete()
    impacto_str = request.POST.get('impacto', '[]')
    impactos = json.loads(impacto_str)
    if isinstance(impactos, list):
        for impacto_data in impactos:
            if isinstance(impacto_data, dict):
                descripcion_impacto = impacto_data.get('descripcion', '').strip()
                if descripcion_impacto:
                    ImpactoxVehiculo.objects.create(
                        paciente=paciente,
                        impacto=descripcion_impacto
                    )

def reporte_servicio(request, clave):
    # Obtener datos principales
    servicio = get_object_or_404(Servicio, clave=clave)
    unidades = UnidadxServicio.objects.filter(servicio=clave).first()
    paramedico = ParamedicoxPaciente.objects.filter(servicio=clave).first()
    paciente = PacientexServicio.objects.filter(servicio=clave).first()
    
    # Obtener datos relacionados si existe paciente
    datos_relacionados = {}
    if paciente:
        datos_relacionados = {
            'procedimiento': ProcedimientoxPaciente.objects.filter(paciente=clave).first(),
            'alergia': AlergiaxPaciente.objects.filter(paciente=clave).first(),
            'material': MaterialxPaciente.objects.filter(paciente=clave).first(),
            'ingerido': MedIngeridoxPaciente.objects.filter(paciente=clave).first(),
            'administrado': MedAdministradoxPaciente.objects.filter(paciente=clave).first(),
            'equipo': EquipoxPaciente.objects.filter(paciente=clave).first(),
            'lesion': LesionxPaciente.objects.filter(paciente=clave).first(),
            'impacto': ImpactoxVehiculo.objects.filter(paciente=clave).first()
        }

    # Configurar respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="reporte_servicio_{clave}.pdf"'

    # Registrar fuentes
    try:
        pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
    except:
        pass  # Usar fuentes por defecto si falla el registro

    # Obtener estilos base y modificarlos
    styles = getSampleStyleSheet()
    
    # Modificar el estilo Title existente en lugar de crear uno nuevo
    styles['Title'].textColor = colors.HexColor('#003366')
    styles['Title'].fontSize = 18
    styles['Title'].leading = 22
    styles['Title'].spaceAfter = 20
    
    # Crear nuevos estilos solo si no existen
    if 'SectionHeader' not in styles:
        styles.add(ParagraphStyle(
            name='SectionHeader',
            fontSize=14,
            leading=18,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#990000')
        ))
    
    if 'Label' not in styles:
        styles.add(ParagraphStyle(
            name='Label',
            fontSize=10,
            leading=12,
            spaceAfter=5,
            textColor=colors.HexColor('#333333')
        ))
    
    if 'Value' not in styles:
        styles.add(ParagraphStyle(
            name='Value',
            fontSize=10,
            leading=12,
            spaceAfter=10,
            textColor=colors.black
        ))
    
    if 'Footer' not in styles:
        styles.add(ParagraphStyle(
            name='Footer',
            fontSize=8,
            leading=10,
            alignment=1,  # Centrado
            textColor=colors.grey
        ))

    # Crear documento
    doc = SimpleDocTemplate(response, pagesize=letter, 
                          rightMargin=inch/2, leftMargin=inch/2,
                          topMargin=inch/2, bottomMargin=inch/2)
    
    elements = []

    # Título del reporte
    elements.append(Paragraph(f"REPORTE DE SERVICIO #{servicio.clave}", styles['Title']))
    elements.append(Spacer(1, 0.2*inch))

    # Sección de información general del servicio
    elements.append(Paragraph("INFORMACIÓN GENERAL DEL SERVICIO", styles['SectionHeader']))
    
    general_data = [
        ["Nombre:", servicio.nombre_persona_reporta or "No especificado"],
        ["Fecha:", servicio.fecha.strftime('%d/%m/%Y')],
        ["Edad/Sexo:", f"{servicio.edad_persona_reporta or 'N/A'} / {servicio.sexo_persona_reporta or 'N/A'}"],
        ["Ubicación:", f"{servicio.direccion_emergencia.calle if servicio.direccion_emergencia else 'N/A'}, "
                              f"{servicio.colonia_emergencia.colonia if servicio.colonia_emergencia else 'N/A'}, "
                              f"Entre calle: {servicio.calle_entre or 'N/A'}"],
        ["Teléfono:", servicio.telefono_persona_reporta or "No especificado"],
        ["Estatus:", "En Proceso" if servicio.estatus == "P" else "Finalizado"],
        ["Tipo de Servicio Realizado:", servicio.tipo_servicio_realizado.descripcion if servicio.tipo_servicio_realizado else "Urgencia"],
        ["Tipo de Servicio Reportado:", servicio.tipo_servicio_reporta.descripcion if servicio.tipo_servicio_reporta else "Urgencia"],
        ["Paramedico:", paramedico.paramedico.nombre if paramedico and paramedico.paramedico else "No asignado"],
        ["Unidad:", unidades.unidad.descripcion if unidades and unidades.unidad else "No asignada"],
        ["ID Agente:", unidades.numero_unidad if unidades else "No asignado"],
        ["Agente Nombre:", unidades.agente_nombre if unidades else "No asignado"]
    ]
    
    general_table = Table(general_data, colWidths=[2*inch, 4*inch])
    general_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEADING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5)
    ]))
    
    elements.append(general_table)
    elements.append(Spacer(1, 0.2*inch))

    # Sección de información del paciente si existe
    if paciente:
        elements.append(PageBreak())
        elements.append(Paragraph("INFORMACIÓN DETALLADA DEL PACIENTE", styles['SectionHeader']))
        
        # Datos básicos del paciente
        patient_basic_data = [
            ["Nombre:", f"{paciente.nombre or ''} {paciente.apellido_paterno or ''} {paciente.apellido_materno or ''}"],
            ["Edad:", f"{paciente.edad or 'N/A'} ({paciente.edad_tipo or 'N/A'})"],
            ["Sexo:", paciente.sexo or "No especificado"],
            ["Estado Civil:", paciente.estado_civil or "No especificado"],
            ["Teléfono:", paciente.telefono or "No especificado"],
            ["Domicilio:", f"{paciente.domicilio or 'N/A'} {paciente.domicilio_numero or ''}, {paciente.colonia or 'N/A'}"],
            ["Estatura/Complexión/Tez:", f"{paciente.estatura or 'N/A'} / {paciente.complexion or 'N/A'} / {paciente.tez or 'N/A'}"],
            ["Pelo/Ropa:", f"{paciente.pelo or 'N/A'} / {paciente.ropa or 'N/A'}"],
            ["Vehículo:", f"{paciente.marca_vehiculo or 'N/A'} {paciente.color_vehiculo or ''} {paciente.placa_vehiculo or ''}"],
            ["Última comida:", paciente.fecha_ultima_comida.strftime('%d/%m/%Y %H:%M') if paciente.fecha_ultima_comida else "No especificado"],
            ["Falleció:", "Sí" if paciente.fallecio else "No"],
            ["Hospital:", paciente.hospital or "No especificado"],
            ["Ambulancia:", paciente.ambulancia or "No especificado"],
            ["Base:", paciente.base or "No especificado"]
        ]
        
        patient_table = Table(patient_basic_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('LEADING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0'))
        ]))
        
        elements.append(patient_table)
        elements.append(Spacer(1, 0.2*inch))

        # Sección de acompañante si aplica
        if paciente.tiene_acompanante:
            elements.append(Paragraph("INFORMACIÓN DEL ACOMPAÑANTE", styles['SectionHeader']))
            
            acompanante_data = [
                ["Nombre:", paciente.nombre_acompanante or "No especificado"],
                ["Edad:", paciente.edad_acompanante or "No especificado"],
                ["Sexo:", paciente.sexo_acompanante or "No especificado"],
                ["Domicilio:", paciente.domicilio_acompanante or "No especificado"],
                ["Parentesco:", paciente.parentesco_acompanante or "No especificado"]
            ]
            
            acompanante_table = Table(acompanante_data, colWidths=[2*inch, 4*inch])
            acompanante_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (0,0), (0,-1), 'LEFT'),
                ('ALIGN', (1,0), (1,-1), 'LEFT'),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('LEADING', (0,0), (-1,-1), 12),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5)
            ]))
            
            elements.append(acompanante_table)
            elements.append(Spacer(1, 0.2*inch))

        # Sección de diagnóstico y signos vitales
        elements.append(Paragraph("DIAGNÓSTICO Y SIGNOS VITALES", styles['SectionHeader']))
        
        diagnostico_data = [
            ["Nivel de Conciencia:", paciente.nivel_concienciaa or "No especificado"],
            ["Piel:", paciente.piel or "No especificado"],
            ["Antecedente:", paciente.antecedente or "No especificado"],
            ["Síntoma:", paciente.sintoma or "No especificado"],
            ["Pulso Diagnóstico:", paciente.pulso_diagnostico or "No especificado"],
            ["Respiración Diagnóstico:", paciente.respiracion_diagnostico or "No especificado"],
            ["Pupilas:", paciente.pupilas or "No especificado"],
            ["Hemorragia:", paciente.hemorragia or "No especificado"],
            ["Dolor:", paciente.dolor or "No especificado"],
            ["Pulso:", paciente.pulso or "No especificado"],
            ["Respiración:", paciente.respiracion or "No especificado"],
            ["Presión Inicial/Posterior:", f"{paciente.presion_inicial or 'N/A'} / {paciente.presion_posterior or 'N/A'}"],
            ["Destroxtix:", paciente.destroxtix or "No especificado"],
            ["Escala Glasgow:", f"Ojos: {paciente.apertura_ojos_glasgow or 'N/A'}, "
                                     f"Verbal: {paciente.respuesta_verbal_glasgow or 'N/A'}, "
                                     f"Motora: {paciente.respuesta_motora_glasgow or 'N/A'}"],
            ["Oximetría:", paciente.oximetria or "No especificado"],
            ["Temperatura:", paciente.temperatura or "No especificado"]
        ]
        
        diagnostico_table = Table(diagnostico_data, colWidths=[2*inch, 4*inch])
        diagnostico_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('LEADING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0'))
        ]))
        
        elements.append(diagnostico_table)
        elements.append(Spacer(1, 0.2*inch))

        # Sección de procedimientos y tratamientos
        elements.append(Paragraph("PROCEDIMIENTOS Y TRATAMIENTOS", styles['SectionHeader']))
        
        tratamientos_data = []
        
        if datos_relacionados['procedimiento']:
            tratamientos_data.append(["Procedimiento:", datos_relacionados['procedimiento'].procedimiento.descripcion])
        
        if datos_relacionados['alergia']:
            tratamientos_data.append(["Alergias:", datos_relacionados['alergia'].alergia.descripcion])
        
        if datos_relacionados['material']:
            tratamientos_data.append(["Materiales usados:", 
                                   f"{datos_relacionados['material'].material.descripcion} - "
                                   f"{datos_relacionados['material'].cantidad} {datos_relacionados['material'].material.unidad}"])
        
        if datos_relacionados['ingerido']:
            tratamientos_data.append(["Medicamento ingerido:", 
                                   f"{datos_relacionados['ingerido'].medicamento.descripcion} - "
                                   f"{datos_relacionados['ingerido'].cantidad} {datos_relacionados['ingerido'].medicamento.unidad}"])
        
        if datos_relacionados['administrado']:
            tratamientos_data.append(["Medicamento administrado:", 
                                   f"{datos_relacionados['administrado'].medicamento.descripcion} - "
                                   f"{datos_relacionados['administrado'].cantidad} {datos_relacionados['administrado'].medicamento.unidad}"])
        
        if datos_relacionados['equipo']:
            tratamientos_data.append(["Equipo utilizado:", datos_relacionados['equipo'].equipo.descripcion])
        
        if datos_relacionados['lesion']:
            tratamientos_data.append(["Lesiones:", datos_relacionados['lesion'].lesion])
        
        if datos_relacionados['impacto']:
            tratamientos_data.append(["Impacto vehicular:", datos_relacionados['impacto'].impacto])
        
        if not tratamientos_data:
            tratamientos_data.append(["No se registraron", "procedimientos o tratamientos"])
        
        tratamientos_table = Table(tratamientos_data, colWidths=[2*inch, 4*inch])
        tratamientos_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('LEADING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5)
        ]))
        
        elements.append(tratamientos_table)
        elements.append(Spacer(1, 0.2*inch))

        # Sección de responsabilidades
        elements.append(Paragraph("RESPONSABILIDADES Y DOCUMENTACIÓN", styles['SectionHeader']))
        
        responsabilidades_data = [
            ["Entrega de pertenencias:", "Sí" if paciente.entregan_pertenencias else "No"],
            ["Descripción pertenencias:", paciente.descripcion_pertenencias or "No especificado"],
            ["Liberación de responsabilidad:", "Sí" if paciente.libera_responsabilidad else "No"],
            ["Fecha liberación:", paciente.fecha_liberacion_respon.strftime('%d/%m/%Y %H:%M') if paciente.fecha_liberacion_respon else "No aplica"],
            ["Firmó liberación:", "Sí" if paciente.firmo_liberacion else "No"],
            ["Niega firmar:", "Sí" if paciente.niega_firmar else "No"],
            ["Responsable en hospital:", paciente.nombre_respon_hospital or "No especificado"],
            ["Agente:", f"{paciente.nombre_agente or 'N/A'} ({paciente.numero_agente or 'N/A'})"]
        ]
        
        responsabilidades_table = Table(responsabilidades_data, colWidths=[2*inch, 4*inch])
        responsabilidades_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('LEADING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5)
        ]))
        
        elements.append(responsabilidades_table)

    # Pie de página
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Este reporte fue generado automáticamente por el sistema de gestión de servicios.", styles['Footer']))
    elements.append(Paragraph(f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Footer']))

    # Construir el PDF
    doc.build(elements)
    
    return response