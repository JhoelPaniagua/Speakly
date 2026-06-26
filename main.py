import customtkinter as ctk
from perfil import PerfilUsuario
from PIL import Image

from aprender import PantallaAprender
from constructor import PantallaConstructor

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Speakly")
        self.geometry("1000x600")
        self.resizable(True, True)
        self.state("normal")


        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_barra_lateral()
        self.crear_area_contenido()

    def crear_barra_lateral(self):
        self.barra = ctk.CTkScrollableFrame(self, width=230, corner_radius=0, fg_color="#FF9600")
        self.barra._scrollbar.grid_remove()
        self.barra.grid(row=0, column=0, sticky="nsew")

        # Logo
        img = Image.open("imagenes/logo-speakly.png")
        

        logo_img = ctk.CTkImage(img, size=(120, 50))  # usa el tamaño real
        self.logo_label = ctk.CTkLabel(self.barra, image=logo_img, text="")
        self.logo_label.pack(pady=(25,30), anchor="nw", padx=(15, 0))  

        self.separador_logo = ctk.CTkFrame(self.barra, height=2, fg_color="#FCA327")
        self.separador_logo.pack(fill="x", padx=15, pady=(0, 5))

        # Usuario
        foto_usuario_img = ctk.CTkImage(Image.open("imagenes/usuario_pred.png"), size=(45, 45))
        self.usuario_frame = ctk.CTkButton(self.barra,
            image=foto_usuario_img, text="Jhoel\n#5 ranking",
            font=("Arial", 13), anchor="w", compound="left",
            fg_color="#FFA626", hover_color="#FFB040",
            command=self.abrir_perfil, height=65, corner_radius=20)
        self.usuario_frame.pack(pady=(3, 3), padx=15, fill="x")

        # Cargar íconos
        ico_home       = ctk.CTkImage(Image.open("imagenes/home.png"),    size=(22, 22))
        ico_vocabulary = ctk.CTkImage(Image.open("imagenes/libros.png"),  size=(22, 22))
        ico_ranking    = ctk.CTkImage(Image.open("imagenes/trofeo.png"),  size=(22, 22))
        ico_logout     = ctk.CTkImage(Image.open("imagenes/door.png"),    size=(32, 32)) 
        ico_fire       = ctk.CTkImage(Image.open("imagenes/flamita.png"), size=(28, 28))
        ico_books      = ctk.CTkImage(Image.open("imagenes/libros.png"),  size=(28, 28))


        # Botones navegación
        self.btn_home = ctk.CTkButton(self.barra, text="  Home", image=ico_home,
            font=("Arial", 14), anchor="w", compound="left",
            fg_color="white", text_color="#FF8C00", hover_color="#FFA626", height=55, corner_radius=20,
            command=self.mostrar_home)
        self.btn_home.pack(pady=(3, 3), padx=15, fill="x")

        self.btn_vocabulary = ctk.CTkButton(self.barra, text="  Vocabulary", image=ico_vocabulary,
            font=("Arial", 14), anchor="w",
            fg_color="transparent", text_color="white", hover_color="#FFA626", height=55, corner_radius=20,
            command=self.mostrar_aprender)
        self.btn_vocabulary.pack(pady=3, padx=15, fill="x")

        self.separador = ctk.CTkFrame(self.barra, height=2, fg_color="#FCA327")
        self.separador.pack(fill="x", padx=15, pady=5)

        self.btn_ranking = ctk.CTkButton(self.barra, text="  Ranking", image=ico_ranking,
            font=("Arial", 14), anchor="w",
            fg_color="transparent", text_color="white", hover_color="#FFA626", height=55, corner_radius=20,
            command=lambda: self.cargar_texto("🏆 Aquí va el Ranking"))
        self.btn_ranking.pack(pady=0, padx=15, fill="x")

        # Cuadros stats
        self.stats_frame = ctk.CTkFrame(self.barra, fg_color="transparent")
        self.stats_frame.pack(pady=3, padx=15, fill="x")

        self.cuadro_racha = ctk.CTkFrame(self.stats_frame, corner_radius=10, fg_color="#ff9626", height=70)
        self.cuadro_racha.pack(side="left", padx=(0, 5), expand=True, fill="both")
        ctk.CTkLabel(self.cuadro_racha, image=ico_fire, text="7 days",
            compound="top", font=("Arial", 11, "bold"), text_color="white").pack(expand=True)

        self.cuadro_verbos = ctk.CTkFrame(self.stats_frame, corner_radius=10, fg_color="#ff9626", height=70)
        self.cuadro_verbos.pack(side="left", padx=(5, 0), expand=True, fill="both")
        ctk.CTkLabel(self.cuadro_verbos, image=ico_books, text="0/16",
            compound="top", font=("Arial", 11, "bold"), text_color="white").pack(expand=True)

        # Log out y KODA
        ctk.CTkLabel(self.barra, text="").pack(expand=True, fill="both")

        self.btn_logout = ctk.CTkButton(self.barra, text="  Log out", image=ico_logout,
            font=("Arial", 14), anchor="w",
            fg_color="transparent", text_color="white", hover_color="#FF7B00", height=50, corner_radius=20,
            command=self.cerrar_sesion)
        self.btn_logout.pack(pady=(93, 1), padx=15, fill="x")

        ctk.CTkLabel(self.barra, text="BY", font=("Arial", 12), text_color="#D4D4D4").pack(pady=(0, 0))
        

        # Logo KODA
        logo_img = ctk.CTkImage(Image.open("imagenes/Logo-KODA.png"), size=(50, 50))
        self.logo_label = ctk.CTkLabel(self.barra, image=logo_img, text="")
        self.logo_label.pack(pady=(0, 3))

    def crear_area_contenido(self):
        self.contenido = ctk.CTkFrame(self, fg_color="#FFF5EC")
        self.contenido.grid(row=0, column=1, sticky="nsew")
        self.mostrar_home()

    def limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def mostrar_home(self):
        self.limpiar_contenido()

        ctk.CTkLabel(self.contenido, text="Welcome back, Jhoel! 👋",
            font=("Arial", 26, "bold"), text_color="#1a1a1a").pack(anchor="w", padx=40, pady=(30, 0))

        ctk.CTkLabel(self.contenido, text="Continue your progress. Keep it up!",
            font=("Arial", 14), text_color="gray").pack(anchor="w", padx=40, pady=(5, 20))

        tarjeta = ctk.CTkFrame(self.contenido, corner_radius=15, fg_color="#FF9600")
        tarjeta.pack(padx=40, pady=10, fill="x")

        ctk.CTkLabel(tarjeta, text="YOUR PROGRESS",
            font=("Arial", 12, "bold"), text_color="#2b1500").pack(anchor="w", padx=20, pady=(15, 0))

        ctk.CTkLabel(tarjeta, text="0 / 16 verbos",
            font=("Arial", 22, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(0, 15))

    def cargar_texto(self, texto):
        self.limpiar_contenido()
        ctk.CTkLabel(self.contenido, text=texto, font=("Arial", 20)).pack(expand=True)

    def abrir_perfil(self):
        if hasattr(self, 'ventana_perfil') and self.ventana_perfil.winfo_exists():
            return

        # Esperar que la ventana esté lista
        self.update_idletasks()
        
        x = self.winfo_rootx() + self.barra.winfo_width()
        y = self.winfo_rooty()
        ancho = self.contenido.winfo_width()
        alto = self.contenido.winfo_height()

        px = x + (ancho // 2) - 225
        py = y + (alto // 2) - 290

        # Fondo oscuro semitransparente
        self.fondo_oscuro = ctk.CTkToplevel(self)
        self.fondo_oscuro.overrideredirect(True)
        self.fondo_oscuro.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.fondo_oscuro.configure(fg_color="#000000")
        self.fondo_oscuro.attributes("-alpha", 0.4)

        # Popup encima
        self.ventana_perfil = ctk.CTkToplevel(self)
        self.ventana_perfil.overrideredirect(True)
        self.ventana_perfil.geometry(f"450x560+{px}+{py}")
        self.ventana_perfil.grab_set()
        self.ventana_perfil.lift()

        def actualizar_posicion(event=None):
            if hasattr(self, 'ventana_perfil') and self.ventana_perfil.winfo_exists():
                self.update_idletasks()
                x = self.winfo_rootx() + self.barra.winfo_width()
                y = self.winfo_rooty()
                ancho = self.contenido.winfo_width()
                alto = self.contenido.winfo_height()
                px = x + (ancho // 2) - 225
                py = y + (alto // 2) - 290
                self.ventana_perfil.geometry(f"450x560+{px}+{py}")
                if hasattr(self, 'fondo_oscuro') and self.fondo_oscuro.winfo_exists():
                    self.fondo_oscuro.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.bind("<Configure>", actualizar_posicion)

        usuario = {"nombre": "Jhoel", "correo": "jhoel@est.umss.edu", "pais": "Bolivia", "bio": ""}
        perfil = PerfilUsuario(self.ventana_perfil, usuario)
        perfil.pack(expand=True, fill="both")

    def cerrar_sesion(self):
        self.cargar_texto("🚪 Sesión cerrada")

    def mostrar_aprender(self, indice_verbo=0):
        self.limpiar_contenido()
        pantalla = PantallaAprender(
            self.contenido,
            usuario="Jhoel",
            indice_inicial=indice_verbo,
            al_completar=self.mostrar_constructor
        )
        pantalla.pack(fill="both", expand=True)

    def mostrar_constructor(self, indice_verbo):
        self.limpiar_contenido()
        pantalla = PantallaConstructor(
            self.contenido,
            usuario="Jhoel",
            indice_inicial=indice_verbo,
            al_completar_verbo=lambda verbo: self.mostrar_aprender(indice_verbo + 1)
            # ↑ avanza al siguiente
        )
        pantalla.pack(fill="both", expand=True) 


if __name__ == "__main__":
    app = App()
    app.mainloop()