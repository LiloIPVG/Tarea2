from django.apps import AppConfig


class CancionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'canciones'

    def ready(self):
        import canciones.signals