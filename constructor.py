"""
constructor.py
===============
Pantalla "Sentences - Verbo" de Speakly (Presente / Pasado / Futuro).

Sigue la convencion de pantallas que acordo el equipo:
    - Clase: PantallaConstructor(ctk.CTkFrame)
    - Firma: __init__(self, master, usuario, **kwargs)
    - Datos en JSON (datos/verbos.json y datos/progreso.json), no en .txt

Correspondencia con el diagrama de clases del equipo:
    SentenceExercise (armar oracion) -> clase OracionEjercicio
        sourcePhrase   -> frase_origen
        wordBank       -> banco_palabras
        selectedWords  -> palabras_seleccionadas
        instruction    -> instruccion
        checkOrder()   -> verificar_orden()

Que hace este modulo:
    1) Por cada verbo, muestra 3 tarjetas numeradas: PRESENT, PAST, FUTURE.
    2) Cada tarjeta tiene una frase en español y un banco de palabras en
       ingles (las correctas + algunas de relleno) para que el usuario
       las vaya click-eando EN ORDEN y arme la oracion.
    3) Hay un boton para escuchar la oracion correcta en ingles.
    4) Si se equivoca, puede "Try again" (se le permiten varios intentos).
    5) Cuando termina las 3 oraciones de un verbo, guarda el progreso en
       datos/progreso.json y ELLA MISMA importa y muestra PantallaAprender
       para que el usuario siga con el vocabulario del siguiente verbo
       (tal como se acordo: cada pantalla llama a la siguiente).

Como lo integra el resto del equipo (main.py):
    from constructor import PantallaConstructor

    frame = PantallaConstructor(self.contenido, usuario_actual)
    frame.pack(fill="both", expand=True)

aprender.py debe tener, en algun punto equivalente (cuando el usuario
acierta una palabra), este mismo tipo de llamado pero al reves:
    from constructor import PantallaConstructor
    PantallaConstructor(self.master, self.usuario).pack(fill="both", expand=True)

Este archivo se puede ejecutar solo (python constructor.py) para probarlo
sin depender de que el resto del proyecto este terminado. Si aprender.py
todavia no existe o no tiene la clase PantallaAprender, este modulo NO se
rompe: simplemente sigue mostrando el constructor con el siguiente verbo.
"""

import os
import json
import random
import threading

import customtkinter as ctk
from PIL import Image

# Ya NO se usa pyttsx3 "en vivo" dentro de la app (eso era lo que se
# buggeaba: cada click creaba un motor de voz nuevo y chocaba con el
# anterior). Ahora se reproducen archivos .wav pre-generados con
# generar_audios.py (correrlo UNA VEZ, ver ese archivo).
# winsound es de la libreria estandar de Python en Windows; en Mac/Linux
# no existe, por eso el import va adentro de un try/except.
try:
    import winsound
except ImportError:
    winsound = None

_audio_ocupado = False


# ---------------------------------------------------------------------------
# Rutas (todo relativo a este archivo)
# ---------------------------------------------------------------------------
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_VERBOS_JSON = os.path.join(RUTA_BASE, "datos", "verbos.json")
RUTA_PROGRESO_JSON = os.path.join(RUTA_BASE, "datos", "progreso.json")
RUTA_IMAGENES_VERBOS = os.path.join(RUTA_BASE, "imagenes_verbos")
RUTA_AUDIOS_ORACIONES = os.path.join(RUTA_BASE, "audios", "oraciones")


TIEMPOS = ["presente", "pasado", "futuro"]
ETIQUETA_TIEMPO = {"presente": "PRESENT", "pasado": "PAST", "futuro": "FUTURE"}

MAX_INTENTOS = 5
XP_POR_ORACION = 10


# ---------------------------------------------------------------------------
# Lectura / escritura de los .json
# ---------------------------------------------------------------------------
def cargar_verbos():
    """Lee datos/verbos.json y devuelve:
        datos:  {"play": {"espanol":..., "imagen":..., "oraciones": {...}}, ...}
        orden:  ["play", "eat", "read", ...]  (orden en que aparecen en el archivo)
    """
    if not os.path.exists(RUTA_VERBOS_JSON):
        return {}, []

    with open(RUTA_VERBOS_JSON, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos, list(datos.keys())


def leer_progreso():
    """Lee datos/progreso.json completo (todos los usuarios)."""
    if not os.path.exists(RUTA_PROGRESO_JSON):
        return {}
    with open(RUTA_PROGRESO_JSON, "r", encoding="utf-8") as archivo:
        try:
            return json.load(archivo)
        except json.JSONDecodeError:
            return {}


def guardar_progreso_completo(progreso):
    os.makedirs(os.path.dirname(RUTA_PROGRESO_JSON), exist_ok=True)
    with open(RUTA_PROGRESO_JSON, "w", encoding="utf-8") as archivo:
        json.dump(progreso, archivo, indent=4, ensure_ascii=False)


def actualizar_progreso_oracion(usuario, verbo, tiempo, estado, xp_ganado):
    """Actualiza datos/progreso.json para usuario->oraciones->verbo->tiempo.
    Estructura esperada en el archivo:
        {
          "andres": {
            "vocabulario": { "play": {"estado":..., "intentos":..., "xp":...}, ... },
            "oraciones":   { "play": { "presente": {...}, "pasado": {...}, "futuro": {...} } }
          }
        }
    progreso.py (PantallaProgreso) puede leer este mismo archivo para
    armar la barra de porcentaje y la lista de "verbos debiles".
    """
    progreso = leer_progreso()
    datos_usuario = progreso.setdefault(usuario, {"vocabulario": {}, "oraciones": {}})
    datos_oraciones = datos_usuario.setdefault("oraciones", {})
    datos_verbo = datos_oraciones.setdefault(verbo, {})

    anterior = datos_verbo.get(tiempo, {"estado": "pendiente", "intentos": 0, "xp": 0})
    datos_verbo[tiempo] = {
        "estado": estado,
        "intentos": anterior["intentos"] + 1,
        "xp": anterior["xp"] + xp_ganado,
    }

    guardar_progreso_completo(progreso)


def _tiempo_completado(progreso, usuario, verbo, tiempo):
    try:
        estado = progreso[usuario]["oraciones"][verbo][tiempo]["estado"]
    except KeyError:
        return False
    return estado in ("correcto", "revelado")


def determinar_punto_de_partida(usuario, orden_verbos):
    """Recorre los verbos en orden y devuelve (indice_verbo, indice_tiempo)
    del primer ejercicio de oraciones que el usuario todavia no completo,
    leyendo datos/progreso.json. Si ya completo todo, devuelve
    (len(orden_verbos), 0)."""
    progreso = leer_progreso()
    for i, verbo in enumerate(orden_verbos):
        for j, tiempo in enumerate(TIEMPOS):
            if not _tiempo_completado(progreso, usuario, verbo, tiempo):
                return i, j
    return len(orden_verbos), 0


# ---------------------------------------------------------------------------
# SentenceExercise del diagrama -> OracionEjercicio
# ---------------------------------------------------------------------------
class OracionEjercicio:
    """Una oracion individual para armar (una de las 3: presente/pasado/futuro).

    Atributos (igual que en el diagrama de clases):
        frase_origen        -> sourcePhrase   (la frase en español)
        banco_palabras       -> wordBank        (fichas disponibles, mezcladas)
        palabras_seleccionadas -> selectedWords (lo que el usuario ya armo, en orden)
        instruccion          -> instruction
    """

    def __init__(self, frase_origen, palabras_correctas, palabras_distractoras, instruccion):
        self.frase_origen = frase_origen
        self.instruccion = instruccion
        self.palabras_correctas = list(palabras_correctas)

        fichas = [{"texto": p, "usada": False} for p in palabras_correctas + palabras_distractoras]
        random.shuffle(fichas)
        self.banco_palabras = fichas
        self.palabras_seleccionadas = []

    def seleccionar(self, indice_ficha):
        """El usuario hizo click en una palabra del banco: pasa al area de respuesta."""
        ficha = self.banco_palabras[indice_ficha]
        if ficha["usada"]:
            return
        ficha["usada"] = True
        self.palabras_seleccionadas.append(ficha["texto"])

    def quitar_seleccionada(self, indice_seleccion):
        """El usuario hizo click en una palabra ya puesta: vuelve al banco."""
        palabra = self.palabras_seleccionadas.pop(indice_seleccion)
        for ficha in self.banco_palabras:
            if ficha["texto"] == palabra and ficha["usada"]:
                ficha["usada"] = False
                break

    def reiniciar_seleccion(self):
        """Devuelve todas las fichas al banco (para 'Try again')."""
        for ficha in self.banco_palabras:
            ficha["usada"] = False
        self.palabras_seleccionadas = []

    def esta_completa(self):
        return len(self.palabras_seleccionadas) == len(self.palabras_correctas)

    def verificar_orden(self):
        """checkOrder(): boolean"""
        return self.palabras_seleccionadas == self.palabras_correctas

    def texto_correcto(self):
        return " ".join(self.palabras_correctas)


# ---------------------------------------------------------------------------
# Pantalla "Sentences - Verbo"
# ---------------------------------------------------------------------------
class PantallaConstructor(ctk.CTkFrame):
    """Pantalla donde se arman las 3 oraciones (presente/pasado/futuro) de
    cada verbo, seleccionando palabras de un banco.

    Firma estandar acordada por el equipo:
        PantallaConstructor(master, usuario, **kwargs)

    No recibe un callback de "siguiente verbo": cuando el usuario termina
    las 3 oraciones de un verbo, esta misma clase importa y muestra
    PantallaAprender (ver completar_verbo / ir_a_pantalla_aprender).
    """

    def __init__(self, master, usuario, indice_inicial=None, nombre_verbo_inicial=None, **kwargs):
        super().__init__(master, fg_color="#FFF5EC", **kwargs)
        self.usuario = usuario
        self.datos_verbos, self.orden_verbos = cargar_verbos()

        self.indice_tiempo = 0

        # ← Nueva lógica de punto de partida
        if nombre_verbo_inicial is not None and nombre_verbo_inicial in self.orden_verbos:
            self.indice_verbo = self.orden_verbos.index(nombre_verbo_inicial)
        elif indice_inicial is not None:
            self.indice_verbo = indice_inicial
        elif self.orden_verbos:
            self.indice_verbo, self.indice_tiempo = determinar_punto_de_partida(
                self.usuario, self.orden_verbos)
        else:
            self.indice_verbo = 0

        self.intentos_actual = 0
        self.mostrar_error = False
        self.revelada = False
        self.xp_sesion = 0
        self.ejercicio_actual = None
        self.imagen_widget_actual = None

        self.crear_widgets()

        if not self.orden_verbos:
            self.mostrar_sin_datos()
        elif self.indice_verbo >= len(self.orden_verbos):
            self.mostrar_modulo_completo()
        else:
            self.preparar_ejercicio_actual()
            self.refrescar_pantalla()

    # ------------------------------------------------------------------
    # Construccion de la interfaz (partes fijas)
    # ------------------------------------------------------------------
    def crear_widgets(self):
        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.pack(fill="x", padx=40, pady=(30, 0))

        columna_titulo = ctk.CTkFrame(encabezado, fg_color="transparent")
        columna_titulo.pack(side="left", anchor="w")

        self.label_titulo = ctk.CTkLabel(columna_titulo, text="Sentences",
            font=("Arial", 24, "bold"), text_color="#1a1a1a")
        self.label_titulo.pack(anchor="w")

        ctk.CTkLabel(columna_titulo, text="Build all 3 sentences in different tenses",
            font=("Arial", 13), text_color="gray").pack(anchor="w", pady=(2, 0))

        self.label_contador = ctk.CTkLabel(encabezado, text="",
            font=("Arial", 12), text_color="gray")
        self.label_contador.pack(side="right", anchor="e")

        self.barra_progreso = ctk.CTkProgressBar(self, height=8,
            progress_color="#FF8C00", fg_color="#FFE0C2")
        self.barra_progreso.pack(fill="x", padx=40, pady=(15, 25))
        self.barra_progreso.set(0)

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=40, pady=(0, 30))

        # --- Tarjeta de imagen (izquierda) ---
        self.tarjeta_imagen = ctk.CTkFrame(cuerpo, corner_radius=15,
            fg_color="white", border_width=1, border_color="#eeeeee", width=280)
        self.tarjeta_imagen.pack(side="left", fill="y", padx=(0, 30))
        self.tarjeta_imagen.pack_propagate(False)

        self.contenedor_imagen = ctk.CTkLabel(self.tarjeta_imagen, text="",
            width=240, height=220)
        self.contenedor_imagen.pack(padx=20, pady=(20, 15))

        self.fila_puntos = ctk.CTkFrame(self.tarjeta_imagen, fg_color="transparent")
        self.fila_puntos.pack(pady=(0, 5))

        self.label_sentence_of = ctk.CTkLabel(self.tarjeta_imagen, text="",
            font=("Arial", 11), text_color="gray")
        self.label_sentence_of.pack(pady=(0, 15))

        # --- Columna de tarjetas de tiempo (derecha), con scroll por si no entra ---
        self.contenedor_tarjetas = ctk.CTkScrollableFrame(cuerpo, fg_color="transparent")
        self.contenedor_tarjetas.pack(side="left", fill="both", expand=True)
        try:
            self.contenedor_tarjetas._scrollbar.grid_remove()
        except Exception:
            pass

    def mostrar_sin_datos(self):
        ctk.CTkLabel(self, text="⚠️ No se encontraron verbos en datos/verbos.json",
            font=("Arial", 16), text_color="gray").pack(expand=True)

    # ------------------------------------------------------------------
    # Preparar el ejercicio actual (verbo + tiempo)
    # ------------------------------------------------------------------
    def preparar_ejercicio_actual(self):
        verbo = self.orden_verbos[self.indice_verbo]
        tiempo = TIEMPOS[self.indice_tiempo]
        info = self.datos_verbos[verbo]["oraciones"][tiempo]

        self.ejercicio_actual = OracionEjercicio(
            frase_origen=info["frase"],
            palabras_correctas=info["correcta"],
            palabras_distractoras=info["distractores"],
            instruccion="Build all 3 sentences in different tenses",
        )
        self.intentos_actual = 0
        self.mostrar_error = False
        self.revelada = False

    def verbo_actual(self):
        return self.orden_verbos[self.indice_verbo]

    def cargar_imagen_verbo(self):
        verbo = self.verbo_actual()
        nombre_archivo = self.datos_verbos[verbo].get("imagen", f"{verbo}.jpg")
        ruta = os.path.join(RUTA_IMAGENES_VERBOS, nombre_archivo)
        try:
            imagen_pil = Image.open(ruta)
            imagen_ctk = ctk.CTkImage(imagen_pil, size=(200, 200))
            self.contenedor_imagen.configure(image=imagen_ctk, text="")
            self.imagen_widget_actual = imagen_ctk
        except Exception:
            self.contenedor_imagen.configure(image=None, text="🖼️\nimage missing",
                font=("Arial", 14), text_color="gray")

    # ------------------------------------------------------------------
    # Refrescar toda la pantalla segun el estado actual
    # ------------------------------------------------------------------
    def refrescar_pantalla(self):
        verbo = self.verbo_actual()

        self.label_titulo.configure(text=f"Sentences — {verbo.capitalize()}")
        self.label_contador.configure(
            text=f"Verb {self.indice_verbo + 1}/{len(self.orden_verbos)}")

        progreso_total = (self.indice_verbo * 3 + self.indice_tiempo) / (len(self.orden_verbos) * 3)
        self.barra_progreso.set(progreso_total)

        self.cargar_imagen_verbo()

        for widget in self.fila_puntos.winfo_children():
            widget.destroy()
        for i in range(3):
            color = "#2bb673" if i < self.indice_tiempo else ("#FF8C00" if i == self.indice_tiempo else "#e0e0e0")
            ctk.CTkLabel(self.fila_puntos, text="●", font=("Arial", 14),
                text_color=color).pack(side="left", padx=3)
        self.label_sentence_of.configure(text=f"Sentence {self.indice_tiempo + 1} of 3")

        for widget in self.contenedor_tarjetas.winfo_children():
            widget.destroy()

        for i, tiempo in enumerate(TIEMPOS):
            if i < self.indice_tiempo:
                estado = "completada"
            elif i == self.indice_tiempo:
                estado = "activa"
            else:
                estado = "pendiente"
            self.construir_tarjeta(self.contenedor_tarjetas, i, tiempo, estado)

    # ------------------------------------------------------------------
    # Construccion de cada tarjeta numerada (PRESENT / PAST / FUTURE)
    # ------------------------------------------------------------------
    def construir_tarjeta(self, master, numero_tiempo, tiempo, estado):
        verbo = self.verbo_actual()
        info = self.datos_verbos[verbo]["oraciones"][tiempo]

        colores_borde = {"completada": "#2bb673", "activa": "#FF8C00", "pendiente": "#eeeeee"}
        tarjeta = ctk.CTkFrame(master, corner_radius=12, fg_color="white",
            border_width=2, border_color=colores_borde[estado])
        tarjeta.pack(fill="x", pady=(0, 12))

        encabezado_tarjeta = ctk.CTkFrame(tarjeta, fg_color="transparent")
        encabezado_tarjeta.pack(fill="x", padx=18, pady=(15, 5))

        color_circulo = "#2bb673" if estado == "completada" else ("#FF8C00" if estado == "activa" else "#cccccc")
        texto_circulo = "✓" if estado == "completada" else str(numero_tiempo + 1)
        ctk.CTkLabel(encabezado_tarjeta, text=texto_circulo, width=26, height=26,
            corner_radius=13, fg_color=color_circulo, text_color="white",
            font=("Arial", 12, "bold")).pack(side="left", padx=(0, 12))

        columna_texto = ctk.CTkFrame(encabezado_tarjeta, fg_color="transparent")
        columna_texto.pack(side="left", anchor="w")

        ctk.CTkLabel(columna_texto, text=ETIQUETA_TIEMPO[tiempo],
            font=("Arial", 10, "bold"), text_color="gray" if estado != "pendiente" else "#cccccc").pack(anchor="w")
        # NOTA: a pedido del equipo, ya NO se muestra la oracion en español
        # (antes aca iba un CTkLabel con info["frase"]). El usuario ahora
        # arma la oracion en ingles solo guiandose por la imagen y el audio.

        if estado == "completada":
            ctk.CTkLabel(encabezado_tarjeta, text=info["correcta"] and " ".join(info["correcta"]),
                font=("Arial", 12, "bold"), text_color="#2e7d32",
                fg_color="#e6f7ee", corner_radius=8).pack(side="right", padx=(10, 0))
            tarjeta.configure(fg_color="#fbfffd")

        if estado == "activa":
            self.construir_cuerpo_tarjeta_activa(tarjeta)

        if estado == "pendiente":
            tarjeta.configure(fg_color="#fafafa")

    def construir_cuerpo_tarjeta_activa(self, tarjeta):
        ejercicio = self.ejercicio_actual

        # --- boton de audio (reproduce el .wav pre-generado de esta oracion) ---
        boton_audio = ctk.CTkButton(tarjeta, text="🔊 Listen to the sentence",
            font=("Arial", 12), fg_color="transparent", text_color="#FF8C00",
            hover_color="#fff0e0", anchor="w", command=self.reproducir_audio)
        boton_audio.pack(fill="x", padx=18, pady=(0, 8))
        if winsound is None:
            boton_audio.configure(state="disabled", text="🔇 Audio not available on this OS")
        elif not os.path.exists(self.ruta_audio_actual()):
            boton_audio.configure(state="disabled", text="🔇 Run generar_audios.py first")

        # --- area de respuesta (dropzone) ---
        color_borde_dropzone = "#c0392b" if self.mostrar_error else "#dddddd"
        dropzone = ctk.CTkFrame(tarjeta, corner_radius=10, fg_color="#fafafa",
            border_width=1, border_color=color_borde_dropzone)
        dropzone.pack(padx=18, pady=(0, 10), anchor="w", fill="x")

        if ejercicio.palabras_seleccionadas:
            fila_drop = ctk.CTkFrame(dropzone, fg_color="transparent")
            fila_drop.pack(fill="x", pady=4)
            contador_drop = 0

            for i, palabra in enumerate(ejercicio.palabras_seleccionadas):
                if contador_drop == 4:
                    fila_drop = ctk.CTkFrame(dropzone, fg_color="transparent")
                    fila_drop.pack(fill="x", pady=2)
                    contador_drop = 0

                ctk.CTkButton(fila_drop, text=palabra, height=30, corner_radius=15,
                    fg_color="#ffe0c2", text_color="#FF8C00", hover_color="#ffd2a8",
                    font=("Arial", 12, "bold"), width=0,
                    command=lambda idx=i: self.click_seleccionada(idx)).pack(side="left", padx=2, pady=2)
                contador_drop += 1
        else:
            ctk.CTkLabel(dropzone, text="Click the words to build the sentence",
                font=("Arial", 12), text_color="gray").pack(pady=10)

        # --- banco de palabras disponibles (en filas) ---
        banco_frame = ctk.CTkFrame(tarjeta, fg_color="transparent")
        banco_frame.pack(fill="x", padx=18, pady=(0, 5))

        fila_actual = ctk.CTkFrame(banco_frame, fg_color="transparent")
        fila_actual.pack(anchor="w", pady=2)
        contador = 0
        ancho_fila = 0
        ancho_maximo = 380  # ← ajusta este valor si la tarjeta es más ancha o más angosta

        for i, ficha in enumerate(ejercicio.banco_palabras):
            if ficha["usada"]:
                continue

            # calcular ancho aproximado del boton segun largo del texto
            ancho_boton = len(ficha["texto"]) * 9 + 24

            if ancho_fila + ancho_boton > ancho_maximo:
                fila_actual = ctk.CTkFrame(banco_frame, fg_color="transparent")
                fila_actual.pack(anchor="w", pady=2)
                ancho_fila = 0

            ctk.CTkButton(fila_actual, text=ficha["texto"], height=30, corner_radius=15,
                fg_color="#f0f0f0", text_color="#1a1a1a", hover_color="#e2e2e2",
                font=("Arial", 12), width=0,
                command=lambda idx=i: self.click_banco(idx)).pack(side="left", padx=2, pady=2)

            ancho_fila += ancho_boton + 4

        # --- mensaje de intentos / error / revelada ---
        if self.revelada:
            ctk.CTkLabel(tarjeta, text=f"The right answer was: {ejercicio.texto_correcto()}",
                font=("Arial", 12, "bold"), text_color="#8a6d00",
                fg_color="#fff8d6", corner_radius=8).pack(fill="x", padx=18, pady=(0, 10))
        elif self.mostrar_error:
            ctk.CTkLabel(tarjeta, text="❌ Incorrect. Try again.",
                font=("Arial", 12, "bold"), text_color="#c0392b",
                fg_color="#fdecea", corner_radius=8).pack(fill="x", padx=18, pady=(0, 5))
            ctk.CTkLabel(tarjeta, text=f"Attempt {self.intentos_actual + 1}/{MAX_INTENTOS}",
                font=("Arial", 11), text_color="#c0392b").pack(anchor="w", padx=18, pady=(0, 10))
        elif self.intentos_actual > 0:
            # ya fallo antes, pero esta armando un intento nuevo: solo
            # mostramos el contador, sin el cartel rojo de error
            ctk.CTkLabel(tarjeta, text=f"Attempt {self.intentos_actual + 1}/{MAX_INTENTOS}",
                font=("Arial", 11), text_color="gray").pack(anchor="w", padx=18, pady=(0, 10))

        # --- boton principal: Check / Try again / Continue ---
        if self.revelada:
            ctk.CTkButton(tarjeta, text="Continue →", height=40, corner_radius=10,
                font=("Arial", 14, "bold"), fg_color="#5B5FEF", hover_color="#4548c9",
                command=self.continuar_revelada).pack(fill="x", padx=18, pady=(0, 18))
        elif self.mostrar_error:
            ctk.CTkButton(tarjeta, text="↻ Try again", height=40, corner_radius=10,
                font=("Arial", 14, "bold"), fg_color="#FF8C00", hover_color="#e67700",
                command=self.reintentar).pack(fill="x", padx=18, pady=(0, 18))
        else:
            habilitado = ejercicio.esta_completa()
            ctk.CTkButton(tarjeta, text="Check", height=40, corner_radius=10,
                font=("Arial", 14, "bold"),
                fg_color="#2bb673" if habilitado else "#cfead9",
                hover_color="#239d60" if habilitado else "#cfead9",
                state="normal" if habilitado else "disabled",
                command=self.verificar).pack(fill="x", padx=18, pady=(0, 18))

    # ------------------------------------------------------------------
    # Eventos de click sobre las palabras
    # ------------------------------------------------------------------
    def click_banco(self, indice_ficha):
        self.ejercicio_actual.seleccionar(indice_ficha)
        self.mostrar_error = False  # esta armando un intento nuevo
        self.refrescar_pantalla()

    def click_seleccionada(self, indice_seleccion):
        self.ejercicio_actual.quitar_seleccionada(indice_seleccion)
        self.mostrar_error = False  # esta armando un intento nuevo
        self.refrescar_pantalla()

    # ------------------------------------------------------------------
    # Audio (reproduce el .wav pre-generado de la oracion actual)
    # ------------------------------------------------------------------
    def ruta_audio_actual(self):
        verbo = self.verbo_actual()
        tiempo = TIEMPOS[self.indice_tiempo]
        return os.path.join(RUTA_AUDIOS_ORACIONES, f"{verbo}_{tiempo}.wav")

    def reproducir_audio(self):
        global _audio_ocupado

        if winsound is None or self.ejercicio_actual is None:
            return
        if _audio_ocupado:
            return  # ya esta sonando un audio: ignoramos el click

        ruta = self.ruta_audio_actual()
        if not os.path.exists(ruta):
            print(f"[constructor.py] Falta el audio: {ruta}. "
                  f"Corre 'python generar_audios.py' una vez para crearlo.")
            return

        def reproducir():
            global _audio_ocupado
            _audio_ocupado = True
            try:
                winsound.PlaySound(ruta, winsound.SND_FILENAME)
            except Exception as error:
                print(f"[constructor.py] No se pudo reproducir {ruta}: {error}")
            finally:
                _audio_ocupado = False

        # en un hilo aparte para que la ventana no se congele mientras suena
        threading.Thread(target=reproducir, daemon=True).start()

    # ------------------------------------------------------------------
    # Verificar / reintentar / avanzar
    # ------------------------------------------------------------------
    def verificar(self):
        """Se ejecuta al apretar 'Check'. Equivale a usar checkOrder()."""
        ejercicio = self.ejercicio_actual
        if not ejercicio.esta_completa():
            return

        if ejercicio.verificar_orden():
            verbo = self.verbo_actual()
            tiempo = TIEMPOS[self.indice_tiempo]
            self.xp_sesion += XP_POR_ORACION
            actualizar_progreso_oracion(self.usuario, verbo, tiempo, "correcto", XP_POR_ORACION)
            self.avanzar_tiempo()
        else:
            self.intentos_actual += 1
            self.mostrar_error = True
            if self.intentos_actual >= MAX_INTENTOS:
                verbo = self.verbo_actual()
                tiempo = TIEMPOS[self.indice_tiempo]
                actualizar_progreso_oracion(self.usuario, verbo, tiempo, "revelado", 0)
                self.revelada = True
            self.refrescar_pantalla()

    def reintentar(self):
        """Se ejecuta al apretar 'Try again': limpia la seleccion pero
        mantiene el contador de intentos."""
        self.ejercicio_actual.reiniciar_seleccion()
        self.mostrar_error = False
        self.refrescar_pantalla()

    def continuar_revelada(self):
        """Se ejecuta al apretar 'Continue' despues de que se revelo la
        respuesta tras agotar los intentos."""
        self.avanzar_tiempo()

    def avanzar_tiempo(self):
        """Pasa a la siguiente oracion (presente -> pasado -> futuro) o,
        si ya se completaron las 3, pasa al siguiente verbo."""
        if self.indice_tiempo < 2:
            self.indice_tiempo += 1
            self.preparar_ejercicio_actual()
            self.refrescar_pantalla()
        else:
            self.completar_verbo()

    def completar_verbo(self):
        self.indice_verbo += 1
        self.indice_tiempo = 0

        if self.indice_verbo >= len(self.orden_verbos):
            self.mostrar_modulo_completo()
        else:
            self.ir_a_pantalla_aprender()

    def ir_a_pantalla_aprender(self):
        contenedor = self.master
        usuario = self.usuario
        indice_siguiente = self.indice_verbo  # ya incrementado, es el siguiente verbo

        try:
            from aprender import PantallaAprender

            def ir_a_constructor(nombre_verbo):          # ← ahora es un string
                # Buscar el índice real de ese verbo en el JSON
                if nombre_verbo in self.orden_verbos:
                    indice = self.orden_verbos.index(nombre_verbo)
                else:
                    indice = self.indice_verbo           # fallback: quedarse donde estaba

                for widget in contenedor.winfo_children():
                    widget.destroy()
                nuevo = PantallaConstructor(contenedor, usuario, indice_inicial=indice)
                nuevo.pack(fill="both", expand=True)

            siguiente_pantalla = PantallaAprender(
                contenedor,
                usuario,
                indice_inicial=indice_siguiente,
                al_completar=ir_a_constructor
            )
        except Exception as error:
            print(f"[constructor.py] No se pudo abrir PantallaAprender ({error})")
            self.preparar_ejercicio_actual()
            self.refrescar_pantalla()
            return

        self.destroy()
        siguiente_pantalla.pack(fill="both", expand=True)

    def _ir_a_constructor_desde_aprender(self, indice_verbo):
        contenedor = self.master if self.winfo_exists() else None
        if contenedor is None:
            return
        for widget in contenedor.winfo_children():
            widget.destroy()
        nuevo_constructor = PantallaConstructor(contenedor, self.usuario)
        nuevo_constructor.pack(fill="both", expand=True)

    def mostrar_modulo_completo(self):
        for widget in self.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self, text="🎉", font=("Arial", 50)).pack(pady=(80, 10))
        ctk.CTkLabel(self, text="You built every sentence for all the verbs!",
            font=("Arial", 20, "bold"), text_color="#1a1a1a").pack()
        ctk.CTkLabel(self, text=f"+ {self.xp_sesion} XP this session",
            font=("Arial", 14, "bold"), text_color="#2e7d32").pack(pady=(5, 20))

        ctk.CTkButton(self, text="🔁 Practice again", height=40,
            fg_color="#FF8C00", hover_color="#e67700",
            command=self.reiniciar_sesion).pack()

    def reiniciar_sesion(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.indice_verbo = 0
        self.indice_tiempo = 0
        self.xp_sesion = 0
        self.crear_widgets()
        self.preparar_ejercicio_actual()
        self.refrescar_pantalla()


# ---------------------------------------------------------------------------
# Permite probar este archivo solo: python constructor.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    ventana = ctk.CTk()
    ventana.title("Speakly - Constructor de oraciones (prueba aislada)")
    ventana.geometry("950x680")

    pantalla = PantallaConstructor(ventana, "invitado")
    pantalla.pack(fill="both", expand=True)

    ventana.mainloop()
