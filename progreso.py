import customtkinter as ctk
import json
import os

NARANJA = "#FF9600"
NARANJA_OSCURO = "#FFA626"
FONDO = "#FFF5EC"
TOTAL_VERBOS = 16


def cargar_progreso(nombre_usuario):
    ruta = "datos/progreso.json"
    if not os.path.exists(ruta):
        return {}
    with open(ruta, "r") as f:
        datos = json.load(f)
    return datos.get(nombre_usuario, {})


def calcular_verbos_dominados(progreso_usuario):
    verbos_dominados = 0
    verbos_debiles = 0
    oraciones = progreso_usuario.get("oraciones", {})
    for verbo, tiempos in oraciones.items():
        estados = [t.get("estado", "") for t in tiempos.values()]
        if all(e == "correcto" for e in estados) and len(estados) == 3:
            verbos_dominados += 1
        elif any(e == "incorrecto" for e in estados):
            verbos_debiles += 1
    return verbos_dominados, verbos_debiles


class PantallaProgreso(ctk.CTkFrame):

    def __init__(self, master, usuario, **kwargs):
        super().__init__(master, fg_color=FONDO, **kwargs)
        self.usuario = usuario
        self.nombre = usuario.get("usuario", usuario.get("nombre", ""))
        self._construir()

    def _construir(self):
        progreso = cargar_progreso(self.nombre)
        dominados, debiles = calcular_verbos_dominados(progreso)
        porcentaje = int((dominados / TOTAL_VERBOS) * 100)
        racha = self.usuario.get("racha", 7)

        # Título
        ctk.CTkLabel(self, text=f"Welcome back, {self.usuario.get('nombre', self.nombre)}! 👋",
                     font=("Arial", 26, "bold"), text_color="#1a1a1a").pack(anchor="w", padx=40, pady=(30, 0))

        ctk.CTkLabel(self, text="Continue your 7-day streak. Keep it up!",
                     font=("Arial", 14), text_color="gray").pack(anchor="w", padx=40, pady=(5, 20))

        # Tarjeta naranja
        tarjeta = ctk.CTkFrame(self, corner_radius=15, fg_color=NARANJA)
        tarjeta.pack(padx=40, pady=10, fill="x")

        fila_top = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila_top.pack(fill="x", padx=20, pady=(15, 5))

        lado_izq = ctk.CTkFrame(fila_top, fg_color="transparent")
        lado_izq.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(lado_izq, text="YOUR PROGRESS",
                     font=("Arial", 12, "bold"), text_color="#2b1500").pack(anchor="w")
        ctk.CTkLabel(lado_izq, text=f"{dominados} / {TOTAL_VERBOS} verbos",
                     font=("Arial", 22, "bold"), text_color="white").pack(anchor="w", pady=(3, 0))

        lado_der = ctk.CTkFrame(fila_top, fg_color="transparent")
        lado_der.pack(side="right")

        stats = [
            ("🔥", f"{racha} days", "Streak"),
            ("🏆", "#5", "Ranking"),
            ("⚠️", str(debiles), "Weak"),
        ]
        for icono, valor, etiqueta in stats:
            cuadro = ctk.CTkFrame(lado_der, corner_radius=12, fg_color="#FFA626", width=75, height=75)
            cuadro.pack(side="left", padx=4)
            cuadro.pack_propagate(False)
            ctk.CTkLabel(cuadro, text=icono, font=("Arial", 20)).place(relx=0.5, rely=0.28, anchor="center")
            ctk.CTkLabel(cuadro, text=valor, font=("Arial", 11, "bold"), text_color="white").place(relx=0.5, rely=0.58, anchor="center")
            ctk.CTkLabel(cuadro, text=etiqueta, font=("Arial", 9), text_color="#FFE0A0").place(relx=0.5, rely=0.82, anchor="center")

        # Barra de progreso
        fila_barra = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila_barra.pack(fill="x", padx=20, pady=(8, 2))
        ctk.CTkLabel(fila_barra, text="Mastered verbs", font=("Arial", 11), text_color="#FFE8C0").pack(side="left")
        ctk.CTkLabel(fila_barra, text=f"{porcentaje}%", font=("Arial", 11, "bold"), text_color="white").pack(side="right")

        barra = ctk.CTkProgressBar(tarjeta, height=10, corner_radius=5,
                                    fg_color="#FFA626", progress_color="white")
        barra.set(porcentaje / 100)
        barra.pack(fill="x", padx=20, pady=(3, 5))

        if dominados == 0:
            mensaje = "Start practicing to track your progress!"
        elif dominados < 8:
            mensaje = "Great job! Keep going, you're doing well! 💪"
        else:
            mensaje = "Amazing! You're almost there! 🌟"

        ctk.CTkLabel(tarjeta, text=mensaje,
                     font=("Arial", 12), text_color="#FFE8C0").pack(anchor="w", padx=20, pady=(2, 15))

        # Learning Mode
        ctk.CTkLabel(self, text="📖  LEARNING MODE",
                     font=("Arial", 13, "bold"), text_color="#555555").pack(anchor="w", padx=40, pady=(25, 8))

        btn_learn = ctk.CTkFrame(self, corner_radius=15, fg_color=NARANJA)
        btn_learn.pack(padx=40, fill="x")

        fila_btn = ctk.CTkFrame(btn_learn, fg_color="transparent")
        fila_btn.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(fila_btn, text="📚", font=("Arial", 30)).pack(side="left", padx=(0, 15))

        textos = ctk.CTkFrame(fila_btn, fg_color="transparent")
        textos.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(textos, text="Learn Vocabulary",
                     font=("Arial", 16, "bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(textos, text="Vocabulary + sentences for each verb",
                     font=("Arial", 12), text_color="#FFE8C0").pack(anchor="w")

        ctk.CTkLabel(fila_btn, text="›", font=("Arial", 24, "bold"), text_color="white").pack(side="right")
