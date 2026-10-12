from django.contrib import admin
from .models import Perfil, Incidencia, Comentario


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'categoria', 'prioridad', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'categoria', 'prioridad')
    search_fields = ('titulo', 'descripcion', 'usuario__username')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'edificio', 'piso_puerta')
    list_filter = ('edificio',)
    search_fields = ('usuario__username', 'edificio')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('incidencia', 'autor', 'fecha')
    search_fields = ('texto', 'autor__username')