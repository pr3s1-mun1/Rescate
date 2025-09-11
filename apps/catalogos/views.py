from django.shortcuts import render, get_object_or_404, redirect

from functools import wraps
from django.contrib import messages
from django.db.models import Max, IntegerField
from django.db.models.functions import Cast
from django.contrib.auth.hashers import make_password
from .models import *
from .forms import *


CATALOGOS = {
    'alergias': {
        'model': Alergia,
        'form': AlergiaForm,
        'template': 'alergias.html',
        'update_template': 'updt/update_alergias.html',
        'nombre': 'Alergia'
    },
    'bases': {
        'model': Bases,
        'form': BaseForm,
        'template': 'bases.html',
        'update_template': 'updt/update_base.html',
        'nombre': 'Base'
    },
    'ambulancias': {
        'model': Ambulancias,
        'form': AmbulanciaForm,
        'template': 'ambulancias.html',
        'update_template': 'updt/update_ambulancias.html',
        'nombre': 'Ambulancia'
    },
    'paramedicos': {
        'model': Paramedicos,
        'form': ParamedicoForm,
        'template': 'paramedicos.html',
        'update_template': 'updt/update_paramedicos.html',
        'nombre': 'Paramédico'
    },
    'hospitales': {
        'model': Hospitales,
        'form': HospitalesForm,
        'template': 'hospitales.html',
        'update_template': 'updt/update_hospitales.html',
        'nombre': 'Hospital'
    },
    'tipos_servicio': {
        'model': TiposServicio,
        'form': TiposServicioForm,
        'template': 'tipos_servicio.html',
        'update_template': 'updt/update_tipos_servicio.html',
        'nombre': 'Tipo de Servicio'
    },
    'grupos_servicio': {
        'model': GrupoServicio,
        'form': GruposServicioForm,
        'template': 'grupos_servicio.html',
        'update_template': 'updt/update_grupos_servicio.html',
        'nombre': 'Grupo de Servicio'
    },
    'procedimientos': {
        'model': Procedimiento,
        'form': ProcedimientoForm,
        'template': 'procedimientos.html',
        'update_template': 'updt/update_procedimientos.html',
        'nombre': 'Procedimiento'
    },
    'tipos_unidades': {
        'model': TipoUnidad,
        'form': TiposUnidadesForm,
        'template': 'tipos_unidades.html',
        'update_template': 'updt/update_tipos_unidades.html',
        'nombre': 'Tipo de Unidad'
    },
    'enfermedades': {
        'model': Enfermedad,
        'form': EnfermedadesForm,
        'template': 'enfermedades.html',
        'update_template': 'updt/update_enfermedades.html',
        'nombre': 'Enfermedad'
    },
    'grupos_enfermedades': {
        'model': GrupoEnfermedad,
        'form': GruposEnfermedadesForm,
        'template': 'grupos_enfermedades.html',
        'update_template': 'updt/update_grupos_enfermedades.html',
        'nombre': 'Grupo de Enfermedad'
    },
    'medicamentos': {
        'model': Medicamento,
        'form': MedicamentosForm,
        'template': 'medicamentos.html',
        'update_template': 'updt/update_medicamentos.html',
        'nombre': 'Medicamento'
    },
    'materiales': {
        'model': Material,
        'form': MaterialesForm,
        'template': 'materiales.html',
        'update_template': 'updt/update_materiales.html',
        'nombre': 'Material'
    },
    'equipos': {
        'model': Equipo,
        'form': EquiposForm,
        'template': 'equipos.html',
        'update_template': 'updt/update_equipos.html',
        'nombre': 'Equipo'
    },
    'marcas_vehiculos': {
        'model': MarcaVehiculo,
        'form': MarcasVehiculosForm,
        'template': 'marcas_vehiculos.html',
        'update_template': 'updt/update_marcas_vehiculos.html',
        'nombre': 'Marca de Vehículo'
    },
    'calles': {
        'model': Calle,
        'form': CallesForm,
        'template': 'calles.html',
        'update_template': 'updt/update_calles.html',
        'nombre': 'Calle'
    },
    'colonias': {
        'model': Colonia,
        'form': ColoniasForm,
        'template': 'colonias.html',
        'update_template': 'updt/update_colonias.html',
        'nombre': 'Colonia'
    },
    'callexcolonias': {
        'model': Calle_Colonia,
        'form': CalleColoniaForm,
        'template': 'calle_colonia.html',
        'update_template': 'updt/calle_colonia.html',
        'nombre': 'Calle por Colonia'
    },
}



def requiere_tipo_paramedico(*niveles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            permisos = request.session.get("permisos")
            if permisos not in niveles_permitidos:
                return render(request, "bloqueo.html")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Permiso = 1: Paramédico       Solo puede crear hojas de servicio
# Permiso = 2: Supervisor       Puede crear hojas de servicio y gestionarlas
# Permiso = 3: Jefe de Área     Puede gestionar hojas de servicios, reportes, reloj checador y gasolinas
# Permiso = 4: Administrador    Tiene todos los permisos completos

# Permiso = 5: Root             Tiene todos los permisos completos y acceso a la configuración del sistema

def requiere_sesion(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get("clave"):
            messages.warning(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect("login")  # nombre de tu URL de login
        return view_func(request, *args, **kwargs)
    return _wrapped_view

#Envío de listas de catalogos a HTML
@requiere_sesion
@requiere_tipo_paramedico(4, 5)
def catalogo_general(request, tipo):
    if tipo not in CATALOGOS:
        return render(request, '404.html', {'error': 'Catálogo no encontrado'})

    query = request.GET.get('q', '')
    catalogo = CATALOGOS[tipo]
    modelo = catalogo['model']
    template = catalogo['template']

    campos = [field.name for field in modelo._meta.get_fields()]
    tiene_descripcion = 'nombre' in campos

    if tiene_descripcion:
        objetos = modelo.objects.filter(descripcion__icontains=query) if query else modelo.objects.all().order_by('nombre')
    else:
        objetos = modelo.objects.all()

    # Excluir clave=1 solo si es el catálogo de paramédicos
    if tipo == 'paramedicos':
        objetos = objetos.exclude(clave=16)

    return render(request, template, {tipo: objetos, 'query': query})


#Actualización de rows de las bases de datos
@requiere_sesion
@requiere_tipo_paramedico(4, 5)
def update_catalogo(request, tipo, clave):
    if tipo not in CATALOGOS or 'form' not in CATALOGOS[tipo] or not CATALOGOS[tipo]['form']:
        return redirect('error')

    catalogo = CATALOGOS[tipo]
    modelo = catalogo['model']
    form_class = catalogo['form']

    objeto = get_object_or_404(modelo, clave=clave)

    if request.method == "POST":
        form = form_class(request.POST, instance=objeto)
        if form.is_valid():
            form.save()

            #Registro de log
            Logs_Sistema.objects.create(
                usuario=request.session.get("user", "Desconocido"),
                accion=f"Actualizó {tipo} con clave {clave}"
            )
            return redirect('catalogo_general', tipo=tipo)
        print("test")
    else:
        form = form_class(instance=objeto)

    return render(request, "updt/update.html", {
        'form': form,
        'tipo': tipo,
        'titulo': catalogo.get('nombre', tipo)
    })


#Eliminar rows de la base de datos
@requiere_sesion
@requiere_tipo_paramedico(4, 5)
def delete_catalogo(request, tipo, clave):
    if tipo not in CATALOGOS:
        return redirect('error')

    catalogo = CATALOGOS[tipo]
    modelo = catalogo['model']
    objeto = get_object_or_404(modelo, clave=clave)

    if request.method == "POST":
        objeto.delete()
        Logs_Sistema.objects.create(
            usuario=request.session.get("user", "Desconocido"),
            accion=f"Eliminó {tipo} con clave {clave}"
        )
        return redirect('catalogo_general', tipo=tipo)

    return render(request, 'confirm_delete.html', {'objeto': objeto, 'tipo': tipo})

@requiere_sesion
@requiere_tipo_paramedico(4, 5)
def add_catalogo(request, tipo):
    if tipo not in CATALOGOS or 'form' not in CATALOGOS[tipo] or not CATALOGOS[tipo]['form']:
        return redirect('error')

    catalogo = CATALOGOS[tipo]
    modelo = catalogo['model']
    form_class = catalogo['form']

    CLAVE_MANUAL_MODELOS = ['Bases', 'Ambulancias']
    clave_manual = modelo.__name__ in CLAVE_MANUAL_MODELOS

    nueva_clave = ""
    if not clave_manual:
        clave_field = modelo._meta.get_field('clave')

        if isinstance(clave_field, models.IntegerField):
            max_clave = modelo.objects.aggregate(Max('clave'))['clave__max']
            nueva_clave = max_clave + 1 if max_clave is not None else 1

        elif isinstance(clave_field, models.CharField):
            try:
                max_clave = modelo.objects.annotate(
                    clave_int=Cast('clave', IntegerField())
                ).aggregate(Max('clave_int'))['clave_int__max']
                nueva_clave = str(max_clave + 1) if max_clave is not None else "1"
            except Exception:
                nueva_clave = ""

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            nuevo_registro = form.save(commit=False)
            if not clave_manual and nueva_clave != "":
                nuevo_registro.clave = nueva_clave

            # Si el modelo es Paramedicos, hashear la contraseña
            if tipo == 'Paramedicos' and hasattr(nuevo_registro, 'contrasena'):
                nuevo_registro.password = make_password(nuevo_registro.password)
            
            nuevo_registro.save()

            # Registro de log
            Logs_Sistema.objects.create(
                usuario=request.session.get("user", "Desconocido"),
                accion=f"Agregó {tipo} con clave {nuevo_registro.clave}"
            )

            return redirect('catalogo_general', tipo=tipo)
    else:
        initial_data = {}
        if not clave_manual and nueva_clave != "":
            initial_data['clave'] = nueva_clave
        form = form_class(initial=initial_data)

    return render(request, 'add/add.html', {
        'form': form,
        'tipo': tipo,
        'titulo': catalogo.get('nombre', tipo),
        'nueva_clave': nueva_clave,
    })

@requiere_sesion
@requiere_tipo_paramedico(4, 5)
def relacionar_calle_colonia(request):
    colonias = Colonia.objects.all().order_by('colonia')
    calles = Calle.objects.all().order_by('calle')

    colonia_id = request.GET.get('colonia_id')
    colonia_seleccionada = None
    calles_relacionadas = []
    calles_no_relacionadas = []

    if colonia_id:
        colonia_seleccionada = get_object_or_404(Colonia, pk=colonia_id)
        calles_relacionadas = Calle_Colonia.objects.filter(colonia=colonia_seleccionada).order_by('calle__calle')
        relacionadas_ids = calles_relacionadas.values_list('calle__clave', flat=True)
        calles_no_relacionadas = Calle.objects.exclude(clave__in=relacionadas_ids).order_by('calle')
    else:
        calles_no_relacionadas = calles  # si no hay colonia seleccionada, mostrar todas las calles disponibles para asignar

    if request.method == 'POST':
        action = request.POST.get('action')
        calle_id = request.POST.get('calle_id')
        colonia_id_post = request.POST.get('colonia_id')

        if calle_id and colonia_id_post:
            colonia = get_object_or_404(Colonia, pk=colonia_id_post)
            calle = get_object_or_404(Calle, pk=calle_id)

            if action == 'add':
                obj, created = Calle_Colonia.objects.get_or_create(colonia=colonia, calle=calle)
            elif action == 'remove':
                Calle_Colonia.objects.filter(colonia=colonia, calle=calle).delete()

        return redirect(f'{request.path}?colonia_id={colonia_id_post}')

    return render(request, 'calle_colonia.html', {
        'colonias': colonias,
        'calles_relacionadas': calles_relacionadas,
        'calles_no_relacionadas': calles_no_relacionadas,
        'colonia_seleccionada': colonia_seleccionada,
    })
