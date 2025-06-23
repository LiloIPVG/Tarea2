from django.shortcuts import render, redirect, get_object_or_404
import uuid
from datetime import date
from django.contrib import messages
from django.urls import reverse

from .models import Cancion, Usuario, UsuarioCancion

# --- Vistas de Autenticación ---

def login(request):
    if 'nombre_usuario' in request.session:
        return redirect(reverse('canciones:lista_canciones', kwargs={'name': request.session['nombre_usuario']}))
    if request.method == 'POST':
        name = request.POST['nombre']
        password = request.POST['pass']
        try:
            usuario = Usuario.objects.get(nombre=name, contrasena=password)
            request.session['nombre_usuario'] = usuario.nombre
            messages.success(request, f"¡Bienvenido de nuevo, {usuario.nombre}!")
            return redirect(reverse('canciones:lista_canciones', kwargs={'name': usuario.nombre}))
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return render(request, "canciones/trueIndex.html")
    return render(request, "canciones/trueIndex.html")


def register(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('nombre')
        contrasena = request.POST.get('pass')
        if not nombre_usuario or not nombre_usuario.strip():
            messages.error(request, "El nombre de usuario no puede estar vacío ni contener solo espacios.")
            return render(request, "canciones/register.html", {'nombre_usuario_previo': nombre_usuario})
        
        if Usuario.objects.filter(nombre=nombre_usuario).exists():
            messages.error(request, "Este usuario ya existe. Por favor, elige otro nombre.")
            return render(request, "canciones/register.html", {'nombre_usuario_previo': nombre_usuario})
        
        if not contrasena or len(contrasena) < 3:
            messages.error(request, "La contraseña debe tener al menos 3 caracteres.")
            return render(request, "canciones/register.html", {'nombre_usuario_previo': nombre_usuario})

        usuario = Usuario(
            nombre = nombre_usuario,
            contrasena = contrasena,
            uuid = uuid.uuid4(),
            fecha_registro=date.today()
        )
        usuario.save()
        messages.success(request, "Cuenta registrada exitosamente. Ahora puedes iniciar sesión.")
        return redirect('login')
    
    return render(request, "canciones/register.html")


def logout_view(request):

    if 'nombre_usuario' in request.session:
        del request.session['nombre_usuario']
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect('login')


def lista_canciones(request, name):

    if 'nombre_usuario' not in request.session:
        messages.error(request, "Debes iniciar sesión para acceder a esta página.")
        return redirect('login')
    
    if request.session.get('nombre_usuario') != name:
        messages.error(request, "Acceso no autorizado a la lista de otro usuario.")
        return redirect('login')

    usuario = get_object_or_404(Usuario, nombre=name)
    
    canciones_favoritas = {rel.clave_relacion: rel.cancion for rel in usuario.canciones_favoritas.all()}
    
    context = {
        "canciones": canciones_favoritas,
        "name": name,
        "is_authenticated": True
    }
    return render(request, "canciones/listar_canciones.html", context)


def crear_cancion(request, name):
    if 'nombre_usuario' not in request.session or request.session.get('nombre_usuario') != name:
        messages.error(request, "Acceso no autorizado.")
        return redirect('login')

    user = get_object_or_404(Usuario, nombre=name)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        artista = request.POST.get('artista')
        album = request.POST.get('album')
        ano_lanzamiento_str = request.POST.get('ano_lanzamiento')
        es_favorita_global = 'es_favorita' in request.POST 
        if not titulo or not titulo.strip():
            messages.error(request, "El título de la canción es obligatorio y no puede estar vacío.")
            context = {
                "name": name,
                "is_authenticated": True,
                "current_year": date.today().year,
                "cancion": {
                    'titulo': titulo,
                    'artista': artista,
                    'album': album,
                    'ano_lanzamiento': ano_lanzamiento_str,
                    'es_favorita': es_favorita_global
                }
            }
            return render(request, "canciones/crear_cancion.html", context)

        if UsuarioCancion.objects.filter(usuario=user, cancion__titulo=titulo).exists():
            messages.error(request, f"Ya tienes una canción llamada '{titulo}' en tus favoritos.")
            context = {
                "name": name,
                "is_authenticated": True,
                "current_year": date.today().year,
                "cancion": {
                    'titulo': titulo,
                    'artista': artista,
                    'album': album,
                    'ano_lanzamiento': ano_lanzamiento_str,
                    'es_favorita': es_favorita_global
                }
            }
            return render(request, "canciones/crear_cancion.html", context)

        try:
            ano_lanzamiento = int(ano_lanzamiento_str) if ano_lanzamiento_str else None
            if ano_lanzamiento is not None and (ano_lanzamiento < 1900 or ano_lanzamiento > date.today().year):
                messages.error(request, f"El año de lanzamiento debe estar entre 1900 y {date.today().year}.")
                context = {
                    "is_authenticated": True,
                    "current_year": date.today().year,
                    "cancion": {
                        'titulo': titulo,
                        'artista': artista,
                        'album': album,
                        'ano_lanzamiento': ano_lanzamiento_str,
                        'es_favorita': es_favorita_global
                    }
                }
                return render(request, "canciones/crear_cancion.html", context)

        except ValueError:
            messages.error(request, "El año de lanzamiento debe ser un número válido.")
            context = {
                "name": name,
                "is_authenticated": True,
                "current_year": date.today().year,
                "cancion": {
                    'titulo': titulo,
                    'artista': artista,
                    'album': album,
                    'ano_lanzamiento': ano_lanzamiento_str,
                    'es_favorita': es_favorita_global
                }
            }
            return render(request, "canciones/crear_cancion.html", context)

        cancion, created = Cancion.objects.get_or_create(
            titulo=titulo,
            artista=artista if artista else '',
            album=album if album else '',
            defaults={
                'ano_lanzamiento': ano_lanzamiento,
                'es_favorita': es_favorita_global,
                'fecha_agregada': date.today()
            }
        )
        if not created:
            cancion.ano_lanzamiento = ano_lanzamiento
            cancion.es_favorita = es_favorita_global
            cancion.save()

        try:
            UsuarioCancion.objects.create(usuario=user, cancion=cancion, clave_relacion=uuid.uuid4())
            messages.success(request, f"Canción '{cancion.titulo}' agregada a tus favoritos.")
        except Exception:
            messages.info(request, f"La canción '{cancion.titulo}' ya estaba en tus favoritos.")

        return redirect('canciones:lista_canciones', name=name)

    context = {
        "name": name,
        "is_authenticated": True,
        "current_year": date.today().year 
    }
    return render(request, "canciones/crear_cancion.html", context)


def editar_cancion(request, name, id):

    if 'nombre_usuario' not in request.session or request.session.get('nombre_usuario') != name:
        messages.error(request, "Acceso no autorizado.")
        return redirect('login')

    user = get_object_or_404(Usuario, nombre=name)
    relacion = get_object_or_404(UsuarioCancion, usuario=user, cancion__id=id)
    cancion = relacion.cancion

    if request.method == 'POST':
        nuevo_titulo = request.POST.get('titulo')
        nuevo_artista = request.POST.get('artista')
        nuevo_album = request.POST.get('album')
        nuevo_ano_lanzamiento_str = request.POST.get('ano_lanzamiento')
        nueva_es_favorita_global = 'es_favorita' in request.POST

        if not nuevo_titulo or not nuevo_titulo.strip():
            messages.error(request, "El título de la canción no puede estar vacío.")
            context = {"cancion": cancion, "name": name, "is_authenticated": True, "current_year": date.today().year}
            return render(request, "canciones/editar_cancion.html", context)
        
        if UsuarioCancion.objects.filter(
            usuario=user, 
            cancion__titulo=nuevo_titulo
        ).exclude(cancion=cancion).exists():
            messages.error(request, f"Ya tienes otra canción con el título '{nuevo_titulo}'.")
            context = {"cancion": cancion, "name": name, "is_authenticated": True, "current_year": date.today().year}
            return render(request, "canciones/editar_cancion.html", context)

        try:
            nuevo_ano_lanzamiento = int(nuevo_ano_lanzamiento_str) if nuevo_ano_lanzamiento_str else None
            if nuevo_ano_lanzamiento is not None and (nuevo_ano_lanzamiento < 1900 or nuevo_ano_lanzamiento > date.today().year):
                messages.error(request, f"El año de lanzamiento debe estar entre 1900 y {date.today().year}.")
                context = {"cancion": cancion, "name": name, "is_authenticated": True, "current_year": date.today().year}
                return render(request, "canciones/editar_cancion.html", context)
        except ValueError:
            messages.error(request, "El año de lanzamiento debe ser un número válido.")
            context = {"cancion": cancion, "name": name, "is_authenticated": True, "current_year": date.today().year}
            return render(request, "canciones/editar_cancion.html", context)

        cancion.titulo = nuevo_titulo
        cancion.artista = nuevo_artista
        cancion.album = nuevo_album
        cancion.ano_lanzamiento = nuevo_ano_lanzamiento
        cancion.es_favorita = nueva_es_favorita_global
        cancion.save()

        messages.success(request, f"Canción '{cancion.titulo}' actualizada exitosamente.")
        return redirect('canciones:lista_canciones', name=name)

    context = {
        "cancion": cancion,
        "name": name,
        "is_authenticated": True,
        "current_year": date.today().year
    }
    return render(request, "canciones/editar_cancion.html", context)


def borrar_cancion(request, name, id):
    if 'nombre_usuario' not in request.session or request.session.get('nombre_usuario') != name:
        messages.error(request, "Acceso no autorizado.")
        return redirect('login')

    user = get_object_or_404(Usuario, nombre=name)
    relacion = get_object_or_404(UsuarioCancion, usuario=user, cancion__id=id)
    cancion_titulo = relacion.cancion.titulo

    if request.method == 'POST':
        relacion.delete()
        messages.info(request, f"Canción '{cancion_titulo}' eliminada de tus favoritos.")
    
    return redirect('canciones:lista_canciones', name=name)


# --- Vistas Públicas ---

def vista_publica_canciones(request):
    canciones_favoritas_publicas = Cancion.objects.filter(es_favorita=True).distinct().order_by('titulo')
    
    context = {
        "canciones": canciones_favoritas_publicas,
        "is_authenticated": 'nombre_usuario' in request.session 
    }
    return render(request, "canciones/vista_publica_canciones.html", context)


def detalle_cancion_publico(request, cancion_id):

    cancion = get_object_or_404(Cancion, id=cancion_id, es_favorita=True)
    
    context = {
        "cancion": cancion,
        "is_authenticated": 'nombre_usuario' in request.session
    }
    return render(request, "canciones/detalle_cancion_publico.html", context)