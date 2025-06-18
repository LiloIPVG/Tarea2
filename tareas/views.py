from django.shortcuts import render
from django.shortcuts import redirect
import uuid
from datetime import date

# tareas/views.py
from django.http import HttpResponse
from django.http import Http404
from .models import Tarea
from .models import Usuario
from .models import usuarioTarea
from django.template import loader
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse

def login(request):
    if request.method == 'POST':
        name = request.POST['nombre']
        password = request.POST['pass']
        try:
            usuario = Usuario.objects.get(nombre=name, contraseña=password)
            # Redirige a la URL /nombre
            return redirect(reverse('index', kwargs={'name': usuario.nombre}))
        except Usuario.DoesNotExist:
            return redirect('/')
    return render(request, "tareas/trueIndex.html")


def register(request):
    if request.method == 'POST':
            if Usuario.objects.filter(nombre=request.POST.get('nombre')).exists():
                messages.error(request, "Este usuario ya existe")
                return redirect('/register')
            usuario = Usuario(
                nombre = request.POST.get('nombre'),
                contraseña = request.POST.get('pass'),
                uuid = str(uuid.uuid4()),
                fecha=date.today()
            )
            usuario.save()
            return redirect('/')
    return render(request, "tareas/register.html")

def index(request, name):
    usuario =  Usuario.objects.get(nombre=name)
    tareas = {rel.clave: rel.tarea for rel in usuario.tiene.all()}
    template = loader.get_template("tareas/index.html")
    context = {
        "tareas": tareas,
        "name": name
    }
    return HttpResponse(template.render(context, request))
    #tareas = Tarea.objects.order_by("-id")
    #template = loader.get_template("tareas/index.html")
    #context = {"tareas": tareas}
    #return HttpResponse(template.render(context, request))

def editar(request, name, id):
    try:
        user = Usuario.objects.get(nombre=name)
    except Usuario.DoesNotExist:
        raise Http404("Usuario no existe")
    try:
        relacion = user.tiene.filter(tarea__id=id).first()
        tarea = relacion.tarea
        if request.method == 'POST':
            tarea.titulo = request.POST.get('titulo')
            tarea.completado = 'completado' in request.POST
            tarea.save()
            return redirect('index', name = name)
        return render(request, "tareas/editar.html", {"tarea": tarea, "name": name})
    except Tarea.DoesNotExist:
        raise Http404("Tarea no encontrada")
    
def crear(request, name):
    if request.method == 'POST':
        try:
            user = Usuario.objects.get(nombre=name)
        except Usuario.DoesNotExist:
            raise Http404("Usuario no existe")
        tarea = Tarea(
            titulo = request.POST.get('titulo'),
            completado = 'completado' in request.POST,
            uuid = str(uuid.uuid4()),
            important = 'importante' in request.POST,
            fecha=date.today()
        )
        tarea.save()
        relacion=usuarioTarea.objects.create(usuario = user, tarea = tarea, clave = tarea.uuid)
        relacion.save()
        return redirect('index', name = name)
    return render(request, "tareas/crear.html", {"name": name})

def borrar(request, name, id):
    try:
        user = Usuario.objects.get(nombre=name)
    except Usuario.DoesNotExist:
        raise Http404("Usuario no existe")
    try:
        relacion = user.tiene.filter(tarea__id=id).first()
        tarea = relacion.tarea
        tarea.delete()
        return redirect('index', name = name)
    except Tarea.DoesNotExist:
        raise Http404("Tarea no encontrada")
    """tarea = Tarea.objects.get(pk=id)
    if request.method == 'POST':
        tarea.delete()
        return redirect('index')
    return redirect('index')"""