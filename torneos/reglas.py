"""Reglas de negocio de los torneos, compartidas por los formularios web y la API REST."""
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Torneo


def normalizar_nombre(nombre, excluir_pk=None):
    """Quita espacios sobrantes y valida largo mínimo y unicidad (sin importar mayúsculas)."""
    nombre = ' '.join(nombre.split())
    if len(nombre) < 5:
        raise ValidationError('El nombre debe tener al menos 5 caracteres.')
    if Torneo.objects.filter(nombre__iexact=nombre).exclude(pk=excluir_pk).exists():
        raise ValidationError('Ya existe un torneo con ese nombre.')
    return nombre


def validar_fecha(fecha, torneo=None):
    """La fecha no puede quedar en el pasado (si al editar no cambia, se acepta)."""
    cambio_fecha = torneo is None or torneo.pk is None or fecha != torneo.fecha
    if cambio_fecha and fecha < timezone.now():
        raise ValidationError('La fecha del torneo no puede estar en el pasado.')
    return fecha


def errores_estado(torneo, estado, maximo):
    """Devuelve la lista de motivos por los que `torneo` no puede pasar a `estado`."""
    errores = []
    inscritos = torneo.inscritos_count
    if estado == Torneo.Estado.DISPONIBLE and inscritos >= maximo:
        errores.append('No puede quedar Disponible: no hay cupos libres.')
    if estado == Torneo.Estado.COMPLETO and inscritos < maximo:
        errores.append(f'Solo queda Completo al llenarse los cupos ({inscritos}/{maximo}).')
    if estado in (Torneo.Estado.EN_CURSO, Torneo.Estado.FINALIZADO) and inscritos < 2:
        errores.append('Se necesitan al menos 2 jugadores inscritos para iniciar o finalizar el torneo.')
    if estado == Torneo.Estado.FINALIZADO and torneo.estado != Torneo.Estado.FINALIZADO:
        pendientes = torneo.inscritos_sin_resultado
        if pendientes:
            errores.append(f'Para finalizar, registra los resultados de todos los jugadores (faltan {pendientes}).')
    if torneo.estado == Torneo.Estado.FINALIZADO and estado != Torneo.Estado.FINALIZADO:
        errores.append('Un torneo finalizado no puede volver a un estado anterior.')
    return errores
