from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.views import exception_handler


def manejador_errores(exc, context):
    """Igual al de DRF, pero el 404 responde un mensaje en español en vez del texto interno de Django."""
    if isinstance(exc, Http404):
        exc = NotFound('El recurso solicitado no existe.')
    return exception_handler(exc, context)
