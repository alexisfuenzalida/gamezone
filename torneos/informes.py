"""Estadísticas de la plataforma, calculadas con consultas agregadas."""
from django.db.models import Count, F, Q, Sum

from .models import Resultado, Torneo


def resumen():
    por_estado = dict(Torneo.objects.values_list('estado').annotate(n=Count('id')))
    return {
        'total': sum(por_estado.values()),
        'disponibles': por_estado.get(Torneo.Estado.DISPONIBLE, 0),
        'en_curso': por_estado.get(Torneo.Estado.EN_CURSO, 0),
        'finalizados': por_estado.get(Torneo.Estado.FINALIZADO, 0),
        # Realizados = ya comenzaron (En Curso + Finalizado)
        'realizados': por_estado.get(Torneo.Estado.EN_CURSO, 0) + por_estado.get(Torneo.Estado.FINALIZADO, 0),
    }


def informe_completo():
    inscritos_por_torneo = (
        Torneo.objects.select_related('videojuego')
        .annotate(num_inscritos=Count('inscripciones'))
        .order_by('-num_inscritos', 'fecha')
    )
    ranking = (
        Resultado.objects.values(jugador=F('inscripcion__jugador__username'))
        .annotate(puntos=Sum('puntos'), torneos=Count('id'), victorias=Count('id', filter=Q(posicion=1)))
        .order_by('-puntos', '-victorias')[:10]
    )
    return {
        'resumen': resumen(),
        'inscritos_por_torneo': inscritos_por_torneo,
        'mayor_participacion': inscritos_por_torneo[:5],
        'ranking': ranking,
    }
