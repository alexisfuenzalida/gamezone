"""Rutas principales del proyecto GAMEZONE."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('cuentas/', include('usuarios.urls')),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('', include('torneos.urls')),
]
