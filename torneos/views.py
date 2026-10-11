import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from usuarios.decorators import solo_admin
from usuarios.models import Perfil

from . import informes, servicios
from .forms import FiltroTorneoForm, ResultadoForm, TorneoForm, validar_posiciones_unicas
from .models import Inscripcion, Resultado, Torneo

logger = logging.getLogger(__name__)


def _torneos_con_inscritos():
    # order_by explícito: Django no aplica Meta.ordering en consultas con agregados
    return (
        Torneo.objects.select_related('videojuego')
        .annotate(num_inscritos=Count('inscripciones'))
        .order_by('fecha')
    )


def inicio(request):
    """Página de inicio: resumen general y próximos torneos."""
    conteo_estados = dict(
        Torneo.objects.values_list('estado').annotate(total=Count('id')).values_list('estado', 'total')
    )
    resumen = {
        'total': sum(conteo_estados.values()),
        'disponibles': conteo_estados.get(Torneo.Estado.DISPONIBLE, 0),
        'en_curso': conteo_estados.get(Torneo.Estado.EN_CURSO, 0),
        'finalizados': conteo_estados.get(Torneo.Estado.FINALIZADO, 0),
        'jugadores': User.objects.filter(perfil__rol=Perfil.Rol.JUGADOR).count(),
    }

    con_inscritos = _torneos_con_inscritos()
    proximos = con_inscritos.filter(
        estado__in=[Torneo.Estado.DISPONIBLE, Torneo.Estado.COMPLETO],
        fecha__gte=timezone.now(),
    )[:6]
    en_curso = con_inscritos.filter(estado=Torneo.Estado.EN_CURSO)[:4]

    return render(request, 'torneos/inicio.html', {
        'resumen': resumen,
        'proximos': proximos,
        'en_curso': en_curso,
    })


def lista(request):
    """Listado de torneos con filtros por videojuego, fecha, estado y participantes."""
    filtro = FiltroTorneoForm(request.GET or None)
    torneos = filtro.filtrar(_torneos_con_inscritos())

    pagina = Paginator(torneos, 9).get_page(request.GET.get('pagina'))
    parametros = request.GET.copy()
    parametros.pop('pagina', None)

    return render(request, 'torneos/lista.html', {
        'filtro': filtro,
        'pagina': pagina,
        'parametros': parametros.urlencode(),
        'hay_filtros': any(v for k, v in request.GET.items() if k not in ('pagina', 'orden')),
    })


def detalle(request, pk):
    torneo = get_object_or_404(_torneos_con_inscritos(), pk=pk)
    inscripciones = (
        torneo.inscripciones.select_related('jugador__perfil', 'resultado')
        .order_by('resultado__posicion', 'fecha_inscripcion')
    )
    mi_inscripcion = None
    if request.user.is_authenticated:
        mi_inscripcion = next((i for i in inscripciones if i.jugador_id == request.user.id), None)
    return render(request, 'torneos/detalle.html', {
        'torneo': torneo,
        'inscripciones': inscripciones,
        'mi_inscripcion': mi_inscripcion,
    })


@solo_admin
def crear(request):
    form = TorneoForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        torneo = form.save(commit=False)
        torneo.creado_por = request.user
        torneo.save()
        messages.success(request, f'Torneo "{torneo.nombre}" creado correctamente.')
        return redirect('torneos:detalle', pk=torneo.pk)
    if request.method == 'POST':
        messages.error(request, 'Revisa los campos marcados en rojo.')
    return render(request, 'torneos/form.html', {'form': form, 'titulo': 'Nuevo torneo'})


@solo_admin
def editar(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    form = TorneoForm(request.POST if request.method == 'POST' else None, instance=torneo)
    if request.method == 'POST' and form.is_valid():
        torneo = form.save()
        # Si cambió el máximo, el estado Disponible/Completo se recalcula
        torneo.sincronizar_estado_por_cupos()
        messages.success(request, f'Torneo "{torneo.nombre}" actualizado.')
        return redirect('torneos:detalle', pk=torneo.pk)
    if request.method == 'POST':
        messages.error(request, 'Revisa los campos marcados en rojo.')
    return render(request, 'torneos/form.html', {
        'form': form, 'torneo': torneo, 'titulo': f'Editar: {torneo.nombre}',
    })


@solo_admin
@require_http_methods(['GET', 'POST'])
def eliminar(request, pk):
    torneo = get_object_or_404(_torneos_con_inscritos(), pk=pk)
    try:
        servicios.validar_eliminacion(torneo)
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
        return redirect('torneos:detalle', pk=torneo.pk)
    if request.method == 'POST':
        nombre = torneo.nombre
        torneo.delete()
        logger.info('Torneo "%s" (id=%s) eliminado por %s', nombre, pk, request.user)
        messages.success(request, f'Torneo "{nombre}" eliminado.')
        return redirect('torneos:lista')
    return render(request, 'torneos/confirmar_eliminar.html', {'torneo': torneo})


# ---------- Inscripciones ----------

@login_required
@require_POST
def inscribirse(request, pk):
    try:
        inscripcion = servicios.inscribir(request.user, pk)
    except (ValidationError, PermissionDenied) as error:
        messages.error(request, ' '.join(getattr(error, 'messages', [str(error)])))
    else:
        messages.success(request, f'¡Inscripción confirmada en "{inscripcion.torneo.nombre}"!')
    return redirect('torneos:detalle', pk=pk)


@login_required
@require_POST
def cancelar_inscripcion(request, pk):
    try:
        servicios.cancelar(request.user, pk)
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
    else:
        messages.success(request, 'Tu inscripción fue cancelada.')
    return redirect('torneos:detalle', pk=pk)


@solo_admin
@require_POST
def quitar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion.objects.select_related('torneo', 'jugador__perfil'), pk=pk)
    torneo = inscripcion.torneo
    if torneo.estado == Torneo.Estado.FINALIZADO:
        messages.error(request, 'No se pueden quitar jugadores de un torneo finalizado.')
    else:
        inscripcion.delete()
        messages.success(request, f'{inscripcion.jugador.perfil} fue retirado de "{torneo.nombre}".')
    return redirect('torneos:detalle', pk=torneo.pk)


@login_required
def mis_torneos(request):
    inscripciones = (
        Inscripcion.objects.filter(jugador=request.user)
        .select_related('torneo__videojuego', 'resultado')
        .order_by('-torneo__fecha')
    )
    return render(request, 'torneos/mis_torneos.html', {'inscripciones': inscripciones})


# ---------- Resultados ----------

@solo_admin
def resultados(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    if not torneo.admite_resultados:
        messages.error(request, 'Solo se registran resultados de torneos En Curso o Finalizados.')
        return redirect('torneos:detalle', pk=pk)

    inscripciones = list(torneo.inscripciones.select_related('jugador__perfil', 'resultado'))
    datos = request.POST if request.method == 'POST' else None
    filas = []
    for inscripcion in inscripciones:
        try:
            instancia = inscripcion.resultado
        except Resultado.DoesNotExist:
            instancia = Resultado(inscripcion=inscripcion)
        filas.append((inscripcion, ResultadoForm(datos, instance=instancia, prefix=f'r{inscripcion.pk}')))

    if request.method == 'POST':
        formularios = [form for _, form in filas]
        validos = all([form.is_valid() for form in formularios])  # lista: valida todos, no se corta
        if validos and validar_posiciones_unicas(formularios):
            with transaction.atomic():
                for form in formularios:
                    form.save()
                if request.POST.get('finalizar') and torneo.estado == Torneo.Estado.EN_CURSO:
                    torneo.estado = Torneo.Estado.FINALIZADO
                    torneo.save(update_fields=['estado'])
            messages.success(request, 'Resultados guardados.'
                             + (' El torneo quedó Finalizado.' if torneo.estado == Torneo.Estado.FINALIZADO else ''))
            return redirect('torneos:detalle', pk=pk)
        messages.error(request, 'Revisa los resultados marcados en rojo.')

    return render(request, 'torneos/resultados.html', {'torneo': torneo, 'filas': filas})


# ---------- Informes ----------

@solo_admin
def informes_view(request):
    datos = informes.informe_completo()
    # Escalas para las barras: el valor más alto ocupa el 100% del ancho
    datos['max_participacion'] = max((t['inscritos'] for t in datos['mayor_participacion']), default=0)
    datos['max_videojuego'] = max((v['inscritos'] for v in datos['por_videojuego']), default=0)
    r = datos['resumen']
    datos['kpis'] = [
        ('Torneos totales', r['torneos'], 'bi-trophy'),
        ('Torneos realizados', r['realizados'], 'bi-flag'),
        ('Torneos finalizados', r['finalizados'], 'bi-check2-circle'),
        ('Jugadores registrados', r['jugadores'], 'bi-people'),
        ('Inscripciones', r['inscripciones'], 'bi-ticket-perforated'),
        ('Promedio por torneo', r['promedio_inscritos'], 'bi-person-lines-fill'),
        ('Ocupación promedio', f"{r['ocupacion_promedio']}%", 'bi-pie-chart'),
        ('Jugadores en ranking', len(datos['ranking_jugadores']), 'bi-bar-chart-steps'),
    ]
    return render(request, 'torneos/informes.html', datos)
