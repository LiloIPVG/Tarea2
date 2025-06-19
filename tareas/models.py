from django.db import models
from datetime import date

# tareas/models.py

class Tarea(models.Model):
    titulo = models.TextField(max_length=100,default="Sin título")
    uuid = models.TextField(max_length=200, default="Sin uuid")
    completado = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    fecha = models.DateField(default=date.today)
    
class Usuario(models.Model):
    nombre = models.TextField(max_length=100)
    contraseña = models.TextField(max_length=100)
    uuid = models.TextField(max_length=200)
    fecha = models.DateField(default=date.today)

class usuarioTarea(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="tiene")
    clave = models.CharField(max_length=100)
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)