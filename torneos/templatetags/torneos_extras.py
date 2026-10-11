from django import template

register = template.Library()

COLORES_ESTADO = {
    'DISPONIBLE': 'estado-disponible',
    'COMPLETO': 'estado-completo',
    'EN_CURSO': 'estado-en-curso',
    'FINALIZADO': 'estado-finalizado',
}


@register.filter
def clase_estado(estado):
    """Devuelve la clase CSS del badge según el estado del torneo."""
    return COLORES_ESTADO.get(estado, 'estado-finalizado')


@register.filter
def porcentaje(valor, total):
    """Porcentaje entero (0-100) para barras de progreso."""
    try:
        return min(round(int(valor) * 100 / int(total)), 100)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0


@register.filter
def es_admin(user):
    # getattr: en páginas de error el contexto puede venir sin usuario
    if not getattr(user, 'is_authenticated', False):
        return False
    perfil = getattr(user, 'perfil', None)
    return bool(perfil and perfil.es_admin)
