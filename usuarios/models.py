from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    """Rol del usuario dentro de la plataforma."""

    class Rol(models.TextChoices):
        JUGADOR = 'JUGADOR', 'Jugador'
        ADMIN = 'ADMIN', 'Administrador'

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.JUGADOR)

    class Meta:
        verbose_name_plural = 'perfiles'

    def __str__(self):
        return f'{self.usuario.username} ({self.get_rol_display()})'

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.usuario.is_superuser


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil(sender, instance, **kwargs):
    """Todo usuario tiene un Perfil; los superusuarios quedan como Administrador."""
    rol = Perfil.Rol.ADMIN if instance.is_superuser else Perfil.Rol.JUGADOR
    Perfil.objects.get_or_create(usuario=instance, defaults={'rol': rol})
