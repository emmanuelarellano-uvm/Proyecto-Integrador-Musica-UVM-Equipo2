from django.contrib import admin
from .models import (
    Album,
    Artista,
    ListaReproduccion,
    ListaReproduccionPista,
    Pista,
    Seguidor,
    Usuario,
)

admin.site.site_header = "UVM MUSIC | Administracion de Plataforma"
admin.site.site_title = "UVM Music Admin"
admin.site.index_title = "Panel de Control Institucional UVM - Base de Datos Musical"


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id_usuario", "nombre", "correo_electronico", "fecha_nacimiento")
    search_fields = ("nombre", "correo_electronico")
    ordering = ("id_usuario",)


@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ("id_artista", "nombre", "genero")
    search_fields = ("nombre", "genero")
    list_filter = ("genero",)
    ordering = ("nombre",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("id_album", "nombre", "artista", "fecha_lanzamiento")
    search_fields = ("nombre", "artista__nombre")
    list_filter = ("artista",)
    ordering = ("nombre",)


@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ("id_pista", "nombre", "album", "duracion", "racha", "posicion", "favorito")
    search_fields = ("nombre", "album__nombre", "album__artista__nombre", "escritores", "productor")
    list_filter = ("favorito", "posicion")
    list_editable = ("favorito",)
    ordering = ("id_pista",)


@admin.register(ListaReproduccion)
class ListaReproduccionAdmin(admin.ModelAdmin):
    list_display = ("id_lista_reproduccion", "nombre", "usuario")
    search_fields = ("nombre", "usuario__nombre")


@admin.register(ListaReproduccionPista)
class ListaReproduccionPistaAdmin(admin.ModelAdmin):
    list_display = ("id", "lista_reproduccion", "orden", "pista")
    list_filter = ("lista_reproduccion",)
    ordering = ("lista_reproduccion", "orden")


@admin.register(Seguidor)
class SeguidorAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "artista")
    list_filter = ("artista",)
    search_fields = ("usuario__nombre", "artista__nombre")
