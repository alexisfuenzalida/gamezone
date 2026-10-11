from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import TorneoViewSet

router = DefaultRouter()
router.register('torneos', TorneoViewSet, basename='torneo')

app_name = 'api'

urlpatterns = [
    path('token/', obtain_auth_token, name='token'),
    path('', include(router.urls)),
]
