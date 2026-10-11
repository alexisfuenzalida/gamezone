from rest_framework.permissions import SAFE_METHODS, BasePermission


class EsAdminOSoloLectura(BasePermission):
    """Lectura para cualquier usuario autenticado; escritura solo para Administradores."""
    message = 'Solo los administradores pueden modificar torneos.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.method in SAFE_METHODS or request.user.perfil.es_admin
