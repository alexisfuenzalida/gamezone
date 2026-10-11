from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistroForm


def registro(request):
    if request.user.is_authenticated:
        return redirect('torneos:inicio')

    form = RegistroForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, f'¡Bienvenido a GAMEZONE, {usuario.perfil}! Ya puedes inscribirte en torneos.')
        return redirect('torneos:lista')
    return render(request, 'registration/registro.html', {'form': form})
