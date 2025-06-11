from django.db import models
from django.core.validators import RegexValidator

class Alergia(models.Model):
    clave = models.IntegerField(primary_key=1)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.descripcion}"

class Bases(models.Model):
    clave = models.CharField(primary_key=True, max_length=20)
    estacion = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=100)
    color_hex = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6})$',
                message='El color debe estar en formato hexadecimal, por ejemplo: #FF5733'
            )
        ],
        help_text="Código de color en formato hexadecimal (ej. #FF5733)"
    )

    def __str__(self):
        return f"{self.clave}"

class Ambulancias(models.Model):
    clave = models.CharField(primary_key=1, max_length=5)
    descripcion = models.CharField(max_length=50)
    estado = models.CharField(max_length=1)
    base = models.ForeignKey('Bases', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.descripcion}"

class Paramedicos(models.Model):
    clave = models.IntegerField(primary_key=1)
    nombre = models.CharField(max_length=100)
    usuario = models.CharField(max_length=10)
    contrasena = models.CharField(max_length=10)
    mando = models.CharField(max_length=1)
    conocimiento = models.CharField(max_length=1)
    tipo = models.CharField(max_length=1)
    estatus = models.CharField(max_length=1)
    observacion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre}"


class Hospitales(models.Model):
    clave = models.IntegerField(primary_key=1)
    nombre = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=70)

    def __str__(self):
        return f"{self.nombre}"

class GrupoServicio(models.Model):
    clave = models.IntegerField(primary_key=1)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.descripcion}"

class TiposServicio(models.Model):
    clave = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    gruposervicio = models.ForeignKey('GrupoServicio', on_delete=models.SET_NULL, null=True)
    sobresaliente = models.CharField(max_length=1, null=True)
    engrafica = models.CharField(max_length=1, null=True)

    def __str__(self):
        return f" {self.descripcion}"

class Procedimiento(models.Model):
    clave = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    protocolo = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.descripcion}"

class TipoUnidad(models.Model):
    clave = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.descripcion}"

class GrupoEnfermedad(models.Model):
    clave = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=70)

    def __str__(self):
        return f"{self.descripcion}"

class Enfermedad(models.Model):
    clave = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=70)
    grupoenfermedad = models.ForeignKey('GrupoEnfermedad', on_delete=models.SET_NULL, null=True)
    engrafica = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.nombre}"

class Medicamento(models.Model):
    clave = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    unidad = models.CharField(max_length=10)
    administrado = models.BooleanField()
    costo = models.DecimalField(max_digits=18, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.descripcion}"

class Material(models.Model):
    clave = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    unidad = models.CharField(max_length=10)
    costo = models.DecimalField(max_digits=18, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.descripcion}"

class Equipo(models.Model):
    clave = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    unidad = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.descripcion}"

class MarcaVehiculo(models.Model):
    clave = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.descripcion}"

class Calle(models.Model):
    clave = models.AutoField(primary_key=True)
    calle = models.TextField(max_length=255)

    def __str__(self):
        return f"{self.calle}"

class Colonia(models.Model):
    clave = models.AutoField(primary_key=True)
    colonia = models.TextField(max_length=255)

    def __str__(self):
        return f"{self.colonia}"

class Calle_Colonia(models.Model):
    id = models.AutoField(primary_key=True)
    calle = models.ForeignKey(Calle, on_delete=models.SET_NULL, null=True)
    colonia = models.ForeignKey(Colonia, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.calle} - {self.colonia}"
    

class Logs_Sistema(models.Model):
    clave = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=50)
    accion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.fecha} - {self.usuario} - {self.accion}"