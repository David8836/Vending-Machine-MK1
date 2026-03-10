import tkinter as tk
import sqlite3
from config import DB_NAME


def connect():
    return sqlite3.connect(DB_NAME)


class AdminUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Vending Machine Admin Controller")
        self.root.geometry("1000x600")

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=2)
        root.grid_rowconfigure(0, weight=1)

        # LEFT PANEL (machine list)

        left = tk.Frame(root)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        tk.Label(left, text="Machines", font=("Arial", 14, "bold")).pack(anchor="w")

        self.machine_list = tk.Listbox(left, height=20)
        self.machine_list.pack(fill="both", expand=True)

        self.machine_list.bind("<<ListboxSelect>>", self.load_machine)

        # RIGHT PANEL

        right = tk.Frame(root)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        right.grid_rowconfigure(1, weight=1)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # ADMIN INFO

        info_frame = tk.LabelFrame(right, text="Machine Info")
        info_frame.grid(row=0, column=0, sticky="ew", pady=5)

        self.info_label = tk.Label(info_frame, text="Select a machine")
        self.info_label.pack(anchor="w", padx=10, pady=5)

        # STOCK PANEL

        stock_frame = tk.LabelFrame(right, text="Machine Stock")
        stock_frame.grid(row=1, column=0, sticky="nsew", pady=5)

        self.stock_list = tk.Listbox(stock_frame)
        self.stock_list.pack(fill="both", expand=True)

        # STATS PANEL

        stats_frame = tk.LabelFrame(right, text="Sales Statistics")
        stats_frame.grid(row=2, column=0, sticky="nsew", pady=5)

        self.stats_text = tk.Text(stats_frame, height=10)
        self.stats_text.pack(fill="both", expand=True)

        self.load_machines()

    # --------------------------

    def load_machines(self):

        conn = connect()
        cur = conn.cursor()

        cur.execute("SELECT machine_id FROM machine_status")

        rows = cur.fetchall()

        conn.close()

        self.machine_list.delete(0, tk.END)

        for row in rows:
            self.machine_list.insert(tk.END, row[0])

    # --------------------------

    def load_machine(self, event):

        sel = self.machine_list.curselection()

        if not sel:
            return

        machine_id = self.machine_list.get(sel[0])

        conn = connect()
        cur = conn.cursor()

        # MACHINE INFO

        cur.execute("""
        SELECT state, temperature, humidity
        FROM machine_status
        WHERE machine_id = ?
        """, (machine_id,))

        row = cur.fetchone()

        if row:
            state, temp, hum = row
            self.info_label.config(
                text=f"Machine: {machine_id}\nState: {state}\nTemp: {temp}\nHumidity: {hum}"
            )

        # STOCK

        self.stock_list.delete(0, tk.END)

        cur.execute("""
        SELECT item_code, name, stock
        FROM inventory
        ORDER BY item_code
        """)

        for code, name, stock in cur.fetchall():
            self.stock_list.insert(tk.END, f"{code} | {name} | Stock: {stock}")

        # STATS

        self.stats_text.delete("1.0", tk.END)

        cur.execute("""
        SELECT item_name, SUM(profit)
        FROM sales
        GROUP BY item_name
        ORDER BY SUM(profit) DESC
        LIMIT 1
        """)

        best_profit = cur.fetchone()

        cur.execute("""
        SELECT item_name, COUNT(*)
        FROM sales
        GROUP BY item_name
        ORDER BY COUNT(*) DESC
        LIMIT 1
        """)

        most_bought = cur.fetchone()

        cur.execute("""
        SELECT item_name, COUNT(*)
        FROM sales
        GROUP BY item_name
        ORDER BY COUNT(*) ASC
        LIMIT 1
        """)

        least_bought = cur.fetchone()

        text = ""

        if best_profit:
            text += f"Best Profit Item: {best_profit[0]} (${best_profit[1]:.2f})\n"

        if most_bought:
            text += f"Most Bought Item: {most_bought[0]} ({most_bought[1]} sales)\n"

        if least_bought:
            text += f"Least Bought Item: {least_bought[0]} ({least_bought[1]} sales)\n"

        self.stats_text.insert(tk.END, text)

        conn.close()


# ------------------------------

if __name__ == "__main__":

    root = tk.Tk()
    app = AdminUI(root)
    root.mainloop()