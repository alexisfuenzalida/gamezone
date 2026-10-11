from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from torneos.models import Torneo


class TorneoSerializer(serializers.ModelSerializer):
    videojuego_nombre = serializers.CharField(source='videojuego.nombre', read_only=True)
    inscritos = serializers.IntegerField(source='inscritos_count', read_only=True)
    cupos_disponibles = serializers.IntegerField(read_only=True)

    class Meta:
        model = Torneo
        fields = ['id', 'nombre', 'videojuego', 'videojuego_nombre', 'fecha', 'max_participantes',
                  'descripcion', 'estado', 'inscritos', 'cupos_disponibles']

    def validate(self, datos):
        # Reutiliza las validaciones del modelo (Torneo.clean), las mismas del formulario web
        torneo = Torneo(**datos) if self.instance is None else self.instance
        if self.instance is not None:
            for campo, valor in datos.items():
                setattr(torneo, campo, valor)
        try:
            torneo.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict)
        datos['nombre'] = torneo.nombre  # nombre normalizado por clean()
        return datos
