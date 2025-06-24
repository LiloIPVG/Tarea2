from django.db import models
from datetime import date
import uuid as uuid_lib

class Cancion(models.Model):
    titulo = models.CharField(max_length=200, default="Sin título")
    artista = models.CharField(max_length=100, blank=True, null=True)
    album = models.CharField(max_length=100, blank=True, null=True)
    ano_lanzamiento = models.IntegerField(blank=True, null=True)
    es_favorita = models.BooleanField(default=False)
    fecha_agregada = models.DateField(default=date.today)
    #uuid = models.TextField(max_length=200, default="Sin uuid")

    def __str__(self):
        return f"{self.titulo} por {self.artista if self.artista else 'Artista Desconocido'}"

class Usuario(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, unique=True)
    fecha_registro = models.DateField(default=date.today)

    def __str__(self):
        return self.nombre

class UsuarioCancion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="canciones_favoritas")
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE)
    clave_relacion = models.CharField(max_length=100, unique=True, default=uuid_lib.uuid4)

    class Meta:
        unique_together = ('usuario', 'cancion')

    def save(self, *args, **kwargs):
        if not self.clave_relacion:
            self.clave_relacion = str(uuid_lib.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.nombre} - {self.cancion.titulo}"