from django import forms
from .models import (
    Album,
    Artista,
    ListaReproduccion,
    ListaReproduccionPista,
    Pista,
    Seguidor,
    Usuario,
)


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["nombre", "correo_electronico", "contrasena", "fecha_nacimiento"]
        widgets = {
            "contrasena": forms.PasswordInput(attrs={"placeholder": "Ingresa una contrasena"}),
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }


class ArtistaForm(forms.ModelForm):
    class Meta:
        model = Artista
        fields = ["nombre", "genero"]


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ["artista", "nombre", "fecha_lanzamiento"]


class PistaForm(forms.ModelForm):
    class Meta:
        model = Pista
        fields = [
            "album",
            "nombre",
            "duracion",
            "ruta",
            "escritores",
            "productor",
            "racha",
            "posicion",
            "favorito",
        ]


class ListaReproduccionForm(forms.ModelForm):
    class Meta:
        model = ListaReproduccion
        fields = ["usuario", "nombre"]


class ListaReproduccionPistaForm(forms.ModelForm):
    class Meta:
        model = ListaReproduccionPista
        fields = ["lista_reproduccion", "pista", "orden"]


class SeguidorForm(forms.ModelForm):
    class Meta:
        model = Seguidor
        fields = ["usuario", "artista"]


class BusquedaAvanzadaForm(forms.Form):
    titulo = forms.CharField(
        required=False,
        label="Titulo de la cancion",
        widget=forms.TextInput(attrs={"placeholder": "Ej. Buddy Holly, Clocks..."}),
    )
    artista = forms.CharField(
        required=False,
        label="Artista",
        widget=forms.TextInput(attrs={"placeholder": "Ej. The Beatles, Weezer..."}),
    )
    album = forms.CharField(
        required=False,
        label="Album",
        widget=forms.TextInput(attrs={"placeholder": "Ej. Nevermind, Some Girls..."}),
    )
    racha = forms.CharField(
        required=False,
        label="Racha",
        widget=forms.TextInput(attrs={"placeholder": "Ej. 20 weeks, Sin ingreso..."}),
    )
    posicion = forms.CharField(
        required=False,
        label="Posicion en lista",
        widget=forms.TextInput(attrs={"placeholder": "Ej. No. 1, No. 2..."}),
    )
    solo_favoritos = forms.BooleanField(required=False, label="Mostrar solo favoritos")
    metodo = forms.ChoiceField(
        required=False,
        label="Algoritmo de busqueda",
        choices=[
            ("avanzada", "Busqueda avanzada multicriterio"),
            ("binaria", "Busqueda binaria exacta por titulo"),
            ("abb", "Arbol binario de busqueda (ABB)"),
        ],
        initial="avanzada",
    )
    ordenar_por = forms.ChoiceField(
        required=False,
        label="Ordenar con Quicksort por",
        choices=[
            ("nombre", "Titulo (A-Z)"),
            ("artista", "Artista (A-Z)"),
            ("album", "Album (A-Z)"),
        ],
        initial="nombre",
    )
