from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Perfil


class RegistroForm(UserCreationForm):
    """Registro público: crea siempre usuarios con rol Jugador."""

    email = forms.EmailField(label='Correo electrónico')
    nickname = forms.CharField(
        label='Nickname', min_length=3, max_length=30,
        help_text='Tu nombre visible en los torneos (3 a 30 caracteres).',
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname']
        labels = {'username': 'Usuario'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault('class', 'form-control')

    def full_clean(self):
        super().full_clean()
        for nombre in self.errors:
            if nombre in self.fields:
                self.fields[nombre].widget.attrs['class'] += ' is-invalid'

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname'].strip()
        if not nickname.replace('_', '').replace('-', '').isalnum():
            raise forms.ValidationError('Solo letras, números, guion y guion bajo.')
        if Perfil.objects.filter(nickname__iexact=nickname).exists():
            raise forms.ValidationError('Ese nickname ya está en uso.')
        return nickname

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            # El Perfil lo crea la señal post_save; aquí solo se completa
            Perfil.objects.filter(usuario=usuario).update(
                rol=Perfil.Rol.JUGADOR, nickname=self.cleaned_data['nickname'],
            )
        return usuario
