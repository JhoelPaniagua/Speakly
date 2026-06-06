import customtkinter as ctk

app = ctk.CTk()
app.title("Speakly")
app.geometry("800x500")

label = ctk.CTkLabel(app, text="¡Bienvenido a Speakly!", font=("Arial", 24))
label.pack(pady=50)

app.mainloop()