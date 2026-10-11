from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from torneos.models import Inscripcion, Resultado, Torneo, Videojuego
from usuarios.models import Perfil

PASSWORD_DEMO = 'Gamezone2026!'

VIDEOJUEGOS = [
    ('League of Legends', 'MOBA'),
    ('Valorant', 'Shooter táctico'),
    ('EA Sports FC 26', 'Deportes'),
    ('Street Fighter 6', 'Pelea'),
    ('Rocket League', 'Deportes'),
]

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
    help = 'Carga datos de demostración (videojuegos, usuarios, torneos, inscripciones y resultados).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reiniciar', action='store_true',
            help='Borra TODOS los torneos (con sus inscripciones y resultados) y los vuelve a crear '
                 'con fechas relativas a hoy. Útil antes de una demostración.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reiniciar']:
            borrados = Torneo.objects.count()
            Torneo.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Se eliminaron {borrados} torneos existentes.'))

        juegos = {
            nombre: Videojuego.objects.get_or_create(nombre=nombre, defaults={'genero': genero})[0]
            for nombre, genero in VIDEOJUEGOS
        }

        admin = self._usuario('admin_demo', Perfil.Rol.ADMIN, 'AdminGZ', superusuario=True)
        jugadores = [self._usuario(nick, Perfil.Rol.JUGADOR, nick) for nick in JUGADORES]

        ahora = timezone.localtime().replace(minute=0, second=0, microsecond=0)
        for nombre, juego, dias, maximo, estado, inscritos in TORNEOS:
            torneo, creado = Torneo.objects.get_or_create(nombre=nombre, defaults={
                'videojuego': juegos[juego],
                'fecha': ahora + timedelta(days=dias, hours=19 - ahora.hour),
                'max_participantes': maximo,
                'descripcion': f'Torneo de {juego} organizado por GAMEZONE. Formato eliminación directa.',
                'creado_por': admin,
            })
            if not creado:
                continue
            for jugador in jugadores[:inscritos]:
                Inscripcion.objects.create(jugador=jugador, torneo=torneo)
            torneo.refresh_from_db()
            if estado in (Torneo.Estado.EN_CURSO, Torneo.Estado.FINALIZADO):
                torneo.estado = estado
                torneo.save(update_fields=['estado'])
            if estado == Torneo.Estado.FINALIZADO:
                for posicion, inscripcion in enumerate(torneo.inscripciones.all(), start=1):
                    jugadas = 3
                    Resultado.objects.create(
                        inscripcion=inscripcion,
                        posicion=posicion,
                        puntos=max(100 - (posicion - 1) * 15, 10),
                        partidas_jugadas=jugadas,
                        partidas_ganadas=max(jugadas - posicion + 1, 0),
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Datos demo listos: {Torneo.objects.count()} torneos, {len(jugadores)} jugadores. '
            f'Usuarios: admin_demo / jugadores ({", ".join(JUGADORES[:2])}...) - clave: {PASSWORD_DEMO}'
        ))

    def _usuario(self, username, rol, nickname, superusuario=False):
        usuario, creado = User.objects.get_or_create(
            username=username, defaults={'is_staff': superusuario, 'is_superuser': superusuario},
        )
        if creado:
            usuario.set_password(PASSWORD_DEMO)
            usuario.save()
        Perfil.objects.filter(usuario=usuario).update(rol=rol, nickname=nickname)
        usuario.refresh_from_db()
        return usuario
