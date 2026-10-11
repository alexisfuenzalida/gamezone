from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from torneos.models import Inscripcion, Resultado, Torneo, Videojuego
from usuarios.models import Perfil

PASSWORD_DEMO = 'Gamezone2026!'
JUGADORES = ['shadowfox', 'pixelqueen', 'n00bmaster', 'lagkiller', 'curicoace', 'frostbyte', 'neonviper', 'zerocool']

# (nombre, videojuego, días desde hoy, máximo, estado, cantidad de inscritos)
TORNEOS = [
    ('Copa Invierno LoL', 'League of Legends', 12, 8, 'DISPONIBLE', 3),
    ('Valorant Clash Curicó', 'Valorant', 7, 4, 'DISPONIBLE', 4),
    ('FC Masters Primavera', 'EA Sports FC 26', 20, 16, 'DISPONIBLE', 5),
    ('Street Fighter Showdown', 'Street Fighter 6', 3, 8, 'DISPONIBLE', 1),
    ('Rocket League Rumble', 'Rocket League', 0, 6, 'EN_CURSO', 6),
    ('Liga Relámpago Valorant', 'Valorant', -15, 8, 'FINALIZADO', 8),
    ('Torneo Apertura LoL', 'League of Legends', -40, 4, 'FINALIZADO', 4),
]


class Command(BaseCommand):
    help = 'Carga datos de demostración. Con --reiniciar borra y recrea todos los torneos con fechas desde hoy.'

    def add_arguments(self, parser):
        parser.add_argument('--reiniciar', action='store_true', help='Borra TODOS los torneos antes de cargar.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reiniciar']:
            Torneo.objects.all().delete()

        self._usuario('admin_demo', admin=True)
        jugadores = [self._usuario(nombre) for nombre in JUGADORES]

        hoy_19h = timezone.localtime().replace(hour=19, minute=0, second=0, microsecond=0)
        for nombre, juego, dias, maximo, estado, inscritos in TORNEOS:
            torneo, creado = Torneo.objects.get_or_create(nombre=nombre, defaults={
                'videojuego': Videojuego.objects.get_or_create(nombre=juego)[0],
                'fecha': hoy_19h + timedelta(days=dias),
                'max_participantes': maximo,
                'descripcion': f'Torneo de {juego} organizado por GAMEZONE.',
            })
            if not creado:
                continue
            for posicion, jugador in enumerate(jugadores[:inscritos], start=1):
                inscripcion = Inscripcion.objects.create(jugador=jugador, torneo=torneo)
                if estado == 'FINALIZADO':
                    Resultado.objects.create(inscripcion=inscripcion, posicion=posicion,
                                             puntos=max(100 - (posicion - 1) * 15, 10))
            torneo.actualizar_estado_por_cupos()
            if estado != 'DISPONIBLE':
                Torneo.objects.filter(pk=torneo.pk).update(estado=estado)

        self.stdout.write(self.style.SUCCESS(
            f'Datos demo listos: {Torneo.objects.count()} torneos. Usuarios: admin_demo y '
            f'{", ".join(JUGADORES[:2])}... (clave: {PASSWORD_DEMO})'
        ))

    def _usuario(self, username, admin=False):
        usuario, creado = User.objects.get_or_create(
            username=username, defaults={'is_staff': admin, 'is_superuser': admin},
        )
        if creado:
            usuario.set_password(PASSWORD_DEMO)
            usuario.save()
        Perfil.objects.filter(usuario=usuario).update(rol=Perfil.Rol.ADMIN if admin else Perfil.Rol.JUGADOR)
        return usuario
