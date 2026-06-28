import customtkinter as ctk
from PIL import Image
from main import App
import os
import json


# ── Tema general ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

ORANGE      = "#F5A623"
ORANGE_DARK = "#E09410"
BG_WHITE    = "#FFFFFF"
BG_FIELD    = "#F2F2F2"
TEXT_DARK   = "#1A1A2E"
TEXT_GRAY   = "#9E9E9E"
TEXT_LIGHT  = "#CCCCCC"


# ══════════════════════════════════════════════════════════════════════════════
class SpeaklyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Speakly")
        self.geometry("1100x700")
        self.resizable(True, True)
        self.configure(fg_color=BG_WHITE)
        self.usuario_actual = None

        # Panel izquierdo (naranja) — fijo
        self.left = ctk.CTkFrame(self, width=730, corner_radius=0, fg_color=ORANGE)
        self.left.place(x=0, y=0, relheight=1)
        self.left.pack_propagate(False)
        self._build_left_panel()

        # Contenedor derecho (blanco) — las pantallas se intercambian aquí
        self.right = ctk.CTkFrame(self, width=370, corner_radius=0, fg_color=BG_WHITE)
        self.right.place(x=730, y=0, relheight=1)
        self.right.pack_propagate(False)

        self.show_login()

    # ── Panel izquierdo ───────────────────────────────────────────────────────
    def _build_left_panel(self):
        center = ctk.CTkFrame(self.left, fg_color="transparent")
        center.place(relx=0.5, rely=0.45, anchor="center")


        # Logo imagen
        logo_path = os.path.join(os.path.dirname(__file__), "imagenes", "logo-speakly.png")
        logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(180, 60))
        ctk.CTkLabel(center, image=logo_img, text="").pack()

        ctk.CTkLabel(center, text="Learn English in a fun way",
                        font=("Arial", 14), text_color="#FDEAC0").pack(pady=(6, 20))
    
        # Ícono Vocabulary
        vocab_box = ctk.CTkFrame(center, width=80, height=80, corner_radius=16,
                                    fg_color="#FDEAC0")
        vocab_box.pack()
        vocab_box.pack_propagate(False)
        ctk.CTkLabel(vocab_box, text="📚", font=("Arial", 28)).place(relx=0.5, rely=0.42, anchor="center")
        ctk.CTkLabel(vocab_box, text="Vocabulary", font=("Arial", 9, "bold"),
                        text_color=TEXT_DARK).place(relx=0.5, rely=0.82, anchor="center")
    
    # ── Utilidades de pantalla ────────────────────────────────────────────────
    def _clear_right(self):
        for w in self.right.winfo_children():
            w.destroy()
    
    # ══════════════════════════════════════════════════════════════════════════
    # PANTALLA 1 — LOGIN
    # ══════════════════════════════════════════════════════════════════════════
    def show_login(self):
        self._clear_right()
        f = self.right
    
        wrap = ctk.CTkFrame(f, fg_color="transparent")
        wrap.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88)
    
        ctk.CTkLabel(wrap, text="Log in", font=("Arial Black", 26, "bold"),
                        text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(wrap, text="Welcome back! 👋", font=("Arial", 13),
                        text_color=TEXT_GRAY).pack(anchor="w", pady=(2, 20))
    
        # Username / Email
        ctk.CTkLabel(wrap, text="USERNAME OR EMAIL", font=("Arial", 10, "bold"),
                        text_color=TEXT_DARK).pack(anchor="w")
        self.login_user = ctk.CTkEntry(wrap, placeholder_text="Username or email",
                                        height=42, corner_radius=10,
                                        fg_color=BG_FIELD, border_width=0,
                                        font=("Arial", 13))
        self.login_user.pack(fill="x", pady=(4, 14))
    
        # Password label row
        pwd_row = ctk.CTkFrame(wrap, fg_color="transparent")
        pwd_row.pack(fill="x")
        ctk.CTkLabel(pwd_row, text="PASSWORD", font=("Arial", 10, "bold"),
                        text_color=TEXT_DARK).pack(side="left")
        ctk.CTkButton(pwd_row, text="Forgot your password?", font=("Arial", 10),
                        text_color=ORANGE, fg_color="transparent", hover=False,
                        cursor="hand2", command=self.show_forgot,
                        width=0, height=20).pack(side="right")
    
        self.login_pwd = ctk.CTkEntry(wrap, placeholder_text="••••••••",
                                        height=42, corner_radius=10,
                                        fg_color=BG_FIELD, border_width=0,
                                        show="•", font=("Arial", 13))
        self.login_pwd.pack(fill="x", pady=(4, 22))
    
        # Sign in button
        ctk.CTkButton(wrap, text="Sign in", height=46, corner_radius=24,
                        fg_color=ORANGE, hover_color=ORANGE_DARK,
                        font=("Arial", 14, "bold"), text_color="white",
                        command=self._on_signin).pack(fill="x")
    
        # Sign up link
        link_row = ctk.CTkFrame(wrap, fg_color="transparent")
        link_row.pack(pady=(16, 0))
        ctk.CTkLabel(link_row, text="Don't have an account? ", font=("Arial", 12),
                        text_color=TEXT_GRAY).pack(side="left")
        ctk.CTkButton(link_row, text="Sign up", font=("Arial", 12, "bold"),
                        text_color=ORANGE, fg_color="transparent", hover=False,
                        cursor="hand2", command=self.show_register,
                        width=0, height=20).pack(side="left")
    
        # BY KODA
        koda_path = os.path.join(os.path.dirname(__file__), "imagenes", "Logo-KODA.png")
        koda_img = ctk.CTkImage(light_image=Image.open(koda_path), size=(80, 80))
        ctk.CTkLabel(wrap, image=koda_img, text="").pack(pady=(30, 0))

    def _on_signin(self):
        user = self.login_user.get().strip()
        pwd = self.login_pwd.get().strip()

        if not user or not pwd:
            self._show_msg(
                self.right,
                "Please fill in all fields.",
                "red"
            )
            return

        usuarios = self.cargar_usuarios()
        usuario_encontrado = None

        for usuario in usuarios:
            if ((usuario["usuario"] == user or 
                usuario["correo"] == user)
                and usuario["password"] == pwd):

                usuario_encontrado = usuario
                break

        if usuario_encontrado:

            self.destroy()


            app = App(usuario_encontrado)

            app.mainloop()
        else:

            self._show_msg(
                self.right,
                "Incorrect username or password",
                "red"
            )
    
    # ══════════════════════════════════════════════════════════════════════════
    # PANTALLA 2 — REGISTRO
    # ══════════════════════════════════════════════════════════════════════════
    def show_register(self):
        self._clear_right()
        f = self.right
    
        wrap = ctk.CTkFrame(f, fg_color="transparent")
        wrap.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88)
    
        ctk.CTkLabel(wrap, text="Create account", font=("Arial Black", 24, "bold"),
                        text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(wrap, text="Join and start learning! 🚀", font=("Arial", 13),
                        text_color=TEXT_GRAY).pack(anchor="w", pady=(2, 16))
    
        fields = [
            ("FULL NAME",         "John Smith",        False),
            ("USERNAME",          "john123",           False),
            ("EMAIL ADDRESS",     "john@email.com",    False),
            ("PASSWORD",          "Min. 8 characters", True),
            ("CONFIRM PASSWORD",  "Repeat your password", True),
        ]
        self.reg_entries = {}
        for label, placeholder, is_pwd in fields:
            ctk.CTkLabel(wrap, text=label, font=("Arial", 10, "bold"),
                            text_color=TEXT_DARK).pack(anchor="w")
            e = ctk.CTkEntry(wrap, placeholder_text=placeholder,
                                height=40, corner_radius=10,
                                fg_color=BG_FIELD, border_width=0,
                                show="•" if is_pwd else "",
                                font=("Arial", 13))
            e.pack(fill="x", pady=(3, 10))
            self.reg_entries[label] = e
    
        ctk.CTkButton(wrap, text="Create account", height=46, corner_radius=24,
                        fg_color=ORANGE, hover_color=ORANGE_DARK,
                        font=("Arial", 14, "bold"), text_color="white",
                        command=self._on_register).pack(fill="x", pady=(4, 0))
    
        link_row = ctk.CTkFrame(wrap, fg_color="transparent")
        link_row.pack(pady=(12, 0))
        ctk.CTkLabel(link_row, text="Already have an account? ", font=("Arial", 12),
                        text_color=TEXT_GRAY).pack(side="left")
        ctk.CTkButton(link_row, text="Log in", font=("Arial", 12, "bold"),
                        text_color=ORANGE, fg_color="transparent", hover=False,
                        cursor="hand2", command=self.show_login,
                        width=0, height=20).pack(side="left")
    
    def _on_register(self):
        vals = {k: e.get().strip() for k, e in self.reg_entries.items()}
        if any(v == "" for v in vals.values()):
            self._show_msg(self.right, "Please fill in all fields.", "red")
            return
        if vals["PASSWORD"] != vals["CONFIRM PASSWORD"]:
            self._show_msg(self.right, "Passwords do not match.", "red")
            return
        if len(vals["PASSWORD"]) < 8:
            self._show_msg(self.right, "Password must be at least 8 characters.", "red")
            return
        
        usuarios = self.cargar_usuarios()

        nuevo = {

            "nombre": vals["FULL NAME"],
            "usuario": vals["USERNAME"],
            "correo": vals["EMAIL ADDRESS"],
            "password": vals["PASSWORD"]

        }

        usuarios.append(nuevo)

        self.guardar_usuarios(usuarios)
        # Registro exitoso → ir a Login
        self._show_msg(self.right, "Account created! Please log in.", "green")
        self.after(1500, self.show_login)
    
    # ══════════════════════════════════════════════════════════════════════════
    # PANTALLA 3 — FORGOT PASSWORD
    # ══════════════════════════════════════════════════════════════════════════
    def show_forgot(self):
        self._clear_right()
        f = self.right
    
        wrap = ctk.CTkFrame(f, fg_color="transparent")
        wrap.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88)
    
        # ← Back
        ctk.CTkButton(wrap, text="← Back", font=("Arial", 12),
                        text_color=TEXT_GRAY, fg_color="transparent", hover=False,
                        cursor="hand2", command=self.show_login,
                        anchor="w", width=0, height=24).pack(anchor="w", pady=(0, 14))
    
        ctk.CTkLabel(wrap, text="Forgot your password?",
                        font=("Arial Black", 22, "bold"),
                        text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(wrap, text="Enter your email and we'll send you a reset link.",
                        font=("Arial", 12), text_color=TEXT_GRAY,
                        wraplength=300, justify="left").pack(anchor="w", pady=(4, 20))
    
        ctk.CTkLabel(wrap, text="EMAIL ADDRESS", font=("Arial", 10, "bold"),
                        text_color=TEXT_DARK).pack(anchor="w")
        self.forgot_email = ctk.CTkEntry(wrap, placeholder_text="john@email.com",
                                            height=42, corner_radius=10,
                                            fg_color=BG_FIELD, border_width=0,
                                            font=("Arial", 13))
        self.forgot_email.pack(fill="x", pady=(4, 22))
    
        ctk.CTkButton(wrap, text="Send link", height=46, corner_radius=24,
                        fg_color=ORANGE, hover_color=ORANGE_DARK,
                        font=("Arial", 14, "bold"), text_color="white",
                        command=self._on_forgot).pack(fill="x")
    
        link_row = ctk.CTkFrame(wrap, fg_color="transparent")
        link_row.pack(pady=(16, 0))
        ctk.CTkLabel(link_row, text="Don't have an account? ", font=("Arial", 12),
                        text_color=TEXT_GRAY).pack(side="left")
        ctk.CTkButton(link_row, text="Sign up", font=("Arial", 12, "bold"),
                        text_color=ORANGE, fg_color="transparent", hover=False,
                        cursor="hand2", command=self.show_register,
                        width=0, height=20).pack(side="left")
    
    def _on_forgot(self):
        email = self.forgot_email.get().strip()
        if not email or "@" not in email:
            self._show_msg(self.right, "Enter a valid email address.", "red")
            return
        self._show_msg(self.right, "Reset link sent! Check your inbox.", "green")
        self.after(1800, self.show_login)
    
    # ── Helper: mensaje flotante ──────────────────────────────────────────────
    def _show_msg(self, parent, text, color):
        colors = {"red": "#FF4444", "green": "#27AE60"}
        msg = ctk.CTkLabel(parent, text=text, font=("Arial", 12),
                            text_color=colors.get(color, color),
                            fg_color="transparent")
        msg.place(relx=0.5, rely=0.97, anchor="s")
        self.after(2500, msg.destroy)

    def cargar_usuarios(self):
        if not os.path.exists("usuarios.json"):
            with open("usuarios.json","w") as archivo:
                json.dump([], archivo)

            return []

        with open("usuarios.json","r") as archivo:
            return json.load(archivo)



    def guardar_usuarios(self, usuarios):
        with open("usuarios.json","w") as archivo:
            json.dump(
                usuarios,
                archivo,
                indent=4
            )    
    
    
# ── Punto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SpeaklyApp()
    app.mainloop()