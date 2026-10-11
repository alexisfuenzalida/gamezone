from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """Datos extra del usuario: rol dentro de la plataforma y nickname gamer."""

    class Rol(models.TextChoices):
        JUGADOR = 'JUGADOR', 'Jugador'
        ADMIN = 'ADMIN', 'Administrador'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil'
    )
    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.JUGADOR)
    nickname = models.CharField(max_length=30, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'

    def __str__(self):
        return self.nickname or self.usuario.username

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.usuario.is_superuser
