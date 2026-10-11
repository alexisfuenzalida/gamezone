from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Inscripcion, Torneo


@receiver(post_save, sender=Inscripcion)
@receiver(post_delete, sender=Inscripcion)
def actualizar_estado_torneo(sender, instance, **kwargs):
    """Cada alta o baja de inscripción recalcula si el torneo queda Completo o Disponible."""
    try:
        torneo = Torneo.objects.get(pk=instance.torneo_id)
    except Torneo.DoesNotExist:  # el torneo se está eliminando en cascada
        return
    torneo.sincronizar_estado_por_cupos()
