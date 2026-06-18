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

    def crear_barra_lateral(self):
        self.barra = ctk.CTkScrollableFrame(self, width=250, corner_radius=0, fg_color="#FF9600")
        self.barra.grid(row=0, column=0, sticky="nsew")

       # Logo
        logo_img = ctk.CTkImage(Image.open("imagenes/logo-speakly.png"), size=(120, 120))
        self.logo_label = ctk.CTkLabel(self.barra, image=logo_img, text="")
        self.logo_label.pack(pady=(20, 10))
        self.separador_logo = ctk.CTkFrame(self.barra, height=2, fg_color="#e67700")
        self.separador_logo.pack(fill="x", padx=15, pady=(0, 10))

        # Contenedor horizontal para foto + nombre (todo un solo botón)
        foto_usuario_img = ctk.CTkImage(Image.open("imagenes/usuario_pred.png"), size=(45, 45))
        
        self.usuario_frame = ctk.CTkButton(self.barra, 
            image=foto_usuario_img,
            text="Jhoel\n#5 ranking",
            font=("Arial", 13),
            anchor="w",
            compound="left",
            fg_color="transparent", 
            hover_color="#e67700", 
            command=self.abrir_perfil, 
            height=60)
        self.usuario_frame.pack(pady=(10, 20), padx=15, fill="x")

        

        # Botones de navegación
        self.btn_home = ctk.CTkButton(self.barra, text="🏠  Home", 
            font=("Arial", 14), anchor="w",
            fg_color="white", text_color="#FF8C00", hover_color="#f0f0f0",
            command=lambda: self.cambiar_contenido("📊 Aquí va Mi Progreso"))
        self.btn_home.pack(pady=(10, 5), padx=15, fill="x")

        self.btn_vocabulary = ctk.CTkButton(self.barra, text="📚  Vocabulary", 
            font=("Arial", 14), anchor="w",
            fg_color="transparent", text_color="white", hover_color="#e67700",
            command=lambda: self.cambiar_contenido("📚 Aquí va Aprender"))
        self.btn_vocabulary.pack(pady=5, padx=15, fill="x")

        # Separador
        self.separador = ctk.CTkFrame(self.barra, height=2, fg_color="#e67700")
        self.separador.pack(fill="x", padx=15, pady=15)

        self.btn_ranking = ctk.CTkButton(self.barra, text="🏆  Ranking", 
            font=("Arial", 14), anchor="w",
            fg_color="transparent", text_color="white", hover_color="#e67700",
            command=lambda: self.cambiar_contenido("🏆 Aquí va el Ranking (popup)"))
        self.btn_ranking.pack(pady=5, padx=15, fill="x")

        # Cuadros de racha y verbos
        self.stats_frame = ctk.CTkFrame(self.barra, fg_color="transparent")
        self.stats_frame.pack(pady=15, padx=15, fill="x")

        self.cuadro_racha = ctk.CTkFrame(self.stats_frame, corner_radius=10, 
            fg_color="#e67700", width=80, height=70)
        self.cuadro_racha.pack(side="left", padx=(0, 5), expand=True, fill="both")

        self.label_racha = ctk.CTkLabel(self.cuadro_racha, text="🔥\n7 days", 
            font=("Arial", 12, "bold"), text_color="white")
        self.label_racha.pack(expand=True)

        self.cuadro_verbos = ctk.CTkFrame(self.stats_frame, corner_radius=10, 
            fg_color="#e67700", width=80, height=70)
        self.cuadro_verbos.pack(side="left", padx=(5, 0), expand=True, fill="both")

        self.label_verbos_completados = ctk.CTkLabel(self.cuadro_verbos, text="📚\n0/16", 
            font=("Arial", 12, "bold"), text_color="white")
        self.label_verbos_completados.pack(expand=True)


        # Espacio flexible para empujar lo siguiente hacia abajo
        self.espacio_flexible = ctk.CTkLabel(self.barra, text="")
        self.espacio_flexible.pack(expand=True, fill="both")

        # Botón Log out
        self.btn_logout = ctk.CTkButton(self.barra, text="🚪  Log out", 
            font=("Arial", 14), anchor="w",
            fg_color="transparent", text_color="white", hover_color="#e67700",
            command=self.cerrar_sesion)
        self.btn_logout.pack(pady=10, padx=15, fill="x")

        # Texto "BY KODA"
        self.label_by = ctk.CTkLabel(self.barra, text="BY", 
            font=("Arial", 9), text_color="#2b1500")
        self.label_by.pack(pady=(10, 0))

        self.label_koda = ctk.CTkLabel(self.barra, text="KODA", 
            font=("Arial", 12, "bold"), text_color="white")
        self.label_koda.pack(pady=(0, 15))

    def crear_area_contenido(self):
        self.contenido = ctk.CTkFrame(self, fg_color="#FFF5EC")
        self.contenido.grid(row=0, column=1, sticky="nsew")

        # Saludo
        self.saludo = ctk.CTkLabel(self.contenido, text="Welcome back, Jhoel! 👋",
            font=("Arial", 26, "bold"), text_color="#1a1a1a")
        self.saludo.pack(anchor="w", padx=40, pady=(30, 0))

        self.subtitulo = ctk.CTkLabel(self.contenido, text="Continue your progress. Keep it up!",
            font=("Arial", 14), text_color="gray")
        self.subtitulo.pack(anchor="w", padx=40, pady=(5, 20))

        # Tarjeta de progreso
        self.tarjeta_progreso = ctk.CTkFrame(self.contenido, corner_radius=15, fg_color="#FF8C00")
        self.tarjeta_progreso.pack(padx=40, pady=10, fill="x")

        self.titulo_progreso = ctk.CTkLabel(self.tarjeta_progreso, text="YOUR PROGRESS",
            font=("Arial", 12, "bold"), text_color="#2b1500")
        self.titulo_progreso.pack(anchor="w", padx=20, pady=(15, 0))

        self.numero_verbos = ctk.CTkLabel(self.tarjeta_progreso, text="0 / 16 verbos",
            font=("Arial", 22, "bold"), text_color="white")
        self.numero_verbos.pack(anchor="w", padx=20, pady=(0, 15))

    def cambiar_contenido(self, texto):
        self.label_contenido.configure(text=texto)

    def cerrar_sesion(self):
        self.cambiar_contenido("🚪 Sesión cerrada (esto lo conecta el compañero de login)")    

    def abrir_perfil(self):
        if hasattr(self, 'popup_perfil') and self.popup_perfil.winfo_exists():
            return

        usuario_prueba = {"nombre": "Jhoel", "correo": "jhoel@example.com", "foto": ""}
        self.popup_perfil = PerfilUsuario(self.contenido, usuario_prueba)
        self.popup_perfil.place(relx=0.5, rely=0.5, anchor="center")      


if __name__ == "__main__":
    app = App()
    app.mainloop()