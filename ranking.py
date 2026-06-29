import customtkinter as ctk
import json
import os

NARANJA = "#FF9600"
TOTAL_VERBOS = 16

USUARIOS_DEMO = [
    {"nombre": "María García",   "pais": "MX", "dominados": 14},
    {"nombre": "Carlos López",   "pais": "CO", "dominados": 10},
    {"nombre": "Sofía Martín",   "pais": "AR", "dominados": 5},
    {"nombre": "Juan Rodríguez", "pais": "PE", "dominados": 3},
]

MEDALLAS = {1: "🥇", 2: "🥈", 3: "🥉"}


def cargar_progreso_usuario(nombre):
    ruta = "datos/progreso.json"
    if not os.path.exists(ruta):
        return 0
    with open(ruta, "r") as f:
        datos = json.load(f)
    progreso = datos.get(nombre, {})
    oraciones = progreso.get("oraciones", {})
    count = 0
    for verbo, tiempos in oraciones.items():
        estados = [t.get("estado", "") for t in tiempos.values()]
        if all(e == "correcto" for e in estados) and len(estados) == 3:
            count += 1
    return count


class PantallaRanking(ctk.CTkFrame):

    def __init__(self, master, usuario, cerrar_cmd=None, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=16, **kwargs)
        self.usuario = usuario
        self.nombre = usuario.get("usuario", usuario.get("nombre", ""))
        self.cerrar_cmd = cerrar_cmd
        self._construir()

    def _construir(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 5))

        ctk.CTkLabel(header, text="🏆  Ranking — Progress",
                     font=("Arial", 17, "bold"), text_color="#1a1a1a").pack(side="left")

        if self.cerrar_cmd:
            ctk.CTkButton(header, text="✕", width=28, height=28,
                          corner_radius=14, fg_color="#EEEEEE",
                          text_color="#555555", hover_color="#DDDDDD",
                          font=("Arial", 13), command=self.cerrar_cmd).pack(side="right")

        ctk.CTkFrame(self, height=1, fg_color="#EEEEEE").pack(fill="x", padx=20, pady=(5, 0))

        enc = ctk.CTkFrame(self, fg_color="transparent")
        enc.pack(fill="x", padx=20, pady=(6, 4))
        ctk.CTkLabel(enc, text="MASTERED VERBS / 16",
                     font=("Arial", 9, "bold"), text_color="#AAAAAA").pack(side="right")

        # Ranking
        dominados_yo = cargar_progreso_usuario(self.nombre)
        porcentaje_yo = int((dominados_yo / TOTAL_VERBOS) * 100)

        ranking = []
        for u in USUARIOS_DEMO:
            ranking.append({
                "nombre": u["nombre"],
                "pais": u["pais"],
                "dominados": u["dominados"],
                "porcentaje": int((u["dominados"] / TOTAL_VERBOS) * 100),
                "es_yo": False,
            })
        ranking.append({
            "nombre": self.usuario.get("nombre", self.nombre),
            "pais": self.usuario.get("pais", "BO"),
            "dominados": dominados_yo,
            "porcentaje": porcentaje_yo,
            "es_yo": True,
        })
        ranking.sort(key=lambda x: x["dominados"], reverse=True)

        lista = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        lista.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for i, entrada in enumerate(ranking):
            posicion = i + 1
            es_yo = entrada["es_yo"]

            color_fila = "#FFF5EC" if es_yo else "#F9F9F9"
            color_nombre = NARANJA if es_yo else "#1a1a1a"

            fila = ctk.CTkFrame(lista, corner_radius=10, fg_color=color_fila,
                                border_width=2 if es_yo else 0, border_color=NARANJA)
            fila.pack(fill="x", pady=4)

            contenido = ctk.CTkFrame(fila, fg_color="transparent")
            contenido.pack(fill="x", padx=12, pady=8)

            medalla = MEDALLAS.get(posicion, f"#{posicion}")
            ctk.CTkLabel(contenido, text=medalla, font=("Arial", 16),
                         text_color=NARANJA if es_yo else "#555555", width=30).pack(side="left")

            ctk.CTkLabel(contenido, text=entrada["pais"], font=("Arial", 10, "bold"),
                         text_color="#888888", width=30).pack(side="left", padx=(4, 0))

            nombre_display = f"{entrada['nombre']} (tú)" if es_yo else entrada["nombre"]
            ctk.CTkLabel(contenido, text=nombre_display,
                         font=("Arial", 12, "bold" if es_yo else "normal"),
                         text_color=color_nombre).pack(side="left", padx=(6, 0))

            stats_text = f"{entrada['dominados']}/{TOTAL_VERBOS} · {entrada['porcentaje']}%"
            ctk.CTkLabel(contenido, text=stats_text, font=("Arial", 11),
                         text_color=color_nombre).pack(side="right")

            barra = ctk.CTkProgressBar(fila, height=5, corner_radius=3,
                                        fg_color="#EEEEEE",
                                        progress_color=NARANJA if es_yo else "#CCCCCC")
            barra.set(entrada["dominados"] / TOTAL_VERBOS)
            barra.pack(fill="x", padx=12, pady=(0, 8))
