from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Cancion, Usuario 
#Aprender bien
@receiver(pre_delete, sender=Usuario)
def borrar_canciones_relacionadas(sender, instance, **kwargs): 
    canciones = Cancion.objects.filter( 
        id__in = instance.tiene.values_list('cancion_id', flat=True)
    )
    canciones.delete()