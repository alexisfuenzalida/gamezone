from django import forms

from . import reglas
from .models import Resultado, Torneo, Videojuego

FORMATO_FECHA = '%Y-%m-%dT%H:%M'


class EstiloBootstrapMixin:
    """Agrega las clases de Bootstrap a cada widget del formulario."""

    def aplicar_estilos(self):
        for campo in self.fields.values():
            clase = 'form-select' if isinstance(campo.widget, forms.Select) else 'form-control'
            campo.widget.attrs.setdefault('class', clase)

    def full_clean(self):
        super().full_clean()
        # Marca en rojo los campos con error
        for nombre in self.errors:
            if nombre in self.fields:
                widget = self.fields[nombre].widget
                widget.attrs['class'] = widget.attrs.get('class', '') + ' is-invalid'


class TorneoForm(EstiloBootstrapMixin, forms.ModelForm):

    class Meta:
        model = Torneo
        fields = ['nombre', 'videojuego', 'fecha', 'max_participantes', 'descripcion', 'estado']
        labels = {
            'max_participantes': 'Máximo de participantes',
            'descripcion': 'Descripción',
        }
        help_texts = {
            'max_participantes': 'Entre 2 y 128 jugadores.',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Copa Primavera Valorant', 'maxlength': 100}),
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format=FORMATO_FECHA),
            'max_participantes': forms.NumberInput(attrs={'min': 2, 'max': 128}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Formato, reglas, premios...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].input_formats = [FORMATO_FECHA]
        self.fields['videojuego'].empty_label = 'Selecciona un videojuego'
        if not self.instance.pk:
            # Un torneo nuevo siempre parte Disponible
            del self.fields['estado']
        self.aplicar_estilos()

    def clean_nombre(self):
        return reglas.normalizar_nombre(self.cleaned_data['nombre'], excluir_pk=self.instance.pk)

    def clean_fecha(self):
        return reglas.validar_fecha(self.cleaned_data['fecha'], self.instance)

    def clean(self):
        datos = super().clean()
        estado = datos.get('estado')
        if self.instance.pk and estado:
            maximo = datos.get('max_participantes') or self.instance.max_participantes
            for error in reglas.errores_estado(self.instance, estado, maximo):
                self.add_error('estado', error)
        return datos


class FiltroTorneoForm(EstiloBootstrapMixin, forms.Form):
    ORDEN = [
        ('fecha', 'Fecha (más próxima)'),
        ('-fecha', 'Fecha (más lejana)'),
        ('nombre', 'Nombre (A-Z)'),
        ('-num_inscritos', 'Más inscritos'),
    ]

    q = forms.CharField(label='Buscar', required=False,
                        widget=forms.TextInput(attrs={'placeholder': 'Nombre del torneo'}))
    videojuego = forms.ModelChoiceField(queryset=Videojuego.objects.all(), required=False,
                                        empty_label='Todos')
    estado = forms.ChoiceField(choices=[('', 'Todos')] + Torneo.Estado.choices, required=False)
    fecha_desde = forms.DateField(label='Desde', required=False,
                                  widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_hasta = forms.DateField(label='Hasta', required=False,
                                  widget=forms.DateInput(attrs={'type': 'date'}))
    min_inscritos = forms.IntegerField(label='Mín. inscritos', required=False, min_value=0,
                                       widget=forms.NumberInput(attrs={'placeholder': '0'}))
    max_inscritos = forms.IntegerField(label='Máx. inscritos', required=False, min_value=0,
                                       widget=forms.NumberInput(attrs={'placeholder': '128'}))
    orden = forms.ChoiceField(choices=ORDEN, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()

    def clean(self):
        datos = super().clean()
        desde, hasta = datos.get('fecha_desde'), datos.get('fecha_hasta')
        if desde and hasta and desde > hasta:
            self.add_error('fecha_hasta', 'Debe ser posterior a "Desde".')
        minimo, maximo = datos.get('min_inscritos'), datos.get('max_inscritos')
        if minimo is not None and maximo is not None and minimo > maximo:
            self.add_error('max_inscritos', 'Debe ser mayor o igual al mínimo.')
        return datos

    def filtrar(self, queryset):
        if not self.is_valid():
            return queryset
        d = self.cleaned_data
        if d['q']:
            queryset = queryset.filter(nombre__icontains=d['q'].strip())
        if d['videojuego']:
            queryset = queryset.filter(videojuego=d['videojuego'])
        if d['estado']:
            queryset = queryset.filter(estado=d['estado'])
        if d['fecha_desde']:
            queryset = queryset.filter(fecha__date__gte=d['fecha_desde'])
        if d['fecha_hasta']:
            queryset = queryset.filter(fecha__date__lte=d['fecha_hasta'])
        if d['min_inscritos'] is not None:
            queryset = queryset.filter(num_inscritos__gte=d['min_inscritos'])
        if d['max_inscritos'] is not None:
            queryset = queryset.filter(num_inscritos__lte=d['max_inscritos'])
        return queryset.order_by(d['orden'] or 'fecha', 'pk')


class ResultadoForm(EstiloBootstrapMixin, forms.ModelForm):

    class Meta:
        model = Resultado
        fields = ['posicion', 'puntos', 'partidas_ganadas', 'partidas_jugadas', 'observacion']
        widgets = {
            'posicion': forms.NumberInput(attrs={'min': 1}),
            'puntos': forms.NumberInput(attrs={'min': 0}),
            'partidas_ganadas': forms.NumberInput(attrs={'min': 0}),
            'partidas_jugadas': forms.NumberInput(attrs={'min': 0}),
            'observacion': forms.TextInput(attrs={'placeholder': 'Opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilos()
        for campo in self.fields.values():
            campo.widget.attrs['class'] += ' form-control-sm'
            campo.widget.attrs['aria-label'] = campo.label


def validar_posiciones_unicas(formularios):
    """Dos jugadores del mismo torneo no pueden compartir posición."""
    vistas = {}
    for form in formularios:
        posicion = form.cleaned_data.get('posicion')
        if posicion is None:
            continue
        if posicion in vistas:
            for repetido in (form, vistas[posicion]):
                repetido.add_error('posicion', f'La posición {posicion} está repetida.')
                repetido.fields['posicion'].widget.attrs['class'] += ' is-invalid'
        else:
            vistas[posicion] = form
    return all(not f.errors for f in formularios)
