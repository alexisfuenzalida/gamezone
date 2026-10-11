from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistroForm


def registro(request):
    form = RegistroForm(request.POST if request.method == 'POST' else None)
    if form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, f'¡Bienvenido a GAMEZONE, {usuario.username}!')
        return redirect('torneos:lista')
    return render(request, 'registration/registro.html', {'form': form})
