from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def solo_admin(vista):
    """Exige sesión iniciada y rol Administrador; si no, responde 403."""

    @wraps(vista)
    @login_required
    def envoltura(request, *args, **kwargs):
        if not request.user.perfil.es_admin:
            raise PermissionDenied('Solo los administradores pueden realizar esta acción.')
        return vista(request, *args, **kwargs)

    return envoltura
