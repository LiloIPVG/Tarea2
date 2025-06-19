# tareas/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("<str:name>", views.index, name="index"),
    path("<str:name>/<int:id>/", views.editar, name="editar"),
    path("<str:name>/crear/", views.crear, name="crear"),
    path("<str:name>/borrar/<int:id>/", views.borrar, name="borrar"),
    path("logout", views.logout, name="logout")
]