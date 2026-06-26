import customtkinter as ctk
from PIL import Image
import winsound  # Librería nativa de Windows para audio
import os

# Configuración inicial de la interfaz
ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue")

class ConstructorVerbos(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Speakly - Vocabulary")
        self.geometry("1250x720")
        self.configure(fg_color="#FFF8F3") # Fondo crema
        
        # Banco de datos 
        self.vocabulario = [
            {"en": "play", "es": "Jugar", "img": "1.jpg", "audio": "play.wav"},
            {"en": "eat", "es": "Comer", "img": "2.jpg", "audio": "eat.wav"},
            {"en": "read", "es": "Leer", "img": "3.jpg", "audio": "read.wav"},
            {"en": "sing", "es": "Cantar", "img": "4.jpg", "audio": "sing.wav"},
            {"en": "write", "es": "Escribir", "img": "5.jpg", "audio": "write.wav"},
            {"en": "sleep", "es": "Dormir", "img": "6.jpg", "audio": "sleep.wav"},
            {"en": "run", "es": "Correr", "img": "7.jpg", "audio": "run.wav"},
            {"en": "talk", "es": "Hablar", "img": "8.jpg", "audio": "talk.wav"},
            {"en": "dance", "es": "Bailar", "img": "9.jpg", "audio": "dance.wav"},
            {"en": "listen", "es": "Escuchar", "img": "10.jpg", "audio": "listen.wav"},
            {"en": "speak", "es": "Hablar", "img": "11.jpg", "audio": "speak.wav"},
            {"en": "ask", "es": "Preguntar", "img": "12.jpg", "audio": "ask.wav"},
            {"en": "answer", "es": "Responder", "img": "13.jpg", "audio": "answer.wav"},
            {"en": "learn", "es": "Aprender", "img": "14.jpg", "audio": "learn.wav"},
            {"en": "teach", "es": "Enseñar", "img": "15.jpg", "audio": "teach.wav"},
            {"en": "practice", "es": "Practicar", "img": "16.jpg", "audio": "practice.wav"}
        ]

        self.carpeta_imagenes = "imagenes"
        self.carpeta_audios = "audios"
        self.indice_actual = 0
        
        # Dibujar los componentes
        
        self.crear_contenedor_principal()
        
        # Cargar primera pregunta
        self.cargar_pregunta()

    

    def crear_contenedor_principal(self):
        self.contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido.pack(side="right", fill="both", expand=True, padx=40, pady=30)
        
        header_frame = ctk.CTkFrame(self.contenido, fg_color="transparent")
        header_frame.pack(fill="x")
        
        title_vocab = ctk.CTkLabel(header_frame, text="Vocabulary - Word", font=("Arial Black", 22), text_color="#1E3050")
        title_vocab.pack(side="left")
        
        self.lbl_contador = ctk.CTkLabel(header_frame, text="1/16", font=("Arial Bold", 14), text_color="#A0A0A0")
        self.lbl_contador.pack(side="right")
        
        sub_vocab = ctk.CTkLabel(self.contenido, text="Look at the English word and write it in Spanish", font=("Arial", 13), text_color="#A0A0A0")
        sub_vocab.pack(anchor="w", pady=(0, 20))
        
        self.progreso = ctk.CTkProgressBar(self.contenido, progress_color="#FF9209", fg_color="#E0E0E0", height=6)
        self.progreso.pack(fill="x", pady=(0, 30))
        self.progreso.set(1/16)
        
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
        col_derecha = ctk.CTkFrame(bloque_interactivo, fg_color="transparent", width=350)
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
        # Limpiar feedback e input anterior
        self.lbl_feedback.configure(text="")
        self.input_respuesta.delete(0, 'end')
        self.input_respuesta.configure(border_color="#FFB067")
        self.btn_check.configure(text="Check", fg_color="#FF9209", command=self.verificar_respuesta)
        
        datos = self.vocabulario[self.indice_actual]
        
        # Actualizar textos del contador y barra de progreso
        self.lbl_contador.configure(text=f"{self.indice_actual + 1}/16")
        self.progreso.set((self.indice_actual + 1) / 16)
        
        ruta_completa_img = os.path.join(self.carpeta_imagenes, datos["img"])
        
        if os.path.exists(ruta_completa_img):
            img_pil = Image.open(ruta_completa_img)
            img_ctk = ctk.CTkImage(light_image=img_pil, size=(520, 450))
            self.lbl_imagen.configure(image=img_ctk, text="")
        else:
            self.lbl_imagen.configure(image=None, text=f"[No se encontró: {ruta_completa_img}]")

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
        if self.indice_actual < 15:
            self.indice_actual += 1
            self.cargar_pregunta()
        else:
            self.lbl_feedback.configure(text="¡Felicidades! Has completado las 16 palabras.", text_color="#FF9209")
            self.btn_check.configure(state="disabled", text="Terminado")

if __name__ == "__main__":
    app = ConstructorVerbos()
    app.mainloop()