from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False


class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ('username', 'email', 'get_rol', 'is_active')

    @admin.display(description='Rol')
    def get_rol(self, obj):
        return obj.perfil.get_rol_display() if hasattr(obj, 'perfil') else '-'

    def get_inline_instances(self, request, obj=None):
        # Al crear, el Perfil lo genera la señal; el inline solo se muestra al editar
        return super().get_inline_instances(request, obj) if obj else []


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nickname', 'rol')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'nickname')
