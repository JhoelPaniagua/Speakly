import customtkinter as ctk
from PIL import Image
from tkinter import filedialog


class PerfilUsuario(ctk.CTkFrame):
    def __init__(self, master, usuario, **kwargs):
        super().__init__(master, width=450, height=550, corner_radius=15,
            fg_color="#2b2b2b", border_width=2, border_color="#FF8C00", **kwargs)

        self.pack_propagate(False)

        self.usuario = usuario
        self.modo_edicion = False

        self.crear_widgets()

    def crear_widgets(self):
        # Título
        self.titulo = ctk.CTkLabel(self, text="Mi Perfil", font=("Arial", 20, "bold"))
        self.titulo.pack(pady=(20, 10))

        # Foto de perfil
        self.foto_label = ctk.CTkLabel(self, text="👤", font=("Arial", 50))
        self.foto_label.pack(pady=10)

        self.btn_cambiar_foto = ctk.CTkButton(self, text="Cambiar foto",
            command=self.cambiar_foto, width=150)
        self.btn_cambiar_foto.pack(pady=5)

        # Nombre
        self.entry_nombre = ctk.CTkEntry(self, placeholder_text="Nombre")
        self.entry_nombre.insert(0, self.usuario.get("nombre", ""))
        self.entry_nombre.configure(state="disabled")
        self.entry_nombre.pack(pady=8, padx=30, fill="x")

        # Correo
        self.entry_correo = ctk.CTkEntry(self, placeholder_text="Correo")
        self.entry_correo.insert(0, self.usuario.get("correo", ""))
        self.entry_correo.configure(state="disabled")
        self.entry_correo.pack(pady=8, padx=30, fill="x")

        # Botones inferiores
        self.btn_editar = ctk.CTkButton(self, text="Editar", command=self.toggle_edicion)
        self.btn_editar.pack(pady=(20, 5), padx=30, fill="x")

        self.btn_cerrar = ctk.CTkButton(self, text="Cerrar", fg_color="red",
            hover_color="darkred", command=self.destroy)
        self.btn_cerrar.pack(pady=5, padx=30, fill="x")

    def cambiar_foto(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imagenes", "*.png *.jpg *.jpeg")])
        if ruta:
            img = Image.open(ruta)
            ctk_img = ctk.CTkImage(img, size=(80, 80))
            self.foto_label.configure(image=ctk_img, text="")
            self.usuario["foto"] = ruta

    def toggle_edicion(self):
        if not self.modo_edicion:
            self.entry_nombre.configure(state="normal")
            self.entry_correo.configure(state="normal")
            self.btn_editar.configure(text="Guardar")
            self.modo_edicion = True
        else:
            self.usuario["nombre"] = self.entry_nombre.get()
            self.usuario["correo"] = self.entry_correo.get()
            self.entry_nombre.configure(state="disabled")
            self.entry_correo.configure(state="disabled")
            self.btn_editar.configure(text="Editar")
            self.modo_edicion = False