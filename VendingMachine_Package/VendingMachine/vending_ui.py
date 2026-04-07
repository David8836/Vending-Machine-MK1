import tkinter as tk
from tkinter import messagebox
import time

from data import itemsMaster, categories
import machine_service
from ui_helpers import load_icon, make_button
from ui_conditions import read_sensors, process_machine_state


def start_ui():
    global root
    global category_index
    global product_type_label
    global listbox, cartbox
    global balance_label, cost_label
    global status_frame, icon_label, status_text, temp_label, hum_label

    category_index = 0
    last_sensor_update = 0
    cached_temp = 0
    cached_hum = 0

    root = tk.Tk()
    root.title("Vending Machine")

    ICON_COLD = load_icon("assets/icons/Cooled.png")
    ICON_NORMAL = load_icon("assets/icons/Normal.png")
    ICON_WARNING = load_icon("assets/icons/Warning.png")
    ICON_CRITICAL = load_icon("assets/icons/Temp_not_working.png")

    ITEM_LOGOS = {
        "Pepsi": "assets/logos/pepsi.png",
        "Doritos Nacho Cheese": "assets/logos/doritos.png",
        "Gatorade Cool Blue": "assets/logos/gatorade.png",
        "Oreo Cookies": "assets/logos/oreo.png",
        "Dasani Water": "assets/logos/dasani.png"
    }

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)

    top = tk.Frame(root)
    top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    top.grid_columnconfigure(0, weight=1)
    top.grid_columnconfigure(1, weight=1)

    balance_label = tk.Label(top, text="Balance: $0.00", font=("Arial", 16))
    balance_label.grid(row=0, column=0, sticky="w")

    status_frame = tk.Frame(top, bg="#2ECC71", padx=10, pady=6)
    status_frame.grid(row=0, column=1, sticky="e", padx=10)

    icon_label = tk.Label(status_frame, image=ICON_NORMAL, bg="#2ECC71")
    icon_label.grid(row=0, column=0, rowspan=2, padx=6)

    status_text = tk.Label(
        status_frame,
        text="NORMAL",
        font=("Arial", 10, "bold"),
        bg="#2ECC71",
        fg="white"
    )
    status_text.grid(row=0, column=1, sticky="w")

    temp_label = tk.Label(
        status_frame,
        text="--°F",
        font=("Arial", 10),
        bg="#2ECC71",
        fg="white"
    )
    temp_label.grid(row=1, column=1, sticky="w")

    hum_label = tk.Label(
        status_frame,
        text="--%",
        font=("Arial", 10),
        bg="#2ECC71",
        fg="white"
    )
    hum_label.grid(row=1, column=2, padx=6)

    middle = tk.Frame(root)
    middle.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

    middle.grid_columnconfigure(0, weight=1)
    middle.grid_columnconfigure(1, weight=1)
    middle.grid_rowconfigure(0, weight=1)

    left = tk.Frame(middle)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(1, weight=1)

    header_frame = tk.Frame(left)
    header_frame.grid(row=0, column=0, sticky="w")

    product_type_label = tk.Label(
        header_frame,
        text="Product Type: Consumable",
        font=("Arial", 12, "bold")
    )
    product_type_label.pack(side="left")

    selected_item_logo_label = tk.Label(header_frame)
    selected_item_logo_label.pack(side="left", padx=(12, 0))

    listbox = tk.Listbox(left, width=50, height=15)
    listbox.grid(row=1, column=0, sticky="nsew", pady=(5, 10))

    left_buttons = tk.Frame(left)
    left_buttons.grid(row=2, column=0, sticky="ew")
    left_buttons.grid_columnconfigure(0, weight=1)
    left_buttons.grid_columnconfigure(1, weight=1)
    left_buttons.grid_columnconfigure(2, weight=1)
    left_buttons.grid_columnconfigure(3, weight=1)

    right = tk.Frame(middle)
    right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(1, weight=1)

    cart_label = tk.Label(right, text="Cart", font=("Arial", 12, "bold"))
    cart_label.grid(row=0, column=0, sticky="w")

    cartbox = tk.Listbox(right, width=50, height=15)
    cartbox.grid(row=1, column=0, sticky="nsew", pady=(5, 10))

    right_buttons = tk.Frame(right)
    right_buttons.grid(row=2, column=0, sticky="ew")
    for i in range(4):
        right_buttons.grid_columnconfigure(i, weight=1)

    def current_category():
        return categories[category_index]

    def filtered_codes():
        machine_service.refresh_inventory()
        return [
            code for code, data in itemsMaster.items()
            if data["category"] == current_category()
        ]

    def cart_total():
        return sum(itemsMaster[c]["price"] for c in machine_service.cart)

    def status_visible():
        return current_category() == "Consumable"

    def update_sensor_visibility():
        if status_visible():
            status_frame.grid(row=0, column=1, sticky="e", padx=10)
        else:
            status_frame.grid_remove()

    def update_action_states():
        cart_has_items = len(machine_service.cart) > 0
        can_checkout = cart_has_items and (
            not status_visible() or status_text.cget("text") != "CRITICAL"
        )

        checkout_btn.config(state="normal" if can_checkout else "disabled")
        remove_btn.config(state="normal" if cart_has_items else "disabled")

    def clear_selected_logo():
        selected_item_logo_label.config(image="", text="")
        selected_item_logo_label.image = None

    def update_selected_logo(event=None):
        sel = listbox.curselection()

        if not sel:
            clear_selected_logo()
            return

        code = listbox.get(sel[0]).split(" | ")[0]
        item = itemsMaster[code]

        if item["category"] != "Consumable":
            clear_selected_logo()
            return

        logo_path = ITEM_LOGOS.get(item["name"])

        if not logo_path:
            clear_selected_logo()
            return

        try:
            logo_image = load_icon(logo_path, size=45)
            selected_item_logo_label.config(image=logo_image, text="")
            selected_item_logo_label.image = logo_image
        except Exception:
            clear_selected_logo()

    def update_display():
        machine_service.refresh_inventory()

        product_type_label.config(text=f"Product Type: {current_category()}")

        listbox.delete(0, tk.END)
        for code in filtered_codes():
            item = itemsMaster[code]
            listbox.insert(
                tk.END,
                f"{code} | {item['name']} | ${item['price']:.2f} | Stock:{item['stock']}"
            )

        cartbox.delete(0, tk.END)
        for code in machine_service.cart:
            item = itemsMaster[code]
            cartbox.insert(
                tk.END,
                f"{code} | {item['name']} | ${item['price']:.2f}"
            )

        balance_label.config(text=f"Balance: ${machine_service.balance:.2f}")
        cost_label.config(text=f"Cost: ${cart_total():.2f}")
        update_sensor_visibility()
        update_action_states()
        clear_selected_logo()

    def add_selected():
        sel = listbox.curselection()

        if not sel:
            messagebox.showerror("Error", "Select an item first")
            return

        code = listbox.get(sel[0]).split(" | ")[0]

        if not machine_service.add_to_cart(code):
            messagebox.showerror("Error", "Out of stock")

        update_display()

    def remove_selected():
        sel = cartbox.curselection()

        if not sel:
            messagebox.showerror("Error", "Select a cart item first")
            return

        code = cartbox.get(sel[0]).split(" | ")[0]
        machine_service.remove_from_cart(code)
        update_display()

    def checkout_items():
        current_state = status_text.cget("text")

        if status_visible() and current_state == "CRITICAL":
            messagebox.showerror("Error", "Machine is in CRITICAL status. Checkout disabled.")
            return

        if len(machine_service.cart) == 0:
            messagebox.showerror("Error", "Cart is empty")
            return

        ok, msg = machine_service.checkout()

        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

        update_display()

    def money_and_refresh(amount):
        machine_service.insert_money(amount)
        update_display()

    def return_change_and_refresh():
        machine_service.return_change()
        update_display()

    def reset_stock_and_refresh():
        machine_service.reset_stock_to_data()
        update_display()
        messagebox.showinfo("Reset Stock", "Stock reset from data.py")

    def next_category():
        global category_index
        category_index = (category_index + 1) % len(categories)
        update_display()

    def prev_category():
        global category_index
        category_index = (category_index - 1) % len(categories)
        update_display()

    ADMIN_PIN = "1999"
    ADMIN_NAME = "D&E"
    MACHINE_NAME = "VM001"
    SERIAL_NUMBER = "SN-VM-001"

    def show_admin_info():
        info_window = tk.Toplevel(root)
        info_window.title("Admin Panel")
        info_window.resizable(False, False)

        info_frame = tk.Frame(info_window, padx=20, pady=20)
        info_frame.pack()

        tk.Label(
            info_frame,
            text="Admin Access Granted",
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 12))

        tk.Label(
            info_frame,
            text=f"Admin Name: {ADMIN_NAME}",
            font=("Arial", 12)
        ).pack(anchor="w", pady=2)

        tk.Label(
            info_frame,
            text=f"Machine Name: {MACHINE_NAME}",
            font=("Arial", 12)
        ).pack(anchor="w", pady=2)

        tk.Label(
            info_frame,
            text=f"Serial Number: {SERIAL_NUMBER}",
            font=("Arial", 12)
        ).pack(anchor="w", pady=2)

        make_button(
            info_frame,
            "Close",
            "#95A5A6",
            "#7F8C8D",
            info_window.destroy,
            width=10
        ).pack(pady=(12, 0))

    def open_admin_keypad():
        pin_window = tk.Toplevel(root)
        pin_window.title("Admin Access")
        pin_window.resizable(False, False)
        pin_window.grab_set()

        pin_value = tk.StringVar(value="")

        container = tk.Frame(pin_window, padx=15, pady=15)
        container.pack()

        tk.Label(
            container,
            text="Enter Admin PIN",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, columnspan=3, pady=(0, 10))

        pin_entry = tk.Entry(
            container,
            textvariable=pin_value,
            font=("Arial", 16),
            justify="center",
            show="*",
            state="readonly",
            width=10
        )
        pin_entry.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        def press_digit(digit):
            current = pin_value.get()
            if len(current) < 4:
                pin_value.set(current + str(digit))

        def clear_pin():
            pin_value.set("")

        def delete_last():
            pin_value.set(pin_value.get()[:-1])

        def submit_pin():
            if pin_value.get() == ADMIN_PIN:
                pin_window.destroy()
                show_admin_info()
            else:
                messagebox.showerror("Access Denied", "Incorrect PIN")
                clear_pin()

        keypad = [
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2),
            ("7", 4, 0), ("8", 4, 1), ("9", 4, 2),
            ("Clear", 5, 0), ("0", 5, 1), ("Del", 5, 2),
        ]

        for label, row, col in keypad:
            if label == "Clear":
                cmd = clear_pin
                width = 8
            elif label == "Del":
                cmd = delete_last
                width = 8
            else:
                cmd = lambda x=label: press_digit(x)
                width = 8

            make_button(
                container,
                label,
                "#34495E",
                "#2C3E50",
                cmd,
                width=width
            ).grid(row=row, column=col, padx=3, pady=3)

        make_button(
            container,
            "Enter",
            "#2ECC71",
            "#27AE60",
            submit_pin,
            width=12
        ).grid(row=6, column=0, columnspan=3, pady=(10, 0))

    back_btn = make_button(left_buttons, "Back", "#95A5A6", "#7F8C8D", prev_category, width=10)
    back_btn.grid(row=0, column=0, sticky="w", padx=(1, 1))

    admin_btn = make_button(left_buttons, "Admin Access", "#1ABC9C", "#16A085", open_admin_keypad, width=12)
    admin_btn.grid(row=1, column=0, sticky="w", padx=(1, 1), pady=(6, 0))

    next_btn = make_button(left_buttons, "Next", "#95A5A6", "#7F8C8D", next_category, width=10)
    next_btn.grid(row=0, column=1, padx=(1, 1))

    add_btn = make_button(left_buttons, "Add", "#3498DB", "#2980B9", add_selected, width=10)
    add_btn.grid(row=0, column=2, padx=(1, 1))

    reset_btn = make_button(left_buttons, "Reset Stock", "#8E44AD", "#7D3C98", reset_stock_and_refresh, width=12)
    reset_btn.grid(row=0, column=3, sticky="e", padx=(1, 1))

    b1 = make_button(right_buttons, "$1", "#34495E", "#2C3E50", lambda: money_and_refresh(1), width=6)
    b1.grid(row=0, column=0, sticky="ew", padx=1)

    b5 = make_button(right_buttons, "$5", "#34495E", "#2C3E50", lambda: money_and_refresh(5), width=6)
    b5.grid(row=0, column=1, sticky="ew", padx=1)

    b10 = make_button(right_buttons, "$10", "#34495E", "#2C3E50", lambda: money_and_refresh(10), width=6)
    b10.grid(row=0, column=2, sticky="ew", padx=1)

    remove_btn = make_button(right_buttons, "Remove", "#E74C3C", "#C0392B", remove_selected, width=8)
    remove_btn.grid(row=0, column=3, sticky="ew", padx=(30, 1))

    bottom = tk.Frame(root)
    bottom.grid(row=2, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))

    cost_label = tk.Label(bottom, text="Cost: $0.00", font=("Arial", 14))
    cost_label.grid(row=0, column=0, padx=(0, 10))

    checkout_btn = make_button(bottom, "Checkout", "#2ECC71", "#27AE60", checkout_items, width=12)
    checkout_btn.grid(row=0, column=1, padx=(0, 10))

    return_btn = make_button(bottom, "Return", "#F39C12", "#D68910", return_change_and_refresh, width=12)
    return_btn.grid(row=0, column=2)

    listbox.bind("<<ListboxSelect>>", update_selected_logo)

    def update_conditions():
        nonlocal last_sensor_update, cached_temp, cached_hum

        current_time = time.time()

        if current_time - last_sensor_update >= 30:
            cached_temp, cached_hum = read_sensors()
            last_sensor_update = current_time

        temp, hum = cached_temp, cached_hum

        temp_label.config(text=f"{temp:.1f}°F")
        hum_label.config(text=f"{hum:.0f}%")

        state = process_machine_state(temp, hum)
        status_text.config(text=state)

        if state == "TOO COLD":
            icon_label.config(image=ICON_COLD, bg="#3498DB")
            status_frame.config(bg="#3498DB")
            status_text.config(bg="#3498DB")
            temp_label.config(bg="#3498DB")
            hum_label.config(bg="#3498DB")

        elif state == "NORMAL":
            icon_label.config(image=ICON_NORMAL, bg="#2ECC71")
            status_frame.config(bg="#2ECC71")
            status_text.config(bg="#2ECC71")
            temp_label.config(bg="#2ECC71")
            hum_label.config(bg="#2ECC71")

        elif state == "WARNING":
            icon_label.config(image=ICON_WARNING, bg="#F39C12")
            status_frame.config(bg="#F39C12")
            status_text.config(bg="#F39C12")
            temp_label.config(bg="#F39C12")
            hum_label.config(bg="#F39C12")

        else:
            icon_label.config(image=ICON_CRITICAL, bg="#E74C3C")
            status_frame.config(bg="#E74C3C")
            status_text.config(bg="#E74C3C")
            temp_label.config(bg="#E74C3C")
            hum_label.config(bg="#E74C3C")

        update_sensor_visibility()
        update_action_states()
        root.after(2000, update_conditions)

    update_display()
    update_conditions()
    root.mainloop()