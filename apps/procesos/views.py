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
def crear_servicio(request):
    servicio = None
    if request.method == 'POST':
        servicio_form = ServicioForm(request.POST)

        if servicio_form.is_valid():
            print("El formulario de servicio es válido")
            servicio = servicio_form.save()

            # Manejo de unidades asignadas
            unidades_asignadas = []
            for clave, valor in request.POST.items():
                if clave.startswith('unidades['):
                    print(f"Clave: {clave}, Valor: {valor}")
                    clave_unidad = clave.split('[')[1].split(']')[0]
                    campo = clave.split('[')[2].split(']')[0]
                    unidad = next((u for u in unidades_asignadas if u.get('clave') == clave_unidad), None)
                    if unidad is None:
                        unidad = {'clave': clave_unidad}
                        unidades_asignadas.append(unidad)
                    unidad[campo] = valor

            # Guardar las unidades asignadas
            for unidad in unidades_asignadas:
                try:
                    tipo_unidad = TipoUnidad.objects.get(clave=unidad.get('clave'))
                    unidad_asignado = UnidadxServicio(
                        servicio=servicio,
                        unidad=tipo_unidad,
                        numero_unidad=unidad.get('id_unidad'),
                        agente_nombre=unidad.get('agente')
                    )
                    unidad_asignado.save()
                    print("Unidad asignada guardada correctamente")
                except Exception as e:
                    print(f"Error al guardar unidad asignada: {e}")

            # Manejo de paramédicos asignados
            paramedicos_asignados = []
            for clave, valor in request.POST.items():
                if clave.startswith('paramedicos['):
                    print(f"Clave: {clave}, Valor: {valor}")
                    clave_paramedico = clave.split('[')[1].split(']')[0]
                    paramedico = next((p for p in paramedicos_asignados if p.get('clave') == clave_paramedico), None)
                    if paramedico is None:
                        paramedico = {'clave': clave_paramedico}
                        paramedicos_asignados.append(paramedico)
                    paramedico['valor'] = valor  # Guardar el valor como 'valor' o el campo adecuado

            # Guardar los paramédicos asignados
            for paramedico in paramedicos_asignados:
                try:
                    paramedico_obj = Paramedicos.objects.get(clave=paramedico['clave'])
                    paramedico_asignado = ParamedicoxPaciente(
                        servicio=servicio,
                        paramedico=paramedico_obj
                    )
                    paramedico_asignado.save()
                    print("Paramédico asignado guardado correctamente")
                except Exception as e:
                    print(f"Error al guardar paramédico asignado: {e}")

            if servicio:
                return redirect('carga_modifica', pk=servicio.clave)
            else:
                return redirect('pagina_error')  # O cualquier otra página de error que tengas definida

        else:
            print("Errores en el formulario de servicio:", servicio_form.errors)
    else:
        servicio_form = ServicioForm()

    return render(request, 'modificar_servicio.html', {
        'servicio_form': servicio_form,
        'unidades': TipoUnidad.objects.all(),
        'paramedicos': Paramedicos.objects.all(),
        'pk': servicio.clave if servicio else None
    })




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

        guardar_paramedicos(request, servicio)
        guardar_unidades(request, servicio)
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

def guardar_paramedicos(request, servicio):
    ParamedicoxPaciente.objects.filter(servicio=servicio).delete()
    paramedicos_claves = [valor for clave, valor in request.POST.items() if clave.startswith('paramedicos[')]
    for clave in paramedicos_claves:
        paramedico = Paramedicos.objects.get(clave=clave)
        ParamedicoxPaciente.objects.create(servicio=servicio, paramedico=paramedico)

def guardar_unidades(request, servicio):
    UnidadxServicio.objects.filter(servicio=servicio).delete()
    unidades_data = {clave.split('[')[1].split(']')[0]: valor for clave, valor in request.POST.items() if clave.startswith('unidades[') and 'id_unidad' in clave}
    for clave_unidad, numero_unidad in unidades_data.items():
        unidad = TipoUnidad.objects.get(clave=clave_unidad)
        agente = request.POST.get(f'unidades[{clave_unidad}][agente]', '')
        UnidadxServicio.objects.create(
            servicio=servicio,
            unidad=unidad,
            numero_unidad=numero_unidad,
            agente_nombre=agente
        )

def guardar_procedimientos(request, paciente):
    procedimientos_claves = [clave.split('[')[1].split(']')[0] for clave, valor in request.POST.items() if clave.startswith('procedimientos[') and 'clave' in clave]
    for clave_procedimiento in procedimientos_claves:
        procedimiento = Procedimiento.objects.get(clave=clave_procedimiento)
        ProcedimientoxPaciente.objects.create(procedimiento=procedimiento, paciente=paciente)

def guardar_alergias(request, paciente):
    AlergiaxPaciente.objects.filter(paciente=paciente).delete()
    alergias_claves = [clave.split('[')[1].split(']')[0] for clave in request.POST if clave.startswith('alergias[') and 'clave' in clave]
    for clave_alergia in alergias_claves:
        try:
            alergia = Alergia.objects.get(clave=clave_alergia)
            AlergiaxPaciente.objects.create(alergia=alergia, paciente=paciente)
        except Alergia.DoesNotExist:
            print(f"Alergia con clave {clave_alergia} no encontrada.")

def guardar_materiales(request, paciente):
    materiales_data = {}
    for clave in request.POST:
        if clave.startswith('materiales[') and '][cantidad]' in clave:
            clave_material = clave.split('[')[1].split(']')[0]
            cantidad = request.POST.get(clave)
            if cantidad is not None and cantidad.strip() != '':
                materiales_data[clave_material] = cantidad
    
    for clave_material, cantidad in materiales_data.items():
        try:
            material = Material.objects.get(clave=clave_material)
            MaterialxPaciente.objects.create(
                paciente=paciente, 
                material=material, 
                cantidad=cantidad, 
                costo=0
            )
        except Material.DoesNotExist:
            print(f"Material con clave {clave_material} no encontrado.")
        except Exception as e:
            print(f"Ocurrió un error con material {clave_material}: {e}")

def guardar_ingeridos(request, paciente):
    ingeridos_data = {}
    for clave in request.POST:
        if clave.startswith('ingeridos[') and '][cantidad]' in clave:
            clave_ingerido = clave.split('[')[1].split(']')[0]
            cantidad = request.POST.get(clave)
            if cantidad is not None and cantidad.strip() != '':
                ingeridos_data[clave_ingerido] = cantidad
    
    for clave_ingerido, cantidad in ingeridos_data.items():
        try:
            medicamento = Medicamento.objects.get(clave=clave_ingerido)
            MedIngeridoxPaciente.objects.create(
                paciente=paciente, 
                medicamento=medicamento, 
                cantidad=cantidad
            )
        except Medicamento.DoesNotExist:
            print(f"Error: Medicamento con clave {clave_ingerido} no encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al asignar el ingerido: {str(e)}")

def guardar_administrados(request, paciente):
    administrados_data = {}
    for clave in request.POST:
        if clave.startswith('administrados[') and '][cantidad]' in clave:
            clave_administrados = clave.split('[')[1].split(']')[0]
            cantidad = request.POST.get(clave)
            if cantidad is not None and cantidad.strip() != '':
                administrados_data[clave_administrados] = cantidad
    for clave_administrados, cantidad in administrados_data.items():
        try:
            medicamento = Medicamento.objects.get(clave=clave_administrados)
            MedAdministradoxPaciente.objects.create(
                paciente=paciente, 
                medicamento=medicamento, 
                cantidad=cantidad
            )
        except Medicamento.DoesNotExist:
            print(f"Error: Medicamento con clave {clave_administrados} no encontrado.")
        except Exception as e:
            print(f"Ocurrió un error al asignar el administrado: {str(e)}")

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