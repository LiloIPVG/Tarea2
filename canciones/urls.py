# canciones/urls.py
from django.urls import path
from . import views

app_name = 'canciones' 

urlpatterns = [
    path("u/<str:name>/", views.lista_canciones, name="lista_canciones"),
    path("u/<str:name>/<int:id>/editar/", views.editar_cancion, name="editar_cancion"),
    path("u/<str:name>/crear/", views.crear_cancion, name="crear_cancion"),
    path("u/<str:name>/borrar/<int:id>/", views.borrar_cancion, name="borrar_cancion"),
    path("publica/", views.vista_publica_canciones, name="vista_publica_canciones"),
    path("publica/<int:cancion_id>/", views.detalle_cancion_publico, name="detalle_cancion_publico"),
]