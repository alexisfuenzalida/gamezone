from django.urls import path

from . import views

app_name = 'torneos'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('torneos/', views.lista, name='lista'),
    path('torneos/nuevo/', views.crear, name='crear'),
    path('torneos/<int:pk>/', views.detalle, name='detalle'),
    path('torneos/<int:pk>/editar/', views.editar, name='editar'),
    path('torneos/<int:pk>/eliminar/', views.eliminar, name='eliminar'),
    path('torneos/<int:pk>/inscribirse/', views.inscribirse, name='inscribirse'),
    path('torneos/<int:pk>/resultados/', views.resultados, name='resultados'),
    path('informes/', views.informes_view, name='informes'),
]
