from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from apps.catalogos.forms import *
from .forms import ParamedicosForm, ServicioForm, PacientesForm, UnidadAsignadoForm, ParamedicoAsignadoForm

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

            paramedicos_asignados = []
            for clave, valor in request.POST.items():
                if clave.startswith('paramedicos['):
                    print(f"Clave: {clave}, Valor: {valor}")
                    clave_paramedico = clave.split('[')[1].split(']')[0]
                    paramedico = next((p for p in paramedicos_asignados if p.get('clave') == clave_paramedico), None)
                    if paramedico is None:
                        paramedico = {'clave': clave_paramedico}
                        paramedicos_asignados.append(paramedico)
                    paramedico['clave'] = valor

            for paramedico in paramedicos_asignados:
                try:
                    paramedico_obj = Paramedicos.objects.get(clave=paramedico['clave'])
                    paramedico_asignado = ParamedicoxPaciente(
                        servicio=servicio,
                        paramedico=paramedico_obj
                    )
                    paramedico_asignado.save()
                except Exception as e:
                    print(f"Error al guardar paramédico asignado: {e}")


                return redirect('modificar_servicio', pk=servicio.id if servicio else None)
        else:
            print(servicio_form.errors)
    else:
        servicio_form = ServicioForm()

    return render(request, 'crear_servicio.html', {
        'servicio_form': servicio_form,
        'unidades': TipoUnidad.objects.all(),
        'paramedicos': Paramedicos.objects.all()
    })

def carga_modifica(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    form_servicio = ServicioForm(instance=servicio)  
    
    try:
        paciente = PacientexServicio.objects.get(servicio=servicio)
        form_paciente = PacientesForm(instance=paciente)  # Cargar datos existentes
    except PacientexServicio.DoesNotExist:
        form_paciente = PacientesForm(initial={'clave': PacientexServicio.obtener_siguiente_numero()})

    pacientes = PacientexServicio.objects.filter(servicio=servicio)
    paramedicos_asignados = ParamedicoxPaciente.objects.filter(servicio=servicio)
    unidades_asignadas = UnidadxServicio.objects.filter(servicio=servicio)
    
    context = {
        'form': form_servicio,
        'form_paciente': form_paciente,
        
        'paramedicos': Paramedicos.objects.all(),
        'unidades': TipoUnidad.objects.all(),
        'alergias': Alergia.objects.all(),
        'materiales': Material.objects.all(),
        'medicamentos': Medicamento.objects.all(),
        'equipos': Equipo.objects.all(),
        'procedimientos': Procedimiento.objects.all(),

        'paramedicos_asignados': paramedicos_asignados,
        'unidades_asignadas': unidades_asignadas,
        
        'editar': True,
        'pacientes': pacientes,
        'servicio': servicio  
    }
    
    return render(request, 'modificar_servicio.html', context)

def guardar_todo(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    
    if request.method == 'POST':   
        form_servicio = ServicioForm(request.POST, instance=servicio)
        pacientes_form = PacientesForm(request.POST)
        
        if form_servicio.is_valid():
            servicio = form_servicio.save()
        else:
            print("Errores en formulario de servicio:", form_servicio.errors)
        
        if pacientes_form.is_valid():
            try:
                paciente = pacientes_form.save(commit=False)
                paciente.servicio = servicio
                paciente.save()  
            except Exception as e:
                print(f"Error al guardar paciente: {e}")
                messages.error(request, f"Error al guardar paciente: {e}")
        else:
            print("\nErrores en formulario de paciente:")
            for campo, errores in pacientes_form.errors.items():
                print(f"- {campo}: {', '.join(errores)}")
        
        try:
            ParamedicoxPaciente.objects.filter(servicio=servicio).delete()
            for clave, valor in request.POST.items():
                if clave.startswith('paramedicos['):
                    paramedico_id = clave.split('[')[1].split(']')[0]
                    paramedico = Paramedicos.objects.get(clave=valor)
                    ParamedicoxPaciente.objects.create(
                        servicio=servicio,
                        paramedico=paramedico
                    )
        except Exception as e:
            print(f"Error al procesar paramédicos: {e}")
        
        try:
            UnidadxServicio.objects.filter(servicio=servicio).delete()
            for clave, valor in request.POST.items():
                if clave.startswith('unidades['):
                    clave_unidad = clave.split('[')[1].split(']')[0]
                    campo = clave.split('[')[2].split(']')[0]
                    if campo == 'id_unidad':
                        unidad = TipoUnidad.objects.get(clave=clave_unidad)
                        UnidadxServicio.objects.create(
                            servicio=servicio,
                            unidad=unidad,
                            numero_unidad=valor
                        )
        except Exception as e:
            print(f"Error al procesar unidades: {e}")
        
        return redirect('vista_main')
    
    form_servicio = ServicioForm(instance=servicio)
    pacientes_form = PacientesForm()
    
    return render(request, 'buscador_servicios.html', {
        'form_servicio': form_servicio,
        'pacientes_form': pacientes_form,
        'servicio': servicio,
        'editar': True 
    })
