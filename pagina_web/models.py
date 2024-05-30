from datetime import date
from django.db import models
from django.contrib.auth.models import User


class cliente(models.Model):
    id_usuario=models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1)
    nombre=models.CharField(max_length=100)
    apellido=models.CharField(max_length=100)
    rfc=models.CharField(max_length=13)

class registro(models.Model):
    subtotal = models.FloatField(default=0)
    total = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    id_cliente = models.ForeignKey(cliente, on_delete=models.DO_NOTHING)
    tipo = models.BooleanField() #0 Ingresos 1 Gastos
    fecha = models.DateField(default=date.today)

class registro_detalle(models.Model):
    fecha = models.DateField()
    folio = models.CharField(max_length=100)
    subtotal = models.FloatField(default=0)
    total = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    emisor=models.CharField(max_length=15)
    receptor=models.CharField(max_length=15, default="1234567890987")
    id_registro = models.ForeignKey(registro, on_delete=models.DO_NOTHING)