import customtkinter as ctk
from PIL import Image
import winsound  # Librería nativa de Windows para audio
import os
import json

# Configuración inicial de la interfaz
ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue")

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_VERBOS_JSON = os.path.join(RUTA_BASE, "datos", "verbos.json")

class PantallaAprender(ctk.CTkFrame):
    def __init__(self, master, usuario, indice_inicial=0, al_completar=None, **kwargs):
        super().__init__(master, fg_color="#FFF5EC", **kwargs)
        self.usuario = usuario
        self.al_completar = al_completar
        self.indice_actual = indice_inicial

        # cargar verbos desde JSON
        with open(RUTA_VERBOS_JSON, "r", encoding="utf-8") as f:
            datos_json = json.load(f)

        self.vocabulario = []
        for i, (verbo, info) in enumerate(datos_json.items()):
            self.vocabulario.append({
                "en": verbo,
                "es": info.get("espanol", verbo),
                "img": info.get("imagen", f"{i+1}.jpg"),
                "audio": f"{verbo}.wav",
            })

        self.total = len(self.vocabulario)
        self.carpeta_imagenes = os.path.join(RUTA_BASE, "imagenes")
        self.carpeta_audios = os.path.join(RUTA_BASE, "audios")  

        self.crear_contenedor_principal()
        self.cargar_pregunta()          # ← AQUÍ, después de crear todos los widgets

    

    def crear_contenedor_principal(self):
        self.contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido.pack(side="right", fill="both", expand=True, padx=20, pady=15)

        header_frame = ctk.CTkFrame(self.contenido, fg_color="transparent")
        header_frame.pack(fill="x")

        title_vocab = ctk.CTkLabel(header_frame, text="Vocabulary - Word",
            font=("Arial Black", 22), text_color="#1E3050")
        title_vocab.pack(side="left")

        # ← Solo se CREA el widget, sin configurar texto aún
        self.lbl_contador = ctk.CTkLabel(header_frame, text="",
            font=("Arial Bold", 14), text_color="#A0A0A0")
        self.lbl_contador.pack(side="right")

        sub_vocab = ctk.CTkLabel(self.contenido,
            text="Look at the English word and write it in Spanish",
            font=("Arial", 13), text_color="#A0A0A0")
        sub_vocab.pack(anchor="w", pady=(0, 20))

        self.progreso = ctk.CTkProgressBar(self.contenido,
            progress_color="#FF9209", fg_color="#E0E0E0", height=6)
        self.progreso.pack(fill="x", pady=(0, 30))
        self.progreso.set(0)            # ← valor neutro, cargar_pregunta lo actualizará

    
        
        bloque_interactivo = ctk.CTkFrame(self.contenido, fg_color="transparent")
        bloque_interactivo.pack(fill="both", expand=True)
        
        # Tarjeta Izquierda 
        self.card_palabra = ctk.CTkFrame(bloque_interactivo, fg_color="white", corner_radius=15, width=600)
        self.card_palabra.pack(side="left", fill="both", expand=True, padx=(0, 20))
        self.card_palabra.pack_propagate(False)
        
        # Widget para la ilustración
        self.lbl_imagen = ctk.CTkLabel(self.card_palabra, text="")
        self.lbl_imagen.pack(pady=15, expand=True)
        
        # Sección inferior de la tarjeta 
        info_card = ctk.CTkFrame(self.card_palabra, fg_color="transparent")
        info_card.pack(fill="x", padx=20, pady=15)
        
        self.btn_audio = ctk.CTkButton(info_card, text="🔊 Listen", fg_color="#FF9209", hover_color="#D87800", font=("Arial Bold", 13), width=100, command=self.reproducir_audio)
        self.btn_audio.pack(anchor="w")
        
        # Tarjeta Derecha (Input y Check)
        col_derecha = ctk.CTkFrame(bloque_interactivo, fg_color="transparent", width=250)
        col_derecha.pack(side="right", fill="both", padx=(20, 0))
        col_derecha.pack_propagate(False)
        
        form_card = ctk.CTkFrame(col_derecha, fg_color="white", corner_radius=15, height=130)
        form_card.pack(fill="x", pady=(0, 20))
        
        lbl_prompt = ctk.CTkLabel(form_card, text="HOW DO YOU SAY IT IN ENGLISH?", font=("Arial Black", 11), text_color="#A0A0A0")
        lbl_prompt.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.input_respuesta = ctk.CTkEntry(form_card, placeholder_text="", fg_color="white", border_color="#FFB067", border_width=2, height=45, font=("Arial", 16), text_color="#1E3050")
        self.input_respuesta.pack(fill="x", padx=20, pady=(0, 15))
        
        self.btn_check = ctk.CTkButton(col_derecha, text="Check", fg_color="#FF9209", hover_color="#D87800", height=50, font=("Arial Black", 16), corner_radius=10, command=self.verificar_respuesta)
        self.btn_check.pack(fill="x")
        
        self.lbl_feedback = ctk.CTkLabel(col_derecha, text="", font=("Arial Bold", 14))
        self.lbl_feedback.pack(pady=10)

    def cargar_pregunta(self):
        self.lbl_feedback.configure(text="")
        self.input_respuesta.delete(0, 'end')
        self.input_respuesta.configure(border_color="#FFB067")
        self.btn_check.configure(text="Check", fg_color="#FF9209",
            command=self.verificar_respuesta)

        datos = self.vocabulario[self.indice_actual]

        # Estos configure() ahora son seguros porque el widget ya existe
        self.lbl_contador.configure(text=f"{self.indice_actual + 1}/{self.total}")
        self.progreso.set((self.indice_actual + 1) / self.total)

        ruta_img = os.path.join(self.carpeta_imagenes, datos["img"])
        if os.path.exists(ruta_img):
            img_pil = Image.open(ruta_img)
            img_ctk = ctk.CTkImage(light_image=img_pil, size=(690, 550))
            self.lbl_imagen.configure(image=img_ctk, text="")
        else:
            self.lbl_imagen.configure(image=None,
                text=f"[No imagen: {datos['img']}]")

    def reproducir_audio(self):
        ruta_completa_audio = os.path.join(self.carpeta_audios, self.vocabulario[self.indice_actual]["audio"])
        
        if os.path.exists(ruta_completa_audio):
            winsound.PlaySound(ruta_completa_audio, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            print(f"Archivo de audio no encontrado: {ruta_completa_audio}")

    def verificar_respuesta(self):
        respuesta_usuario = self.input_respuesta.get().strip().lower()
        respuesta_correcta = self.vocabulario[self.indice_actual]["en"].lower()
        
        if respuesta_usuario == respuesta_correcta:
            self.input_respuesta.configure(border_color="#2DB757")
            self.lbl_feedback.configure(text="¡Excelent! Correct answer.", text_color="#2DB757")
            self.btn_check.configure(text="Next", fg_color="#2DB757", hover_color="#228B41", command=self.siguiente_pregunta)
        else:
            self.input_respuesta.configure(border_color="#E74C3C")
            self.lbl_feedback.configure(text=f"Incorrect. Try again.", text_color="#E74C3C")

    def siguiente_pregunta(self):
        verbo_actual = self.vocabulario[self.indice_actual]["en"]  # ← nombre del verbo

        if self.al_completar:
            self.al_completar(verbo_actual)  # ← pasa el STRING, no el índice
        elif self.indice_actual < self.total - 1:
            self.indice_actual += 1
            self.cargar_pregunta()
        else:
            self.lbl_feedback.configure(
                text="¡Felicidades! Has completado todas las palabras.",
                text_color="#FF9209"
            )
            self.btn_check.configure(state="disabled", text="Terminado")

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1250x720")

    usuario = {
        "nombre": "Jhoel"
    }

    pantalla = PantallaAprender(
        app,
        usuario=usuario["nombre"]
    )

    pantalla.pack(fill="both", expand=True)
    app.mainloop()