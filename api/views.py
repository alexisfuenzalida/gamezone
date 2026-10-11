from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Prefetch
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from torneos import informes, servicios
from torneos.forms import FiltroTorneoForm
from torneos.models import Inscripcion, Torneo, Videojuego

from .permissions import EsAdmin, EsAdminOSoloLectura, es_admin
from .serializers import (
    InscripcionSerializer, TorneoDetalleSerializer, TorneoSerializer, VideojuegoSerializer,
)


class VideojuegoViewSet(viewsets.ModelViewSet):
    """Catálogo de videojuegos. Lectura: usuarios autenticados. Escritura: administradores."""
    queryset = Videojuego.objects.all()
    serializer_class = VideojuegoSerializer
    permission_classes = [EsAdminOSoloLectura]


class TorneoViewSet(viewsets.ModelViewSet):
    """
    CRUD de torneos.

    Filtros (query params): `q`, `videojuego`, `estado`, `fecha_desde`, `fecha_hasta`
    (AAAA-MM-DD), `min_inscritos`, `max_inscritos`, `orden` (fecha, -fecha, nombre, -num_inscritos).
    """
    permission_classes = [EsAdminOSoloLectura]

    def get_queryset(self):
        queryset = (
            Torneo.objects.select_related('videojuego', 'creado_por')
            .annotate(num_inscritos=Count('inscripciones'))
            .order_by('fecha', 'pk')
        )
        if self.action == 'list':
            filtro = FiltroTorneoForm(self.request.query_params)
            if self.request.query_params and not filtro.is_valid():
                raise ValidationError({campo: list(errores) for campo, errores in filtro.errors.items()})
            queryset = filtro.filtrar(queryset)
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(Prefetch(
                'inscripciones',
                queryset=Inscripcion.objects.select_related('jugador__perfil', 'torneo', 'resultado')
                .order_by('resultado__posicion', 'fecha_inscripcion'),
            ))
        return queryset

    def get_serializer_class(self):
        return TorneoDetalleSerializer if self.action == 'retrieve' else TorneoSerializer

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    def perform_update(self, serializer):
        torneo = serializer.save()
        torneo.sincronizar_estado_por_cupos()

    def destroy(self, request, *args, **kwargs):
        torneo = self.get_object()
        try:
            servicios.validar_eliminacion(torneo)
        except DjangoValidationError as error:
            return Response({'detail': ' '.join(error.messages)}, status=status.HTTP_409_CONFLICT)
        torneo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def inscripcion(self, request, pk=None):
        """POST: inscribe al usuario actual. DELETE: cancela su inscripción."""
        try:
            if request.method == 'POST':
                inscripcion = servicios.inscribir(request.user, pk)
                return Response(InscripcionSerializer(inscripcion).data, status=status.HTTP_201_CREATED)
            servicios.cancelar(request.user, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))
        except DjangoValidationError as error:
            raise ValidationError({'detail': error.messages})

    @action(detail=True, methods=['get'])
    def inscritos(self, request, pk=None):
        torneo = self.get_object()
        inscripciones = (
            torneo.inscripciones.select_related('jugador__perfil', 'torneo', 'resultado')
            .order_by('resultado__posicion', 'fecha_inscripcion')
        )
        return Response(InscripcionSerializer(inscripciones, many=True).data)


class InscripcionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Inscripciones: el jugador ve solo las suyas; el administrador ve todas (filtro opcional `torneo`)."""
    serializer_class = InscripcionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Inscripcion.objects.select_related('jugador__perfil', 'torneo', 'resultado')
            .order_by('-fecha_inscripcion')
        )
        if not es_admin(self.request.user):
            queryset = queryset.filter(jugador=self.request.user)
        torneo = self.request.query_params.get('torneo')
        if torneo:
            if not torneo.isdigit():
                raise ValidationError({'torneo': 'Debe ser un número entero.'})
            queryset = queryset.filter(torneo_id=torneo)
        return queryset


class InformesView(APIView):
    """Estadísticas de la plataforma (solo administradores)."""
    permission_classes = [EsAdmin]

    def get(self, request):
        return Response(informes.informe_completo())
