from django.db import models
from apps.catalogos.models import *
from datetime import datetime

class Servicio(models.Model):
    clave = models.IntegerField(primary_key=True)
    fecha = models.DateTimeField(default=datetime.now)
    direccion_emergencia = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True)
    colonia_emergencia = models.ForeignKey(Colonia, on_delete=models.SET_NULL, null=True)
    descripcion_evento = models.TextField()
    nombre_persona_reporta = models.CharField(max_length=100)
    telefono_persona_reporta = models.CharField(max_length=20)
    sexo_persona_reporta = models.CharField(max_length=1)
    edad_persona_reporta = models.IntegerField()
    tipo_servicio_reporta = models.ForeignKey(
        TiposServicio, on_delete=models.SET_NULL, null=True, related_name="servicios_reportados"
    )
    
    tipo_servicio_realizado = models.ForeignKey(
        TiposServicio, on_delete=models.SET_NULL, null=True, related_name="servicios_realizados"
    )
    
    estatus = models.CharField(max_length=1)
    calle_entre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.descripcion_evento[:30]}"

    @classmethod
    def obtener_siguiente_numero(cls):
        ultimo = cls.objects.order_by('-clave').first()
        return ultimo.clave + 1 if ultimo else 1


class ParamedicoxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    paciente = models.CharField(max_length=100, null=True)
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
    clave = models.IntegerField(primary_key=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True)
    ambulancia = models.ForeignKey(Ambulancias, on_delete=models.SET_NULL, null=True)
    base = models.ForeignKey(Bases, on_delete=models.SET_NULL, null=True)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    fecha_retorno = models.DateTimeField()

    #Datos generales
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=1)
    estado_civil = models.CharField(max_length=1)
    domicilio = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True)
    telefono = models.CharField(max_length=20)
    colonia = models.ForeignKey(Colonia, on_delete=models.SET_NULL, null=True)
    estatura = models.DecimalField(max_digits=5, decimal_places=2)
    complexion = models.CharField(max_length=1)
    tez = models.CharField(max_length=1)
    pelo = models.CharField(max_length=1)
    ropa = models.CharField(max_length=100)

    
    enfermedad = models.ForeignKey(Enfermedad, on_delete=models.SET_NULL, null=True)
    marca_vehiculo = models.ForeignKey(MarcaVehiculo, on_delete=models.SET_NULL, null=True)
    placa_vehiculo = models.CharField(max_length=10)
    color_vehiculo = models.CharField(max_length=2)
    fecha_ultima_comida = models.DateTimeField()
    fallecio = models.BooleanField(default=False)
    hospital = models.ForeignKey(Hospitales, on_delete=models.SET_NULL, null=True)
    tiene_acompanante = models.BooleanField(default=False)
    nombre_acompanante = models.CharField(max_length=100)
    edad_acompanante = models.IntegerField()
    domicilio_acompanante = models.CharField(max_length=150)
    parentesco_acompanante = models.CharField(max_length=2)
    sexo_acompanante = models.CharField(max_length=1)
    entregan_pertenencias = models.BooleanField(default=False)
    descripcion_pertenencias = models.CharField(max_length=255)
    libera_responsabilidad = models.BooleanField(default=False)
    fecha_liberacion_respon = models.DateTimeField(default=False)
    firmo_liberacion = models.BooleanField(default=False)
    niega_firmar = models.BooleanField(default=False)
    nombre_respon_hospital = models.CharField(max_length=100)
    nombre_agente = models.CharField(max_length=100)
    numero_agente = models.CharField(max_length=10)
    nivel_concienciaa = models.CharField(max_length=1)
    piel = models.CharField(max_length=1)
    antecedente = models.CharField(max_length=255)
    sintoma = models.CharField(max_length=255)
    pulso_diagnostico = models.CharField(max_length=1)    
    respiracion_diagnostico = models.CharField(max_length=1)    
    pupilas = models.CharField(max_length=1)    
    hemorragia = models.CharField(max_length=1)    
    dolor = models.CharField(max_length=1)   
    pulso = models.CharField(max_length=10)   
    respiracion = models.CharField(max_length=10)   
    presion_inicial = models.CharField(max_length=10)   
    presion_posterior = models.CharField(max_length=10)   
    destroxtix = models.CharField(max_length=10)
    oximetria = models.CharField(max_length=10)
    temperatura = models.CharField(max_length=10)
    apertura_ojos_glasgow = models.CharField(max_length=1)    
    respuesta_verbal_glasgow = models.CharField(max_length=1)    
    respuesta_motora_glasgow = models.CharField(max_length=1)    
    edad_tipo = models.CharField(max_length=1)
    domicilio_numero = models.CharField(max_length=10)

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
    costo = models.DecimalField(max_digits=18, decimal_places=2)

class EquipoxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()

class LesionxPaciente(models.Model):
    clave = models.AutoField(primary_key=True)
    lesion = models.CharField(max_length=100)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
    valor = models.DecimalField(max_digits=5, decimal_places=2)

class ImpactoxVehiculo(models.Model):
    clave = models.AutoField(primary_key=True)
    impacto = models.CharField(max_length=100)
    paciente = models.ForeignKey(PacientexServicio, on_delete=models.SET_NULL, null=True)
