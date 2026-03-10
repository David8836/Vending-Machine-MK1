import tkinter as tk
from PIL import Image, ImageTk


def load_icon(path, size=30):
    return ImageTk.PhotoImage(Image.open(path).resize((size, size)))


def make_button(parent, text, bg, hover_bg, command=None, width=None):

    b = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        bg=bg,
        fg="white",
        activebackground=hover_bg,
        relief="flat",
        bd=0,
        padx=10,
        pady=6,
        font=("Arial", 10, "bold"),
        cursor="hand2"
    )

    def enter(_):
        if str(b["state"]) == "normal":
            b.config(bg=hover_bg)

    def leave(_):
        if str(b["state"]) == "normal":
            b.config(bg=bg)

    b.bind("<Enter>", enter)
    b.bind("<Leave>", leave)

    return b