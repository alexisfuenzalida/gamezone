from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from usuarios.decorators import solo_admin

from . import informes
from .forms import FiltroTorneoForm, ResultadoForm, TorneoForm
from .models import Resultado, Torneo


def torneos_con_inscritos():
    # order_by explícito: Django no aplica Meta.ordering en consultas con agregados
    return Torneo.objects.select_related('videojuego').annotate(num_inscritos=Count('inscripciones')).order_by('fecha')


def inicio(request):
    torneos = torneos_con_inscritos()
    return render(request, 'torneos/inicio.html', {
        'resumen': informes.resumen(),
        'proximos': torneos.filter(estado__in=['DISPONIBLE', 'COMPLETO'], fecha__gte=timezone.now())[:6],
        'en_curso': torneos.filter(estado=Torneo.Estado.EN_CURSO)[:4],
    })


def lista(request):
    filtro = FiltroTorneoForm(request.GET or None)
    return render(request, 'torneos/lista.html', {
        'filtro': filtro,
        'torneos': filtro.filtrar(torneos_con_inscritos()),
    })


def detalle(request, pk):
    torneo = get_object_or_404(torneos_con_inscritos(), pk=pk)
    inscripciones = torneo.inscripciones.select_related('jugador', 'resultado').order_by('resultado__posicion')
    return render(request, 'torneos/detalle.html', {
        'torneo': torneo,
        'inscripciones': inscripciones,
        'inscrito': any(i.jugador_id == request.user.id for i in inscripciones),
    })


@solo_admin
def crear(request):
    form = TorneoForm(request.POST if request.method == 'POST' else None)
    if form.is_valid():
        torneo = form.save()
        messages.success(request, f'Torneo "{torneo.nombre}" creado.')
        return redirect('torneos:detalle', pk=torneo.pk)
    return render(request, 'torneos/form.html', {'form': form, 'titulo': 'Nuevo torneo'})


@solo_admin
def editar(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    form = TorneoForm(request.POST if request.method == 'POST' else None, instance=torneo)
    if form.is_valid():
        form.save().actualizar_estado_por_cupos()
        messages.success(request, 'Torneo actualizado.')
        return redirect('torneos:detalle', pk=pk)
    return render(request, 'torneos/form.html', {'form': form, 'titulo': f'Editar: {torneo.nombre}'})


@solo_admin
def eliminar(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    if request.method == 'POST':
        torneo.delete()
        messages.success(request, f'Torneo "{torneo.nombre}" eliminado.')
        return redirect('torneos:lista')
    return render(request, 'torneos/confirmar_eliminar.html', {'torneo': torneo})


@login_required
@require_POST
def inscribirse(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    if request.user.perfil.es_admin:
        messages.error(request, 'Los administradores no pueden inscribirse en torneos.')
    else:
        try:
            torneo.inscribir(request.user)
            messages.success(request, f'¡Te inscribiste en "{torneo.nombre}"!')
        except ValidationError as error:
            messages.error(request, error.messages[0])
    return redirect('torneos:detalle', pk=pk)


@solo_admin
def resultados(request, pk):
    """Registra la posición y los puntos de cada inscrito."""
    torneo = get_object_or_404(Torneo, pk=pk)
    datos = request.POST if request.method == 'POST' else None
    filas = []
    for inscripcion in torneo.inscripciones.select_related('jugador'):
        instancia = getattr(inscripcion, 'resultado', None) or Resultado(inscripcion=inscripcion)
        filas.append((inscripcion, ResultadoForm(datos, instance=instancia, prefix=f'r{inscripcion.pk}')))

    if request.method == 'POST' and all([form.is_valid() for _, form in filas]):
        for _, form in filas:
            form.save()
        messages.success(request, 'Resultados guardados.')
        return redirect('torneos:detalle', pk=pk)
    return render(request, 'torneos/resultados.html', {'torneo': torneo, 'filas': filas})


@solo_admin
def informes_view(request):
    return render(request, 'torneos/informes.html', informes.informe_completo())
