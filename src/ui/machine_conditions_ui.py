import tkinter as tk
from PIL import Image, ImageTk
import random

def load_icon(path, size=40):
    return ImageTk.PhotoImage(Image.open(path).resize((size, size)))

class MachineConditionsUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Machine Conditions")

        self.ICON_SNOW = load_icon("assets/icons/snow.png")
        self.ICON_LEAF = load_icon("assets/icons/leaf.png")
        self.ICON_SUN  = load_icon("assets/icons/sun.png")
        self.ICON_WARN = load_icon("assets/icons/warning.png")
        self.ICON_X    = load_icon("assets/icons/redx.png")
        self.blank_icon = ImageTk.PhotoImage(Image.new("RGBA", (40, 40), (0, 0, 0, 0)))

        self.refrigeration_ok = True
        self.current_icon = self.ICON_LEAF
        self.blink_job = None
        self.blink_visible = True

        top = tk.Frame(root, padx=15, pady=12)
        top.pack(fill="x")

        self.temp_var = tk.StringVar(value="Temp: -- °F")
        self.hum_var = tk.StringVar(value="Hum: -- %")
        self.status_var = tk.StringVar(value="NORMAL")

        tk.Label(top, textvariable=self.temp_var, font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=5)
        tk.Label(top, textvariable=self.hum_var, font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=5)

        status_frame = tk.Frame(top)
        status_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=10)

        self.icon_label = tk.Label(status_frame, image=self.ICON_LEAF)
        self.icon_label.grid(row=0, column=0, sticky="e")

        self.status_label = tk.Label(status_frame, textvariable=self.status_var, font=("Arial", 10, "bold"))
        self.status_label.grid(row=1, column=0, sticky="e")

        self.update_conditions()

    def stop_blink(self):
        if self.blink_job is not None:
            self.root.after_cancel(self.blink_job)
            self.blink_job = None
        self.icon_label.config(image=self.current_icon)

    def blink(self, speed_ms):
        self.blink_visible = not self.blink_visible
        self.icon_label.config(image=self.current_icon if self.blink_visible else self.blank_icon)
        self.blink_job = self.root.after(speed_ms, lambda: self.blink(speed_ms))

    def set_status(self, state, icon):
        self.current_icon = icon
        self.icon_label.config(image=self.current_icon)
        self.status_var.set(state)

        if state == "CRITICAL":
            self.refrigeration_ok = False
            self.stop_blink()
            self.blink(250)
        elif state == "WARNING":
            self.refrigeration_ok = True
            self.stop_blink()
            self.blink(450)
        else:
            self.refrigeration_ok = True
            self.stop_blink()

    def read_sensors(self):
        temp_f = round(random.uniform(30, 55), 2)
        hum = round(random.uniform(20, 90), 2)
        return temp_f, hum

    def update_conditions(self):
        temp, hum = self.read_sensors()
        self.temp_var.set(f"Temp: {temp:.2f} °F")
        self.hum_var.set(f"Hum: {hum:.0f} %")

        if temp < 35:
            self.set_status("TOO COLD", self.ICON_SNOW)
        elif 35 <= temp <= 40:
            self.set_status("NORMAL", self.ICON_LEAF)
        elif 41 <= temp <= 45:
            self.set_status("WARNING", self.ICON_WARN)
        else:
            self.set_status("CRITICAL", self.ICON_X)

        self.root.after(2000, self.update_conditions)

if __name__ == "__main__":
    root = tk.Tk()
    app = MachineConditionsUI(root)
    root.mainloop()
