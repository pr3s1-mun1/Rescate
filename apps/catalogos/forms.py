from django import forms
from .models import *

class BootstrapFormMixin:
    EXCLUDED_FIELDS = ['clave']
    CHECKED_BOX = ['administrado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in self.CHECKED_BOX:
                continue  
            elif field_name in self.EXCLUDED_FIELDS:
                field.widget.attrs.update({
                    'class': 'form-control bg-light mb-3',
                    'readonly': True
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control mb-3'
                })


class BaseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Bases
        fields = '__all__'

class AmbulanciaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ambulancias
        fields = '__all__'

class AlergiaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Alergia
        fields = '__all__'

class ParamedicoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Paramedicos
        fields = '__all__'
        widgets = {
            'mando': forms.Select(choices=[
                ('C', 'CAPITAN'),
                ('O', 'COMANDANTE'),
                ('T', 'TENIENTE'),
                ('P', 'PARAMEDICO'),
                ('S', 'SARGENTO'),
                ('A', 'ADMINISTRATIVO'),
            ]),
            'conocimiento': forms.Select(choices=[
                ('B', 'BASICO'),
                ('I', 'INTERMEDIO'),
                ('P', 'PARAMEDICO'),
                ('E', 'EMPLEADO'),

            ]),
            'tipo': forms.Select(choices=[
                ('U', 'USUARIO'),
                ('P', 'PARAMEDICO'),
                ('A', 'ADMINISTRATIVO'),               
            ]),
            'estatus': forms.Select(choices=[
                ('I', 'INCAPACIDAD'),
                ('S', 'SUSPENSION'),
                ('D', 'DESCANSO'),
                ('B', 'BASICO'),
                ('F', 'BAJA'),
                ('A', 'ACTIVO'),
                ('V', 'VACACIONES'),
                ('D', 'DESCANSO ADICIONAL'),
            ])
        }

class HospitalesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Hospitales
        fields = '__all__'

class TiposServicioForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TiposServicio
        fields = '__all__'

class GruposServicioForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GrupoServicio
        fields = '__all__'

class ProcedimientoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Procedimiento
        fields = '__all__'

class TiposUnidadesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TipoUnidad
        fields = '__all__'

class EnfermedadesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Enfermedad
        fields = '__all__'

class GruposEnfermedadesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GrupoEnfermedad
        fields = '__all__'

class MedicamentosForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = '__all__'

class MaterialesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'

class EquiposForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'

class MarcasVehiculosForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MarcaVehiculo
        fields = '__all__'

class CallesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Calle
        fields = '__all__'

class ColoniasForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Colonia
        fields = '__all__'

