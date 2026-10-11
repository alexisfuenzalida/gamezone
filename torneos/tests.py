from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from usuarios.models import Perfil

from .models import Inscripcion, Torneo, Videojuego


def en_dias(dias):
    return (timezone.localtime() + timedelta(days=dias)).strftime('%Y-%m-%dT%H:%M')


class GamezoneTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.vj = Videojuego.objects.create(nombre='Valorant')
        cls.admin = User.objects.create_user('admin1', password='clave12345')
        Perfil.objects.filter(usuario=cls.admin).update(rol=Perfil.Rol.ADMIN)
        cls.jugador = User.objects.create_user('jug1', password='clave12345')
        cls.torneo = Torneo.objects.create(nombre='Copa Test', videojuego=cls.vj,
                                           fecha=timezone.now() + timedelta(days=5), max_participantes=2)

    def datos(self, **extra):
        return {'nombre': 'Nuevo Torneo', 'videojuego': self.vj.pk, 'fecha': en_dias(10),
                'max_participantes': 8, 'descripcion': '', **extra}

    def login(self, usuario):
        self.client.login(username=usuario, password='clave12345')

    # --- CRUD (criterios 3, 4, 5) ---
    def test_crud_admin(self):
        self.login('admin1')
        self.client.post(reverse('torneos:crear'), self.datos())
        nuevo = Torneo.objects.get(nombre='Nuevo Torneo')
        self.assertContains(self.client.get(reverse('torneos:lista')), 'Nuevo Torneo')
        self.client.post(reverse('torneos:editar', args=[nuevo.pk]),
                         self.datos(nombre='Torneo Editado', estado='DISPONIBLE'))
        nuevo.refresh_from_db()
        self.assertEqual(nuevo.nombre, 'Torneo Editado')
        self.client.post(reverse('torneos:eliminar', args=[nuevo.pk]))
        self.assertFalse(Torneo.objects.filter(pk=nuevo.pk).exists())

    # --- Validaciones (criterio 9) ---
    def test_validaciones_formulario(self):
        self.login('admin1')
        pasada = (timezone.localtime() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        r = self.client.post(reverse('torneos:crear'), self.datos(nombre='copa test', fecha=pasada, max_participantes=500))
        self.assertEqual(set(r.context['form'].errors), {'nombre', 'fecha', 'max_participantes'})

    def test_maximo_no_menor_que_inscritos(self):
        Inscripcion.objects.create(jugador=self.jugador, torneo=self.torneo)
        Inscripcion.objects.create(jugador=self.admin, torneo=self.torneo)
        self.login('admin1')
        fecha = timezone.localtime(self.torneo.fecha).strftime('%Y-%m-%dT%H:%M')
        r = self.client.post(reverse('torneos:editar', args=[self.torneo.pk]),
                             self.datos(nombre='Copa Test', fecha=fecha, max_participantes=1, estado='DISPONIBLE'))
        self.assertIn('max_participantes', r.context['form'].errors)

    # --- Filtros del listado ---
    def test_filtros(self):
        otro = Torneo.objects.create(nombre='Torneo Final', videojuego=self.vj, estado='FINALIZADO',
                                     fecha=timezone.now() + timedelta(days=30), max_participantes=8)
        r = self.client.get(reverse('torneos:lista'), {'estado': 'FINALIZADO'})
        self.assertEqual(list(r.context['torneos']), [otro])

    # --- Inscripciones y estados ---
    def test_inscripcion_duplicada_y_torneo_completo(self):
        self.login('jug1')
        url = reverse('torneos:inscribirse', args=[self.torneo.pk])
        self.client.post(url)
        r = self.client.post(url, follow=True)
        self.assertContains(r, 'Ya estás inscrito')
        self.assertEqual(Inscripcion.objects.count(), 1)

        self.torneo.inscribir(User.objects.create_user('jug2'))
        self.torneo.refresh_from_db()
        self.assertEqual(self.torneo.estado, Torneo.Estado.COMPLETO)

    # --- Sesiones, roles y errores (criterio 10) ---
    def test_permisos_y_errores(self):
        self.assertRedirects(self.client.get(reverse('torneos:crear')),
                             f"{reverse('login')}?next={reverse('torneos:crear')}")
        self.login('jug1')
        self.assertEqual(self.client.get(reverse('torneos:crear')).status_code, 403)
        self.assertEqual(self.client.get(reverse('torneos:informes')).status_code, 403)
        r = self.client.get(reverse('torneos:detalle', args=[9999]))
        self.assertEqual(r.status_code, 404)
        self.assertTemplateUsed(r, '404.html')

    def test_informes(self):
        self.login('admin1')
        self.assertContains(self.client.get(reverse('torneos:informes')), 'Copa Test')

    # --- API REST ---
    def test_api(self):
        api = APIClient()
        self.assertEqual(api.get('/api/torneos/').status_code, 401)

        token = api.post('/api/token/', {'username': 'jug1', 'password': 'clave12345'}).json()['token']
        api.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(api.get('/api/torneos/').json()[0]['nombre'], 'Copa Test')
        self.assertEqual(api.post('/api/torneos/', self.datos()).status_code, 403)
        self.assertEqual(api.post(f'/api/torneos/{self.torneo.pk}/inscribirse/').status_code, 201)
        self.assertEqual(api.post(f'/api/torneos/{self.torneo.pk}/inscribirse/').status_code, 400)

        api.force_authenticate(User.objects.get(pk=self.admin.pk))
        self.assertEqual(api.post('/api/torneos/', self.datos()).status_code, 201)
        self.assertEqual(api.post('/api/torneos/', self.datos(nombre='abc')).status_code, 400)
