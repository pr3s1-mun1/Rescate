from django import forms
from .models import *

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}, 
                format='%Y-%m-%dT%H:%M'
            ),
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
        # Agrega la clase 'form-control' a todos los widgets
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        # Para el campo 'clave', lo pones como readonly y con otras clases
        if 'clave' in self.fields:
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
    CHOICES = [
        'fallecio', 'entregan_pertenencias', 'tiene_acompanante',
        'libera_responsabilidad', 'firmo_liberacion', 'niega_firmar'
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
        exclude = ['servicio']
        widgets = {
            'estado_civil': forms.Select(choices=[('1', 'CASADO (A)'), ('2', 'DESCONOCIDO'), ('3', 'DIVORCIADO (A)'), ('4', 'SOLTERO (A)'), ('5', 'UNION LIBRE'), ('6', 'VIUDO (A)')]),
            'sexo': forms.Select(choices=[('1', 'NO INGRESADO'), ('2', 'MASCULINO'), ('3', 'FEMENINO')]),
            'pelo': forms.Select(choices=[('1', 'NEGRO'), ('2', 'CASTAÑO'), ('3', 'RUBIO'), ('4', 'PELIROJO'), ('5', 'TEÑIDO'), ('6', 'CANOSO'), ('7', 'CALVO')]),
            'nivel_concienciaa': forms.Select(choices=[('1', 'ALERTA'), ('2', 'ESTIMULO VERBAL'), ('3', 'ESTIMULO DOLOROSO'), ('4', 'INCONSCIENTE')]),
            'piel': forms.Select(choices=[('1', 'NORMAL'), ('2', 'HUMEDA'), ('3', 'SECA'), ('4', 'FRIA'), ('5', 'CALIENTE'), ('6', 'DIAFORETICA'), ('7', 'RUBICUNDA'), ('8', 'PALIDA - BLANCA'), ('9', 'CIANOTICA - AZUL')]),
            'pupilas': forms.Select(choices=[('1', 'REACTIVAS'), ('2', 'NO REACTIVAS'), ('3', 'ISOCORIA'), ('4', 'MIOSIS'), ('5', 'MIDRIASIS'), ('6', 'ANISICORA'), ('7', 'DISCORIA')]),
            'complexion': forms.Select(choices=[('1', 'CAQUEXIA'), ('2', 'DELGADO'), ('3', 'REGULAR'), ('4', 'ROBUSTA'), ('5', 'OBESA'), ('6', 'OBESIDAD MÓRBIDA')]),
            'tez': forms.Select(choices=[('1', 'BLANCO'), ('2', 'MEDIO'), ('3', 'MORENO'), ('4', 'NEGRO')]),
            'pulso_diagnostico': forms.Select(choices=[('1', 'REGULAR'), ('2', 'IRREGULAR'), ('3', 'LLENO'), ('4', 'DEBIL'), ('5', 'FILIFORME'), ('6', 'AUSENTE')]),
            'respiracion_diagnostico': forms.Select(choices=[('1', 'NORMAL'), ('2', 'SUPERFICIAL'), ('3', 'LABORIOSA'), ('4', 'APNEA'), ('5', 'KUSSMAULL'), ('6', 'AUSENTE')]),
            'hemorragia': forms.Select(choices=[('1', 'NO'), ('2', 'MINIMA'), ('3', 'MODERADA'), ('4', 'SEVERA')]),
            'dolor': forms.Select(choices=[('1', 'NO'), ('2', 'MINIMO'), ('3', 'MODERADO'), ('4', 'SEVERO')]),
            'apertura_ojos_glasgow': forms.Select(choices=[('1', 'NO EVALUADO'), ('2', 'ESPONTANEO'), ('3', 'AL ESTIMULO VERBAL'), ('4', 'AL DOLOR'), ('5', 'NO RESPUESTA')]),
            'respuesta_verbal_glasgow': forms.Select(choices=[('1', 'ORIENTADO EN 3 ESFERAS'), ('2', 'CONFUSO PERO CONTESTA'), ('3', 'PALABRAS INCOHERENTES'), ('4', 'PALABRAS INCOMPRENSIBLES'), ('5', 'NO HAY RESPUESTA'), ('6', 'NO EVALUADO')]),
            'respuesta_motora_glasgow': forms.Select(choices=[('1', 'NO EVALUADO'), ('2', 'OBEDECE ORDENES'), ('3', 'LOCALIZA DOLOR'), ('4', 'RECHAZO AL DOLOR'), ('5', 'FLEXION ANORMAL AL DOLOR'), ('6', 'EXTENSION ANORMAL AL DOLOR'), ('7', 'NO RESPUESTA')]),
            'edad_tipo': forms.Select(choices=[('1', 'DIAS'), ('2', 'SEMANAS'), ('3', 'MESES'), ('4', 'AÑOS')]),
            'color_vehiculo': forms.Select(choices=[('1', 'NINGUNO'), ('2', 'BLANCO'), ('3', 'NEGRO'), ('4', 'ROJO'), ('5', 'AMARILLO'), ('6', 'VERDE'), ('7', 'CAFE'), ('8', 'GRIS')]),
            'parentesco_acompanante': forms.Select(choices=[('1', 'NINGUNO'), ('2', 'PADRE'), ('3', 'MADRE'), ('4', 'HERMANO(A)'), ('5', 'TIO(A)'), ('6', 'ABUELO(A)'), ('7', 'CUÑADO(A)'), ('8', 'HIJO(A)')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name in self.__class__.DATE_FIELDS:
                field.widget = forms.DateTimeInput(
                    attrs={
                        'type': 'datetime-local',
                        'class': 'form-control mb-3'
                    },
                    format='%Y-%m-%dT%H:%M'
                )
                if self.instance and hasattr(self.instance, field_name):
                    date_value = getattr(self.instance, field_name)
                    if date_value:
                        field.initial = date_value.strftime('%Y-%m-%dT%H:%M')

            elif field_name in self.__class__.CHOICES:
                field.widget = forms.Select(
                    choices=[(True, 'Sí'), (False, 'No')],
                    attrs={'class': 'form-control mb-3'}
                )

            elif field_name in self.__class__.EXCLUDED_FIELDS:
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

class EmbarazoAsignadoForm(forms.ModelForm):
    DATE_FIELDS = ['utlima_menstruacion', 'inicio_contracciones']
    CHOICES = ['presenta_sangrado', 'bolsa_rota', 'atencion_medica_embarazo']
    EXCLUDED_FIELDS = ['paciente', 'secuencia']  # Por ejemplo, campos que quieres hacer readonly

    class Meta:
        model = EmbarazoxPaciente
        fields = '__all__'
        exclude = ['paciente']
        widgets = {
            'utlima_menstruacion': forms.DateInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'inicio_contracciones': forms.DateInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Campo tipo fecha
            if field_name in self.DATE_FIELDS:
                field.widget = forms.DateTimeInput(
                    attrs={
                        'type': 'datetime-local',
                        'class': 'form-control mb-3'
                    },
                    format='%Y-%m-%dT%H:%M'
                )
                # Formatear valor inicial
                if self.instance and hasattr(self.instance, field_name):
                    date_value = getattr(self.instance, field_name)
                    if date_value:
                        field.initial = date_value.strftime('%Y-%m-%dT%H:%M')

            # Campos booleanos como select "Sí/No"
            elif field_name in self.CHOICES:
                field.widget = forms.Select(
                    choices=[(True, 'Sí'), (False, 'No')],
                    attrs={'class': 'form-control mb-3'}
                )

            # Campos solo lectura
            elif field_name in self.EXCLUDED_FIELDS:
                field.widget.attrs.update({
                    'class': 'form-control bg-light mb-3',
                    'readonly': 'readonly'
                })
                
            # Otros campos
            else:
                field.widget.attrs.update({
                    'class': 'form-control mb-3'
                })

class PartesAsignadoForm(forms.ModelForm):
    class Meta:
        model = PartexServico
        exclude = ['servicio']
        fields = '__all__'
        widgets = {
            'parte': forms.Textarea(attrs={
                'rows': 20,
                'class': 'form-control mb-3'
            }),
        }


    