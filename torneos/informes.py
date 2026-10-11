"""Cálculo de estadísticas de la plataforma, usado por la página de informes y por la API."""
from django.contrib.auth.models import User
from django.db.models import Avg, Count, F, FloatField, Q, Sum
from django.db.models.functions import Cast

from usuarios.models import Perfil

from .models import Inscripcion, Resultado, Torneo, Videojuego


def _porcentaje(parte, total):
    return round(parte * 100 / total) if total else 0


def resumen_general():
    por_estado = dict(
        Torneo.objects.values_list('estado').annotate(n=Count('id')).values_list('estado', 'n')
    )
    total = sum(por_estado.values())
    inscripciones = Inscripcion.objects.count()
    capacidad = Torneo.objects.aggregate(total=Sum('max_participantes'))['total'] or 0
    return {
        'torneos': total,
        'realizados': por_estado.get(Torneo.Estado.EN_CURSO, 0) + por_estado.get(Torneo.Estado.FINALIZADO, 0),
        'finalizados': por_estado.get(Torneo.Estado.FINALIZADO, 0),
        'por_estado': [
            {'estado': valor, 'nombre': nombre, 'total': por_estado.get(valor, 0)}
            for valor, nombre in Torneo.Estado.choices
        ],
        'jugadores': User.objects.filter(perfil__rol=Perfil.Rol.JUGADOR).count(),
        'inscripciones': inscripciones,
        'promedio_inscritos': round(inscripciones / total, 1) if total else 0,
        'ocupacion_promedio': _porcentaje(inscripciones, capacidad),
    }


def inscritos_por_torneo(limite=None):
    """Torneos ordenados por cantidad de inscritos (mayor participación primero)."""
    torneos = (
        Torneo.objects.select_related('videojuego')
        .annotate(num_inscritos=Count('inscripciones'))
        .order_by('-num_inscritos', 'fecha')
    )
    if limite:
        torneos = torneos[:limite]
    return [
        {
            'id': t.pk,
            'nombre': t.nombre,
            'videojuego': t.videojuego.nombre,
            'estado': t.estado,
            'estado_display': t.get_estado_display(),
            'inscritos': t.num_inscritos,
            'max_participantes': t.max_participantes,
            'ocupacion': _porcentaje(t.num_inscritos, t.max_participantes),
        }
        for t in torneos
    ]


def participacion_por_videojuego():
    juegos = (
        Videojuego.objects.annotate(
            num_torneos=Count('torneos', distinct=True),
            num_inscritos=Count('torneos__inscripciones'),
        )
        .filter(num_torneos__gt=0)
        .order_by('-num_inscritos', 'nombre')
    )
    return [{'videojuego': j.nombre, 'torneos': j.num_torneos, 'inscritos': j.num_inscritos} for j in juegos]


def ranking_jugadores(limite=10):
    """Jugadores con mejores resultados: puntos totales, luego victorias y podios."""
    filas = (
        Resultado.objects.values(
            usuario=F('inscripcion__jugador__username'),
            nickname=F('inscripcion__jugador__perfil__nickname'),
        )
        .annotate(
            torneos=Count('id'),
            puntos=Sum('puntos'),
            victorias=Count('id', filter=Q(posicion=1)),
            podios=Count('id', filter=Q(posicion__lte=3)),
            ganadas=Sum('partidas_ganadas'),
            jugadas=Sum('partidas_jugadas'),
            posicion_promedio=Avg(Cast('posicion', FloatField())),
        )
        .order_by('-puntos', '-victorias', '-podios', 'posicion_promedio', 'usuario')[:limite]
    )
    return [
        {
            'jugador': f['nickname'] or f['usuario'],
            'torneos': f['torneos'],
            'puntos': f['puntos'] or 0,
            'victorias': f['victorias'],
            'podios': f['podios'],
            'partidas_ganadas': f['ganadas'] or 0,
            'partidas_jugadas': f['jugadas'] or 0,
            'efectividad': _porcentaje(f['ganadas'] or 0, f['jugadas'] or 0),
            'posicion_promedio': round(f['posicion_promedio'], 1),
        }
        for f in filas
    ]


def informe_completo():
    por_torneo = inscritos_por_torneo()
    return {
        'resumen': resumen_general(),
        'inscritos_por_torneo': por_torneo,
        'mayor_participacion': por_torneo[:5],
        'por_videojuego': participacion_por_videojuego(),
        'ranking_jugadores': ranking_jugadores(),
    }
