import customtkinter as ctk
import os
from perfil import PerfilUsuario
from PIL import Image

from aprender import PantallaAprender
from constructor import PantallaConstructor
from progreso import PantallaProgreso
from ranking import PantallaRanking


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):

    def __init__(self, usuario):
        super().__init__()


        self.usuario = usuario
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

        ruta_foto = self.usuario.get(
            "foto",
            "imagenes/usuario_pred.png"
        )

        # por si la foto fue borrada
        if not os.path.exists(ruta_foto):
            ruta_foto = "imagenes/usuario_pred.png"


        foto_usuario_img = ctk.CTkImage(
            Image.open(ruta_foto),
            size=(45, 45)
        )


        # guardar referencia para que no desaparezca la imagen
        self.usuario_img = foto_usuario_img


        self.usuario_frame = ctk.CTkButton(
            self.barra,
            image=self.usuario_img,
            text=f"{self.usuario['nombre']}\n#5 ranking",
            font=("Arial", 13),
            anchor="w",
            compound="left",
            fg_color="#FFA626",
            hover_color="#FFB040",
            command=self.abrir_perfil,
            height=65,
            corner_radius=20
        )


        self.usuario_frame.pack(
            pady=(3, 3),
            padx=15,
            fill="x"
        )

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
            command=self.mostrar_ranking)
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
        self.mostrar_progreso()

    def cargar_texto(self, texto):
        self.limpiar_contenido()
        ctk.CTkLabel(self.contenido, text=texto, font=("Arial", 20)).pack(expand=True)

    def abrir_perfil(self):
        if hasattr(self, 'ventana_perfil') and self.ventana_perfil.winfo_exists():
            return

        self.update_idletasks()
        
        x = self.winfo_rootx() + self.barra.winfo_width()
        y = self.winfo_rooty()
        ancho = self.contenido.winfo_width()
        alto = self.contenido.winfo_height()

        px = x + (ancho // 2) - 225
        py = y + (alto // 2) - 290

        self.fondo_oscuro = ctk.CTkToplevel(self)
        self.fondo_oscuro.overrideredirect(True)
        self.fondo_oscuro.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.fondo_oscuro.configure(fg_color="#000000")
        self.fondo_oscuro.attributes("-alpha", 0.4)

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

        # ← limpiar el binding cuando se cierre el popup
        def al_cerrar_perfil():
            self.unbind("<Configure>")

        self.ventana_perfil.bind("<Destroy>", lambda e: al_cerrar_perfil())

        usuario = self.usuario
        perfil = PerfilUsuario(self.ventana_perfil, usuario)
        perfil.pack(expand=True, fill="both")

    def cerrar_sesion(self):

        self.after(100, self.abrir_login)


    def abrir_login(self):

        from login import SpeaklyApp

        self.destroy()

        login = SpeaklyApp()
        login.mainloop()

    def mostrar_progreso(self):
        self.limpiar_contenido()
        pantalla = PantallaProgreso(self.contenido, usuario=self.usuario)
        pantalla.pack(fill="both", expand=True)

    def mostrar_ranking(self):
        if hasattr(self, 'ventana_ranking') and self.ventana_ranking.winfo_exists():
            return

        self.update_idletasks()

        x = self.winfo_rootx() + self.barra.winfo_width()
        y = self.winfo_rooty()
        ancho = self.contenido.winfo_width()
        alto = self.contenido.winfo_height()

        px = x + (ancho // 2) - 230
        py = y + (alto // 2) - 260

        self.fondo_oscuro_ranking = ctk.CTkToplevel(self)
        self.fondo_oscuro_ranking.overrideredirect(True)
        self.fondo_oscuro_ranking.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.fondo_oscuro_ranking.configure(fg_color="#000000")
        self.fondo_oscuro_ranking.attributes("-alpha", 0.4)

        self.ventana_ranking = ctk.CTkToplevel(self)
        self.ventana_ranking.overrideredirect(True)
        self.ventana_ranking.geometry(f"460x520+{px}+{py}")
        self.ventana_ranking.grab_set()
        self.fondo_oscuro_ranking.lift()
        self.ventana_ranking.lift()

        def actualizar_pos(event=None):
            if hasattr(self, 'ventana_ranking') and self.ventana_ranking.winfo_exists():
                self.update_idletasks()
                x = self.winfo_rootx() + self.barra.winfo_width()
                y = self.winfo_rooty()
                ancho = self.contenido.winfo_width()
                alto = self.contenido.winfo_height()
                px = x + (ancho // 2) - 230
                py = y + (alto // 2) - 260
                self.ventana_ranking.geometry(f"460x520+{px}+{py}")
                if hasattr(self, 'fondo_oscuro_ranking') and self.fondo_oscuro_ranking.winfo_exists():
                    self.fondo_oscuro_ranking.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.bind("<Configure>", actualizar_pos)

        def al_cerrar_ranking():
            self.unbind("<Configure>")
            if hasattr(self, 'fondo_oscuro_ranking') and self.fondo_oscuro_ranking.winfo_exists():
                self.fondo_oscuro_ranking.destroy()

        self.ventana_ranking.bind("<Destroy>", lambda e: al_cerrar_ranking())

        from ranking import PantallaRanking
        popup = PantallaRanking(self.ventana_ranking, usuario=self.usuario, cerrar_cmd=self.ventana_ranking.destroy)
        popup.pack(expand=True, fill="both")

    def mostrar_aprender(self):                        # ← sin indice_verbo
        self.limpiar_contenido()
        pantalla = PantallaAprender(
            self.contenido,
            usuario=self.usuario.get("usuario", self.usuario.get("nombre", "")),
            indice_inicial=0,
            al_completar=self.mostrar_constructor      # ← recibe el string del verbo
        )
        pantalla.pack(fill="both", expand=True)

    def mostrar_constructor(self, nombre_verbo):      # ← renombrar parámetro
        self.limpiar_contenido()
        pantalla = PantallaConstructor(
            self.contenido,
            usuario=self.usuario.get("usuario", self.usuario.get("nombre", "")),
            nombre_verbo_inicial=nombre_verbo          # ← pasar el string
        )
        pantalla.pack(fill="both", expand=True)


if __name__ == "__main__":
    usuario_prueba = {
        "nombre":"Prueba",
        "correo":"prueba@gmail.com"
    }

    app = App(usuario_prueba)
    app.mainloop()