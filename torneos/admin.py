from django.contrib import admin

from .models import Inscripcion, Resultado, Torneo, Videojuego


@admin.register(Videojuego)
class VideojuegoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'genero')
    search_fields = ('nombre',)


class InscripcionInline(admin.TabularInline):
    model = Inscripcion
    extra = 0
    readonly_fields = ('fecha_inscripcion',)


@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'videojuego', 'fecha', 'estado', 'inscritos', 'max_participantes')
    list_filter = ('estado', 'videojuego')
    search_fields = ('nombre', 'descripcion')
    date_hierarchy = 'fecha'
    inlines = [InscripcionInline]

    @admin.display(description='Inscritos')
    def inscritos(self, obj):
        return obj.inscritos_count


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'torneo', 'fecha_inscripcion')
    list_filter = ('torneo',)
    search_fields = ('jugador__username', 'torneo__nombre')


@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'posicion', 'puntos', 'partidas_ganadas', 'partidas_jugadas')
    list_filter = ('inscripcion__torneo',)
