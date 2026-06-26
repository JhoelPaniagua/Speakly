"""
constructor.py
===============
Pantalla "Sentences - Verbo" de Speakly (Presente / Pasado / Futuro).

Correspondencia con el diagrama de clases del equipo:
    SentenceExercise (armar oracion) -> clase OracionEjercicio
        sourcePhrase   -> frase_origen
        wordBank       -> banco_palabras
        selectedWords  -> palabras_seleccionadas
        instruction    -> instruccion
        checkOrder()   -> verificar_orden()

    El contenedor de pantalla (equivalente a como VocabularySession
    contiene a WordCard) es la clase ConstructorOraciones (CTkFrame).

Que hace este modulo:
    1) Por cada verbo, muestra 3 tarjetas numeradas: PRESENT, PAST, FUTURE.
    2) Cada tarjeta tiene una frase en español y un banco de palabras en
       ingles (las correctas + algunas de relleno) para que el usuario
       las vaya click-eando EN ORDEN y arme la oracion.
    3) Hay un boton para escuchar la oracion correcta en ingles.
    4) Si se equivoca, puede "Try again" (se le permiten varios intentos).
    5) Cuando termina las 3 oraciones de un verbo, se guarda el progreso
       y se avisa al resto de la app (callback) para pasar al siguiente
       verbo, donde sea que ese verbo se vuelva a practicar vocabulario.

Como lo integra el resto del equipo (main.py / aprender.py):
    from constructor import ConstructorOraciones

    def ir_al_siguiente_verbo(verbo_ingles):
        # aqui se podria volver a aprender.py con el siguiente verbo
        ...

    frame = ConstructorOraciones(self.contenido, usuario="Andres",
                                  al_completar_verbo=ir_al_siguiente_verbo)
    frame.pack(fill="both", expand=True)

Este archivo se puede ejecutar solo (python constructor.py) para probarlo
sin depender de que el resto del proyecto este terminado.
"""

import os
import random
import threading

import customtkinter as ctk
from PIL import Image

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# Un solo motor de voz para todo el programa (NO se debe llamar a
# pyttsx3.init() una vez por cada click: en Windows eso es lo que provoca
# el error "run loop already started"). _MOTOR_OCUPADO evita que dos
# clicks rapidos intenten hablar al mismo tiempo.
_motor_voz = None
_motor_voz_ocupado = False


def _obtener_motor_voz():
    global _motor_voz
    if _motor_voz is None:
        _motor_voz = pyttsx3.init()
        _motor_voz.setProperty("rate", 150)
    return _motor_voz


# ---------------------------------------------------------------------------
# Rutas (todo relativo a este archivo)
# ---------------------------------------------------------------------------
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_ORACIONES_TXT = os.path.join(RUTA_BASE, "data", "oraciones.txt")
RUTA_PROGRESO_TXT = os.path.join(RUTA_BASE, "data", "progreso_oraciones.txt")
RUTA_IMAGENES_VERBOS = os.path.join(RUTA_BASE, "imagenes_verbos")

TIEMPOS = ["presente", "pasado", "futuro"]
ETIQUETA_TIEMPO = {"presente": "PRESENT", "pasado": "PAST", "futuro": "FUTURE"}

MAX_INTENTOS = 5
XP_POR_ORACION = 10


# ---------------------------------------------------------------------------
# Lectura / escritura de los .txt
# (igual que en aprender.py: el .txt solo guarda texto y el nombre del
#  archivo de imagen; la imagen real vive en imagenes_verbos/)
# ---------------------------------------------------------------------------
def cargar_oraciones():
    """Lee data/oraciones.txt y devuelve:
        datos:  {"play": {"presente": {...}, "pasado": {...}, "futuro": {...}}, ...}
        orden:  ["play", "eat", "read", ...]  (orden en que aparecen en el archivo)
    cada {...} tiene: frase (str), correctas (list[str]), distractoras (list[str])
    """
    datos = {}
    orden = []

    if not os.path.exists(RUTA_ORACIONES_TXT):
        return datos, orden

    with open(RUTA_ORACIONES_TXT, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split("|")
            if len(partes) != 5:
                continue

            verbo, tiempo, frase, oracion_correcta, distractores = partes
            verbo = verbo.strip()
            tiempo = tiempo.strip()

            if verbo not in datos:
                datos[verbo] = {}
                orden.append(verbo)

            datos[verbo][tiempo] = {
                "frase": frase.strip(),
                "correctas": oracion_correcta.strip().split(" "),
                "distractoras": [d.strip() for d in distractores.split(",") if d.strip()],
            }

    return datos, orden


def guardar_progreso_oracion(usuario, verbo, tiempo, estado, xp_ganado):
    """Agrega o actualiza una linea en data/progreso_oraciones.txt.
    Formato: usuario|verbo|tiempo|estado|intentos|xp_acumulado
    """
    os.makedirs(os.path.dirname(RUTA_PROGRESO_TXT), exist_ok=True)

    lineas_previas = []
    if os.path.exists(RUTA_PROGRESO_TXT):
        with open(RUTA_PROGRESO_TXT, "r", encoding="utf-8") as archivo:
            lineas_previas = archivo.readlines()

    lineas_nuevas = []
    encontrada = False
    for linea in lineas_previas:
        if linea.strip().startswith("#") or not linea.strip():
            lineas_nuevas.append(linea)
            continue
        partes = linea.strip().split("|")
        if len(partes) == 6 and partes[0] == usuario and partes[1] == verbo and partes[2] == tiempo:
            intentos = int(partes[4]) + 1
            xp_total = int(partes[5]) + xp_ganado
            lineas_nuevas.append(f"{usuario}|{verbo}|{tiempo}|{estado}|{intentos}|{xp_total}\n")
            encontrada = True
        else:
            lineas_nuevas.append(linea if linea.endswith("\n") else linea + "\n")

    if not encontrada:
        lineas_nuevas.append(f"{usuario}|{verbo}|{tiempo}|{estado}|1|{xp_ganado}\n")

    with open(RUTA_PROGRESO_TXT, "w", encoding="utf-8") as archivo:
        archivo.writelines(lineas_nuevas)


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
class ConstructorOraciones(ctk.CTkFrame):
    """Pantalla donde se arman las 3 oraciones (presente/pasado/futuro) de
    cada verbo, seleccionando palabras de un banco.

    Parametros:
        usuario            -> nombre del usuario logueado (lo da login.py).
        al_completar_verbo -> callback(verbo_ingles) que se llama apenas el
                               usuario termina las 3 oraciones de un verbo.
                               Es el gancho para volver a aprender.py con el
                               siguiente verbo.
    """

    def __init__(self, master, usuario="invitado", al_completar_verbo=None, **kwargs):
        super().__init__(master, fg_color="#FFF5EC", **kwargs)

        self.usuario = usuario
        self.al_completar_verbo = al_completar_verbo

        self.datos_oraciones, self.orden_verbos = cargar_oraciones()

        self.indice_verbo = 0
        self.indice_tiempo = 0       # 0=presente, 1=pasado, 2=futuro
        self.intentos_actual = 0
        self.mostrar_error = False   # True solo justo despues de un Check fallido
        self.revelada = False        # True si se mostro la respuesta tras agotar intentos
        self.xp_sesion = 0
        self.ejercicio_actual = None
        self.imagen_widget_actual = None  # referencia viva para que no la borre el GC

        self.crear_widgets()

        if self.orden_verbos:
            self.preparar_ejercicio_actual()
            self.refrescar_pantalla()
        else:
            self.mostrar_sin_datos()

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
        ctk.CTkLabel(self, text="⚠️ No se encontraron oraciones en data/oraciones.txt",
            font=("Arial", 16), text_color="gray").pack(expand=True)

    # ------------------------------------------------------------------
    # Preparar el ejercicio actual (verbo + tiempo)
    # ------------------------------------------------------------------
    def preparar_ejercicio_actual(self):
        verbo = self.orden_verbos[self.indice_verbo]
        tiempo = TIEMPOS[self.indice_tiempo]
        info = self.datos_oraciones[verbo][tiempo]

        self.ejercicio_actual = OracionEjercicio(
            frase_origen=info["frase"],
            palabras_correctas=info["correctas"],
            palabras_distractoras=info["distractoras"],
            instruccion="Build all 3 sentences in different tenses",
        )
        self.intentos_actual = 0
        self.mostrar_error = False
        self.revelada = False

    def verbo_actual(self):
        return self.orden_verbos[self.indice_verbo]

    def cargar_imagen_verbo(self):
        verbo = self.verbo_actual()
        ruta = os.path.join(RUTA_IMAGENES_VERBOS, f"{verbo}.jpg")
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
        info = self.datos_oraciones[verbo][tiempo]

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

        color_texto = "#1a1a1a" if estado != "pendiente" else "#bbbbbb"
        ctk.CTkLabel(columna_texto, text=ETIQUETA_TIEMPO[tiempo],
            font=("Arial", 10, "bold"), text_color="gray" if estado != "pendiente" else "#cccccc").pack(anchor="w")
        ctk.CTkLabel(columna_texto, text=info["frase"],
            font=("Arial", 14, "bold"), text_color=color_texto).pack(anchor="w")

        if estado == "completada":
            ctk.CTkLabel(encabezado_tarjeta, text=info["correctas"] and " ".join(info["correctas"]),
                font=("Arial", 12, "bold"), text_color="#2e7d32",
                fg_color="#e6f7ee", corner_radius=8).pack(side="right", padx=(10, 0))
            tarjeta.configure(fg_color="#fbfffd")

        if estado == "activa":
            self.construir_cuerpo_tarjeta_activa(tarjeta)

        if estado == "pendiente":
            tarjeta.configure(fg_color="#fafafa")

    def construir_cuerpo_tarjeta_activa(self, tarjeta):
        ejercicio = self.ejercicio_actual

        # --- boton de audio ---
        boton_audio = ctk.CTkButton(tarjeta, text="🔊 Listen to the sentence",
            font=("Arial", 12), fg_color="transparent", text_color="#FF8C00",
            hover_color="#fff0e0", anchor="w", command=self.reproducir_audio)
        boton_audio.pack(fill="x", padx=18, pady=(0, 8))
        if pyttsx3 is None:
            boton_audio.configure(state="disabled", text="🔇 Audio not available")

        # --- area de respuesta (dropzone) ---
        color_borde_dropzone = "#c0392b" if self.mostrar_error else "#dddddd"
        dropzone = ctk.CTkFrame(tarjeta, corner_radius=10, fg_color="#fafafa",
            border_width=1, border_color=color_borde_dropzone, height=46)
        dropzone.pack(fill="x", padx=18, pady=(0, 10))

        if ejercicio.palabras_seleccionadas:
            for i, palabra in enumerate(ejercicio.palabras_seleccionadas):
                ctk.CTkButton(dropzone, text=palabra, height=30, corner_radius=15,
                    fg_color="#ffe0c2", text_color="#FF8C00", hover_color="#ffd2a8",
                    font=("Arial", 12, "bold"),
                    command=lambda idx=i: self.click_seleccionada(idx)).pack(side="left", padx=4, pady=8)
        else:
            ctk.CTkLabel(dropzone, text="Click the words to build the sentence",
                font=("Arial", 12), text_color="gray").pack(pady=10)

        # --- banco de palabras disponibles ---
        fila_banco = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila_banco.pack(fill="x", padx=18, pady=(0, 5))
        for i, ficha in enumerate(ejercicio.banco_palabras):
            if ficha["usada"]:
                continue
            ctk.CTkButton(fila_banco, text=ficha["texto"], height=30, corner_radius=15,
                fg_color="#f0f0f0", text_color="#1a1a1a", hover_color="#e2e2e2",
                font=("Arial", 12),
                command=lambda idx=i: self.click_banco(idx)).pack(side="left", padx=4, pady=4)

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
    # Audio (pronunciacion de la oracion correcta)
    # ------------------------------------------------------------------
    def reproducir_audio(self):
        global _motor_voz_ocupado

        if pyttsx3 is None or self.ejercicio_actual is None:
            return
        if _motor_voz_ocupado:
            return  # ya esta hablando: ignoramos el click para no chocar

        oracion = self.ejercicio_actual.texto_correcto()

        def hablar():
            global _motor_voz_ocupado
            _motor_voz_ocupado = True
            try:
                motor = _obtener_motor_voz()
                motor.say(oracion)
                motor.runAndWait()
            finally:
                _motor_voz_ocupado = False

        threading.Thread(target=hablar, daemon=True).start()

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
            guardar_progreso_oracion(self.usuario, verbo, tiempo, "correcto", XP_POR_ORACION)
            self.avanzar_tiempo()
        else:
            self.intentos_actual += 1
            self.mostrar_error = True
            if self.intentos_actual >= MAX_INTENTOS:
                verbo = self.verbo_actual()
                tiempo = TIEMPOS[self.indice_tiempo]
                guardar_progreso_oracion(self.usuario, verbo, tiempo, "revelado", 0)
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
        """Se completaron las 3 oraciones del verbo actual: avisa al resto
        de la app y pasa al siguiente verbo de la lista."""
        verbo_terminado = self.verbo_actual()

        if self.al_completar_verbo is not None:
            # Aqui es donde el resto del equipo puede volver a aprender.py
            # con el siguiente verbo, mostrar un mensaje de felicitacion, etc.
            self.al_completar_verbo(verbo_terminado)

        self.indice_verbo += 1
        self.indice_tiempo = 0

        if self.indice_verbo >= len(self.orden_verbos):
            self.mostrar_modulo_completo()
        else:
            self.preparar_ejercicio_actual()
            self.refrescar_pantalla()

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

    def simular_siguiente_verbo(verbo):
        print(f"[DEBUG] Verbo '{verbo}' completado. Aqui se pasaria al siguiente verbo en aprender.py")

    pantalla = ConstructorOraciones(ventana, usuario="invitado",
        al_completar_verbo=simular_siguiente_verbo)
    pantalla.pack(fill="both", expand=True)

    ventana.mainloop()
