import customtkinter as ctk
from perfil import PerfilUsuario
from PIL import Image

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
        self.barra = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#FF8C00")
        self.barra.grid(row=0, column=0, sticky="nsew")

        # Logo
        logo_img = ctk.CTkImage(Image.open("imagenes/logo-speakly.png"), size=(120, 120))
        self.logo_label = ctk.CTkLabel(self.barra, image=logo_img, text="")
        self.logo_label.pack(pady=(20, 10))

        # Foto + nombre de usuario (clickeable para abrir perfil)
        self.foto_usuario = ctk.CTkButton(self.barra, text="👤", font=("Arial", 40), 
            fg_color="transparent", hover_color="#e67700",
            command=self.abrir_perfil)
        self.foto_usuario.pack(pady=(10, 0))

        self.nombre_usuario = ctk.CTkButton(self.barra, text="Jhoel", font=("Arial", 14),
            fg_color="transparent", hover_color="#e67700",
            command=self.abrir_perfil)
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

    def abrir_perfil(self):
        if hasattr(self, 'popup_perfil') and self.popup_perfil.winfo_exists():
            return

        usuario_prueba = {"nombre": "Jhoel", "correo": "jhoel@example.com", "foto": ""}
        self.popup_perfil = PerfilUsuario(self.contenido, usuario_prueba)
        self.popup_perfil.place(relx=0.5, rely=0.5, anchor="center")      


if __name__ == "__main__":
    app = App()
    app.mainloop()