from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("registrar/usuario/", views.registrar_usuario, name="registrar_usuario"),
    path("registrar/artista/", views.registrar_artista, name="registrar_artista"),
    path("registrar/album/", views.registrar_album, name="registrar_album"),
    path("registrar/pista/", views.registrar_pista, name="registrar_pista"),
    path("registrar/lista/", views.registrar_lista, name="registrar_lista"),
    path("registrar/lista-pista/", views.agregar_pista_lista, name="agregar_pista_lista"),
    path("registrar/seguidor/", views.registrar_seguidor, name="registrar_seguidor"),
    path("pista/<int:id_pista>/favorito/", views.alternar_favorito, name="alternar_favorito"),
    path("pista/<int:id_pista>/reproducir/", views.reproducir_pista, name="reproducir_pista"),
    path("pista/<int:id_pista>/encolar/", views.encolar_pista, name="encolar_pista"),
    path("cola/siguiente/", views.reproducir_siguiente_cola, name="reproducir_siguiente_cola"),
    path("cola/quitar/<int:indice>/", views.quitar_de_cola, name="quitar_de_cola"),
    path("cola/vaciar/", views.vaciar_cola, name="vaciar_cola"),
]
