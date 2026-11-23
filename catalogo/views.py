from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .estructuras import (
    ArbolBinarioBusqueda,
    CatalogoArreglo,
    ColaReproduccion,
    ListaEnlazada,
    PilaHistorial,
    busqueda_avanzada,
    busqueda_binaria,
    quicksort,
)
from .forms import (
    AlbumForm,
    ArtistaForm,
    BusquedaAvanzadaForm,
    ListaReproduccionForm,
    ListaReproduccionPistaForm,
    PistaForm,
    SeguidorForm,
    UsuarioForm,
)
from .models import (
    Album,
    Artista,
    ListaReproduccion,
    ListaReproduccionPista,
    Pista,
    Seguidor,
    Usuario,
)


def _clave_alfabetica(texto: str) -> str:
    limpio = texto.strip().lstrip("('¿¡ ").lower()
    return limpio or texto.strip().lower()


def _inicial_titulo(nombre: str) -> str:
    for ch in nombre.strip():
        if ch.isalnum():
            return ch.upper()
    return "M"


def _serializar_pistas():
    queryset = Pista.objects.select_related("album", "album__artista").all()
    arreglo = CatalogoArreglo()
    for p in queryset:
        arreglo.agregar(
            {
                "id": p.id_pista,
                "nombre": p.nombre,
                "inicial": _inicial_titulo(p.nombre),
                "artista": p.album.artista.nombre,
                "album": p.album.nombre,
                "duracion": p.duracion,
                "racha": p.racha,
                "posicion": p.posicion,
                "favorito": p.favorito,
                "ruta": p.ruta,
            }
        )
    return arreglo.obtener_todos()


def inicio(request):
    form_busqueda = BusquedaAvanzadaForm(request.GET or None)
    pistas = _serializar_pistas()
    metodo_usado = "Catalogo completo (Arreglo)"
    orden_usado = "nombre"

    if form_busqueda.is_valid():
        datos = form_busqueda.cleaned_data
        metodo = datos.get("metodo") or "avanzada"
        orden_usado = datos.get("ordenar_por") or "nombre"
        titulo = datos.get("titulo") or ""

        if metodo == "binaria" and titulo:
            ordenadas = quicksort(pistas, lambda x: x["nombre"].lower())
            pistas = busqueda_binaria(ordenadas, titulo, lambda x: x["nombre"].lower())
            metodo_usado = "Busqueda binaria exacta O(log n) sobre arreglo ordenado con Quicksort"
        elif metodo == "abb" and titulo:
            abb = ArbolBinarioBusqueda()
            for item in pistas:
                abb.insertar(item["nombre"], item)
            pistas = abb.buscar(titulo)
            metodo_usado = "Arbol binario de busqueda (ABB)"
        else:
            pistas = busqueda_avanzada(
                pistas,
                titulo=titulo,
                artista=datos.get("artista") or "",
                album=datos.get("album") or "",
                racha=datos.get("racha") or "",
                posicion=datos.get("posicion") or "",
                solo_favoritos=bool(datos.get("solo_favoritos")),
            )
            pistas = quicksort(pistas, lambda x: _clave_alfabetica(x[orden_usado]))
            metodo_usado = f"Busqueda avanzada multicriterio + Quicksort por {orden_usado}"
    else:
        pistas = quicksort(pistas, lambda x: _clave_alfabetica(x["nombre"]))

    # Historial (Pila en sesion) y Cola de reproduccion (Cola en sesion)
    pila = PilaHistorial(request.session.get("historial_ids", []))
    cola = ColaReproduccion(request.session.get("cola_ids", []))

    mapa_pistas = {p["id"]: p for p in _serializar_pistas()}
    historial_pistas = [mapa_pistas[pid] for pid in pila.ver_historial() if pid in mapa_pistas]
    cola_pistas = [mapa_pistas[pid] for pid in cola.ver_cola() if pid in mapa_pistas]

    # Listas de reproduccion usando ListaEnlazada y recorrido recursivo
    listas_bd = ListaReproduccion.objects.select_related("usuario").prefetch_related("elementos__pista").all()
    listas_enlazadas = []
    for lista in listas_bd:
        le = ListaEnlazada()
        for elem in lista.elementos.all():
            le.insertar_final(f"{elem.orden}. {elem.pista.nombre}")
        listas_enlazadas.append(
            {
                "nombre": lista.nombre,
                "usuario": lista.usuario.nombre,
                "pistas": le.recorrer_recursivo(),
            }
        )

    contexto = {
        "form_busqueda": form_busqueda,
        "pistas": pistas,
        "total_resultados": len(pistas),
        "metodo_usado": metodo_usado,
        "historial_pistas": historial_pistas,
        "cola_pistas": cola_pistas,
        "listas_enlazadas": listas_enlazadas,
        "conteos": {
            "usuarios": Usuario.objects.count(),
            "artistas": Artista.objects.count(),
            "albumes": Album.objects.count(),
            "pistas": Pista.objects.count(),
            "listas": ListaReproduccion.objects.count(),
            "seguidores": Seguidor.objects.count(),
        },
    }
    return render(request, "catalogo/inicio.html", contexto)


def _vista_formulario(request, form_class, titulo, descripcion):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Registro guardado correctamente en {titulo}.")
            return redirect("inicio")
    else:
        form = form_class()
    return render(
        request,
        "catalogo/formulario.html",
        {"form": form, "titulo": titulo, "descripcion": descripcion},
    )


def registrar_usuario(request):
    return _vista_formulario(request, UsuarioForm, "Usuario", "Alta de un nuevo usuario en la tabla usuarios.")


def registrar_artista(request):
    return _vista_formulario(request, ArtistaForm, "Artista", "Alta de un nuevo artista en la tabla artistas.")


def registrar_album(request):
    return _vista_formulario(request, AlbumForm, "Album", "Alta de un album vinculado a un artista existente.")


def registrar_pista(request):
    return _vista_formulario(request, PistaForm, "Pista / Cancion", "Alta de una cancion vinculada a un album.")


def registrar_lista(request):
    return _vista_formulario(request, ListaReproduccionForm, "Lista de reproduccion", "Crear una lista de reproduccion para un usuario.")


def agregar_pista_lista(request):
    return _vista_formulario(request, ListaReproduccionPistaForm, "Pista en lista de reproduccion", "Vincular una pista a una lista con su numero de orden.")


def registrar_seguidor(request):
    return _vista_formulario(request, SeguidorForm, "Seguidor", "Registrar que un usuario sigue a un artista.")


def alternar_favorito(request, id_pista):
    pista = get_object_or_404(Pista, pk=id_pista)
    pista.favorito = not pista.favorito
    pista.save()
    estado = "agregada a favoritos" if pista.favorito else "retirada de favoritos"
    messages.info(request, f"La pista '{pista.nombre}' fue {estado}.")
    return redirect("inicio")


def reproducir_pista(request, id_pista):
    pista = get_object_or_404(Pista, pk=id_pista)
    pila = PilaHistorial(request.session.get("historial_ids", []))
    pila.apilar(pista.id_pista)
    request.session["historial_ids"] = list(reversed(pila.ver_historial()))
    messages.success(request, f"Reproduciendo '{pista.nombre}' y agregada a la pila de historial.")
    return redirect("inicio")


def encolar_pista(request, id_pista):
    pista = get_object_or_404(Pista, pk=id_pista)
    cola = ColaReproduccion(request.session.get("cola_ids", []))
    cola.encolar(pista.id_pista)
    request.session["cola_ids"] = cola.ver_cola()
    messages.info(request, f"La pista '{pista.nombre}' se agrego a la cola de reproduccion.")
    return redirect("inicio")


def reproducir_siguiente_cola(request):
    cola = ColaReproduccion(request.session.get("cola_ids", []))
    siguiente_id = cola.desencolar()
    request.session["cola_ids"] = cola.ver_cola()
    if siguiente_id is not None:
        pista = get_object_or_404(Pista, pk=siguiente_id)
        pila = PilaHistorial(request.session.get("historial_ids", []))
        pila.apilar(pista.id_pista)
        request.session["historial_ids"] = list(reversed(pila.ver_historial()))
        messages.success(request, f"Siguiente pista de la cola reproducida: '{pista.nombre}'.")
    else:
        messages.warning(request, "La cola de reproduccion esta vacia.")
    return redirect("inicio")

def quitar_de_cola(request, indice):
    cola_ids = list(request.session.get("cola_ids", []))
    if 0 <= indice < len(cola_ids):
        cola_ids.pop(indice)
        request.session["cola_ids"] = cola_ids
    return redirect("inicio")


def vaciar_cola(request):
    request.session["cola_ids"] = []
    return redirect("inicio")
