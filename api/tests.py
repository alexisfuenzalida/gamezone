from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from torneos.models import Inscripcion, Torneo, Videojuego
from usuarios.models import Perfil


class BaseApiTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.vj = Videojuego.objects.create(nombre='Valorant')
        cls.admin = User.objects.create_user('admin1', password='clave12345')
        Perfil.objects.filter(usuario=cls.admin).update(rol=Perfil.Rol.ADMIN)
        cls.jugador = User.objects.create_user('jug1', password='clave12345')
        cls.torneo = Torneo.objects.create(
            nombre='Copa API', videojuego=cls.vj,
            fecha=timezone.now() + timedelta(days=5), max_participantes=2,
        )

    def como(self, usuario):
        token, _ = Token.objects.get_or_create(user=usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def datos(self, **extra):
        base = {'nombre': 'Torneo desde API', 'videojuego': self.vj.pk,
                'fecha': (timezone.now() + timedelta(days=9)).isoformat(), 'max_participantes': 8}
        base.update(extra)
        return base


class AutenticacionApiTest(BaseApiTest):

    def test_obtener_token(self):
        r = self.client.post('/api/token/', {'username': 'jug1', 'password': 'clave12345'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('token', r.json())

    def test_credenciales_invalidas(self):
        r = self.client.post('/api/token/', {'username': 'jug1', 'password': 'mala'})
        self.assertEqual(r.status_code, 400)

    def test_sin_autenticacion_401(self):
        self.assertEqual(self.client.get('/api/torneos/').status_code, 401)

    def test_token_invalido_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token no-existe')
        self.assertEqual(self.client.get('/api/torneos/').status_code, 401)


class TorneoApiTest(BaseApiTest):

    def test_listar_es_json_paginado(self):
        self.como(self.jugador)
        r = self.client.get('/api/torneos/')
        self.assertEqual(r['Content-Type'], 'application/json')
        cuerpo = r.json()
        self.assertEqual(cuerpo['count'], 1)
        self.assertEqual(cuerpo['results'][0]['nombre'], 'Copa API')
        self.assertEqual(cuerpo['results'][0]['cupos_disponibles'], 2)

    def test_filtros(self):
        self.como(self.jugador)
        self.assertEqual(self.client.get('/api/torneos/', {'estado': 'FINALIZADO'}).json()['count'], 0)
        self.assertEqual(self.client.get('/api/torneos/', {'videojuego': self.vj.pk}).json()['count'], 1)
        r = self.client.get('/api/torneos/', {'fecha_desde': '2026-12-31', 'fecha_hasta': '2026-01-01'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('fecha_hasta', r.json())

    def test_detalle_incluye_inscritos(self):
        Inscripcion.objects.create(jugador=self.jugador, torneo=self.torneo)
        self.como(self.jugador)
        r = self.client.get(f'/api/torneos/{self.torneo.pk}/')
        self.assertEqual([i['jugador'] for i in r.json()['inscripciones']], ['jug1'])

    def test_detalle_inexistente_404(self):
        self.como(self.jugador)
        self.assertEqual(self.client.get('/api/torneos/9999/').status_code, 404)

    def test_admin_crea_actualiza_y_elimina(self):
        self.como(self.admin)
        r = self.client.post('/api/torneos/', self.datos(), format='json')
        self.assertEqual(r.status_code, 201, r.json())
        pk = r.json()['id']
        self.assertEqual(r.json()['estado'], 'DISPONIBLE')
        self.assertEqual(r.json()['creado_por'], 'admin1')

        r = self.client.patch(f'/api/torneos/{pk}/', {'descripcion': 'Actualizado'}, format='json')
        self.assertEqual(r.json()['descripcion'], 'Actualizado')

        self.assertEqual(self.client.delete(f'/api/torneos/{pk}/').status_code, 204)
        self.assertFalse(Torneo.objects.filter(pk=pk).exists())

    def test_validaciones(self):
        self.como(self.admin)
        r = self.client.post('/api/torneos/', self.datos(
            nombre='copa api', fecha='2020-01-01T10:00:00Z', max_participantes=500,
        ), format='json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.json()), {'nombre', 'fecha', 'max_participantes'})

    def test_reglas_de_estado(self):
        self.como(self.admin)
        r = self.client.patch(f'/api/torneos/{self.torneo.pk}/', {'estado': 'EN_CURSO'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('estado', r.json())
        r = self.client.post('/api/torneos/', self.datos(estado='FINALIZADO'), format='json')
        self.assertEqual(r.status_code, 400)

    def test_no_elimina_en_curso_409(self):
        Torneo.objects.filter(pk=self.torneo.pk).update(estado=Torneo.Estado.EN_CURSO)
        self.como(self.admin)
        self.assertEqual(self.client.delete(f'/api/torneos/{self.torneo.pk}/').status_code, 409)

    def test_jugador_no_escribe_403(self):
        self.como(self.jugador)
        self.assertEqual(self.client.post('/api/torneos/', self.datos(), format='json').status_code, 403)
        self.assertEqual(self.client.delete(f'/api/torneos/{self.torneo.pk}/').status_code, 403)
        self.assertEqual(self.client.post('/api/videojuegos/', {'nombre': 'X'}).status_code, 403)


class InscripcionApiTest(BaseApiTest):

    def setUp(self):
        self.url = f'/api/torneos/{self.torneo.pk}/inscripcion/'

    def test_inscribirse_y_cancelar(self):
        self.como(self.jugador)
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['torneo_nombre'], 'Copa API')
        self.assertEqual(self.client.delete(self.url).status_code, 204)
        self.assertFalse(Inscripcion.objects.exists())

    def test_doble_inscripcion_400(self):
        self.como(self.jugador)
        self.client.post(self.url)
        r = self.client.post(self.url)
        self.assertEqual(r.status_code, 400)
        self.assertIn('ya está inscrito', str(r.json()))

    def test_torneo_lleno_y_estado_completo(self):
        otro = User.objects.create_user('jug2')
        Inscripcion.objects.create(jugador=otro, torneo=self.torneo)
        self.como(self.jugador)
        self.client.post(self.url)
        self.torneo.refresh_from_db()
        self.assertEqual(self.torneo.estado, Torneo.Estado.COMPLETO)
        tercero = User.objects.create_user('jug3')
        self.como(tercero)
        self.assertEqual(self.client.post(self.url).status_code, 400)

    def test_torneo_inexistente_404(self):
        self.como(self.jugador)
        self.assertEqual(self.client.post('/api/torneos/9999/inscripcion/').status_code, 404)

    def test_admin_no_se_inscribe_403(self):
        self.como(self.admin)
        self.assertEqual(self.client.post(self.url).status_code, 403)

    def test_jugador_ve_solo_sus_inscripciones(self):
        otro = User.objects.create_user('jug2')
        Inscripcion.objects.create(jugador=otro, torneo=self.torneo)
        Inscripcion.objects.create(jugador=self.jugador, torneo=self.torneo)
        self.como(self.jugador)
        self.assertEqual([i['jugador'] for i in self.client.get('/api/inscripciones/').json()['results']], ['jug1'])
        self.como(self.admin)
        self.assertEqual(self.client.get('/api/inscripciones/').json()['count'], 2)
        self.assertEqual(self.client.get(f'/api/torneos/{self.torneo.pk}/inscritos/').status_code, 200)
