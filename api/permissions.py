from rest_framework.permissions import SAFE_METHODS, BasePermission


def es_admin(user):
    perfil = getattr(user, 'perfil', None)
    return bool(user and user.is_authenticated and perfil and perfil.es_admin)


class EsAdminOSoloLectura(BasePermission):
    """Lectura para cualquier usuario autenticado; escritura solo para Administradores."""
    message = 'Solo los administradores pueden modificar esta información.'

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.method in SAFE_METHODS or es_admin(request.user)


class EsAdmin(BasePermission):
    message = 'Solo los administradores pueden realizar esta acción.'

    def has_permission(self, request, view):
        return es_admin(request.user)
