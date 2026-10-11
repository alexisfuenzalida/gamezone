from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from torneos.forms import FiltroTorneoForm
from torneos.models import Torneo

from .permissions import EsAdminOSoloLectura
from .serializers import TorneoSerializer


class TorneoViewSet(viewsets.ModelViewSet):
    """
    CRUD de torneos. Lectura: usuarios autenticados. Escritura: administradores.
    Filtros: ?videojuego=<id>&estado=<ESTADO>&fecha=<AAAA-MM-DD>&min_inscritos=<n>
    """
    serializer_class = TorneoSerializer
    permission_classes = [EsAdminOSoloLectura]

    def get_queryset(self):
        torneos = Torneo.objects.select_related('videojuego').annotate(num_inscritos=Count('inscripciones')).order_by('fecha')
        return FiltroTorneoForm(self.request.query_params).filtrar(torneos)

    def perform_update(self, serializer):
        serializer.save().actualizar_estado_por_cupos()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def inscribirse(self, request, pk=None):
        torneo = self.get_object()
        if request.user.perfil.es_admin:
            raise PermissionDenied('Los administradores no pueden inscribirse en torneos.')
        try:
            torneo.inscribir(request.user)
        except DjangoValidationError as error:
            raise ValidationError({'detail': error.messages[0]})
        return Response({'detail': f'Inscripción confirmada en "{torneo.nombre}".'}, status=status.HTTP_201_CREATED)
