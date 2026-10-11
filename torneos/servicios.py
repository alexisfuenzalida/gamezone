"""Operaciones sobre inscripciones, usadas tanto por las vistas web como por la API REST."""
import logging

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404

from .models import Inscripcion, Torneo

logger = logging.getLogger(__name__)


def inscribir(jugador, torneo_pk):
    """Inscribe al jugador o lanza ValidationError con el motivo. Http404 si el torneo no existe."""
    if jugador.perfil.es_admin:
        raise PermissionDenied('Los administradores no pueden inscribirse en torneos.')

    with transaction.atomic():
        # Bloquea la fila del torneo para que dos inscripciones simultáneas no superen el cupo
        torneo = get_object_or_404(Torneo.objects.select_for_update(), pk=torneo_pk)
        inscripcion = Inscripcion(jugador=jugador, torneo=torneo)
        inscripcion.full_clean()
        try:
            with transaction.atomic():
                inscripcion.save()
        except IntegrityError:
            logger.warning('Inscripción duplicada bloqueada por la BD: usuario=%s torneo=%s', jugador.pk, torneo_pk)
            raise ValidationError('Ya estás inscrito en este torneo.')
    return inscripcion


def cancelar(jugador, torneo_pk):
    """Elimina la inscripción del jugador si el torneo aún no comienza."""
    inscripcion = Inscripcion.objects.filter(torneo_id=torneo_pk, jugador=jugador).select_related('torneo').first()
    if inscripcion is None:
        raise ValidationError('No tienes una inscripción en este torneo.')
    if inscripcion.torneo.estado not in (Torneo.Estado.DISPONIBLE, Torneo.Estado.COMPLETO):
        raise ValidationError('No puedes retirarte de un torneo que ya comenzó o finalizó.')
    inscripcion.delete()
    return inscripcion.torneo


def validar_eliminacion(torneo):
    if torneo.estado == Torneo.Estado.EN_CURSO:
        raise ValidationError('No se puede eliminar un torneo que está en curso.')
