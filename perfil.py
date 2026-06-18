import customtkinter as ctk
from PIL import Image
from tkinter import filedialog


class PerfilUsuario(ctk.CTkFrame):
    def __init__(self, master, usuario, **kwargs):
        super().__init__(master, width=400, height=500, corner_radius=15,
            fg_color="#FFFFFF", border_width=0, **kwargs)

        self.pack_propagate(False)

        self.usuario = usuario
        self.modo_edicion = False

        self.crear_widgets()

    def crear_widgets(self):
        # ---------- HEADER NARANJA ----------
        self.header = ctk.CTkFrame(self, corner_radius=0, fg_color="#FF8C00", height=180)
        self.header.pack(fill="x", side="top")

        # Título + botón cerrar
        self.titulo = ctk.CTkLabel(self.header, text="My Profile",
            font=("Arial", 20, "bold"), text_color="white")
        self.titulo.place(x=25, y=20)

        self.btn_cerrar = ctk.CTkButton(self.header, text="✕", width=30, height=30,
            corner_radius=15, fg_color="#e67700", hover_color="#cc6a00",
            text_color="white", command=self.destroy)
        self.btn_cerrar.place(relx=1.0, x=-25, y=20, anchor="ne")

        # Foto + nombre + correo + badge ranking
        self.foto_label = ctk.CTkLabel(self.header, text="👤", font=("Arial", 30),
            fg_color="#ffb366", corner_radius=10, width=60, height=60)
        self.foto_label.place(x=25, y=70)

        self.nombre_label = ctk.CTkLabel(self.header,
            text=self.usuario.get("nombre", "Usuario"),
            font=("Arial", 16, "bold"), text_color="white")
        self.nombre_label.place(x=95, y=72)

        self.correo_label = ctk.CTkLabel(self.header,
            text=self.usuario.get("correo", ""),
            font=("Arial", 11), text_color="#ffe0c2")
        self.correo_label.place(x=95, y=96)

        self.badge_ranking = ctk.CTkLabel(self.header, text="#5 ranking",
            font=("Arial", 10, "bold"), text_color="#FF8C00",
            fg_color="white", corner_radius=10, width=80, height=20)
        self.badge_ranking.place(x=95, y=118)

        # ---------- TARJETAS STREAK / MASTERED / RANKING ----------
        self.stats_frame = ctk.CTkFrame(self, fg_color="white")
        self.stats_frame.pack(fill="x", padx=25, pady=(15, 10))

        self.tarjeta_streak = self.crear_tarjeta_stat(self.stats_frame, "🔥", "7", "Streak", "#fff0e0")
        self.tarjeta_streak.pack(side="left", expand=True, fill="both", padx=5)

        self.tarjeta_mastered = self.crear_tarjeta_stat(self.stats_frame, "📚", "0/16", "Mastered", "#fff0e0")
        self.tarjeta_mastered.pack(side="left", expand=True, fill="both", padx=5)

        self.tarjeta_ranking = self.crear_tarjeta_stat(self.stats_frame, "🏆", "#5", "Ranking", "#fff8d6")
        self.tarjeta_ranking.pack(side="left", expand=True, fill="both", padx=5)

        # ---------- EDIT DETAILS ----------
        self.edit_header = ctk.CTkFrame(self, fg_color="white")
        self.edit_header.pack(fill="x", padx=25, pady=(15, 5))

        self.label_edit = ctk.CTkLabel(self.edit_header, text="EDIT DETAILS",
            font=("Arial", 13, "bold"), text_color="#1a1a1a")
        self.label_edit.pack(side="left")

        self.btn_editar = ctk.CTkButton(self.edit_header, text="✏ Edit", width=70, height=28,
            corner_radius=12, fg_color="#ffe0c2", text_color="#FF8C00",
            hover_color="#ffd2a8", command=self.toggle_edicion)
        self.btn_editar.pack(side="right")

        # ---------- CAMPOS NAME / EMAIL ----------
        self.fila1 = ctk.CTkFrame(self, fg_color="white")
        self.fila1.pack(fill="x", padx=25, pady=5)

        self.col_nombre = ctk.CTkFrame(self.fila1, fg_color="white")
        self.col_nombre.pack(side="left", expand=True, fill="both", padx=(0, 8))
        ctk.CTkLabel(self.col_nombre, text="NAME", font=("Arial", 10, "bold"),
            text_color="gray", anchor="w").pack(fill="x")
        self.entry_nombre = ctk.CTkEntry(self.col_nombre, fg_color="#f5f5f5",
            border_width=0, corner_radius=8)
        self.entry_nombre.insert(0, self.usuario.get("nombre", ""))
        self.entry_nombre.configure(state="disabled")
        self.entry_nombre.pack(fill="x", pady=(5, 0))

        self.col_correo = ctk.CTkFrame(self.fila1, fg_color="white")
        self.col_correo.pack(side="left", expand=True, fill="both", padx=(8, 0))
        ctk.CTkLabel(self.col_correo, text="EMAIL", font=("Arial", 10, "bold"),
            text_color="gray", anchor="w").pack(fill="x")
        self.entry_correo = ctk.CTkEntry(self.col_correo, fg_color="#f5f5f5",
            border_width=0, corner_radius=8)
        self.entry_correo.insert(0, self.usuario.get("correo", ""))
        self.entry_correo.configure(state="disabled")
        self.entry_correo.pack(fill="x", pady=(5, 0))

        # ---------- COUNTRY ----------
        self.col_pais = ctk.CTkFrame(self, fg_color="white")
        self.col_pais.pack(fill="x", padx=25, pady=8)
        ctk.CTkLabel(self.col_pais, text="COUNTRY", font=("Arial", 10, "bold"),
            text_color="gray", anchor="w").pack(fill="x")
        self.entry_pais = ctk.CTkEntry(self.col_pais, fg_color="#f5f5f5",
            border_width=0, corner_radius=8)
        self.entry_pais.insert(0, self.usuario.get("pais", ""))
        self.entry_pais.configure(state="disabled")
        self.entry_pais.pack(fill="x", pady=(5, 0))

        # ---------- BIO ----------
        self.col_bio = ctk.CTkFrame(self, fg_color="white")
        self.col_bio.pack(fill="x", padx=25, pady=8)
        ctk.CTkLabel(self.col_bio, text="BIO", font=("Arial", 10, "bold"),
            text_color="gray", anchor="w").pack(fill="x")
        self.entry_bio = ctk.CTkTextbox(self.col_bio, fg_color="#f5f5f5",
            border_width=0, corner_radius=8, height=60)
        self.entry_bio.insert("1.0", self.usuario.get("bio", ""))
        self.entry_bio.configure(state="disabled")
        self.entry_bio.pack(fill="x", pady=(5, 0))

    def crear_tarjeta_stat(self, master, emoji, valor, label, color_fondo):
        tarjeta = ctk.CTkFrame(master, corner_radius=12, fg_color=color_fondo, height=90)
        ctk.CTkLabel(tarjeta, text=emoji, font=("Arial", 18)).pack(pady=(12, 0))
        ctk.CTkLabel(tarjeta, text=valor, font=("Arial", 16, "bold"),
            text_color="#1a1a1a").pack()
        ctk.CTkLabel(tarjeta, text=label, font=("Arial", 10),
            text_color="gray").pack(pady=(0, 10))
        return tarjeta

    def toggle_edicion(self):
        if not self.modo_edicion:
            self.entry_nombre.configure(state="normal")
            self.entry_correo.configure(state="normal")
            self.entry_pais.configure(state="normal")
            self.entry_bio.configure(state="normal")
            self.btn_editar.configure(text="💾 Save")
            self.modo_edicion = True
        else:
            self.usuario["nombre"] = self.entry_nombre.get()
            self.usuario["correo"] = self.entry_correo.get()
            self.usuario["pais"] = self.entry_pais.get()
            self.usuario["bio"] = self.entry_bio.get("1.0", "end-1c")
            self.entry_nombre.configure(state="disabled")
            self.entry_correo.configure(state="disabled")
            self.entry_pais.configure(state="disabled")
            self.entry_bio.configure(state="disabled")
            self.btn_editar.configure(text="✏ Edit")
            self.modo_edicion = False