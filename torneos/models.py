from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Videojuego(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    genero = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Torneo(models.Model):

    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        COMPLETO = 'COMPLETO', 'Completo'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        FINALIZADO = 'FINALIZADO', 'Finalizado'

    nombre = models.CharField(max_length=100, unique=True)
    videojuego = models.ForeignKey(Videojuego, on_delete=models.PROTECT, related_name='torneos')
    fecha = models.DateTimeField()
    max_participantes = models.PositiveIntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(128)]
    )
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.DISPONIBLE)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='torneos_creados',
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return self.nombre

    @property
    def inscritos_count(self):
        # Si la consulta ya trae el conteo anotado (annotate num_inscritos), se evita otra query
        anotado = getattr(self, 'num_inscritos', None)
        return anotado if anotado is not None else self.inscripciones.count()

    @property
    def cupos_disponibles(self):
        return max(self.max_participantes - self.inscritos_count, 0)

    @property
    def acepta_inscripciones(self):
        return (
            self.estado == self.Estado.DISPONIBLE
            and self.cupos_disponibles > 0
            and self.fecha > timezone.now()
        )

    @property
    def admite_resultados(self):
        return self.estado in (self.Estado.EN_CURSO, self.Estado.FINALIZADO)

    @property
    def inscritos_sin_resultado(self):
        return self.inscripciones.filter(resultado__isnull=True).count()

    def clean(self):
        # Al editar, no se puede dejar el máximo por debajo de los ya inscritos
        if self.pk and self.max_participantes is not None:
            inscritos = self.inscritos_count
            if self.max_participantes < inscritos:
                raise ValidationError({
                    'max_participantes': f'Ya hay {inscritos} jugadores inscritos; '
                                         f'el máximo no puede ser menor.'
                })

    def sincronizar_estado_por_cupos(self):
        """Pasa entre Disponible y Completo según los cupos. No toca En Curso ni Finalizado."""
        nuevo = self.estado
        if self.estado == self.Estado.DISPONIBLE and self.cupos_disponibles == 0:
            nuevo = self.Estado.COMPLETO
        elif self.estado == self.Estado.COMPLETO and self.cupos_disponibles > 0:
            nuevo = self.Estado.DISPONIBLE
        if nuevo != self.estado:
            self.estado = nuevo
            self.save(update_fields=['estado'])


class Inscripcion(models.Model):
    jugador = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inscripciones'
    )
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'inscripción'
        verbose_name_plural = 'inscripciones'
        ordering = ['fecha_inscripcion']
        constraints = [
            # Un jugador no puede inscribirse dos veces en el mismo torneo
            models.UniqueConstraint(
                fields=['jugador', 'torneo'], name='inscripcion_unica',
                violation_error_message='El jugador ya está inscrito en este torneo.',
            ),
        ]

    def __str__(self):
        return f'{self.jugador} en {self.torneo}'

    def clean(self):
        if self.pk or not self.torneo_id:
            return
        if self.torneo.estado != Torneo.Estado.DISPONIBLE:
            raise ValidationError('El torneo no está recibiendo inscripciones.')
        if self.torneo.fecha <= timezone.now():
            raise ValidationError('El torneo ya comenzó; las inscripciones están cerradas.')
        if self.torneo.cupos_disponibles == 0:
            raise ValidationError('El torneo no tiene cupos disponibles.')
        # La inscripción duplicada la valida la UniqueConstraint (validate_constraints)


class Resultado(models.Model):
    inscripcion = models.OneToOneField(
        Inscripcion, on_delete=models.CASCADE, related_name='resultado'
    )
    posicion = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    puntos = models.PositiveIntegerField(default=0)
    partidas_ganadas = models.PositiveIntegerField(default=0)
    partidas_jugadas = models.PositiveIntegerField(default=0)
    observacion = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['inscripcion__torneo', 'posicion']

    def __str__(self):
        return f'{self.inscripcion.jugador} - #{self.posicion} en {self.inscripcion.torneo}'

    def clean(self):
        if self.partidas_ganadas > self.partidas_jugadas:
            raise ValidationError('Las partidas ganadas no pueden superar a las jugadas.')
        if self.inscripcion_id and self.posicion and self.posicion > self.inscripcion.torneo.max_participantes:
            raise ValidationError({'posicion': 'La posición supera la cantidad de participantes.'})
