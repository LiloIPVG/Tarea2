from django.contrib import admin

# canciones/admin.py
from django.contrib import admin

from .models import Cancion

admin.site.register(Cancion)