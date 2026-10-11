from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from usuarios.models import Perfil

from .models import Inscripcion, Resultado, Torneo, Videojuego


def fecha_futura(dias=10):
    return (timezone.localtime() + timedelta(days=dias)).strftime('%Y-%m-%dT%H:%M')


class BaseTorneoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.vj = Videojuego.objects.create(nombre='Valorant')
        cls.admin = User.objects.create_user('admin1', password='clave12345')
        Perfil.objects.filter(usuario=cls.admin).update(rol=Perfil.Rol.ADMIN)
        cls.jugador = User.objects.create_user('jug1', password='clave12345')
        cls.torneo = Torneo.objects.create(
            nombre='Copa Test', videojuego=cls.vj,
            fecha=timezone.now() + timedelta(days=5), max_participantes=4,
        )

    def datos(self, **extra):
        base = {
            'nombre': 'Nuevo Torneo Pro', 'videojuego': self.vj.pk, 'fecha': fecha_futura(),
            'max_participantes': 8, 'descripcion': 'Descripción de prueba',
        }
        base.update(extra)
        return base


class CrudTorneoTest(BaseTorneoTest):

    def setUp(self):
        self.client.login(username='admin1', password='clave12345')

    def test_crear_torneo(self):
        r = self.client.post(reverse('torneos:crear'), self.datos())
        torneo = Torneo.objects.get(nombre='Nuevo Torneo Pro')
        self.assertRedirects(r, reverse('torneos:detalle', args=[torneo.pk]))
        self.assertEqual(torneo.estado, Torneo.Estado.DISPONIBLE)
        self.assertEqual(torneo.creado_por, self.admin)

    def test_listado_y_detalle(self):
        self.assertContains(self.client.get(reverse('torneos:lista')), 'Copa Test')
        self.assertContains(self.client.get(reverse('torneos:detalle', args=[self.torneo.pk])), 'Copa Test')

    def test_editar_torneo(self):
        r = self.client.post(reverse('torneos:editar', args=[self.torneo.pk]), self.datos(
            nombre='Copa Test Editada', fecha=fecha_futura(7), estado=Torneo.Estado.DISPONIBLE,
        ))
        self.assertEqual(r.status_code, 302)
        self.torneo.refresh_from_db()
        self.assertEqual(self.torneo.nombre, 'Copa Test Editada')

    def test_eliminar_torneo(self):
        url = reverse('torneos:eliminar', args=[self.torneo.pk])
        self.assertContains(self.client.get(url), '¿Eliminar')
        self.assertRedirects(self.client.post(url), reverse('torneos:lista'))
        self.assertFalse(Torneo.objects.filter(pk=self.torneo.pk).exists())

    def test_no_elimina_torneo_en_curso(self):
        Torneo.objects.filter(pk=self.torneo.pk).update(estado=Torneo.Estado.EN_CURSO)
        self.client.post(reverse('torneos:eliminar', args=[self.torneo.pk]))
        self.assertTrue(Torneo.objects.filter(pk=self.torneo.pk).exists())

    def test_detalle_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse('torneos:detalle', args=[9999])).status_code, 404)


class ValidacionTorneoTest(BaseTorneoTest):

    def setUp(self):
        self.client.login(username='admin1', password='clave12345')

    def errores(self, url, datos):
        r = self.client.post(url, datos)
        self.assertEqual(r.status_code, 200)
        return r.context['form'].errors

    def test_campos_obligatorios(self):
        errores = self.errores(reverse('torneos:crear'), {})
        for campo in ('nombre', 'videojuego', 'fecha', 'max_participantes'):
            self.assertIn(campo, errores)

    def test_fecha_pasada(self):
        pasada = (timezone.localtime() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        self.assertIn('fecha', self.errores(reverse('torneos:crear'), self.datos(fecha=pasada)))

    def test_nombre_duplicado_sin_importar_mayusculas(self):
        self.assertIn('nombre', self.errores(reverse('torneos:crear'), self.datos(nombre='COPA TEST')))

    def test_nombre_muy_corto(self):
        self.assertIn('nombre', self.errores(reverse('torneos:crear'), self.datos(nombre='abc')))

    def test_rango_participantes(self):
        for valor in (1, 129):
            self.assertIn('max_participantes', self.errores(reverse('torneos:crear'), self.datos(max_participantes=valor)))

    def test_maximo_menor_que_inscritos(self):
        for nombre in ('a1', 'a2', 'a3'):
            Inscripcion.objects.create(jugador=User.objects.create_user(nombre), torneo=self.torneo)
        errores = self.errores(reverse('torneos:editar', args=[self.torneo.pk]), self.datos(
            nombre='Copa Test', max_participantes=2, estado=Torneo.Estado.DISPONIBLE,
            fecha=self.torneo.fecha.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%dT%H:%M'),
        ))
        self.assertIn('max_participantes', errores)

    def test_en_curso_requiere_dos_inscritos(self):
        errores = self.errores(reverse('torneos:editar', args=[self.torneo.pk]), self.datos(
            nombre='Copa Test', estado=Torneo.Estado.EN_CURSO,
        ))
        self.assertIn('estado', errores)

    def test_aumentar_cupos_reabre_torneo_completo(self):
        for nombre in ('b1', 'b2', 'b3', 'b4'):
            Inscripcion.objects.create(jugador=User.objects.create_user(nombre), torneo=self.torneo)
        self.torneo.refresh_from_db()
        self.assertEqual(self.torneo.estado, Torneo.Estado.COMPLETO)
        self.client.post(reverse('torneos:editar', args=[self.torneo.pk]), self.datos(
            nombre='Copa Test', max_participantes=8, estado=Torneo.Estado.COMPLETO,
        ))
        self.torneo.refresh_from_db()
        # Completo con cupos libres no es válido: debe pedir corregir el estado
        self.assertEqual(self.torneo.max_participantes, 4)
        self.client.post(reverse('torneos:editar', args=[self.torneo.pk]), self.datos(
            nombre='Copa Test', max_participantes=8, estado=Torneo.Estado.DISPONIBLE,
        ))
        self.torneo.refresh_from_db()
        self.assertEqual((self.torneo.max_participantes, self.torneo.estado), (8, Torneo.Estado.DISPONIBLE))


class FiltrosTorneoTest(BaseTorneoTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        otro = Videojuego.objects.create(nombre='Rocket League')
        Torneo.objects.create(nombre='Rocket Cup', videojuego=otro, estado=Torneo.Estado.FINALIZADO,
                              fecha=timezone.now() + timedelta(days=30), max_participantes=8)

    def nombres(self, **params):
        r = self.client.get(reverse('torneos:lista'), params)
        return {t.nombre for t in r.context['pagina']}

    def test_filtros(self):
        self.assertEqual(self.nombres(), {'Copa Test', 'Rocket Cup'})
        self.assertEqual(self.nombres(videojuego=self.vj.pk), {'Copa Test'})
        self.assertEqual(self.nombres(estado='FINALIZADO'), {'Rocket Cup'})
        self.assertEqual(self.nombres(q='rocket'), {'Rocket Cup'})
        hasta = (timezone.localdate() + timedelta(days=10)).isoformat()
        self.assertEqual(self.nombres(fecha_hasta=hasta), {'Copa Test'})
        Inscripcion.objects.create(jugador=self.jugador, torneo=self.torneo)
        self.assertEqual(self.nombres(min_inscritos=1), {'Copa Test'})
        self.assertEqual(self.nombres(max_inscritos=0), {'Rocket Cup'})

    def test_filtro_invalido_no_rompe(self):
        r = self.client.get(reverse('torneos:lista'), {'videojuego': 'abc', 'min_inscritos': '-3'})
        self.assertEqual(r.status_code, 200)


class PermisosTorneoTest(BaseTorneoTest):

    def test_anonimo_redirige_a_login(self):
        r = self.client.get(reverse('torneos:crear'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('torneos:crear')}")

    def test_jugador_no_puede_gestionar(self):
        self.client.login(username='jug1', password='clave12345')
        for nombre in ('editar', 'eliminar'):
            self.assertEqual(self.client.get(reverse(f'torneos:{nombre}', args=[self.torneo.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('torneos:crear'), self.datos()).status_code, 403)
        self.assertFalse(Torneo.objects.filter(nombre='Nuevo Torneo Pro').exists())

    def test_listado_es_publico(self):
        self.assertEqual(self.client.get(reverse('torneos:lista')).status_code, 200)


class InscripcionTest(BaseTorneoTest):

    def setUp(self):
        self.client.login(username='jug1', password='clave12345')
        self.url = reverse('torneos:inscribirse', args=[self.torneo.pk])

    def mensajes(self, respuesta):
        return ' '.join(str(m) for m in respuesta.context['messages'])

    def test_inscribirse(self):
        r = self.client.post(self.url, follow=True)
        self.assertTrue(Inscripcion.objects.filter(jugador=self.jugador, torneo=self.torneo).exists())
        self.assertIn('Inscripción confirmada', self.mensajes(r))
        self.assertContains(r, 'Estás inscrito')

    def test_no_permite_doble_inscripcion(self):
        self.client.post(self.url)
        r = self.client.post(self.url, follow=True)
        self.assertEqual(Inscripcion.objects.filter(jugador=self.jugador).count(), 1)
        self.assertIn('ya está inscrito', self.mensajes(r))

    def test_torneo_lleno(self):
        for i in range(4):
            Inscripcion.objects.create(jugador=User.objects.create_user(f'x{i}'), torneo=self.torneo)
        r = self.client.post(self.url, follow=True)
        self.assertFalse(Inscripcion.objects.filter(jugador=self.jugador).exists())
        self.assertIn('no está recibiendo inscripciones', self.mensajes(r))

    def test_torneo_ya_comenzado(self):
        Torneo.objects.filter(pk=self.torneo.pk).update(fecha=timezone.now() - timedelta(hours=1))
        r = self.client.post(self.url, follow=True)
        self.assertFalse(Inscripcion.objects.exists())
        self.assertIn('ya comenzó', self.mensajes(r))

    def test_inscripcion_requiere_post_y_login(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.post(self.url).status_code, 302)
        self.assertFalse(Inscripcion.objects.exists())

    def test_torneo_inexistente(self):
        self.assertEqual(self.client.post(reverse('torneos:inscribirse', args=[9999])).status_code, 404)

    def test_admin_no_se_inscribe(self):
        self.client.login(username='admin1', password='clave12345')
        self.client.post(self.url)
        self.assertFalse(Inscripcion.objects.exists())

    def test_cancelar_inscripcion(self):
        self.client.post(self.url)
        self.client.post(reverse('torneos:cancelar_inscripcion', args=[self.torneo.pk]))
        self.assertFalse(Inscripcion.objects.exists())

    def test_no_cancela_torneo_en_curso(self):
        self.client.post(self.url)
        Torneo.objects.filter(pk=self.torneo.pk).update(estado=Torneo.Estado.EN_CURSO)
        self.client.post(reverse('torneos:cancelar_inscripcion', args=[self.torneo.pk]))
        self.assertTrue(Inscripcion.objects.exists())

    def test_admin_quita_jugador(self):
        insc = Inscripcion.objects.create(jugador=self.jugador, torneo=self.torneo)
        url = reverse('torneos:quitar_inscripcion', args=[insc.pk])
        self.assertEqual(self.client.post(url).status_code, 403)  # un jugador no puede
        self.client.login(username='admin1', password='clave12345')
        self.client.post(url)
        self.assertFalse(Inscripcion.objects.exists())

    def test_mis_torneos(self):
        self.client.post(self.url)
        self.assertContains(self.client.get(reverse('torneos:mis_torneos')), 'Copa Test')


class ResultadosTest(BaseTorneoTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.jug2 = User.objects.create_user('jug2', password='clave12345')
        cls.i1 = Inscripcion.objects.create(jugador=cls.jugador, torneo=cls.torneo)
        cls.i2 = Inscripcion.objects.create(jugador=cls.jug2, torneo=cls.torneo)

    def setUp(self):
        self.client.login(username='admin1', password='clave12345')
        self.url = reverse('torneos:resultados', args=[self.torneo.pk])
        Torneo.objects.filter(pk=self.torneo.pk).update(estado=Torneo.Estado.EN_CURSO)

    def fila(self, insc, posicion, ganadas=1, jugadas=2):
        p = f'r{insc.pk}-'
        return {p + 'posicion': posicion, p + 'puntos': 10, p + 'partidas_ganadas': ganadas,
                p + 'partidas_jugadas': jugadas, p + 'observacion': ''}

    def test_solo_en_curso_o_finalizado(self):
        Torneo.objects.filter(pk=self.torneo.pk).update(estado=Torneo.Estado.DISPONIBLE)
        self.assertRedirects(self.client.get(self.url), reverse('torneos:detalle', args=[self.torneo.pk]))

    def test_guardar_y_finalizar(self):
        r = self.client.post(self.url, {**self.fila(self.i1, 1), **self.fila(self.i2, 2), 'finalizar': '1'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Resultado.objects.count(), 2)
        self.torneo.refresh_from_db()
        self.assertEqual(self.torneo.estado, Torneo.Estado.FINALIZADO)

    def test_posiciones_repetidas(self):
        r = self.client.post(self.url, {**self.fila(self.i1, 1), **self.fila(self.i2, 1)})
        self.assertContains(r, 'está repetida')
        self.assertEqual(Resultado.objects.count(), 0)

    def test_ganadas_mayor_que_jugadas(self):
        r = self.client.post(self.url, {**self.fila(self.i1, 1, ganadas=5, jugadas=2), **self.fila(self.i2, 2)})
        self.assertContains(r, 'no pueden superar')
        self.assertEqual(Resultado.objects.count(), 0)

    def test_no_finaliza_sin_resultados(self):
        r = self.client.post(reverse('torneos:editar', args=[self.torneo.pk]), self.datos(
            nombre='Copa Test', estado=Torneo.Estado.FINALIZADO,
        ))
        self.assertIn('estado', r.context['form'].errors)

    def test_jugador_no_registra_resultados(self):
        self.client.login(username='jug1', password='clave12345')
        self.assertEqual(self.client.get(self.url).status_code, 403)


class PaginasErrorTest(BaseTorneoTest):
    """Los tests corren con DEBUG=False, así que se usan las plantillas de error propias."""

    def test_404_personalizado(self):
        for url in ('/no-existe/', reverse('torneos:detalle', args=[9999]),
                    reverse('torneos:editar', args=[9999])):
            self.client.login(username='admin1', password='clave12345')
            r = self.client.get(url)
            self.assertEqual(r.status_code, 404)
            self.assertTemplateUsed(r, '404.html')
            self.assertContains(r, 'página no encontrada', status_code=404)

    def test_403_personalizado_con_motivo(self):
        self.client.login(username='jug1', password='clave12345')
        r = self.client.get(reverse('torneos:crear'))
        self.assertTemplateUsed(r, '403.html')
        self.assertContains(r, 'Solo los administradores', status_code=403)

    def test_500_se_renderiza_sin_contexto(self):
        from django.test import RequestFactory
        from django.views.defaults import server_error
        r = server_error(RequestFactory().get('/'))
        self.assertEqual(r.status_code, 500)
        self.assertIn('Algo salió mal', r.content.decode())

    def test_csrf_invalido(self):
        from django.test import Client
        cliente = Client(enforce_csrf_checks=True)
        cliente.login(username='jug1', password='clave12345')
        r = cliente.post(reverse('torneos:inscribirse', args=[self.torneo.pk]))
        self.assertContains(r, 'El formulario expiró', status_code=403)
        self.assertFalse(Inscripcion.objects.exists())

    def test_parametros_basura_no_rompen(self):
        r = self.client.get(reverse('torneos:lista'), {'pagina': 'abc', 'fecha_desde': '2026-99-99', 'orden': 'DROP'})
        self.assertEqual(r.status_code, 200)


class InformesTest(BaseTorneoTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        lol = Videojuego.objects.create(nombre='LoL')
        cls.final = Torneo.objects.create(nombre='Final LoL', videojuego=lol, max_participantes=4,
                                          fecha=timezone.now() + timedelta(days=2))
        cls.jug2 = User.objects.create_user('jug2')
        Perfil.objects.filter(usuario=cls.jug2).update(nickname='Pro2')
        for jugador, pos, pts in ((cls.jugador, 2, 50), (cls.jug2, 1, 100)):
            insc = Inscripcion.objects.create(jugador=jugador, torneo=cls.final)
            Resultado.objects.create(inscripcion=insc, posicion=pos, puntos=pts,
                                     partidas_ganadas=3 - pos, partidas_jugadas=2)
        Torneo.objects.filter(pk=cls.final.pk).update(estado=Torneo.Estado.FINALIZADO)
        Inscripcion.objects.create(jugador=cls.jugador, torneo=cls.torneo)

    def test_calculos(self):
        from .informes import informe_completo
        d = informe_completo()
        r = d['resumen']
        self.assertEqual((r['torneos'], r['finalizados'], r['realizados'], r['inscripciones']), (2, 1, 1, 3))
        self.assertEqual(r['ocupacion_promedio'], 38)  # 3 inscritos / 8 cupos
        self.assertEqual(d['mayor_participacion'][0]['nombre'], 'Final LoL')
        self.assertEqual([(j['jugador'], j['puntos'], j['victorias']) for j in d['ranking_jugadores']],
                         [('Pro2', 100, 1), ('jug1', 50, 0)])
        self.assertEqual({v['videojuego']: v['inscritos'] for v in d['por_videojuego']}, {'LoL': 2, 'Valorant': 1})

    def test_pagina_solo_admin(self):
        url = reverse('torneos:informes')
        self.client.login(username='jug1', password='clave12345')
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.login(username='admin1', password='clave12345')
        r = self.client.get(url)
        self.assertContains(r, 'Jugadores con mejores resultados')
        self.assertContains(r, 'Pro2')

    def test_informes_sin_datos(self):
        Torneo.objects.all().delete()
        self.client.login(username='admin1', password='clave12345')
        self.assertContains(self.client.get(reverse('torneos:informes')), 'Aún no hay resultados')

    def test_api_informes(self):
        from rest_framework.test import APIClient
        api = APIClient()
        api.force_authenticate(self.jugador)
        self.assertEqual(api.get('/api/informes/').status_code, 403)
        api.force_authenticate(User.objects.get(pk=self.admin.pk))  # recarga el perfil con rol Admin
        self.assertEqual(api.get('/api/informes/').json()['resumen']['torneos'], 2)
