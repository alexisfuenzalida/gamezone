from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone


class Videojuego(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

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
        'máximo de participantes', validators=[MinValueValidator(2), MaxValueValidator(128)]
    )
    descripcion = models.TextField('descripción', blank=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.DISPONIBLE)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return self.nombre

    @property
    def inscritos_count(self):
        # Usa el conteo anotado (annotate num_inscritos) si la consulta ya lo trae
        anotado = getattr(self, 'num_inscritos', None)
        return anotado if anotado is not None else self.inscripciones.count()

    @property
    def cupos_disponibles(self):
        return max(self.max_participantes - self.inscritos_count, 0)

    @property
    def acepta_inscripciones(self):
        return self.estado == self.Estado.DISPONIBLE and self.cupos_disponibles > 0 and self.fecha > timezone.now()

    def clean(self):
        """Validaciones de creación y edición; las usan el formulario web y la API."""
        errores = {}
        if self.nombre:
            self.nombre = ' '.join(self.nombre.split())
            if len(self.nombre) < 5:
                errores['nombre'] = 'El nombre debe tener al menos 5 caracteres.'
            elif Torneo.objects.filter(nombre__iexact=self.nombre).exclude(pk=self.pk).exists():
                errores['nombre'] = 'Ya existe un torneo con ese nombre.'
        if self.fecha:
            fecha_original = Torneo.objects.filter(pk=self.pk).values_list('fecha', flat=True).first()
            if self.fecha != fecha_original and self.fecha < timezone.now():
                errores['fecha'] = 'La fecha del torneo no puede estar en el pasado.'
        if self.pk and self.max_participantes and self.max_participantes < self.inscritos_count:
            errores['max_participantes'] = (
                f'Ya hay {self.inscritos_count} jugadores inscritos; el máximo no puede ser menor.'
            )
        if errores:
            raise ValidationError(errores)

    def actualizar_estado_por_cupos(self):
        """Pasa a Completo al llenarse y vuelve a Disponible si se libera un cupo."""
        if self.estado == self.Estado.DISPONIBLE and self.cupos_disponibles == 0:
            self.estado = self.Estado.COMPLETO
        elif self.estado == self.Estado.COMPLETO and self.cupos_disponibles > 0:
            self.estado = self.Estado.DISPONIBLE
        else:
            return
        self.save(update_fields=['estado'])

    def inscribir(self, jugador):
        """Inscribe al jugador o lanza ValidationError con el motivo."""
        with transaction.atomic():
            # Bloquea el torneo para que dos inscripciones simultáneas no superen el cupo
            torneo = Torneo.objects.select_for_update().get(pk=self.pk)
            if Inscripcion.objects.filter(torneo=torneo, jugador=jugador).exists():
                raise ValidationError('Ya estás inscrito en este torneo.')
            if not torneo.acepta_inscripciones:
                raise ValidationError('El torneo no está recibiendo inscripciones.')
            inscripcion = Inscripcion.objects.create(torneo=torneo, jugador=jugador)
            torneo.actualizar_estado_por_cupos()
        return inscripcion


class Inscripcion(models.Model):
    jugador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inscripciones')
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'inscripción'
        verbose_name_plural = 'inscripciones'
        # Un jugador no puede inscribirse dos veces en el mismo torneo (también lo asegura la BD)
        constraints = [models.UniqueConstraint(fields=['jugador', 'torneo'], name='inscripcion_unica')]

    def __str__(self):
        return f'{self.jugador} en {self.torneo}'


class Resultado(models.Model):
    inscripcion = models.OneToOneField(Inscripcion, on_delete=models.CASCADE, related_name='resultado')
    posicion = models.PositiveIntegerField('posición', validators=[MinValueValidator(1)])
    puntos = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.inscripcion.jugador} - #{self.posicion}'
