import customtkinter as ctk

# Configuración general
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Speakly")
        self.geometry("1000x600")
        self.resizable(False, False)

        # Configurar 2 columnas: barra izquierda y contenido derecho
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_barra_lateral()
        self.crear_area_contenido()
        self.barra.grid_propagate(False)

    def crear_barra_lateral(self):
        self.barra = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a1a2e")
        self.barra.grid(row=0, column=0, sticky="nsew")

        # Logo
        self.logo_label = ctk.CTkLabel(self.barra, text="Speakly", font=("Arial", 22, "bold"))
        self.logo_label.pack(pady=(20, 10))

        # Foto + nombre de usuario (datos de prueba por ahora)
        self.foto_usuario = ctk.CTkLabel(self.barra, text="👤", font=("Arial", 40))
        self.foto_usuario.pack(pady=(10, 0))

        self.nombre_usuario = ctk.CTkLabel(self.barra, text="Jhoel", font=("Arial", 14))
        self.nombre_usuario.pack(pady=(0, 20))

        # Botones de navegación
        self.btn_progreso = ctk.CTkButton(self.barra, text="Mi Progreso", 
            command=lambda: self.cambiar_contenido("📊 Aquí va Mi Progreso"))
        self.btn_progreso.pack(pady=10, padx=20, fill="x")

        self.btn_aprender = ctk.CTkButton(self.barra, text="Aprender", 
            command=lambda: self.cambiar_contenido("📚 Aquí va Aprender"))
        self.btn_aprender.pack(pady=10, padx=20, fill="x")

        self.btn_ranking = ctk.CTkButton(self.barra, text="Ranking", 
            command=lambda: self.cambiar_contenido("🏆 Aquí va el Ranking (popup)"))
        self.btn_ranking.pack(pady=10, padx=20, fill="x")

        self.btn_cerrar_sesion = ctk.CTkButton(self.barra, text="Cerrar Sesión", fg_color="red", hover_color="darkred")
        self.btn_cerrar_sesion.pack(pady=(40, 10), padx=20, fill="x")

    def crear_area_contenido(self):
        self.contenido = ctk.CTkFrame(self)
        self.contenido.grid(row=0, column=1, sticky="nsew")

        self.label_contenido = ctk.CTkLabel(
            self.contenido, 
            text="Aquí va el contenido de Progreso", 
            font=("Arial", 20)
        )
        self.label_contenido.pack(expand=True)

    def cambiar_contenido(self, texto):
        self.label_contenido.configure(text=texto)  


if __name__ == "__main__":
    app = App()
    app.mainloop()