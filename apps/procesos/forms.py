from django import forms
from .models import *

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M'),
            'descripcion_evento': forms.Textarea(attrs={'cols': 90}),
            'estatus': forms.Select(choices=[
                ('P', 'EN PROCESO'),
                ('T', 'TERMINADO'),
                ('C', 'CANCELADO')
            ]),
            'sexo_persona_reporta': forms.Select(choices=[
                ('M', 'MASCULINO'),
                ('F', 'FEMENINO'),
                ('D', 'DESCONOCIDO')
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        
        self.fields['clave'].widget.attrs.update({
            'class': 'form-control bg-light highlight-field',
            'readonly': True
        })

class ParamedicosForm(forms.ModelForm):
    class Meta:
        model = Paramedicos
        fields = '__all__'



from django import forms
from .models import PacientexServicio  # Asegúrate de importar correctamente tu modelo

class PacientesForm(forms.ModelForm):
    EXCLUDED_FIELDS = ['clave']
    CHOICES = ['fallecio', 'entregan_pertenencias', 'tiene_acompanante', 'libera_responsabilidad', 'firmo_liberacion', 'niega_firmar']
    DATE_FIELDS = [
        'fecha_salida',
        'fecha_llegada',
        'fecha_retorno',
        'fecha_ultima_comida',
        'fecha_liberacion_respon'
    ]

    class Meta:
        model = PacientexServicio
        exclude = ['servicio']
        widgets = {
            'estado_civil': forms.Select(choices=[
                ('1', 'CASADO (A)'),
                ('2', 'DESCONOCIDO'),
                ('3', 'DIVORCIADO (A)'),
                ('4', 'SOLTERO (A)'),
                ('5', 'UNION LIBRE'),
                ('6', 'VIUDO (A)'),
            ]),            
            'sexo': forms.Select(choices=[
                ('1', 'NO INGRESADO'),
                ('2', 'MASCULINO'),
                ('3', 'FEMENINO'),
            ]),
            'pelo': forms.Select(choices=[
                ('1', 'NEGRO'),
                ('2', 'CASTAÑO'),
                ('3', 'RUBIO'),
                ('4', 'PELIROJO'),
                ('5', 'TEÑIDO'),
                ('6', 'CANOSO'),
                ('7', 'CALVO'),
            ]),
            'nivel_concienciaa': forms.Select(choices=[
                ('1', 'ALERTA'),
                ('2', 'ESTIMULO VERBAL'),
                ('3', 'ESTIMULO DOLOROSO'),
                ('4', 'INCONSCIENTE'),
            ]),
            'piel': forms.Select(choices=[
                ('1', 'NORMAL'),
                ('2', 'HUMEDA'),
                ('3', 'SECA'),
                ('4', 'FRIA'),
                ('5', 'CALIENTE'),
                ('6', 'DIAFORETICA'),
                ('7', 'RUBICUNDA'),
                ('8', 'PALIDA - BLANCA'),
                ('9', 'CIANOTICA - AZUL'),
            ]),
            'pupilas': forms.Select(choices=[
                ('1', 'REACTIVAS'),
                ('2', 'NO REACTIVAS'),
                ('3', 'ISOCORIA'),
                ('4', 'MIOSIS'),
                ('5', 'MIDRIASIS'),
                ('6', 'ANISICORA'),
                ('7', 'DISCORIA'),
            ]),
            'complexion': forms.Select(choices=[
                ('1', 'CAQUEXIA'),
                ('2', 'DELGADO'),
                ('3', 'REGULAR'),
                ('4', 'ROBUSTA'),
                ('5', 'OBESA'),
                ('6', 'OBESIDAD MÓRBIDA'),
            ]),
            'tez': forms.Select(choices=[
                ('1', 'BLANCO'),
                ('2', 'MEDIO'),
                ('3', 'MORENO'),
                ('4', 'NEGRO'),
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configurar campos de fecha con el formato datetime-local
        for field_name, field in self.fields.items():
            if field_name in self.DATE_FIELDS:
                field.widget = forms.DateTimeInput(
                    attrs={
                        'type': 'datetime-local',
                        'class': 'form-control mb-3'
                    },
                    format='%Y-%m-%dT%H:%M'
                )
                
                # Formatear el valor inicial si existe
                if self.instance and hasattr(self.instance, field_name):
                    date_value = getattr(self.instance, field_name)
                    if date_value:
                        field.initial = date_value.strftime('%Y-%m-%dT%H:%M')
            elif field_name in self.CHOICES:
                field.widget = forms.Select(
                    choices=[(True, 'Sí'), (False, 'No')],
                    attrs={'class': 'form-control mb-3'}
                )
            elif field_name in self.EXCLUDED_FIELDS:
                field.widget.attrs.update({
                    'class': 'form-control bg-light mb-3',
                    'readonly': True
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-control mb-3'
                })

class UnidadAsignadoForm(forms.ModelForm):
    class Meta:
        model = UnidadxServicio
        fields = '__all__'

class ParamedicoAsignadoForm(forms.ModelForm):
    class Meta:
        model = ParamedicoxPaciente
        fields = '__all__'