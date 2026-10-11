from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('videojuegos', views.VideojuegoViewSet, basename='videojuego')
router.register('torneos', views.TorneoViewSet, basename='torneo')
router.register('inscripciones', views.InscripcionViewSet, basename='inscripcion')

app_name = 'api'

urlpatterns = [
    path('token/', obtain_auth_token, name='token'),
    path('informes/', views.InformesView.as_view(), name='informes'),
    path('auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
]
