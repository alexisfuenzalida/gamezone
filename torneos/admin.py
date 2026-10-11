from django.contrib import admin

from .models import Inscripcion, Resultado, Torneo, Videojuego

admin.site.register(Videojuego)
admin.site.register(Inscripcion)
admin.site.register(Resultado)


@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'videojuego', 'fecha', 'estado', 'max_participantes')
    list_filter = ('estado', 'videojuego')
