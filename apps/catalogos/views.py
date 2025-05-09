from django.shortcuts import render, get_object_or_404, redirect
from functools import wraps
from django.contrib import messages
from .models import *
from .forms import *

CATALOGOS = {
    'alergias':             {'model': Alergia,              'form': AlergiaForm,             'template': 'alergias.html',            'update_template': 'updt/update_alergias.html'},
    'bases':                {'model': Bases,               'form': BaseForm,                'template': 'bases.html',               'update_template': 'updt/update_base.html'},
    'ambulancias':          {'model': Ambulancias,         'form': AmbulanciaForm,          'template': 'ambulancias.html',         'update_template': 'updt/update_ambulancias.html'},
    'paramedicos':          {'model': Paramedicos,         'form': ParamedicoForm,          'template': 'paramedicos.html',         'update_template': 'updt/update_paramedicos.html'},
    'hospitales':           {'model': Hospitales,          'form': HospitalesForm,          'template': 'hospitales.html',          'update_template': 'updt/update_hospitales.html'},
    'tipos_servicio':       {'model': TiposServicio,       'form': TiposServicioForm,       'template': 'tipos_servicio.html',      'update_template': 'updt/update_tipos_servicio.html'},
    'grupos_servicio':      {'model': GrupoServicio,       'form': GruposServicioForm,      'template': 'grupos_servicio.html',     'update_template': 'updt/update_grupos_servicio.html'},
    'procedimientos':       {'model': Procedimiento,       'form': ProcedimientoForm,      'template': 'procedimientos.html',      'update_template': 'updt/update_procedimientos.html'},
    'tipos_unidades':       {'model': TipoUnidad,         'form': TiposUnidadesForm,        'template': 'tipos_unidades.html',      'update_template': 'updt/update_tipos_unidades.html'},
    'enfermedades':         {'model': Enfermedad,          'form': EnfermedadesForm,        'template': 'enfermedades.html',        'update_template': 'updt/update_enfermedades.html'},
    'grupos_enfermedades':  {'model': GrupoEnfermedad,     'form': GruposEnfermedadesForm,  'template': 'grupos_enfermedades.html', 'update_template': 'updt/update_grupos_enfermedades.html'},
    'medicamentos':         {'model': Medicamento,        'form': MedicamentosForm,        'template': 'medicamentos.html',        'update_template': 'updt/update_medicamentos.html'},
    'materiales':           {'model': Material,           'form': MaterialesForm,          'template': 'materiales.html',          'update_template': 'updt/update_materiales.html'},
    'equipos':              {'model': Equipo,             'form': EquiposForm,             'template': 'equipos.html',             'update_template': 'updt/update_equipos.html'},
    'marcas_vehiculos':     {'model': MarcaVehiculo,      'form': MarcasVehiculosForm,     'template': 'marcas_vehiculos.html',    'update_template': 'updt/update_marcas_vehiculos.html'},
    'calles':               {'model': Calle,              'form': CallesForm,              'template': 'calles.html',              'update_template': 'updt/update_calles.html'},
    'colonias':             {'model': Colonia,            'form': ColoniasForm,            'template': 'colonias.html',            'update_template': 'updt/update_colonias.html'},
}

#Envío de listas de catalogos a HTML
def catalogo_general(request, tipo):
    if tipo not in CATALOGOS:
        return render(request, '404.html', {'error': 'Catálogo no encontrado'})

    query = request.GET.get('q', '')
    catalogo = CATALOGOS[tipo]
    modelo = catalogo['model']
    template = catalogo['template']
    
    objetos = modelo.objects.filter(descripcion__icontains=query) if query else modelo.objects.all()

    return render(request, template, {tipo: objetos, 'query': query})

def requiere_tipo_paramedico(*tipos_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            tipo = request.session.get("tipo")
            if tipo not in tipos_permitidos:
                messages.warning(request, "🚫 No tienes permisos para acceder a esta sección.")
                return render(request, "bloqueo.html")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

#Actualización de rows de las bases de datos
@requiere_tipo_paramedico('A')
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
            return redirect('catalogo_general', tipo=tipo)
    else:
        form = form_class(instance=objeto)

    return render(request, "updt/update.html", {
        'form': form,
        'tipo': tipo,
        'titulo': catalogo.get('nombre', tipo)
    })


#Eliminar rows de la base de datos
@requiere_tipo_paramedico('A')
def delete_catalogo(request, tipo, clave):
    if tipo not in CATALOGOS:
        return redirect('error')

    catalogo = CATALOGOS[tipo]
    modelo = catalogo['model']
    objeto = get_object_or_404(modelo, clave=clave)

    if request.method == "POST":
        objeto.delete()
        return redirect('catalogo_general', tipo=tipo)

    return render(request, 'confirm_delete.html', {'objeto': objeto, 'tipo': tipo})

def add_catalogo(request, tipo):
    if tipo not in CATALOGOS or 'form' not in CATALOGOS[tipo] or not CATALOGOS[tipo]['form']:
        return redirect('error')

    catalogo = CATALOGOS[tipo]
    modelo = catalogo['model']
    form_class = catalogo['form']

    if modelo.objects.exists():
        max_clave = modelo.objects.all().aggregate(models.Max('clave'))['clave__max']
        nueva_clave = max_clave + 1 if max_clave is not None else 1
    else:
        nueva_clave = 1

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            nuevo_registro = form.save(commit=False)
            nuevo_registro.clave = nueva_clave
            nuevo_registro.save() 
            return redirect('catalogo_general', tipo=tipo)

    else:
        form = form_class(initial={'clave': nueva_clave})

    return render(request, 'add/add.html', {'form': form, 'tipo': tipo, 'titulo': catalogo.get('nombre', tipo), 'nueva_clave': nueva_clave})

