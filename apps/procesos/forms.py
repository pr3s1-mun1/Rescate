from django import forms
from .models import *

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
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



class PacientesForm(forms.ModelForm):
    EXCLUDED_FIELDS = ['clave']
    CHOICES = ['fallecio']
    CHECKED_BOX = [
        'firmo_liberacion',
        'tiene_acompanante',
        'entregan_pertenencias',
        'libera_responsabilidad',
        'niega_firmar',
    ]
    DATE_FIELDS = [
        'fecha_salida',
        'fecha_llegada',
        'fecha_retorno',
        'fecha_ultima_comida',
        'fecha_liberacion_respon'
    ]

    class Meta:
        model = PacientexServicio
        fields = '__all__'
        widgets = {
            'estado_civil': forms.Select(choices=[
                ('P', 'CASADO (A)'),
                ('T', 'DESCONOCIDO'),
                ('C', 'DIVORCIADO (A)'),
                ('C', 'SOLTERO (A)'),
                ('C', 'UNION LIBRE'),
                ('C', 'VIUDO (A)'),
            ]),
            'pelo': forms.Select(choices=[
                ('P', 'NEGRO'),
                ('T', 'CASTAÑO'),
                ('C', 'RUBIO'),
                ('C', 'PELIROJO'),
                ('C', 'TEÑIDO'),
                ('C', 'CANOSO'),
                ('C', 'CALVO'),
            ]),
            'nivel_concienciaa': forms.Select(choices=[
                ('P', 'ALERTA'),
                ('T', 'ESTIMULO VERBAL'),
                ('C', 'ESTIMULO DOLOROSO'),
                ('C', 'INCONSCIENTE'),
            ]),
            'piel': forms.Select(choices=[
                ('P', 'NORMAL'),
                ('T', 'HUMEDA'),
                ('C', 'SECA'),
                ('C', 'FRIA'),
                ('C', 'CALIENTE'),
                ('C', 'DIAFORETICA'),
                ('C', 'RUBICUNDA'),
                ('C', 'PALIDA - BLANCA'),
                ('C', 'CIANOTICA - AZUL'),
            ]),
            'pupilas': forms.Select(choices=[
                ('P', 'REACTIVAS'),
                ('T', 'NO REACTIVAS'),
                ('C', 'ISOCORIA'),
                ('C', 'MIOSIS'),
                ('C', 'MIDRIASIS'),
                ('C', 'ANISICORA'),
                ('C', 'DISCORIA'),
            ]),
            'complexion': forms.Select(choices=[
                ('P', 'CAQUEXIA'),
                ('T', 'DELGADO'),
                ('C', 'REGULAR'),
                ('C', 'ROBUSTA'),
                ('C', 'OBESA'),
                ('C', 'OBESIDAD MÓRBIDA'),
            ]),
            'tez': forms.Select(choices=[
                ('P', 'BLANCO'),
                ('T', 'MEDIO'),
                ('C', 'MORENO'),
                ('C', 'NEGRO'),
            ]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name in self.CHECKED_BOX:
                field.widget = forms.RadioSelect(
                    choices=[(True, 'Sí'), (False, 'No')],
                    attrs={'class': 'd-inline mb-3'}
                )
            elif field_name in self.CHOICES:
                field.widget = forms.Select(
                    choices=[(True, 'Sí'), (False, 'No')],
                    attrs={'class': 'form-control mb-3'}
                )
            elif field_name in self.DATE_FIELDS:
                field.widget = forms.DateInput(
                    attrs={'type': 'datetime-local', 'class': 'form-control mb-3'}                
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