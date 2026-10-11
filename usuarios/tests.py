from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Perfil


class RegistroTest(TestCase):

    def datos(self, **extra):
        base = {'username': 'nuevo', 'email': 'nuevo@mail.cl', 'nickname': 'NuevoPro',
                'password1': 'ClaveSegura#2026', 'password2': 'ClaveSegura#2026'}
        base.update(extra)
        return base

    def test_registro_crea_jugador_y_inicia_sesion(self):
        r = self.client.post(reverse('registro'), self.datos())
        self.assertRedirects(r, reverse('torneos:lista'))
        usuario = User.objects.get(username='nuevo')
        self.assertEqual((usuario.perfil.rol, usuario.perfil.nickname), (Perfil.Rol.JUGADOR, 'NuevoPro'))
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def test_validaciones_registro(self):
        User.objects.create_user('otro', email='nuevo@mail.cl')
        Perfil.objects.filter(usuario__username='otro').update(nickname='NuevoPro')
        r = self.client.post(reverse('registro'), self.datos(nickname='nuevopro', password2='distinta'))
        errores = r.context['form'].errors
        for campo in ('email', 'nickname', 'password2'):
            self.assertIn(campo, errores)

    def test_superusuario_queda_admin(self):
        admin = User.objects.create_superuser('root', password='x')
        self.assertTrue(admin.perfil.es_admin)

    def test_sesion_y_logout(self):
        User.objects.create_user('jug', password='clave12345')
        r = self.client.post(reverse('login'), {'username': 'jug', 'password': 'clave12345'})
        self.assertRedirects(r, reverse('torneos:inicio'))
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
