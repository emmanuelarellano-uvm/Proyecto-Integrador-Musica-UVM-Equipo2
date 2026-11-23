"""
Estructuras de datos y algoritmos obligatorios de la Etapa 1:
- Catalogo inicial: Arreglos
- Historial: Pilas (LIFO)
- Cola de reproduccion: Colas (FIFO)
- Listas de reproduccion: Listas enlazadas
- Menus o recorridos: Recursividad
- Busquedas: Arbol binario de busqueda (ABB)
- Buscar canciones: Busqueda binaria
- Ordenamiento: Quicksort
- Busqueda avanzada multicriterio (inciso h)
"""

from collections import deque


# 1. Arreglo (Catalogo inicial)
class CatalogoArreglo:
    def __init__(self, elementos=None):
        self.elementos = list(elementos) if elementos else []

    def agregar(self, pista):
        self.elementos.append(pista)

    def obtener_todos(self):
        return list(self.elementos)


# 2. Pila (Historial de reproduccion - LIFO)
class PilaHistorial:
    def __init__(self, elementos=None):
        self._pila = list(elementos) if elementos else []

    def apilar(self, pista):
        self._pila.append(pista)

    def desapilar(self):
        return self._pila.pop() if self._pila else None

    def ver_historial(self):
        return list(reversed(self._pila))


# 3. Cola (Cola de reproduccion - FIFO)
class ColaReproduccion:
    def __init__(self, elementos=None):
        self._cola = deque(elementos) if elementos else deque()

    def encolar(self, pista):
        self._cola.append(pista)

    def desencolar(self):
        return self._cola.popleft() if self._cola else None

    def ver_cola(self):
        return list(self._cola)


# 4. Lista enlazada (Listas de reproduccion)
class NodoLista:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None

    def insertar_final(self, dato):
        nuevo = NodoLista(dato)
        if not self.cabeza:
            self.cabeza = nuevo
            return
        actual = self.cabeza
        while actual.siguiente:
            actual = actual.siguiente
        actual.siguiente = nuevo

    # 5. Recursividad (recorrido recursivo de la lista enlazada)
    def recorrer_recursivo(self, nodo=None, inicio=True, acumulado=None):
        if acumulado is None:
            acumulado = []
        actual = self.cabeza if inicio else nodo
        if actual is None:
            return acumulado
        acumulado.append(actual.dato)
        return self.recorrer_recursivo(actual.siguiente, inicio=False, acumulado=acumulado)


# 6. Arbol binario de busqueda (ABB)
class NodoABB:
    def __init__(self, clave, dato):
        self.clave = clave.lower()
        self.datos = [dato]
        self.izquierda = None
        self.derecha = None


class ArbolBinarioBusqueda:
    def __init__(self):
        self.raiz = None

    def insertar(self, clave, dato):
        if self.raiz is None:
            self.raiz = NodoABB(clave, dato)
        else:
            self._insertar_rec(self.raiz, clave.lower(), dato)

    def _insertar_rec(self, nodo, clave, dato):
        if clave == nodo.clave:
            nodo.datos.append(dato)
        elif clave < nodo.clave:
            if nodo.izquierda is None:
                nodo.izquierda = NodoABB(clave, dato)
            else:
                self._insertar_rec(nodo.izquierda, clave, dato)
        else:
            if nodo.derecha is None:
                nodo.derecha = NodoABB(clave, dato)
            else:
                self._insertar_rec(nodo.derecha, clave, dato)

    def buscar(self, clave):
        return self._buscar_rec(self.raiz, clave.lower())

    def _buscar_rec(self, nodo, clave):
        if nodo is None:
            return []
        if clave == nodo.clave:
            return list(nodo.datos)
        if clave < nodo.clave:
            return self._buscar_rec(nodo.izquierda, clave)
        return self._buscar_rec(nodo.derecha, clave)

    def recorrido_inorden(self):
        resultado = []
        self._inorden_rec(self.raiz, resultado)
        return resultado

    def _inorden_rec(self, nodo, resultado):
        if nodo is None:
            return
        self._inorden_rec(nodo.izquierda, resultado)
        resultado.extend(nodo.datos)
        self._inorden_rec(nodo.derecha, resultado)


# 7. Ordenamiento Quicksort
def quicksort(elementos, clave_fn):
    if len(elementos) <= 1:
        return list(elementos)
    pivote = clave_fn(elementos[len(elementos) // 2])
    menores = [x for x in elementos if clave_fn(x) < pivote]
    iguales = [x for x in elementos if clave_fn(x) == pivote]
    mayores = [x for x in elementos if clave_fn(x) > pivote]
    return quicksort(menores, clave_fn) + iguales + quicksort(mayores, clave_fn)


# 8. Busqueda binaria sobre arreglo ordenado
def busqueda_binaria(elementos_ordenados, objetivo, clave_fn):
    izquierda = 0
    derecha = len(elementos_ordenados) - 1
    objetivo_norm = objetivo.strip().lower()

    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        valor_medio = clave_fn(elementos_ordenados[medio])
        if valor_medio == objetivo_norm:
            # Recolectar coincidencias contiguas si hay mas de una
            resultados = [elementos_ordenados[medio]]
            i = medio - 1
            while i >= 0 and clave_fn(elementos_ordenados[i]) == objetivo_norm:
                resultados.insert(0, elementos_ordenados[i])
                i -= 1
            j = medio + 1
            while j < len(elementos_ordenados) and clave_fn(elementos_ordenados[j]) == objetivo_norm:
                resultados.append(elementos_ordenados[j])
                j += 1
            return resultados
        elif valor_medio < objetivo_norm:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return []


# 9. Algoritmo de busqueda avanzada multicriterio (Inciso h)
def busqueda_avanzada(
    pistas,
    titulo="",
    artista="",
    album="",
    racha="",
    posicion="",
    solo_favoritos=False,
):
    """
    Filtra el catalogo en memoria aplicando condiciones logicas compuestas
    sobre titulo, artista, album, racha, posicion y estado de favorito.
    Complejidad temporal lineal O(n) sobre el arreglo filtrado.
    """
    t = titulo.strip().lower()
    ar = artista.strip().lower()
    al = album.strip().lower()
    ra = racha.strip().lower()
    po = posicion.strip().lower()

    resultados = []
    for p in pistas:
        if solo_favoritos and not p["favorito"]:
            continue
        if t and t not in p["nombre"].lower():
            continue
        if ar and ar not in p["artista"].lower():
            continue
        if al and al not in p["album"].lower():
            continue
        if ra and ra not in p["racha"].lower():
            continue
        if po and po not in p["posicion"].lower():
            continue
        resultados.append(p)
    return resultados
