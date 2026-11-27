"""
Etapa 2 - Reproductor de Musica UVM MUSIC (Interfaz 3D de Escritorio).
Bibliotecas principales requeridas:
- tkinter y tkinter.filedialog: Interfaz grafica de usuario (GUI) y seleccion de carpetas.
- pygame.mixer: Carga y reproduccion de archivos de audio.
- os: Exploracion del directorio para construir la lista de reproduccion.
"""

import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame.mixer as mixer

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None


FORMATOS_SOPORTADOS = (".mp3", ".wav", ".ogg")

# Paleta Oscura de Alto Contraste + Identidad Institucional UVM
BG_APP = "#0C0E16"
BG_SIDEBAR = "#08090F"
BG_CARD = "#141724"
BG_CARD_ALT = "#1A1E2E"
BG_INPUT = "#1D2234"
BG_PLAYER = "#10131D"
BTN_3D_BASE = "#1B2032"
BTN_3D_FACE = "#262C42"
BTN_3D_GLOSS = "#363E5C"
BTN_3D_HOVER = "#323A56"
BORDER_CONTRAST = "#363D59"
UVM_RED = "#C8102E"
UVM_RED_BRIGHT = "#F22646"
UVM_RED_LIGHT = "#FF6B81"
UVM_RED_DARK = "#750819"
TEXT_MAIN = "#FFFFFF"
TEXT_SOFT = "#E4E8F5"
TEXT_SEC = "#B5BDD6"
TEXT_MUTED = "#8891B0"
PLACEHOLDER_TEXT = "Escribe el nombre de una cancion para filtrar la lista..."


def _rect_redondeado(canvas: tk.Canvas, x1, y1, x2, y2, r, **kwargs):
    pts = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


class Boton3D(tk.Canvas):
    """Boton con efecto 3D elevado por capas de sombra, profundidad y reflejo suave."""

    def __init__(
        self,
        padre,
        comando,
        ancho=48,
        alto=48,
        forma="pill",
        icono=None,
        texto="",
        subtexto="",
        primario=False,
        bg_padre=BG_PLAYER,
    ):
        altura_total = alto + (16 if subtexto else 0)
        super().__init__(
            padre,
            width=ancho,
            height=altura_total,
            bg=bg_padre,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.comando = comando
        self.ancho = ancho
        self.alto_btn = alto
        self.forma = forma
        self.icono = icono
        self.texto = texto
        self.subtexto = subtexto
        self.primario = primario
        self.activo = False
        self.hover = False
        self.presionado = False
        self.nivel_volumen = 70

        self.bind("<Enter>", self._al_entrar)
        self.bind("<Leave>", self._al_salir)
        self.bind("<ButtonPress-1>", self._al_presionar)
        self.bind("<ButtonRelease-1>", self._al_soltar)
        self.redibujar()

    def establecer_activo(self, estado: bool):
        self.activo = estado
        self.redibujar()

    def establecer_texto(self, nuevo_texto: str):
        self.texto = nuevo_texto
        self.redibujar()

    def establecer_volumen(self, nivel: int):
        self.nivel_volumen = nivel
        self.redibujar()

    def _al_entrar(self, _e):
        self.hover = True
        self.redibujar()

    def _al_salir(self, _e):
        self.hover = False
        self.presionado = False
        self.redibujar()

    def _al_presionar(self, _e):
        self.presionado = True
        self.redibujar()

    def _al_soltar(self, _e):
        estaba_presionado = self.presionado
        self.presionado = False
        self.redibujar()
        if estaba_presionado and callable(self.comando):
            self.comando()

    def redibujar(self):
        self.delete("all")
        w = self.ancho
        h = self.alto_btn
        dy = 3 if self.presionado else 0

        if self.primario or self.activo:
            pedestal = "#590413"
            borde_ext = "#9E0D26"
            cara_baja = "#B50E29" if not self.hover else "#D41434"
            cara_media = "#D91536" if not self.hover else "#F22646"
            cara_alta = "#F53858" if not self.hover else "#FF5270"
            brillo_top = "#FF8FA3"
            fg_c = TEXT_MAIN
        else:
            pedestal = "#0B0D16"
            borde_ext = "#1A1F30"
            cara_baja = "#1D2234" if not self.hover else "#272E47"
            cara_media = "#282F47" if not self.hover else "#343D5C"
            cara_alta = "#374060" if not self.hover else "#46527A"
            brillo_top = "#6A77A3" if not self.hover else "#FF6B81"
            fg_c = TEXT_MAIN if self.hover else TEXT_SOFT

        if self.forma == "circle":
            # Sombra 3D profunda proyectada
            self.create_oval(5, 8, w - 1, h, fill="#040509", outline="")
            # Base extruida 3D (espesor real)
            self.create_oval(3, 5 + dy, w - 3, h - 1 + dy, fill=pedestal, outline=borde_ext, width=1)
            # Cuerpo esferico por capas lisas (sin puntitos stipple)
            self.create_oval(3, 1 + dy, w - 3, h - 5 + dy, fill=cara_baja, outline=borde_ext, width=1)
            self.create_oval(5, 2 + dy, w - 5, h - 9 + dy, fill=cara_media, outline="")
            self.create_oval(9, 3 + dy, w - 9, int(h * 0.54) + dy, fill=cara_alta, outline="")
            self.create_arc(9, 4 + dy, w - 9, int(h * 0.56) + dy, start=25, extent=130, style=tk.ARC, outline=brillo_top, width=2)
        else:
            r = 11 if h <= 36 else 13
            # Sombra 3D proyectada
            _rect_redondeado(self, 4, 7, w - 1, h, r, fill="#040509", outline="")
            # Pedestal inferior 3D (da sensacion de tecla fisica elevada)
            _rect_redondeado(self, 2, 5 + dy, w - 2, h - 1 + dy, r, fill=pedestal, outline=borde_ext, width=1)
            # Cara frontal en degradado 3D liso (3 capas suaves)
            _rect_redondeado(self, 2, 1 + dy, w - 2, h - 5 + dy, r, fill=cara_baja, outline=borde_ext, width=1)
            _rect_redondeado(self, 3, 2 + dy, w - 3, int(h * 0.68) + dy, max(6, r - 2), fill=cara_media, outline="")
            _rect_redondeado(self, 5, 2 + dy, w - 5, int(h * 0.42) + dy, max(5, r - 4), fill=cara_alta, outline="")
            # Halo de luz superior limpio
            self.create_line(10, 3 + dy, w - 10, 3 + dy, fill=brillo_top, width=1)

        cx = w / 2
        cy = (h / 2) - 2 + dy

        if self.icono:
            self._dibujar_icono(cx, cy, fg_c)
        elif self.texto:
            self.create_text(
                cx, cy,
                text=self.texto,
                fill=fg_c,
                font=("Arial", 8 if h <= 34 else 9, "bold" if (self.primario or self.activo or h <= 36) else "normal"),
            )

        if self.subtexto:
            self.create_text(
                cx, h + 8,
                text=self.subtexto,
                fill=TEXT_MAIN if (self.hover or self.activo or self.primario) else TEXT_SEC,
                font=("Arial", 7, "bold" if (self.primario or self.activo) else "normal"),
            )

    def _dibujar_icono(self, cx, cy, color):
        ico = self.icono
        if ico == "play":
            pts_sombra = [cx - 5, cy - 9, cx - 5, cy + 12, cx + 13, cy + 1]
            pts = [cx - 7, cy - 11, cx - 7, cy + 11, cx + 12, cy]
            self.create_polygon(pts_sombra, fill="#5A0615", outline="")
            self.create_polygon(pts, fill=color, outline=color)
        elif ico == "pause":
            self.create_rectangle(cx - 7, cy - 9, cx - 2, cy + 9, fill=color, outline="")
            self.create_rectangle(cx + 2, cy - 9, cx + 7, cy + 9, fill=color, outline="")
        elif ico == "stop":
            self.create_rectangle(cx - 7, cy - 7, cx + 7, cy + 7, fill=color, outline="")
        elif ico == "prev":
            self.create_rectangle(cx - 9, cy - 8, cx - 6, cy + 8, fill=color, outline="")
            self.create_polygon([cx - 5, cy, cx + 3, cy - 8, cx + 3, cy + 8], fill=color, outline="")
            self.create_polygon([cx + 2, cy, cx + 10, cy - 8, cx + 10, cy + 8], fill=color, outline="")
        elif ico == "next":
            self.create_polygon([cx - 10, cy - 8, cx - 10, cy + 8, cx - 2, cy], fill=color, outline="")
            self.create_polygon([cx - 3, cy - 8, cx - 3, cy + 8, cx + 5, cy], fill=color, outline="")
            self.create_rectangle(cx + 6, cy - 8, cx + 9, cy + 8, fill=color, outline="")
        elif ico == "back10":
            self.create_arc(cx - 10, cy - 10, cx + 10, cy + 10, start=125, extent=-275, style=tk.ARC, outline=color, width=2)
            self.create_polygon([cx - 9, cy - 9, cx - 3, cy - 11, cx - 6, cy - 4], fill=color, outline="")
            self.create_text(cx, cy + 1, text="10", fill=color, font=("Arial", 7, "bold"))
        elif ico == "fwd10":
            self.create_arc(cx - 10, cy - 10, cx + 10, cy + 10, start=55, extent=275, style=tk.ARC, outline=color, width=2)
            self.create_polygon([cx + 9, cy - 9, cx + 3, cy - 11, cx + 6, cy - 4], fill=color, outline="")
            self.create_text(cx, cy + 1, text="10", fill=color, font=("Arial", 7, "bold"))
        elif ico == "shuffle":
            self.create_line(cx - 10, cy - 6, cx - 3, cy - 6, cx + 4, cy + 6, cx + 9, cy + 6, fill=color, width=2, smooth=True)
            self.create_line(cx - 10, cy + 6, cx - 3, cy + 6, cx + 4, cy - 6, cx + 9, cy - 6, fill=color, width=2, smooth=True)
            self.create_polygon([cx + 7, cy - 9, cx + 11, cy - 6, cx + 7, cy - 3], fill=color, outline="")
            self.create_polygon([cx + 7, cy + 3, cx + 11, cy + 6, cx + 7, cy + 9], fill=color, outline="")
        elif ico == "repeat":
            self.create_line(cx - 9, cy - 4, cx - 9, cy - 7, cx + 8, cy - 7, fill=color, width=2)
            self.create_polygon([cx + 6, cy - 10, cx + 11, cy - 7, cx + 6, cy - 4], fill=color, outline="")
            self.create_line(cx + 9, cy + 4, cx + 9, cy + 7, cx - 8, cy + 7, fill=color, width=2)
            self.create_polygon([cx - 6, cy + 4, cx - 11, cy + 7, cx - 6, cy + 10], fill=color, outline="")
        elif ico == "volume":
            self.create_polygon(
                [cx - 9, cy - 4, cx - 5, cy - 4, cx, cy - 8, cx, cy + 8, cx - 5, cy + 4, cx - 9, cy + 4],
                fill=color, outline=""
            )
            if self.nivel_volumen == 0:
                self.create_line(cx + 3, cy - 5, cx + 10, cy + 5, fill=UVM_RED_LIGHT, width=2)
                self.create_line(cx + 10, cy - 5, cx + 3, cy + 5, fill=UVM_RED_LIGHT, width=2)
            else:
                self.create_arc(cx + 1, cy - 5, cx + 7, cy + 5, start=-55, extent=110, style=tk.ARC, outline=color, width=2)
                if self.nivel_volumen >= 45:
                    self.create_arc(cx + 3, cy - 9, cx + 12, cy + 9, start=-55, extent=110, style=tk.ARC, outline=color, width=2)
        elif ico == "folder":
            self.create_polygon(
                [cx - 90, cy - 7, cx - 81, cy - 7, cx - 78, cy - 4, cx - 69, cy - 4, cx - 69, cy + 7, cx - 90, cy + 7],
                fill=color, outline=""
            )
            self.create_text(cx + 10, cy, text="Cargar carpeta de musica", fill=color, font=("Arial", 9, "bold"))
        elif ico == "add_file":
            self.create_line(cx - 86, cy, cx - 74, cy, fill=color, width=2)
            self.create_line(cx - 80, cy - 6, cx - 80, cy + 6, fill=color, width=2)
            self.create_text(cx + 8, cy, text="Agregar pistas a la lista", fill=color, font=("Arial", 8, "bold"))


class BarraVolumen3D(tk.Canvas):
    """Control deslizante de volumen 3D moderno con barra luminosa y perilla esferica."""

    def __init__(self, padre, comando, valor_inicial=70, ancho=132, alto=26, bg_padre=BG_PLAYER):
        super().__init__(padre, width=ancho, height=alto, bg=bg_padre, highlightthickness=0, bd=0, cursor="hand2")
        self.comando = comando
        self.valor = valor_inicial
        self.ancho = ancho
        self.alto = alto
        self.hover = False

        self.bind("<Button-1>", self._actualizar_desde_evento)
        self.bind("<B1-Motion>", self._actualizar_desde_evento)
        self.bind("<Enter>", self._al_entrar)
        self.bind("<Leave>", self._al_salir)
        self.redibujar()

    def _al_entrar(self, _e):
        self.hover = True
        self.redibujar()

    def _al_salir(self, _e):
        self.hover = False
        self.redibujar()

    def _actualizar_desde_evento(self, evento):
        margen = 10
        x = max(margen, min(self.ancho - margen, evento.x))
        nuevo = int(round(((x - margen) / (self.ancho - 2 * margen)) * 100))
        self.set(nuevo)

    def get(self) -> int:
        return self.valor

    def set(self, nuevo_valor):
        self.valor = max(0, min(100, int(float(nuevo_valor))))
        self.redibujar()
        if callable(self.comando):
            self.comando(self.valor)

    def redibujar(self):
        self.delete("all")
        m = 10
        cy = self.alto / 2
        x0, x1 = m, self.ancho - m
        x_val = x0 + (self.valor / 100.0) * (x1 - x0)

        self.create_line(x0, cy, x1, cy, fill="#06070B", width=8, capstyle=tk.ROUND)
        self.create_line(x0, cy, x1, cy, fill="#282E45", width=6, capstyle=tk.ROUND)
        if self.valor > 0:
            self.create_line(x0, cy, x_val, cy, fill=UVM_RED_BRIGHT, width=6, capstyle=tk.ROUND)
            self.create_line(x0, cy - 1, x_val, cy - 1, fill=UVM_RED_LIGHT, width=1, capstyle=tk.ROUND)
        r = 7 if self.hover else 6
        self.create_oval(x_val - r - 1, cy - r, x_val + r + 1, cy + r + 2, fill="#05060A", outline="")
        self.create_oval(x_val - r, cy - r, x_val + r, cy + r, fill=TEXT_MAIN, outline=UVM_RED_BRIGHT, width=2)


class ScrollbarDarkUVM(tk.Canvas):
    """Barra de desplazamiento oscura moderna acorde al tema UVM MUSIC (sin estilo clasico de Windows)."""

    def __init__(self, padre, comando, ancho=12, bg_track="#111420"):
        super().__init__(padre, width=ancho, bg=bg_track, highlightthickness=0, bd=0, cursor="hand2")
        self.comando = comando
        self.ancho = ancho
        self.bg_track = bg_track
        self.first = 0.0
        self.last = 1.0
        self.hover = False
        self.arrastrando = False
        self.offset_y = 0.0

        self.bind("<Configure>", lambda _e: self.redibujar())
        self.bind("<Enter>", self._al_entrar)
        self.bind("<Leave>", self._al_salir)
        self.bind("<ButtonPress-1>", self._al_presionar)
        self.bind("<B1-Motion>", self._al_arrastrar)
        self.bind("<ButtonRelease-1>", self._al_soltar)

    def set(self, first, last):
        self.first = float(first)
        self.last = float(last)
        self.redibujar()

    def _al_entrar(self, _e):
        self.hover = True
        self.redibujar()

    def _al_salir(self, _e):
        self.hover = False
        self.redibujar()

    def _al_presionar(self, evento):
        h = max(self.winfo_height(), 1)
        y0 = self.first * h
        y1 = self.last * h
        if y0 <= evento.y <= y1:
            self.arrastrando = True
            self.offset_y = evento.y - y0
        else:
            frac = max(0.0, min(1.0, (evento.y / h) - (self.last - self.first) / 2))
            self.comando("moveto", frac)
        self.redibujar()

    def _al_arrastrar(self, evento):
        if not self.arrastrando:
            return
        h = max(self.winfo_height(), 1)
        nueva_first = max(0.0, min(1.0 - (self.last - self.first), (evento.y - self.offset_y) / h))
        self.comando("moveto", nueva_first)

    def _al_soltar(self, _e):
        self.arrastrando = False
        self.redibujar()

    def redibujar(self):
        self.delete("all")
        h = max(self.winfo_height(), 20)
        # Carril oscuro minimalista
        self.create_rectangle(0, 0, self.ancho, h, fill=self.bg_track, outline="")
        y0 = max(4, int(self.first * h) + 2)
        y1 = min(h - 4, max(y0 + 28, int(self.last * h) - 2))
        if self.arrastrando or self.hover:
            color_thumb = UVM_RED_BRIGHT
        else:
            color_thumb = "#3B4363"
        _rect_redondeado(self, 2, y0, self.ancho - 2, y1, 4, fill=color_thumb, outline="")


class ReproductorUVMDeezerPro:
    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.raiz.title("UVM MUSIC - Proyecto Integrador Etapa 2")
        self.raiz.geometry("1140x740")
        self.raiz.minsize(980, 660)
        self.raiz.configure(bg=BG_APP)

        mixer.init()

        self.carpeta_actual = ""
        self.rutas_todas = []
        self.rutas_visibles = []
        self.favoritas = set()
        self.solo_favoritas = False
        self.orden_desc = False
        self.indice_actual = -1
        self.esta_pausado = False
        self.esta_reproduciendo = False
        self.modo_aleatorio = False
        self.modo_repetir = False
        self.esta_silenciado = False
        self.volumen_previo = 70
        self.duracion_total = 0.0
        self.desplazamiento_seg = 0.0
        self.barras_eq = []
        self.topes_eq = []
        self.placeholder_activo = True

        self._construir_interfaz()
        self._actualizar_tiempo()
        self._animar_ecualizador()

    def _construir_interfaz(self):
        zona_superior = tk.Frame(self.raiz, bg=BG_APP)
        zona_superior.pack(fill=tk.BOTH, expand=True)

        # ---- SIDEBAR IZQUIERDO ----
        sidebar = tk.Frame(zona_superior, bg=BG_SIDEBAR, width=290)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Linea vertical de contraste entre sidebar y panel principal
        tk.Frame(zona_superior, bg=BORDER_CONTRAST, width=2).pack(side=tk.LEFT, fill=tk.Y)

        # Logo grande UVM MUSIC en la parte superior del sidebar
        marco_logo = tk.Frame(sidebar, bg=BG_SIDEBAR, padx=20, pady=16)
        marco_logo.pack(fill=tk.X)

        self.canvas_logo = tk.Canvas(marco_logo, width=244, height=112, bg=BG_SIDEBAR, highlightthickness=0)
        self.canvas_logo.pack()

        self.barras_eq = []
        self.topes_eq = []
        for i in range(12):
            x0 = 28 + i * 16
            barra = self.canvas_logo.create_rectangle(x0, 40, x0 + 11, 52, fill=UVM_RED_BRIGHT if i % 2 else UVM_RED, outline="")
            tope = self.canvas_logo.create_rectangle(x0, 37, x0 + 11, 39, fill=UVM_RED_LIGHT, outline="")
            self.barras_eq.append(barra)
            self.topes_eq.append(tope)

        self.canvas_logo.create_text(124, 78, text="UVM MUSIC", fill="#3A0610", font=("Arial", 24, "bold"))
        self.canvas_logo.create_text(122, 76, text="UVM MUSIC", fill=TEXT_MAIN, font=("Arial", 24, "bold"))
        self.canvas_logo.create_text(122, 100, text="REPRODUCTOR DE ESCRITORIO", fill=UVM_RED_LIGHT, font=("Arial", 8, "bold"))

        # Insignia de estado con alto contraste
        self.etiqueta_estado = tk.Label(
            sidebar,
            text="LISTO PARA REPRODUCIR",
            font=("Arial", 8, "bold"),
            bg="#261019",
            fg="#FFD6DE",
            highlightbackground=UVM_RED,
            highlightthickness=1,
            pady=6,
        )
        self.etiqueta_estado.pack(fill=tk.X, padx=20, pady=(0, 10))

        # Inciso e) Boton 3D principal para cargar carpeta de musica
        self.btn_cargar = Boton3D(
            sidebar,
            comando=self.cargar_carpeta,
            ancho=248,
            alto=42,
            forma="pill",
            icono="folder",
            primario=True,
            bg_padre=BG_SIDEBAR,
        )
        self.btn_cargar.pack(padx=20, pady=(0, 6))

        # Funcion extra 1: Agregar pistas individuales sin borrar la carpeta actual
        self.btn_agregar = Boton3D(
            sidebar,
            comando=self.agregar_archivos,
            ancho=248,
            alto=36,
            forma="pill",
            icono="add_file",
            primario=False,
            bg_padre=BG_SIDEBAR,
        )
        self.btn_agregar.pack(padx=20, pady=(0, 6))

        self.etiqueta_carpeta = tk.Label(
            sidebar,
            text="Ninguna carpeta cargada",
            font=("Arial", 8),
            bg=BG_SIDEBAR,
            fg=TEXT_SEC,
            wraplength=244,
            justify=tk.LEFT,
        )
        self.etiqueta_carpeta.pack(fill=tk.X, padx=22, pady=(0, 8))

        # Funcion extra 2: Panel de Gestion de Playlist (Filtros Favoritas y Orden A-Z / Z-A)
        panel_gestion = tk.Frame(
            sidebar,
            bg=BG_CARD,
            highlightbackground=BORDER_CONTRAST,
            highlightthickness=1,
            padx=10,
            pady=8,
        )
        panel_gestion.pack(fill=tk.X, padx=18, pady=(0, 8))

        tk.Label(
            panel_gestion,
            text="GESTION DE PLAYLIST",
            font=("Arial", 7, "bold"),
            bg=BG_CARD,
            fg=UVM_RED_LIGHT,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 6))

        fila_filtros = tk.Frame(panel_gestion, bg=BG_CARD)
        fila_filtros.pack(fill=tk.X, pady=(0, 5))

        self.btn_ver_todas = Boton3D(
            fila_filtros,
            comando=lambda: self._cambiar_vista_favoritas(False),
            ancho=110,
            alto=30,
            forma="pill",
            texto="Todas",
            bg_padre=BG_CARD,
        )
        self.btn_ver_todas.establecer_activo(True)
        self.btn_ver_todas.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_ver_favs = Boton3D(
            fila_filtros,
            comando=lambda: self._cambiar_vista_favoritas(True),
            ancho=110,
            alto=30,
            forma="pill",
            texto="Favoritas (0)",
            bg_padre=BG_CARD,
        )
        self.btn_ver_favs.pack(side=tk.LEFT)

        fila_orden = tk.Frame(panel_gestion, bg=BG_CARD)
        fila_orden.pack(fill=tk.X, pady=(0, 5))

        self.btn_orden_az = Boton3D(
            fila_orden,
            comando=lambda: self._ordenar_lista(descendente=False),
            ancho=110,
            alto=30,
            forma="pill",
            texto="Orden A-Z",
            bg_padre=BG_CARD,
        )
        self.btn_orden_az.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_orden_za = Boton3D(
            fila_orden,
            comando=lambda: self._ordenar_lista(descendente=True),
            ancho=110,
            alto=30,
            forma="pill",
            texto="Orden Z-A",
            bg_padre=BG_CARD,
        )
        self.btn_orden_za.pack(side=tk.LEFT)

        self.btn_marcar_fav = Boton3D(
            panel_gestion,
            comando=self.alternar_favorita_actual,
            ancho=226,
            alto=32,
            forma="pill",
            texto="Marcar pista como Favorita",
            bg_padre=BG_CARD,
        )
        self.btn_marcar_fav.pack(pady=(2, 0))

        # Funcion extra 3: Ficha en vivo de detalles tecnicos de la pista seleccionada
        panel_detalles = tk.Frame(
            sidebar,
            bg=BG_CARD,
            highlightbackground=BORDER_CONTRAST,
            highlightthickness=1,
            padx=10,
            pady=8,
        )
        panel_detalles.pack(fill=tk.X, padx=18, pady=(0, 6))

        tk.Label(
            panel_detalles,
            text="DETALLES DE LA PISTA",
            font=("Arial", 7, "bold"),
            bg=BG_CARD,
            fg=UVM_RED_LIGHT,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        self.lbl_info_pista = tk.Label(
            panel_detalles,
            text="Formato: --  |  Tamano: --\nPosicion: --  |  Favoritas: 0",
            font=("Arial", 8),
            bg=BG_CARD,
            fg=TEXT_SOFT,
            justify=tk.LEFT,
            anchor="w",
        )
        self.lbl_info_pista.pack(fill=tk.X)

        # Tarjeta institucional inferior con materia + Proyecto Integrador Etapa 2 + Equipo 2
        pie_sidebar = tk.Frame(
            sidebar,
            bg="#151824",
            highlightbackground=UVM_RED,
            highlightthickness=1,
            padx=12,
            pady=10,
        )
        pie_sidebar.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=12)

        tk.Label(
            pie_sidebar,
            text="Universidad del Valle de Mexico",
            font=("Arial", 8, "bold"),
            bg="#151824",
            fg=UVM_RED_LIGHT,
            anchor="w",
        ).pack(fill=tk.X)

        tk.Label(
            pie_sidebar,
            text="Algoritmos y Complejidad Computacional",
            font=("Arial", 8, "bold"),
            bg="#151824",
            fg=TEXT_MAIN,
            anchor="w",
            wraplength=224,
            justify=tk.LEFT,
        ).pack(fill=tk.X, pady=(1, 1))

        tk.Label(
            pie_sidebar,
            text="Proyecto Integrador Etapa 2",
            font=("Arial", 8, "bold"),
            bg="#151824",
            fg=TEXT_SEC,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))

        tk.Frame(pie_sidebar, bg=UVM_RED, height=1).pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            pie_sidebar,
            text="EQUIPO 2",
            font=("Arial", 8, "bold"),
            bg="#151824",
            fg=UVM_RED_LIGHT,
            anchor="w",
        ).pack(fill=tk.X)

        tk.Label(
            pie_sidebar,
            text="Emmanuel Arellano Garcia\nHugo Armando Arias Lopez\nJose Augusto Canul Chi",
            font=("Arial", 8),
            bg="#151824",
            fg=TEXT_SOFT,
            justify=tk.LEFT,
            anchor="w",
        ).pack(fill=tk.X, pady=(2, 0))

        # ---- PANEL PRINCIPAL DERECHO ----
        panel_main = tk.Frame(zona_superior, bg=BG_APP, padx=24, pady=18)
        panel_main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Hero Banner de alto contraste
        hero_marco = tk.Frame(panel_main, bg=UVM_RED_BRIGHT, padx=1, pady=1)
        hero_marco.pack(fill=tk.X, pady=(0, 14))

        hero = tk.Frame(hero_marco, bg="#360916", padx=22, pady=16)
        hero.pack(fill=tk.X)

        tk.Label(
            hero,
            text="BIBLIOTECA LOCAL",
            font=("Arial", 8, "bold"),
            bg="#360916",
            fg="#FF9CAE",
            anchor="w",
        ).pack(fill=tk.X)

        # Inciso d) Mostrar titulo de la cancion actualmente seleccionada
        self.etiqueta_titulo = tk.Label(
            hero,
            text="Carga una carpeta para comenzar a escuchar",
            font=("Arial", 18, "bold"),
            bg="#360916",
            fg=TEXT_MAIN,
            anchor="w",
        )
        self.etiqueta_titulo.pack(fill=tk.X, pady=(5, 4))

        self.etiqueta_resumen = tk.Label(
            hero,
            text="0 canciones | Formatos soportados: MP3, WAV, OGG | Haz doble clic en cualquier pista",
            font=("Arial", 9),
            bg="#360916",
            fg="#F5D7DE",
            anchor="w",
        )
        self.etiqueta_resumen.pack(fill=tk.X)

        # Barra de busqueda en vivo de alto contraste con placeholder y boton limpiar
        marco_filtro = tk.Frame(panel_main, bg=BG_APP)
        marco_filtro.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            marco_filtro,
            text="Buscar pista:",
            font=("Arial", 9, "bold"),
            bg=BG_APP,
            fg=TEXT_MAIN,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.caja_busqueda = tk.Frame(
            marco_filtro,
            bg=BG_INPUT,
            highlightbackground=BORDER_CONTRAST,
            highlightthickness=2,
            padx=10,
            pady=4,
        )
        self.caja_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.var_filtro = tk.StringVar()
        self.entrada_busqueda = tk.Entry(
            self.caja_busqueda,
            textvariable=self.var_filtro,
            font=("Arial", 10),
            bg=BG_INPUT,
            fg=TEXT_MUTED,
            insertbackground=TEXT_MAIN,
            relief=tk.FLAT,
            bd=0,
        )
        self.entrada_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.entrada_busqueda.insert(0, PLACEHOLDER_TEXT)
        self.entrada_busqueda.bind("<FocusIn>", self._busqueda_focus_in)
        self.entrada_busqueda.bind("<FocusOut>", self._busqueda_focus_out)
        self.var_filtro.trace_add("write", lambda *_: self._aplicar_filtro())

        btn_limpiar = Boton3D(
            self.caja_busqueda,
            comando=self._limpiar_busqueda,
            ancho=72,
            alto=28,
            forma="pill",
            texto="Limpiar",
            bg_padre=BG_INPUT,
        )
        btn_limpiar.pack(side=tk.RIGHT, padx=(8, 0))

        # Encabezado de tracklist
        cabecera_lista = tk.Frame(panel_main, bg="#191D2B", highlightbackground=BORDER_CONTRAST, highlightthickness=1, padx=12, pady=7)
        cabecera_lista.pack(fill=tk.X)
        tk.Label(cabecera_lista, text="#     NOMBRE DE LA PISTA", font=("Arial", 8, "bold"), bg="#191D2B", fg=TEXT_SOFT).pack(side=tk.LEFT)
        self.etiqueta_conteo = tk.Label(cabecera_lista, text="0 pistas", font=("Arial", 8, "bold"), bg="#191D2B", fg=UVM_RED_LIGHT)
        self.etiqueta_conteo.pack(side=tk.RIGHT)

        # Inciso f) Lista de reproduccion de alto contraste
        marco_lista = tk.Frame(panel_main, bg=BG_CARD, highlightbackground=BORDER_CONTRAST, highlightthickness=1)
        marco_lista.pack(fill=tk.BOTH, expand=True)

        self.lista_canciones = tk.Listbox(
            marco_lista,
            font=("Arial", 10),
            bg=BG_CARD,
            fg=TEXT_MAIN,
            selectbackground=UVM_RED,
            selectforeground=TEXT_MAIN,
            activestyle="none",
            bd=0,
            highlightthickness=0,
            selectmode=tk.SINGLE,
        )
        scroll = ScrollbarDarkUVM(marco_lista, self.lista_canciones.yview, ancho=12, bg_track="#10131F")
        scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 3), pady=4)
        self.lista_canciones.config(yscrollcommand=scroll.set)
        self.lista_canciones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=8)
        self.lista_canciones.bind("<<ListboxSelect>>", self.al_seleccionar_cancion)
        self.lista_canciones.bind("<Double-Button-1>", lambda _e: self.reproducir())

        # ---- BARRA INFERIOR FIJA 3D AISLADA CON LINEA DE CONTRASTE EN TODO EL RECTANGULO ----
        barra_player = tk.Frame(
            self.raiz,
            bg=BG_PLAYER,
            height=158,
            highlightbackground=UVM_RED_BRIGHT,
            highlightthickness=2,
        )
        barra_player.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(2, 2))
        barra_player.pack_propagate(False)

        # Inciso h) Barra de progreso 3D interactiva + tiempo transcurrido y duracion total
        fila_progreso = tk.Frame(barra_player, bg=BG_PLAYER, padx=24, pady=8)
        fila_progreso.pack(fill=tk.X)

        self.etiqueta_actual_seg = tk.Label(fila_progreso, text="00:00", font=("Arial", 9, "bold"), bg=BG_PLAYER, fg=TEXT_MAIN, width=6)
        self.etiqueta_actual_seg.pack(side=tk.LEFT)

        self.canvas_progreso = tk.Canvas(fila_progreso, height=18, bg=BG_PLAYER, highlightthickness=0, cursor="hand2")
        self.canvas_progreso.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)
        self.canvas_progreso.bind("<Button-1>", self._saltar_en_barra)
        self.canvas_progreso.bind("<Configure>", lambda _e: self._dibujar_barra(0.0))

        self.etiqueta_total_seg = tk.Label(fila_progreso, text="00:00", font=("Arial", 9, "bold"), bg=BG_PLAYER, fg=TEXT_SEC, width=6)
        self.etiqueta_total_seg.pack(side=tk.LEFT)

        # Fila principal de controles 3D con iconos vectoriales realistas
        fila_controles = tk.Frame(barra_player, bg=BG_PLAYER, padx=24, pady=4)
        fila_controles.pack(fill=tk.BOTH, expand=True)

        # Izquierda: indicador de tiempo combinado
        marco_tiempo = tk.Frame(fila_controles, bg=BG_CARD_ALT, highlightbackground=BORDER_CONTRAST, highlightthickness=1, padx=12, pady=8)
        marco_tiempo.pack(side=tk.LEFT, pady=8)
        self.etiqueta_tiempo = tk.Label(
            marco_tiempo,
            text="Tiempo: 00:00 / 00:00",
            font=("Arial", 9, "bold"),
            bg=BG_CARD_ALT,
            fg=TEXT_MAIN,
            width=19,
            anchor="w",
        )
        self.etiqueta_tiempo.pack()

        # Centro: botones 3D con simbolos realistas (Incisos c y f)
        marco_botones = tk.Frame(fila_controles, bg=BG_PLAYER)
        marco_botones.pack(side=tk.LEFT, expand=True)

        self.btn_shuffle = Boton3D(marco_botones, self.alternar_aleatorio, ancho=46, alto=42, forma="pill", icono="shuffle", subtexto="Aleatorio")
        self.btn_shuffle.pack(side=tk.LEFT, padx=4)

        self.btn_prev = Boton3D(marco_botones, self.retroceder_cancion, ancho=46, alto=42, forma="pill", icono="prev", subtexto="Anterior")
        self.btn_prev.pack(side=tk.LEFT, padx=4)

        self.btn_back10 = Boton3D(marco_botones, self.devolver_segundos, ancho=46, alto=42, forma="pill", icono="back10", subtexto="-10 seg")
        self.btn_back10.pack(side=tk.LEFT, padx=4)

        self.btn_play = Boton3D(marco_botones, self.reproducir, ancho=56, alto=56, forma="circle", icono="play", subtexto="Reproducir", primario=True)
        self.btn_play.pack(side=tk.LEFT, padx=8)

        self.btn_pause = Boton3D(marco_botones, self.pausar, ancho=46, alto=42, forma="pill", icono="pause", subtexto="Pausar")
        self.btn_pause.pack(side=tk.LEFT, padx=4)

        self.btn_stop = Boton3D(marco_botones, self.detener, ancho=46, alto=42, forma="pill", icono="stop", subtexto="Detener")
        self.btn_stop.pack(side=tk.LEFT, padx=4)

        self.btn_fwd10 = Boton3D(marco_botones, self.avanzar_segundos, ancho=46, alto=42, forma="pill", icono="fwd10", subtexto="+10 seg")
        self.btn_fwd10.pack(side=tk.LEFT, padx=4)

        self.btn_next = Boton3D(marco_botones, self.adelantar_cancion, ancho=46, alto=42, forma="pill", icono="next", subtexto="Siguiente")
        self.btn_next.pack(side=tk.LEFT, padx=4)

        self.btn_repeat = Boton3D(marco_botones, self.alternar_repetir, ancho=46, alto=42, forma="pill", icono="repeat", subtexto="Repetir")
        self.btn_repeat.pack(side=tk.LEFT, padx=4)

        # Derecha: Modulo de volumen 3D moderno (Inciso g)
        marco_vol = tk.Frame(fila_controles, bg=BG_CARD_ALT, highlightbackground=BORDER_CONTRAST, highlightthickness=1, padx=10, pady=6)
        marco_vol.pack(side=tk.RIGHT, pady=6)

        self.btn_mute = Boton3D(
            marco_vol,
            self.alternar_silencio,
            ancho=38,
            alto=38,
            forma="circle",
            icono="volume",
            bg_padre=BG_CARD_ALT,
        )
        self.btn_mute.pack(side=tk.LEFT, padx=(0, 8))

        self.control_volumen = BarraVolumen3D(
            marco_vol,
            comando=self.ajustar_volumen,
            valor_inicial=70,
            ancho=124,
            alto=26,
            bg_padre=BG_CARD_ALT,
        )
        self.control_volumen.pack(side=tk.LEFT, padx=(0, 6))

        self.etiqueta_vol = tk.Label(
            marco_vol,
            text="70%",
            font=("Arial", 9, "bold"),
            bg=BG_CARD_ALT,
            fg=TEXT_MAIN,
            width=4,
            anchor="e",
        )
        self.etiqueta_vol.pack(side=tk.LEFT)
        mixer.music.set_volume(0.7)

    def _busqueda_focus_in(self, _e):
        self.caja_busqueda.config(highlightbackground=UVM_RED_BRIGHT)
        if self.placeholder_activo:
            self.placeholder_activo = False
            self.entrada_busqueda.delete(0, tk.END)
            self.entrada_busqueda.config(fg=TEXT_MAIN)

    def _busqueda_focus_out(self, _e):
        self.caja_busqueda.config(highlightbackground=BORDER_CONTRAST)
        if not self.entrada_busqueda.get().strip():
            self.placeholder_activo = True
            self.entrada_busqueda.delete(0, tk.END)
            self.entrada_busqueda.insert(0, PLACEHOLDER_TEXT)
            self.entrada_busqueda.config(fg=TEXT_MUTED)

    def _limpiar_busqueda(self):
        self.placeholder_activo = False
        self.entrada_busqueda.delete(0, tk.END)
        self.entrada_busqueda.config(fg=TEXT_MAIN)
        self._aplicar_filtro()
        self.entrada_busqueda.focus_set()

    def _dibujar_barra(self, porcentaje: float):
        w = max(self.canvas_progreso.winfo_width(), 100)
        porcentaje = max(0.0, min(100.0, porcentaje))
        x_fill = (porcentaje / 100.0) * w
        self.canvas_progreso.delete("all")
        self.canvas_progreso.create_line(4, 9, w - 4, 9, fill="#06070B", width=8, capstyle=tk.ROUND)
        self.canvas_progreso.create_line(4, 9, w - 4, 9, fill="#282E45", width=6, capstyle=tk.ROUND)
        if x_fill > 4:
            self.canvas_progreso.create_line(4, 9, x_fill, 9, fill=UVM_RED_BRIGHT, width=6, capstyle=tk.ROUND)
            self.canvas_progreso.create_line(4, 8, x_fill, 8, fill=UVM_RED_LIGHT, width=1, capstyle=tk.ROUND)
            self.canvas_progreso.create_oval(x_fill - 7, 2, x_fill + 7, 16, fill=UVM_RED_BRIGHT, outline="")
            self.canvas_progreso.create_oval(x_fill - 5, 4, x_fill + 5, 14, fill=TEXT_MAIN, outline="#D0D5E8", width=1)

    def _saltar_en_barra(self, evento):
        if self.esta_reproduciendo and self.duracion_total > 0 and self.indice_actual >= 0:
            w = max(self.canvas_progreso.winfo_width(), 1)
            fraccion = max(0.0, min(1.0, evento.x / w))
            nuevo_seg = fraccion * self.duracion_total
            self._cargar_y_reproducir_indice(self.indice_actual, inicio_seg=nuevo_seg)

    def _actualizar_detalles_pista(self, idx: int):
        if not self.rutas_visibles or idx < 0 or idx >= len(self.rutas_visibles):
            self.lbl_info_pista.config(text=f"Formato: --  |  Tamano: --\nPosicion: --  |  Favoritas: {len(self.favoritas)}")
            self.btn_marcar_fav.establecer_activo(False)
            self.btn_marcar_fav.establecer_texto("Marcar pista como Favorita")
            return

        ruta = self.rutas_visibles[idx]
        ext = os.path.splitext(ruta)[1].upper().lstrip(".") or "AUDIO"
        try:
            mb = os.path.getsize(ruta) / (1024 * 1024)
            tam_txt = f"{mb:.1f} MB"
        except OSError:
            tam_txt = "--"
        es_fav = ruta in self.favoritas
        self.lbl_info_pista.config(
            text=f"Formato: {ext}  |  Tamano: {tam_txt}\nPosicion: {idx + 1} de {len(self.rutas_visibles)}  |  Favoritas: {len(self.favoritas)}"
        )
        self.btn_marcar_fav.establecer_activo(es_fav)
        self.btn_marcar_fav.establecer_texto("Quitar de Favoritas" if es_fav else "Marcar pista como Favorita")

    def cargar_carpeta(self):
        carpeta = filedialog.askdirectory(title="Selecciona la carpeta con archivos de musica")
        if not carpeta:
            return

        archivos = [
            os.path.join(carpeta, nombre)
            for nombre in sorted(os.listdir(carpeta))
            if nombre.lower().endswith(FORMATOS_SOPORTADOS)
        ]

        if not archivos:
            messagebox.showinfo(
                "Sin archivos compatibles",
                "No se encontraron archivos .mp3, .wav u .ogg en la carpeta seleccionada.",
            )
            return

        self.carpeta_actual = carpeta
        self.rutas_todas = archivos
        self.solo_favoritas = False
        self.btn_ver_todas.establecer_activo(True)
        self.btn_ver_favs.establecer_activo(False)
        if not self.placeholder_activo:
            self.var_filtro.set("")
        self._poblar_lista(self.rutas_todas)

        self.etiqueta_carpeta.config(text=f"Carpeta: {carpeta}")
        self.etiqueta_resumen.config(text=f"{len(archivos)} pistas cargadas | Doble clic o pulsa Reproducir")
        self.indice_actual = 0
        self.lista_canciones.selection_set(0)
        self.etiqueta_titulo.config(text=os.path.basename(self.rutas_visibles[0]))
        self.etiqueta_estado.config(text="LISTO PARA REPRODUCIR", bg="#261019", fg="#FFD6DE")
        self._actualizar_detalles_pista(0)

    def agregar_archivos(self):
        rutas = filedialog.askopenfilenames(
            title="Selecciona pistas de audio para agregar",
            filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg")],
        )
        if not rutas:
            return
        nuevas = [r for r in rutas if r not in self.rutas_todas]
        if not nuevas:
            return
        self.rutas_todas.extend(nuevas)
        self._aplicar_filtro()
        self.etiqueta_resumen.config(text=f"{len(self.rutas_todas)} pistas en lista | Doble clic o pulsa Reproducir")
        if self.indice_actual < 0 and self.rutas_visibles:
            self.indice_actual = 0
            self.lista_canciones.selection_set(0)
            self.etiqueta_titulo.config(text=os.path.basename(self.rutas_visibles[0]))
            self._actualizar_detalles_pista(0)

    def _cambiar_vista_favoritas(self, solo_fav: bool):
        self.solo_favoritas = solo_fav
        self.btn_ver_todas.establecer_activo(not solo_fav)
        self.btn_ver_favs.establecer_activo(solo_fav)
        self._aplicar_filtro()

    def _ordenar_lista(self, descendente: bool):
        self.orden_desc = descendente
        self.btn_orden_az.establecer_activo(not descendente)
        self.btn_orden_za.establecer_activo(descendente)
        self.rutas_todas.sort(key=lambda r: os.path.basename(r).lower(), reverse=descendente)
        self._aplicar_filtro()

    def alternar_favorita_actual(self):
        if not self.rutas_visibles:
            return
        seleccion = self.lista_canciones.curselection()
        idx = seleccion[0] if seleccion else max(self.indice_actual, 0)
        if idx < 0 or idx >= len(self.rutas_visibles):
            return
        ruta = self.rutas_visibles[idx]
        if ruta in self.favoritas:
            self.favoritas.remove(ruta)
        else:
            self.favoritas.add(ruta)
        self.btn_ver_favs.establecer_texto(f"Favoritas ({len(self.favoritas)})")
        self._aplicar_filtro()
        if self.rutas_visibles:
            nuevo_idx = min(idx, len(self.rutas_visibles) - 1)
            self.lista_canciones.selection_set(nuevo_idx)
            self._actualizar_detalles_pista(nuevo_idx)
        else:
            self._actualizar_detalles_pista(-1)

    def _poblar_lista(self, rutas):
        self.rutas_visibles = list(rutas)
        self.lista_canciones.delete(0, tk.END)
        for idx, ruta in enumerate(self.rutas_visibles, start=1):
            marca_fav = "[FAV] " if ruta in self.favoritas else ""
            self.lista_canciones.insert(tk.END, f"  {idx:02d}    {marca_fav}{os.path.basename(ruta)}")
            self.lista_canciones.itemconfig(idx - 1, bg=BG_CARD if idx % 2 else BG_CARD_ALT)
        self.etiqueta_conteo.config(text=f"{len(self.rutas_visibles)} pistas")

    def _aplicar_filtro(self):
        if not self.rutas_todas:
            self._poblar_lista([])
            return
        base = [r for r in self.rutas_todas if r in self.favoritas] if self.solo_favoritas else list(self.rutas_todas)
        texto = "" if self.placeholder_activo else self.var_filtro.get().strip().lower()
        filtradas = base if not texto else [r for r in base if texto in os.path.basename(r).lower()]
        self._poblar_lista(filtradas)

    def al_seleccionar_cancion(self, _evento):
        seleccion = self.lista_canciones.curselection()
        if seleccion and seleccion[0] < len(self.rutas_visibles):
            self.etiqueta_titulo.config(text=os.path.basename(self.rutas_visibles[seleccion[0]]))
            self._actualizar_detalles_pista(seleccion[0])

    def _obtener_duracion(self, ruta: str) -> float:
        if MutagenFile is not None:
            try:
                audio = MutagenFile(ruta)
                if audio is not None and audio.info is not None:
                    return float(audio.info.length)
            except Exception:
                pass
        try:
            sonido = mixer.Sound(ruta)
            return float(sonido.get_length())
        except Exception:
            return 0.0

    def _cargar_y_reproducir_indice(self, idx: int, inicio_seg: float = 0.0):
        if not self.rutas_visibles:
            messagebox.showwarning("Lista vacia", "Primero carga una carpeta con canciones.")
            return

        self.indice_actual = idx % len(self.rutas_visibles)
        ruta = self.rutas_visibles[self.indice_actual]

        self.lista_canciones.selection_clear(0, tk.END)
        self.lista_canciones.selection_set(self.indice_actual)
        self.lista_canciones.activate(self.indice_actual)
        self.lista_canciones.see(self.indice_actual)
        self.etiqueta_titulo.config(text=os.path.basename(ruta))
        self._actualizar_detalles_pista(self.indice_actual)

        try:
            mixer.music.load(ruta)
            self.duracion_total = self._obtener_duracion(ruta)
            self.desplazamiento_seg = max(0.0, inicio_seg)
            mixer.music.play(start=self.desplazamiento_seg)
            self.esta_reproduciendo = True
            self.esta_pausado = False
            self.etiqueta_estado.config(text="REPRODUCIENDO EN VIVO", bg=UVM_RED, fg=TEXT_MAIN)
            self.etiqueta_total_seg.config(text=self._formatear_tiempo(self.duracion_total))
        except Exception as err:
            messagebox.showerror("Error de reproduccion", f"No se pudo reproducir el archivo:\n{err}")

    def reproducir(self):
        if not self.rutas_visibles:
            messagebox.showwarning("Lista vacia", "Primero carga una carpeta con canciones.")
            return

        seleccion = self.lista_canciones.curselection()
        idx_seleccionado = seleccion[0] if seleccion else max(self.indice_actual, 0)

        if self.esta_pausado and idx_seleccionado == self.indice_actual:
            mixer.music.unpause()
            self.esta_pausado = False
            self.esta_reproduciendo = True
            self.etiqueta_estado.config(text="REPRODUCIENDO EN VIVO", bg=UVM_RED, fg=TEXT_MAIN)
        else:
            self._cargar_y_reproducir_indice(idx_seleccionado, inicio_seg=0.0)

    def pausar(self):
        if self.esta_reproduciendo and not self.esta_pausado:
            mixer.music.pause()
            self.esta_pausado = True
            self.etiqueta_estado.config(text="EN PAUSA", bg="#361320", fg="#FFD6DE")

    def detener(self):
        mixer.music.stop()
        self.esta_reproduciendo = False
        self.esta_pausado = False
        self.desplazamiento_seg = 0.0
        self._dibujar_barra(0.0)
        total_txt = self._formatear_tiempo(self.duracion_total)
        self.etiqueta_actual_seg.config(text="00:00")
        self.etiqueta_total_seg.config(text=total_txt)
        self.etiqueta_tiempo.config(text=f"Tiempo: 00:00 / {total_txt}")
        self.etiqueta_estado.config(text="DETENIDO", bg="#261019", fg=TEXT_SOFT)

    def adelantar_cancion(self):
        if not self.rutas_visibles:
            return
        if self.modo_aleatorio and len(self.rutas_visibles) > 1:
            siguiente = random.choice([i for i in range(len(self.rutas_visibles)) if i != self.indice_actual])
            self._cargar_y_reproducir_indice(siguiente, inicio_seg=0.0)
        else:
            self._cargar_y_reproducir_indice(self.indice_actual + 1, inicio_seg=0.0)

    def retroceder_cancion(self):
        if self.rutas_visibles:
            self._cargar_y_reproducir_indice(self.indice_actual - 1, inicio_seg=0.0)

    def avanzar_segundos(self):
        if self.esta_reproduciendo and self.indice_actual >= 0:
            actual = self._tiempo_actual_segundos()
            nuevo_tiempo = min(actual + 10.0, max(self.duracion_total - 1.0, 0.0)) if self.duracion_total > 0 else actual + 10.0
            self._cargar_y_reproducir_indice(self.indice_actual, inicio_seg=nuevo_tiempo)

    def devolver_segundos(self):
        if self.esta_reproduciendo and self.indice_actual >= 0:
            actual = self._tiempo_actual_segundos()
            nuevo_tiempo = max(actual - 10.0, 0.0)
            self._cargar_y_reproducir_indice(self.indice_actual, inicio_seg=nuevo_tiempo)

    def alternar_aleatorio(self):
        self.modo_aleatorio = not self.modo_aleatorio
        self.btn_shuffle.establecer_activo(self.modo_aleatorio)

    def alternar_repetir(self):
        self.modo_repetir = not self.modo_repetir
        self.btn_repeat.establecer_activo(self.modo_repetir)

    def alternar_silencio(self):
        if not self.esta_silenciado:
            self.volumen_previo = int(self.control_volumen.get())
            self.control_volumen.set(0)
            self.esta_silenciado = True
        else:
            self.control_volumen.set(self.volumen_previo if self.volumen_previo > 0 else 70)
            self.esta_silenciado = False

    def ajustar_volumen(self, valor):
        nivel = int(float(valor))
        mixer.music.set_volume(nivel / 100.0)
        self.esta_silenciado = nivel == 0
        self.btn_mute.establecer_volumen(nivel)
        self.btn_mute.establecer_activo(nivel == 0)
        self.etiqueta_vol.config(text="MUTE" if nivel == 0 else f"{nivel}%")

    def _tiempo_actual_segundos(self) -> float:
        pos_ms = mixer.music.get_pos()
        if pos_ms < 0:
            return self.desplazamiento_seg
        return self.desplazamiento_seg + (pos_ms / 1000.0)

    @staticmethod
    def _formatear_tiempo(segundos: float) -> str:
        segundos = max(0, int(segundos))
        minutos, seg = divmod(segundos, 60)
        return f"{minutos:02d}:{seg:02d}"

    def _animar_ecualizador(self):
        alturas_reposo = [12, 22, 32, 18, 28, 38, 24, 34, 20, 30, 16, 22]
        for i, barra in enumerate(self.barras_eq):
            x0 = 28 + i * 16
            altura = random.randint(10, 44) if (self.esta_reproduciendo and not self.esta_pausado) else alturas_reposo[i]
            y_top = 52 - altura
            self.canvas_logo.coords(barra, x0, y_top, x0 + 11, 52)
            self.canvas_logo.coords(self.topes_eq[i], x0, y_top - 3, x0 + 11, y_top - 1)
        self.raiz.after(150, self._animar_ecualizador)

    def _actualizar_tiempo(self):
        if self.esta_reproduciendo and not self.esta_pausado:
            if mixer.music.get_busy():
                transcurrido = self._tiempo_actual_segundos()
                porcentaje = min((transcurrido / self.duracion_total) * 100.0, 100.0) if self.duracion_total > 0 else 0.0
                self._dibujar_barra(porcentaje)
                txt_act = self._formatear_tiempo(transcurrido)
                txt_tot = self._formatear_tiempo(self.duracion_total)
                self.etiqueta_actual_seg.config(text=txt_act)
                self.etiqueta_total_seg.config(text=txt_tot)
                self.etiqueta_tiempo.config(text=f"Tiempo: {txt_act} / {txt_tot}")
            else:
                if self.modo_repetir:
                    self._cargar_y_reproducir_indice(self.indice_actual, inicio_seg=0.0)
                elif len(self.rutas_visibles) > 1:
                    self.adelantar_cancion()
                else:
                    self.detener()
        self.raiz.after(300, self._actualizar_tiempo)

    def cerrar(self):
        mixer.music.stop()
        mixer.quit()
        self.raiz.destroy()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = ReproductorUVMDeezerPro(ventana)
    ventana.protocol("WM_DELETE_WINDOW", app.cerrar)
    ventana.mainloop()