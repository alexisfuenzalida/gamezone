from django import forms, template

register = template.Library()


@register.filter
def clase_estado(estado):
    """Clase CSS del badge según el estado del torneo (DISPONIBLE -> estado-disponible)."""
    return 'estado-' + estado.lower().replace('_', '-')


@register.filter
def porcentaje(valor, total):
    try:
        return min(round(int(valor) * 100 / int(total)), 100)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0


@register.filter
def es_admin(user):
    perfil = getattr(user, 'perfil', None)
    return bool(getattr(user, 'is_authenticated', False) and perfil and perfil.es_admin)


@register.filter
def bootstrap(campo):
    """Dibuja el campo con las clases de Bootstrap y lo marca en rojo si tiene errores."""
    clase = 'form-select' if isinstance(campo.field.widget, forms.Select) else 'form-control'
    if campo.errors:
        clase += ' is-invalid'
    return campo.as_widget(attrs={'class': clase})
