from django.urls import path
from . import views

urlpatterns = [
    path('', views.IncidenciaListView.as_view(), name='lista_incidencias'),
    path('incidencias/nueva/', views.IncidenciaCreateView.as_view(), name='crear_incidencia'),
    path('incidencias/<int:pk>/', views.IncidenciaDetailView.as_view(), name='detalle_incidencia'),
    path('incidencias/<int:pk>/editar/', views.IncidenciaUpdateView.as_view(), name='editar_incidencia'),
    path('incidencias/<int:pk>/eliminar/', views.IncidenciaDeleteView.as_view(), name='eliminar_incidencia'),
    path('incidencias/<int:pk>/comentar/', views.ComentarioCreateView.as_view(), name='comentar'),
    path('perfil/', views.PerfilUpdateView.as_view(), name='perfil'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
]