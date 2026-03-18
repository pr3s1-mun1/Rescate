from django.db import models
from apps.catalogos.models import *
from datetime import datetime
from django.db import transaction

class Servicio(models.Model):
    clave = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(default=datetime.now)
    direccion_emergencia = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True)
    colonia_emergencia = models.ForeignKey(Colonia, on_delete=models.SET_NULL, null=True)
    descripcion_evento = models.TextField()
    nombre_persona_reporta = models.CharField(max_length=100, null=True)
    telefono_persona_reporta = models.CharField(max_length=20, null=True)
    sexo_persona_reporta = models.CharField(max_length=10, null=True)
    edad_persona_reporta = models.IntegerField(null=True)
    tipo_servicio_reporta = models.ForeignKey(
        TiposServicio, on_delete=models.SET_NULL, null=True, related_name="servicios_reportados"
    )
    
    tipo_servicio_realizado = models.ForeignKey(
        TiposServicio, on_delete=models.SET_NULL, null=True, related_name="servicios_realizados"
    )
    
    estatus = models.CharField(max_length=10)
    calle_entre = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True, related_name='calle_entre')

    def __str__(self):
        return f"{self.descripcion_evento[:30]}"

    @classmethod
    def obtener_siguiente_numero(cls):
        with transaction.atomic():
            # Bloquea la fila más reciente para evitar colisiones
            ultimo = cls.objects.select_for_update().order_by('-clave').first()
            return (ultimo.clave + 1) if ultimo else 1


class ParamedicoxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    paciente = models.ForeignKey('PacientexServicio', on_delete=models.SET_NULL, null=True)
    paramedico = models.ForeignKey(Paramedicos, on_delete=models.SET_NULL, null=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True)

class UnidadxServicio(models.Model):
    clave = models.AutoField(primary_key=True)
    unidad = models.ForeignKey(TipoUnidad, on_delete=models.SET_NULL, null=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True)
    numero_unidad = models.CharField(max_length=20)
    agente_nombre = models.CharField(max_length=100)

class PacientexServicio(models.Model):
    #Servicio
    clave = models.AutoField(primary_key=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, related_name='pacientes')
    ambulancia = models.ForeignKey(Ambulancias, on_delete=models.SET_NULL, null=True)
    base = models.ForeignKey(Bases, on_delete=models.SET_NULL, null=True)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    fecha_retorno = models.DateTimeField()

    #Datos generales
    apellido_paterno = models.CharField(max_length=50, null=True, blank=True)
    apellido_materno = models.CharField(max_length=50, null=True, blank=True)
    nombre = models.CharField(max_length=50)
    edad = models.IntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=10)
    estado_civil = models.CharField(max_length=10)
    domicilio = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    colonia = models.ForeignKey(Colonia, on_delete=models.SET_NULL, null=True)
    estatura = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
    complexion = models.CharField(max_length=10)
    tez = models.CharField(max_length=10)
    pelo = models.CharField(max_length=10)
    ropa = models.CharField(max_length=100)

    
    enfermedad = models.ForeignKey(Enfermedad, on_delete=models.SET_NULL, null=True)

    #Vehículo
    marca_vehiculo = models.ForeignKey(MarcaVehiculo, on_delete=models.SET_NULL, null=True, blank=True)
    placa_vehiculo = models.CharField(max_length=10, null=True, blank=True)
    color_vehiculo = models.CharField(max_length=10, null=True, blank=True)


    fecha_ultima_comida = models.DateTimeField() #Null True
    fallecio = models.BooleanField(default=False)
    hospital = models.ForeignKey(Hospitales, on_delete=models.SET_NULL, null=True)

    #Acompañante
    tiene_acompanante = models.BooleanField(default=False)
    nombre_acompanante = models.CharField(max_length=100, null=True, blank=True)
    edad_acompanante = models.IntegerField(null=True, blank=True)
    domicilio_acompanante = models.CharField(max_length=150, null=True, blank=True)
    parentesco_acompanante = models.CharField(max_length=2, null=True, blank=True)
    sexo_acompanante = models.CharField(max_length=10, null=True, blank=True)


    #Datos de liberación
    entregan_pertenencias = models.BooleanField(default=False)
    descripcion_pertenencias = models.TextField(null=True, blank=True)
    nombre_recibe = models.CharField(max_length=100, null=True, blank=True)
    cargo_recibe = models.CharField(max_length=100, null=True, blank=True)
    empleado_recibe = models.ForeignKey(Paramedicos, on_delete=models.SET_NULL, related_name='recibe_paciente', null=True, blank=True)



    libera_responsabilidad = models.BooleanField(default=False)
    fecha_liberacion_respon = models.DateTimeField(null=True, blank=True)
    firmo_liberacion = models.BooleanField(default=False)
    niega_firmar = models.BooleanField(default=False)
    nombre_respon_hospital = models.CharField(max_length=100, null=True, blank=True)
    nombre_agente = models.CharField(max_length=100, null=True, blank=True)
    numero_agente = models.CharField(max_length=10, null=True, blank=True)

    #Impresión Diagnóstica
    nivel_concienciaa = models.CharField(max_length=10, null=True, blank=True)
    piel = models.CharField(max_length=10, null=True, blank=True)
    antecedente = models.CharField(null=True, blank=True)
    sintoma = models.TextField(null=True, blank=True)
    pulso_diagnostico = models.CharField(max_length=10, null=True, blank=True)    
    respiracion_diagnostico = models.CharField(max_length=10, null=True, blank=True)    
    pupilas = models.CharField(max_length=10, null=True, blank=True)    
    hemorragia = models.CharField(max_length=10, null=True, blank=True)    
    dolor = models.CharField(max_length=10, null=True, blank=True)

    #Signos Vitales   
    pulso = models.CharField(max_length=10, null=True, blank=True)   
    respiracion = models.CharField(max_length=10, null=True, blank=True)   
    presion_inicial = models.CharField(max_length=10, null=True, blank=True)   
    presion_posterior = models.CharField(max_length=10, null=True, blank=True)   
    destroxtix = models.CharField(max_length=10, null=True, blank=True)
    oximetria = models.CharField(max_length=10, null=True, blank=True)
    temperatura = models.CharField(max_length=10, null=True, blank=True)

    #Evaluación Glasglow
    apertura_ojos_glasgow = models.CharField(max_length=10, null=True, blank=True)    
    respuesta_verbal_glasgow = models.CharField(max_length=10, null=True, blank=True)    
    respuesta_motora_glasgow = models.CharField(max_length=10, null=True, blank=True)

    edad_tipo = models.CharField(max_length=10, null=True, blank=True)
    domicilio_numero = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.clave}"  
    
    @classmethod
    def obtener_siguiente_numero(cls):
        ultimo = cls.objects.order_by('-clave').first()
        return ultimo.clave + 1 if ultimo else 1


class ProcedimientoxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    procedimiento = models.ForeignKey(Procedimiento, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)


class AlergiaxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    alergia = models.ForeignKey(Alergia, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)

class MaterialxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    costo = models.DecimalField(max_digits=18, decimal_places=2)

class MedIngeridoxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()

class MedAdministradoxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    costo = models.DecimalField(max_digits=18, decimal_places=2, default=0, null=True)

class EquipoxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()

class LesionxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    lesion = models.CharField(max_length=100)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    valor = models.DecimalField(max_digits=5, decimal_places=2, default=0)

class QuemaduraxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    quemadura = models.CharField(max_length=100)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    valor = models.DecimalField(max_digits=5, decimal_places=2, default=0)

class ImpactoxVehiculo(models.Model):
    clave = models.AutoField(primary_key=True)
    impacto = models.CharField(max_length=100)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)

class PartexServico(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True)
    parte = models.TextField(blank=True, null=True)

class TestigoxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=100, null=True)
    edad = models.IntegerField()
    domicilio = models.CharField(max_length=100, null=True)
    telefono = models.CharField(max_length=20, null=True)
    parentesco = models.CharField(max_length=50, null=True, blank=True)


class EmbarazoxPaciente(models.Model):
    secuencia = models.AutoField(primary_key=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    numero_gestaciones = models.IntegerField(blank=True)
    numero_partos = models.IntegerField(blank=True)
    numero_cesareas = models.IntegerField(blank=True)
    numero_abortos = models.IntegerField(blank=True)
    utlima_menstruacion = models.DateTimeField(blank=True)
    edad_gestacional = models.IntegerField(blank=True)
    presenta_sangrado = models.BooleanField(default=False)
    inicio_contracciones = models.DateTimeField(blank=True)
    bolsa_rota = models.BooleanField(default=False)
    atencion_medica_embarazo = models.BooleanField(default=False)
    nota = models.TextField(blank=True)

    def __str__(self):
        return f"{self.secuencia}"  


class Combustible(models.Model):
    clave = models.AutoField(primary_key=True)
    supervisor = models.ForeignKey(Paramedicos, on_delete=models.SET_NULL, null=True)
    encargado = models.ForeignKey(Paramedicos, on_delete=models.SET_NULL, null=True, related_name='encargado_combustible')
    fecha = models.DateTimeField()
    turno = models.IntegerField()
    ambulancia = models.ForeignKey(Ambulancias, on_delete=models.SET_NULL, null=True)
    litros = models.DecimalField(max_digits=7, decimal_places=2)
    valor = models.DecimalField(max_digits=7, decimal_places=2)
    remision = models.CharField(max_length=20, null=True)
    factura = models.CharField(max_length=20, null=True)
    tipo = models.CharField(max_length=1, null=True)

class Reloj(models.Model):
    clave = models.AutoField(primary_key=True)
    paramedico = models.ForeignKey(Paramedicos, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField()
    estatus = models.CharField(max_length=1)
    observacion = models.TextField(null=True, blank=True)
