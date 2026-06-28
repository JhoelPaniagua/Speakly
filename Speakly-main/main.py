import customtkinter as ctk
import os
from perfil import PerfilUsuario
from PIL import Image

from aprender import PantallaAprender
from constructor import PantallaConstructor


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
            command=self.abrir_ranking)
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

        # Título bienvenida
        ctk.CTkLabel(self.contenido, text=f"Welcome back, {self.usuario['nombre']}! 👋",
            font=("Arial", 26, "bold"), text_color="#1a1a1a").pack(anchor="w", padx=40, pady=(30, 0))
        ctk.CTkLabel(self.contenido, text="Continue your 7-day streak. Keep it up!",
            font=("Arial", 14), text_color="gray").pack(anchor="w", padx=40, pady=(5, 20))

        # Tarjeta YOUR PROGRESS
        tarjeta = ctk.CTkFrame(self.contenido, corner_radius=15, fg_color="#FF9600")
        tarjeta.pack(padx=40, pady=10, fill="x")

        # Fila superior: texto + stats
        fila_top = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila_top.pack(fill="x", padx=20, pady=(15, 5))

        # Izquierda: progreso
        izq = ctk.CTkFrame(fila_top, fg_color="transparent")
        izq.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(izq, text="YOUR PROGRESS", font=("Arial", 11, "bold"), text_color="#2b1500").pack(anchor="w")
        ctk.CTkLabel(izq, text="0 / 16 verbos", font=("Arial", 22, "bold"), text_color="white").pack(anchor="w", pady=(4, 0))

        # Derecha: cuadros stats (Streak, Ranking, Weak)
        der = ctk.CTkFrame(fila_top, fg_color="transparent")
        der.pack(side="right")

        stats = [("🔥", "7 days", "Streak"), ("🏆", "#5", "Ranking"), ("⚠️", "0", "Weak")]
        for ico, val, lbl in stats:
            c = ctk.CTkFrame(der, corner_radius=10, fg_color="#FFA726", width=75, height=70)
            c.pack(side="left", padx=4)
            c.pack_propagate(False)
            ctk.CTkLabel(c, text=ico, font=("Arial", 18)).pack(pady=(8, 0))
            ctk.CTkLabel(c, text=val, font=("Arial", 12, "bold"), text_color="white").pack()
            ctk.CTkLabel(c, text=lbl, font=("Arial", 9), text_color="#ffe0b0").pack()

        # Barra de progreso
        barra_frame = ctk.CTkFrame(tarjeta, fg_color="transparent")
        barra_frame.pack(fill="x", padx=20, pady=(10, 5))
        ctk.CTkLabel(barra_frame, text="Mastered verbs", font=("Arial", 11), text_color="#ffe0b0").pack(anchor="w")
        fila_barra = ctk.CTkFrame(barra_frame, fg_color="transparent")
        fila_barra.pack(fill="x")
        barra = ctk.CTkProgressBar(fila_barra, height=8, corner_radius=4,
            fg_color="#FFA726", progress_color="#ffffff")
        barra.set(0)
        barra.pack(side="left", fill="x", expand=True, pady=5)
        ctk.CTkLabel(fila_barra, text="0%", font=("Arial", 11), text_color="white").pack(side="right", padx=(8, 0))
        ctk.CTkLabel(tarjeta, text="Start practicing to track your progress!",
            font=("Arial", 11), text_color="#ffe0b0").pack(anchor="w", padx=20, pady=(0, 15))

        # LEARNING MODE
        ctk.CTkLabel(self.contenido, text="📖  LEARNING MODE",
            font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", padx=40, pady=(20, 8))

        btn_learn = ctk.CTkButton(self.contenido,
            text="Learn Vocabulary\nVocabulary + sentences for each verb",
            font=("Arial", 15, "bold"), text_color="white",
            fg_color="#FF9600", hover_color="#FFA726",
            corner_radius=15, height=70, anchor="w",
            command=self.mostrar_aprender)
        btn_learn.pack(padx=40, fill="x")

    def abrir_ranking(self):
        if hasattr(self, 'ventana_ranking') and self.ventana_ranking.winfo_exists():
            return

        self.update_idletasks()
        x = self.winfo_rootx() + self.barra.winfo_width()
        y = self.winfo_rooty()
        ancho = self.contenido.winfo_width()
        alto = self.contenido.winfo_height()
        px = x + (ancho // 2) - 200
        py = y + (alto // 2) - 230

        # Fondo oscuro
        self.fondo_ranking = ctk.CTkToplevel(self)
        self.fondo_ranking.overrideredirect(True)
        self.fondo_ranking.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.fondo_ranking.configure(fg_color="#000000")
        self.fondo_ranking.attributes("-alpha", 0.4)

        # Popup ranking
        self.ventana_ranking = ctk.CTkToplevel(self)
        self.ventana_ranking.overrideredirect(True)
        self.ventana_ranking.geometry(f"400x460+{px}+{py}")
        self.ventana_ranking.configure(fg_color="white")
        self.ventana_ranking.grab_set()
        self.ventana_ranking.lift()

        def cerrar_ranking():
            if hasattr(self, 'fondo_ranking') and self.fondo_ranking.winfo_exists():
                self.fondo_ranking.destroy()
            if hasattr(self, 'ventana_ranking') and self.ventana_ranking.winfo_exists():
                self.ventana_ranking.destroy()

        # Encabezado
        header = ctk.CTkFrame(self.ventana_ranking, fg_color="white", corner_radius=0)
        header.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkLabel(header, text="🏆  Ranking — Progress",
            font=("Arial", 16, "bold"), text_color="#1a1a1a").pack(side="left")
        ctk.CTkButton(header, text="✕", width=30, height=30, corner_radius=15,
            fg_color="transparent", text_color="gray", hover_color="#f0f0f0",
            command=cerrar_ranking).pack(side="right")

        # Columna header
        ctk.CTkLabel(self.ventana_ranking, text="MASTERED VERBS / 16",
            font=("Arial", 10), text_color="gray").pack(anchor="e", padx=25)

        ctk.CTkFrame(self.ventana_ranking, height=1, fg_color="#e0e0e0").pack(fill="x", padx=20, pady=5)

        # Datos del ranking
        jugadores = [
            (1,  "MX", "María García",     14, "🥇"),
            (2,  "CO", "Carlos López",     10, "🥈"),
            (3,  "AR", "Sofía Martín",      5, "🥉"),
            (4,  "PE", "Juan Rodríguez",    3, None),
            (5,  "BO", f"{self.usuario['nombre']} (tú)", 0, None),
        ]

        nombre_usuario = self.usuario['nombre']

        for pos, pais, nombre, verbos, medalla in jugadores:
            es_usuario = "(tú)" in nombre
            bg = "#FFF5EC" if es_usuario else "transparent"
            fila = ctk.CTkFrame(self.ventana_ranking, fg_color=bg, corner_radius=8)
            fila.pack(fill="x", padx=20, pady=3)

            # Posición o medalla
            pos_text = medalla if medalla else f"#{pos}"
            color_pos = "#FF9600" if es_usuario else "#888"
            ctk.CTkLabel(fila, text=pos_text, font=("Arial", 16), text_color=color_pos, width=35).pack(side="left", padx=(8, 4), pady=8)

            # País
            ctk.CTkLabel(fila, text=pais, font=("Arial", 11, "bold"), text_color="#555", width=28).pack(side="left")

            # Nombre y barra
            info = ctk.CTkFrame(fila, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=8, pady=6)
            color_nombre = "#FF9600" if es_usuario else "#1a1a1a"
            ctk.CTkLabel(info, text=nombre, font=("Arial", 13, "bold" if es_usuario else "normal"),
                text_color=color_nombre, anchor="w").pack(anchor="w")
            barra_r = ctk.CTkProgressBar(info, height=5, corner_radius=3,
                fg_color="#e0e0e0", progress_color="#FF9600" if es_usuario else "#aaa")
            barra_r.set(verbos / 16)
            barra_r.pack(fill="x", pady=(2, 0))

            # Score
            score_color = "#FF9600" if es_usuario else "#555"
            ctk.CTkLabel(fila, text=f"{verbos}/16 · {int(verbos/16*100)}%",
                font=("Arial", 11), text_color=score_color).pack(side="right", padx=12)

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
    usuario_prueba = {
        "nombre":"Prueba",
        "correo":"prueba@gmail.com"
    }

    app = App(usuario_prueba)
    app.mainloop()