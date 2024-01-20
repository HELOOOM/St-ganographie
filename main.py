import threading
import time
from customtkinter import *
from tkinterdnd2 import TkinterDnD, DND_ALL
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from stegano import lsb

set_appearance_mode("dark")
set_default_color_theme("GuiTheme.json")

class Tk(CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

def show_error():
    showerror("ERROR", "Expected a PNG image but received another file")

FILE = None
progressbar = None
img = None
frame = None
selected_method = None

def encode_img(text):
    global progressbar, img
    img = lsb.hide(FILE, text)
    progressbar.stop()

    for x in range(0, 101):
        progressbar.set(2 * x / 100)
        root.update()

    time.sleep(0.5)
    for widget in frame.winfo_children():
        widget.destroy()

    save_btn = CTkButton(frame, text="Enregistrer l'image", font=("HaxrCorp4089", 20), command=save, fg_color="#00ff00")
    save_btn.place(anchor="center", relx=0.5, rely=0.5)

    go_back = CTkButton(frame, text="Revenir en arrière", font=("HaxrCorp4089", 20), command=home, fg_color="#ff0000")
    go_back.place(anchor="nw", x=20, y=20)

def save():
    file = asksaveasfilename()
    if file != "":
        if file.endswith(".png"):
            img.save(file)
        else:
            img.save(file + ".png")

def encode(text):
    global progressbar

    for widget in frame.winfo_children():
        widget.destroy()
    description = CTkLabel(frame, text="Travail en cours.....", font=("HaxrCorp4089", 20), anchor="w", fg_color="#ffffff")
    description.pack(fill="x", pady=20, padx=20)
    progressbar = CTkProgressBar(frame, height=20, corner_radius=3)
    progressbar.pack(expand=True, fill="x", padx=20)
    progressbar.start()
    t1 = threading.Thread(target=encode_img, args=(text,))
    t1.start()

def choose_image_and_encode():
    global FILE
    file = askopenfilename()
    if file != "":
        if file.endswith(".png") or file.endswith(".PNG"):
            FILE = file
            method_selection_ui()
        else:
            show_error()

def method_selection_ui():
    for widget in frame.winfo_children():
        widget.destroy()

    # Create a label for method selection
    method_label = CTkLabel(frame, text="Sélectionnez une méthode de codage:", font=("HaxrCorp4089", 20))
    method_label.pack(pady=20)

    # Define the encoding method options
    methods = ["LSB", "PVD", "DCT", "DHWT"]

    # Create buttons for each method
    for method in methods:
        method_btn = CTkButton(frame, font=("HaxrCorp4089", 20), text=f" {method} ", anchor="w",
                               command=lambda m=method: process_encoding_method(m))
        method_btn.pack(expand=True, fill="both", padx=20, pady=(0, 20))

def process_encoding_method(method):
    global selected_method
    selected_method = method
    encode_ui()

def encode_ui():
    for widget in frame.winfo_children():
        widget.destroy()

    data = CTkTextbox(frame, height=150, font=("HaxrCorp4089", 20))
    data.pack(expand=True, fill="both", padx=20, pady=20)

    encode_btn = CTkButton(frame, font=("HaxrCorp4089", 20), text="Dissimuler le secret", anchor="w", command=lambda: encode(data.get(0.0, "end")), fg_color="#00ff00")
    encode_btn.pack(expand=True, fill="both", padx=20, pady=(0, 20))

def decode_ui():
    for widget in frame.winfo_children():
        widget.destroy()
    try:
        data = lsb.reveal(FILE)
        text = CTkLabel(frame, text=data, font=("HaxrCorp4089", 20), wraplength=500, fg_color="#ffffff", bg_color="transparent")
        text.place(anchor="center", relx=0.5, rely=0.5)

        go_back = CTkButton(frame, text="Revenir en arrière", font=("HaxrCorp4089", 20), command=home, fg_color="#ff0000")
        go_back.place(anchor="nw", x=20, y=20)
    except Exception as e:
        showerror("Error", e)
        go_back = CTkButton(frame, text="Revenir en arrière", font=("HaxrCorp4089", 20), command=home, fg_color="#ff0000")
        go_back.place(anchor="nw", x=20, y=20)

def encode_or_decode_ui():
    for widget in frame.winfo_children():
        widget.destroy()

    hide_btn = CTkButton(frame, text="Dissimuler le secret", font=("HaxrCorp4089", 20), command=choose_image_and_encode, fg_color="#00ff00")
    hide_btn.pack(expand=True, fill="both", padx=20, pady=(20, 20))

    extract_btn = CTkButton(frame, text="Extraire le secret", font=("HaxrCorp4089", 20), command=choose_file_decod, fg_color="#0000ff")
    extract_btn.pack(expand=True, fill="both", padx=20, pady=(0, 20))

def choose_file_decod():
    file = askopenfilename()

    if file != "":
        if file.endswith(".png") or file.endswith(".PNG"):
            global FILE
            FILE = file
            decode_ui()
        else:
            show_error()

def home():
    global frame
    if frame is not None:
        frame.destroy()

    frame = CTkFrame(root)
    frame.pack(padx=20, pady=20, expand=True, fill="both")

    title = CTkLabel(frame, text="Stega Interface", font=("HaxrCorp4089", 50), fg_color="#ffffff")
    title.pack(pady=20)

    description = CTkLabel(frame, text="Bienvenue dans Stega Interface! Cet outil vous permet de dissimuler  et extraire des messages dans des images en utilisant diverses méthodes.", font=("HaxrCorp4089", 16), fg_color="#ffffff")
    description.pack(pady=10)

    start_btn = CTkButton(frame, text="Commencer", font=("HaxrCorp4089", 20), command=encode_or_decode_ui, fg_color="#4CAF50")
    start_btn.pack(expand=True, fill="both", padx=20, pady=(20, 20))

root = Tk()
root.geometry("800x600")
root.title("Cacher des données")
root.configure(bg="#F5F5F5")  # Fond vert foncé

home()
root.mainloop()
