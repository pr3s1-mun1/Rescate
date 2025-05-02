from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from apps.catalogos.forms import *
from .forms import ParamedicosForm, ServicioForm, PacientesForm, UnidadAsignadoForm, ParamedicoAsignadoForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def formulario_servicio(request):
    form_servicio = ServicioForm(initial={'clave': Servicio.obtener_siguiente_numero()})
    
    context = {
        'form': form_servicio,
        'form_paciente': PacientesForm(),
        'paramedicos': Paramedicos.objects.all(),
        'unidades': TipoUnidad.objects.all(),
        'alergias': Alergia.objects.all(),
        'materiales': Material.objects.all(),
        'medicamentos': Medicamento.objects.all(),
        'equipos': Equipo.objects.all(),
        'procedimientos': Procedimiento.objects.all(),
        'pacientes': PacientexServicio.objects.all(),
        
        'editar': False
    }
    
    return render(request, 'create.html', context)

def formulario_buscar(request):
    servicios_filtrados = Servicio.objects.all()

    if request.method == 'POST':
        clave = request.POST.get('clave', '').strip()
        if clave:
            servicios_filtrados = Servicio.objects.filter(clave__icontains=clave)

    return render(request, 'buscador_servicios.html', {
        'servicios': servicios_filtrados
    })

def vista_main(request):
    total_servicios = 5
    servicios_activos = 1
    hojas_hoy = 9
    pendientes = 3
    return render(request, 'serv_principal.html', {
        'total_servicios' : total_servicios,
        'servicios_activos' : servicios_activos,
        'hojas_hoy' : hojas_hoy,
        'pendientes' : pendientes,
    })


def crear_servicio(request):
    if request.method == 'POST':
        print("Recibiendo solicitud POST")
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

            return redirect('modificar_servicio', pk=servicio.id if servicio else None)
        else:
            print("Errores en el formulario de servicio:", servicio_form.errors)
    else:
        servicio_form = ServicioForm()

    return render(request, 'modificar_servicio.html', {
        'servicio_form': servicio_form,
        'unidades': TipoUnidad.objects.all(),
        'paramedicos': Paramedicos.objects.all()
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
    servicio = get_object_or_404(Servicio, clave=clave)
    paciente = PacientexServicio.objects.filter(servicio=clave).first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="servicio_{clave}.pdf"'

    # Crear PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Registrar fuente si se desea
    try:
        pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold.ttf'))
    except:
        pass

    # Encabezado
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.darkblue)
    p.drawCentredString(width / 2, height - 50, f"Reporte del Servicio #{servicio.clave}")

    p.setStrokeColor(colors.grey)
    p.line(40, height - 60, width - 40, height - 60)

    # Datos generales
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.black)
    y = height - 100

    def draw_label_value(label, value):
        nonlocal y
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"{label}:")
        p.setFont("Helvetica", 12)
        p.drawString(180, y, str(value))
        y -= 25

    draw_label_value("Nombre", servicio.nombre_persona_reporta)
    draw_label_value("Fecha", servicio.fecha.strftime('%d/%m/%Y'))
    draw_label_value("Edad/Sexo", f"{servicio.edad_persona_reporta} / {servicio.sexo_persona_reporta}")
    draw_label_value("Ubicación", servicio.direccion_emergencia.calle + ", " + servicio.colonia_emergencia.colonia + " Entre calle " + servicio.calle_entre)
    draw_label_value("Telefono Persona Reporta", servicio.telefono_persona_reporta)
    draw_label_value("Estatus", "En Proceso" if servicio.estatus == "P" else "Finalizado")

    draw_label_value("Tipo de Servicio Realizado", servicio.tipo_servicio_realizado.descripcion if servicio.tipo_servicio_realizado else "Urgencia")
    draw_label_value("Tipo de Servicio Reportado", servicio.tipo_servicio_reporta.descripcion if servicio.tipo_servicio_reporta else "Urgencia")

    if paciente:
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.darkred)
        p.drawString(50, y, "Información del Paciente")
        y -= 30

        p.setFillColor(colors.black)
        draw_label_value("Nombre del Paciente", paciente.nombre)
        draw_label_value("Edad", paciente.edad)
        draw_label_value("Sexo", paciente.sexo)
        draw_label_value("Teléfono", paciente.telefono)

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(colors.grey)
    p.drawString(50, 50, "Este reporte fue generado automáticamente por el sistema.")

    p.showPage()
    p.save()

    return response
