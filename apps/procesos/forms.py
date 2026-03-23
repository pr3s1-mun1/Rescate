from django import forms
from .models import *
from decimal import Decimal, InvalidOperation

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
        self.fields['tipo_servicio_realizado'].queryset = TiposServicio.objects.all().order_by('descripcion')
        self.fields['tipo_servicio_reporta'].queryset = TiposServicio.objects.all().order_by('descripcion')
        # Agrega la clase 'form-control' a todos los widgets
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'required' : 'True',
            })
        # Para el campo 'clave', lo pones como readonly y con otras clases
        if 'clave' in self.fields:
            self.fields['clave'].widget.attrs.update({
                'class': 'form-control bg-light highlight-field',
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

    EXCLUDE_REQUIRED = [
        'telefono', 'descripcion_pertenencias', 'nombre_acompanante',
        'sexo_acompanante', 'edad_acompanante', 'domicilio_acompanante',
        'parentesco_acompanante', 'nombre_recibe', 'cargo_recibe', 'empleado_recibe',
        'fecha_liberacion_respon', 'estatura', 'edad', 'placa_vehiculo', 'marca_vehiculo',
        'nombre_agente', 'numero_agente'
    ]

    DATE_FIELDS = [
        'fecha_salida', 'fecha_llegada', 'fecha_retorno',
        'fecha_ultima_comida', 'fecha_liberacion_respon'
    ]

    def clean_estatura(self):
        valor = self.cleaned_data.get("estatura")

        if valor is None:
            return valor

        # Si viene como string con coma
        if isinstance(valor, str):
            valor = valor.replace(",", ".")

        try:
            return Decimal(valor)
        except InvalidOperation:
            raise forms.ValidationError("Estatura inválida")

    class Meta:
        model = PacientexServicio
        exclude = ['servicio']
        widgets = {
            'estado_civil': forms.Select(choices=[('1', 'CASADO (A)'), ('2', 'DESCONOCIDO'), ('3', 'DIVORCIADO (A)'), ('4', 'SOLTERO (A)'), ('5', 'UNION LIBRE'), ('6', 'VIUDO (A)')]),
            'sexo': forms.Select(choices=[('N', 'NO INGRESADO'), ('M', 'MASCULINO'), ('F', 'FEMENINO')]),
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
            'parentesco_acompanante': forms.Select(choices=[('1', 'NINGUNO'), ('2', 'PADRE'), ('3', 'MADRE'), ('4', 'HERMANO(A)'), ('5', 'TIO(A)'), ('6', 'ABUELO(A)'), ('7', 'CUÑADO(A)'), ('8', 'HIJO(A)'), ('9', 'ESPOSO(A)'), ('10', 'COMPAÑERO(A)'), ('11', 'SOBRINO(A)'), ('12', 'VECINO(A)'), ('13', 'AMIGO(A)'), ('14', 'PRIMO(A)'), ('15', 'PAREJA')]),
            'sexo_acompanante' : forms.Select(choices=[('N', 'NO ESPECIFICA'), ('M', 'MASCULINO'), ('F', 'FEMENINO')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Deshabilitar opción vacía
        """self.fields['enfermedad'].empty_label = None
        self.fields['base'].empty_label = None
        self.fields['ambulancia'].empty_label = None
        self.fields['hospital'].empty_label = None
        self.fields['empleado_recibe'].empty_label = None
        self.fields['marca_vehiculo'].empty_label = None"""





        # Querysets dinámicos
        self.fields['enfermedad'].queryset = Enfermedad.objects.order_by('nombre')
        self.fields['base'].queryset = Bases.objects.order_by('clave')
        self.fields['ambulancia'].queryset = Ambulancias.objects.filter(estado='A').order_by('descripcion')
        self.fields['hospital'].queryset = Hospitales.objects.order_by('nombre')
        self.fields['empleado_recibe'].queryset = Paramedicos.objects.filter(estatus='A', tipo='P').order_by('nombre')

        for field_name, field in self.fields.items():
            if field_name in self.DATE_FIELDS:
                field.input_formats = [
                    '%Y-%m-%dT%H:%M',     # datetime-local
                    '%Y-%m-%d %H:%M:%S',  # formato Django
                ]

                field.widget = forms.DateTimeInput(
                    format='%Y-%m-%dT%H:%M',
                    attrs={
                        'type': 'datetime-local',
                        'class': 'form-control mb-3'
                    }
                )

                if self.instance and getattr(self.instance, field_name, None):
                    field.initial = getattr(self.instance, field_name).strftime(
                        '%Y-%m-%dT%H:%M'
                    )


            # Campos booleanos con "Sí / No"
            elif field_name in self.CHOICES:
                self.fields[field_name] = forms.TypedChoiceField(
                    choices=[(True, 'Sí'), (False, 'No')],
                    coerce=lambda x: x == 'True',
                    widget=forms.Select(attrs={'class': 'form-control mb-3'})
                )

            # Campos bloqueados
            elif field_name in self.EXCLUDED_FIELDS:
                field.widget.attrs.update({
                    'class': 'form-control bg-light mb-3',
                    'readonly': True
                })
                continue  # salta lo demás

            # Por defecto todos requeridos
            field.required = True
            field.widget.attrs['required'] = 'required'

            # Excepto los listados como no requeridos
            if field_name in self.EXCLUDE_REQUIRED:
                field.required = False
                field.widget.attrs.pop('required', None)

            # Agrega la clase base sin sobreescribir
            classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{classes} form-control mb-3'.strip()



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
    EXCLUDED_FIELDS = ['paciente', 'secuencia']  

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
        widgets = {
            'parte': forms.Textarea(attrs={
                'rows': 20,
                'class': 'form-control mb-3'
            }),
        }


class CombustibleForm(forms.ModelForm):
    class Meta:
        model = Combustible
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'encargado': forms.Select(attrs={'class': 'form-control'}),
            'turno': forms.NumberInput(attrs={'class': 'form-control'}),
            'ambulancia': forms.Select(attrs={'class': 'form-control'}),
            'litros': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'remision': forms.TextInput(attrs={'class': 'form-control'}),
            'factura': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(
                choices=[
                    ('G', 'GASOLINA'),
                    ('D', 'DIESEL'),
                ],
                attrs={'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajustar el formato inicial del campo de fecha
        if self.instance and self.instance.fecha:
            self.initial['fecha'] = self.instance.fecha.strftime('%Y-%m-%dT%H:%M')
