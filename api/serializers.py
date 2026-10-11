from rest_framework import serializers

from torneos import reglas
from torneos.models import Inscripcion, Resultado, Torneo, Videojuego


class VideojuegoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videojuego
        fields = ['id', 'nombre', 'genero']


class ResultadoSerializer(serializers.ModelSerializer):
    jugador = serializers.CharField(source='inscripcion.jugador.perfil', read_only=True)

    class Meta:
        model = Resultado
        fields = ['jugador', 'posicion', 'puntos', 'partidas_ganadas', 'partidas_jugadas', 'observacion']


class InscripcionSerializer(serializers.ModelSerializer):
    jugador = serializers.CharField(source='jugador.perfil', read_only=True)
    torneo_nombre = serializers.CharField(source='torneo.nombre', read_only=True)
    resultado = serializers.SerializerMethodField()

    class Meta:
        model = Inscripcion
        fields = ['id', 'jugador', 'torneo', 'torneo_nombre', 'fecha_inscripcion', 'resultado']
        read_only_fields = fields

    def get_resultado(self, obj):
        try:
            return ResultadoSerializer(obj.resultado).data
        except Resultado.DoesNotExist:
            return None


class TorneoSerializer(serializers.ModelSerializer):
    videojuego_nombre = serializers.CharField(source='videojuego.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    inscritos = serializers.IntegerField(source='inscritos_count', read_only=True)
    cupos_disponibles = serializers.IntegerField(read_only=True)
    acepta_inscripciones = serializers.BooleanField(read_only=True)
    creado_por = serializers.CharField(source='creado_por.username', read_only=True, default=None)

    class Meta:
        model = Torneo
        fields = [
            'id', 'nombre', 'videojuego', 'videojuego_nombre', 'fecha', 'max_participantes',
            'descripcion', 'estado', 'estado_display', 'inscritos', 'cupos_disponibles',
            'acepta_inscripciones', 'creado_por', 'creado_en',
        ]
        read_only_fields = ['creado_en']

    def validate_nombre(self, valor):
        return reglas.normalizar_nombre(valor, excluir_pk=getattr(self.instance, 'pk', None))

    def validate_fecha(self, valor):
        return reglas.validar_fecha(valor, self.instance)

    def validate(self, datos):
        torneo = self.instance
        if torneo is None:
            # Al crear, el torneo siempre parte Disponible
            if datos.get('estado', Torneo.Estado.DISPONIBLE) != Torneo.Estado.DISPONIBLE:
                raise serializers.ValidationError({'estado': 'Un torneo nuevo debe partir Disponible.'})
            return datos

        maximo = datos.get('max_participantes', torneo.max_participantes)
        if maximo < torneo.inscritos_count:
            raise serializers.ValidationError({
                'max_participantes': f'Ya hay {torneo.inscritos_count} jugadores inscritos; el máximo no puede ser menor.'
            })
        if 'estado' in datos:
            errores = reglas.errores_estado(torneo, datos['estado'], maximo)
            if errores:
                raise serializers.ValidationError({'estado': errores})
        return datos


class TorneoDetalleSerializer(TorneoSerializer):
    """Detalle con los jugadores inscritos y sus resultados."""
    inscripciones = InscripcionSerializer(many=True, read_only=True)

    class Meta(TorneoSerializer.Meta):
        fields = TorneoSerializer.Meta.fields + ['inscripciones']
