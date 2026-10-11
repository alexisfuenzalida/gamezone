from django import forms

from .models import Resultado, Torneo, Videojuego


class TorneoForm(forms.ModelForm):
    """Las validaciones de negocio están en Torneo.clean(); el ModelForm las ejecuta al validar."""

    class Meta:
        model = Torneo
        fields = ['nombre', 'videojuego', 'fecha', 'max_participantes', 'descripcion', 'estado']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            del self.fields['estado']  # un torneo nuevo siempre parte Disponible


class FiltroTorneoForm(forms.Form):
    videojuego = forms.ModelChoiceField(Videojuego.objects.all(), required=False, empty_label='Todos')
    estado = forms.ChoiceField(choices=[('', 'Todos')] + Torneo.Estado.choices, required=False)
    fecha = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    min_inscritos = forms.IntegerField(label='Mín. inscritos', required=False, min_value=0)

    def filtrar(self, torneos):
        if not self.is_valid():
            return torneos
        d = self.cleaned_data
        if d['videojuego']:
            torneos = torneos.filter(videojuego=d['videojuego'])
        if d['estado']:
            torneos = torneos.filter(estado=d['estado'])
        if d['fecha']:
            torneos = torneos.filter(fecha__date=d['fecha'])
        if d['min_inscritos'] is not None:
            torneos = torneos.filter(num_inscritos__gte=d['min_inscritos'])
        return torneos


class ResultadoForm(forms.ModelForm):
    class Meta:
        model = Resultado
        fields = ['posicion', 'puntos']
