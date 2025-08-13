from django import forms
from django.contrib.auth.hashers import make_password
from .models import *

class BootstrapFormMixin:
    EXCLUDED_FIELDS = ['clave']
    EXCLUDED_MODELS = ['Bases', 'Ambulancias']  # ← Nombres de clase como string

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_name = self._meta.model.__name__  # ← Obtener el nombre del modelo asociado al form

        for field_name, field in self.fields.items():
            if field_name in self.EXCLUDED_FIELDS and model_name not in self.EXCLUDED_MODELS:
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
        widgets = {
            'color_hex': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'estacion' : 'Estación',
            'ubicacion' : 'Ubicación',
            'color_hex' : 'Selecciona el color'
        }

class AmbulanciaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Ambulancias
        fields = '__all__'
        widgets = {
            'estado': forms.Select(choices=[
                ('A', 'ACTIVO'),
                ('I', 'INACTIVO'),
                ('R', 'REPARACIÓN'),
            ]),
            'base': forms.Select(attrs={'class': 'form-control mb-3'})
        }
        labels = {
            'descripcion' : 'Descripción'
        }


class AlergiaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Alergia
        fields = '__all__'
        labels = {
            'descripcion' : 'Descripción'
        }

from django import forms
from django.contrib.auth.hashers import make_password
from .models import Paramedicos  # ajusta la ruta según tu proyecto

class ParamedicoForm(BootstrapFormMixin, forms.ModelForm):
    contrasena = forms.CharField(
        required=True,
        widget=forms.PasswordInput(render_value=True),
        label='Contraseña'
    )

    class Meta:
        model = Paramedicos
        fields = '__all__'
        widgets = {
            'mando': forms.Select(choices=[
                ('C', 'CAPITÁN'),
                ('O', 'COMANDANTE'),
                ('T', 'TENIENTE'),
                ('P', 'PARAMÉDICO'),
                ('S', 'SARGENTO'),
                ('A', 'ADMINISTRATIVO'),
            ]),
            'conocimiento': forms.Select(choices=[
                ('B', 'BÁSICO'),
                ('I', 'INTERMEDIO'),
                ('P', 'PARAMÉDICO'),
                ('E', 'EMPLEADO'),
            ]),
            'tipo': forms.Select(choices=[
                ('U', 'USUARIO'),
                ('P', 'PARAMEDICO'),
                ('A', 'ADMINISTRATIVO'),               
            ]),
            'estatus': forms.Select(choices=[
                ('I', 'INCAPACIDAD'),
                ('S', 'SUSPENSIÓN'),
                ('D', 'DESCANSO'),
                ('B', 'BÁSICO'),
                ('F', 'BAJA'),
                ('A', 'ACTIVO'),
                ('V', 'VACACIONES'),
                ('C', 'DESCANSO ADICIONAL'),
            ]),
            'permisos': forms.Select(choices=[
                (1, 'Lectura'),
                (2, 'Lectura y escritura'),
            ])
        }
        labels = {
            'contrasena' : 'Contraseña',
            'observacion': 'Observación'
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Si el campo contraseña fue modificado, lo hasheamos
        if 'contrasena' in self.cleaned_data and self.cleaned_data['contrasena']:
            instance.contrasena = make_password(self.cleaned_data['contrasena'])

        if commit:
            instance.save()
        return instance


class HospitalesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Hospitales
        fields = '__all__'
        labels = {
            'ubicacion' : 'Ubicación'
        }

class TiposServicioForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TiposServicio
        fields = '__all__'
        widgets = {
            'sobresaliente': forms.Select(choices=[
                ('S', 'SI'),
                ('N', 'NO'),
            ]),
            'engrafica': forms.Select(choices=[
                ('S', 'SI'),
                ('N', 'NO'),
            ])
        }
        labels = {
            'descripcion' : 'Descripción',
            'gruposervicio' : 'Grupo servicio',
            'engrafica' : 'Engráfica'
        }

class GruposServicioForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GrupoServicio
        fields = '__all__'
        labels = {
            'descripcion' : 'Descripción'
        }

class ProcedimientoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Procedimiento
        fields = '__all__'
        widgets = {
            'protocolo': forms.Select(choices=[
                ('B', 'BÁSICO'),
                ('A', 'AVANZADO'),
                ('E', 'ESPECIAL'),
            ])
        }
        labels = {
            'descripcion' : 'Descripción'
        }

class TiposUnidadesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TipoUnidad
        fields = '__all__'
        labels = {
            'descripcion' : 'Descripción'
        }

class EnfermedadesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Enfermedad
        fields = '__all__'
        widgets = {
            'engrafica': forms.Select(choices=[
                ('S', 'SI'),
                ('N', 'NO'),
            ])
        }
        labels = {
            'grupoenfermedad' : 'Grupo de enfermedad',
            'engrafica' : 'Engráfica'
        }

class GruposEnfermedadesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GrupoEnfermedad
        fields = '__all__'
        labels = {
            'descripcion' : 'Descripción'
        }

class MedicamentosForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = '__all__'
        widgets = {
            'administrado': forms.Select(choices=[
                ('S', 'SI'),
                ('N', 'NO'),
            ])
        }
        labels = {
            'descripcion' : 'Descripción'
        }

class MaterialesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Material
        fields = '__all__'
        labels = {
            'descripcion' : 'Descripción'
        }

class EquiposForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'
        labels = {
            'descripcion' : 'Descripción'
        }

class MarcasVehiculosForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MarcaVehiculo
        fields = '__all__'
        labels = {
            'descripcion' : 'Descripción'
        }

class CallesForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Calle
        fields = '__all__'

class ColoniasForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Colonia
        fields = '__all__'

class CalleColoniaForm(forms.ModelForm):
    class Meta:
        model = Calle_Colonia
        fields = ['calle', 'colonia']
        widgets = {
            'calle': forms.Select(attrs={'class': 'form-select'}),
            'colonia': forms.Select(attrs={'class': 'form-select'}),
        }