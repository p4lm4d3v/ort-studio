import customtkinter as ctk
import itertools
import csv
from tkinter import filedialog


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ORT Studio v1")
        ctk.set_appearance_mode("dark")

        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = int(screen_w * 0.75), int(screen_h * 0.75)
        self.geometry(f"{w}x{h}+{(screen_w-w)//2}+{(screen_h-h)//2}")

        self.n, self.m = 3, 2
        self.data_store = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.left_pane = ctk.CTkScrollableFrame(
            self, label_text="Tablica", corner_radius=10
        )
        self.left_pane.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.right_pane = ctk.CTkScrollableFrame(
            self, label_text="Karnoove Mape", corner_radius=10
        )
        self.right_pane.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        # MODERNIZOVANI TOOLBAR SA VIŠE PROSTORA
        self.toolbar = ctk.CTkFrame(
            self, height=90, corner_radius=15, fg_color="#2b2b2b"
        )
        self.toolbar.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 20)
        )  # Više paddinga oko toolbar-a

        # Raspored: Levo, Sredina, Desno
        # Dodajemo padding unutar sekcija da elementi 'dišu'
        self.t_left = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        self.t_left.pack(side="left", padx=30)
        self.t_right = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        self.t_right.pack(side="right", padx=30)

        # Kontrole levo
        self.create_control("Ulaz", "n", self.t_left)
        self.create_control("Izlaz", "m", self.t_left)

        # Generisi sredina (Enter)
        ctk.CTkButton(
            self.t_right,
            text="Generiši (Enter)",
            font=("Arial", 14, "bold"),
            height=40,
            width=100,
            fg_color="#2ecc71",
            text_color="black",
            hover_color="#27ae60",
            command=self.run_all,
        ).pack(side="left", padx=5, pady=15)

        # CSV desno
        ctk.CTkButton(
            self.t_right,
            text="Uvezi CSV",
            font=("Arial", 14),
            height=40,
            width=100,
            fg_color="#444",
            command=self.import_csv,
        ).pack(side="left", padx=5, pady=15)
        ctk.CTkButton(
            self.t_right,
            font=("Arial", 14),
            text="Izvezi CSV",
            height=40,
            width=100,
            fg_color="#444",
            command=self.export_csv,
        ).pack(side="left", padx=5, pady=15)

        # KEYBINDS (Pomeranje + Enter)
        self.bind("<Up>", lambda e: self.update_nm("n", 1))
        self.bind("<Down>", lambda e: self.update_nm("n", -1))
        self.bind("<Right>", lambda e: self.update_nm("m", 1))
        self.bind("<Left>", lambda e: self.update_nm("m", -1))
        self.bind("<Return>", lambda e: self.run_all())
        self.create_interface()

    def create_control(self, label_text, attr, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side="left", padx=10)

        label = ctk.CTkLabel(
            frame,
            text=f"{label_text} = {str(getattr(self, attr))}",
            font=("Arial", 24, "bold"),
            text_color="#2ecc71",
            width=30,
        )
        label.pack(side="left", padx=5)

        if attr == "n":
            self.n_label = label
        else:
            self.m_label = label

    def update_nm(self, attr, delta):
        if attr == "n":
            self.n = max(2, min(4, self.n + delta))
            self.n_label.configure(text=f"Ulaz = {str(getattr(self, attr))}")
        else:
            self.m = max(1, min(6, self.m + delta))
            self.m_label.configure(text=f"Izlaz = {str(getattr(self, attr))}")

    def run_all(self):
        self.create_interface()
        self.render_kmaps()
        self.focus_set()

    def create_interface(self):
        if hasattr(self, "table"):
            self.save_current_data()
        for w in self.left_pane.winfo_children():
            w.destroy()
        self.table = EditableTruthTable(self.left_pane, self.n, self.m, self.data_store)
        self.table.pack(expand=True, fill="both")

    def save_current_data(self):
        if hasattr(self, "table") and self.table.buttons:
            inputs_list = list(itertools.product([0, 1], repeat=self.n))

            # Prolazimo kroz sve moguće kombinacije
            for r, inputs in enumerate(inputs_list):
                # Provera da li red r postoji u tabeli
                if r < len(self.table.buttons):
                    for c in range(self.m):
                        # Provera da li kolona c postoji u tom redu
                        if c < len(self.table.buttons[r]):
                            try:
                                val = int(self.table.buttons[r][c].cget("text"))
                                self.data_store[(inputs, c)] = val
                            except:
                                continue

    def export_csv(self):
        print(self.data_store)
        name = f"{self.n}{self.m}"
        path = filedialog.asksaveasfilename(initialfile=name,defaultextension=".csv")
        if not path:
            return
        self.save_current_data()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [f"X{i+1}" for i in range(self.n)] + [f"Z{i+1}" for i in range(self.m)]
            )
            for inputs in itertools.product([0, 1], repeat=self.n):
                writer.writerow(
                    list(inputs)
                    + [self.data_store.get((inputs, j), 0) for j in range(self.m)]
                )

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "r") as f:
            reader = csv.reader(f)
            next(reader)
            self.data_store = {}
            for row in reader:
                inputs = tuple(int(x) for x in row[: self.n])
                for j, val in enumerate(row[self.n :]):
                    self.data_store[(inputs, j)] = int(val)
        self.run_all()

    def render_kmaps(self):
        # Očisti desni panel
        for w in self.right_pane.winfo_children():
            w.destroy()

        # Grid konfiguracija za desni panel
        self.right_pane.grid_columnconfigure(0, weight=1)
        self.right_pane.grid_columnconfigure(1, weight=1)

        for m_idx in range(self.m):
            data = {k[0]: v for k, v in self.data_store.items() if k[1] == m_idx}

            # Računanje pozicije u gridu (npr. 2 mape u redu)
            row = m_idx // 2
            col = m_idx % 2

            map_frame = KarnaughMapGrid(self.right_pane, f"Z{m_idx+1}", data, self.n)
            map_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")


class EditableTruthTable(ctk.CTkFrame):
    def __init__(self, master, n, m, data_store):
        super().__init__(master, fg_color="transparent")
        self.active_menu = None
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(anchor="center", pady=20)
        self.buttons = []
        header_row = ctk.CTkFrame(container, fg_color="transparent")
        header_row.pack(pady=(0, 5))
        for i in range(n):
            ctk.CTkLabel(
                header_row, text=f"X{i+1}", font=("Arial", 14, "bold"), width=55
            ).pack(side="left")
        for i in range(m):
            ctk.CTkButton(
                header_row,
                text=f"Z{i+1}",
                width=50,
                fg_color="transparent",
                text_color="#2ecc71",
                font=("Arial", 14, "bold"),
                command=lambda idx=i: self.show_menu(idx),
            ).pack(side="left")
        for inputs in itertools.product([0, 1], repeat=n):
            row_frame = ctk.CTkFrame(container, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            for val in inputs:
                box = ctk.CTkFrame(
                    row_frame,
                    width=45,
                    height=45,
                    fg_color="#333333",
                    border_width=1,
                    border_color="#555",
                )
                box.pack(side="left", padx=5)
                ctk.CTkLabel(box, text=str(val)).place(
                    relx=0.5, rely=0.5, anchor="center"
                )
            row_btns = []
            for c in range(m):
                val = data_store.get((inputs, c), 0)
                btn = ctk.CTkButton(
                    row_frame,
                    width=45,
                    height=45,
                    text=str(val),
                    fg_color="#1f538d" if val else "#333333",
                )
                btn.configure(command=lambda b=btn: self.toggle(b))
                btn.pack(side="left", padx=5)
                row_btns.append(btn)
            self.buttons.append(row_btns)

    def show_menu(self, col_idx):
        if self.active_menu:
            self.destroy_menu()
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        x, y = self.winfo_pointerx(), self.winfo_pointery()
        menu.geometry(f"100x120+{x}+{y}")

        def close_and_run(op):
            self.col_op(col_idx, op)
            self.destroy_menu()

        for txt, val in [("Flip (F)", "flip"), ("Sve 0", 0), ("Sve 1", 1)]:
            ctk.CTkButton(
                menu, text=txt, width=80, command=lambda v=val: close_and_run(v)
            ).pack(pady=5)
        menu.bind("<FocusOut>", lambda e: self.destroy_menu())
        self.active_menu = menu

    def destroy_menu(self):
        if self.active_menu:
            self.active_menu.destroy()
            self.active_menu = None

    def col_op(self, col_idx, op):
        for row in self.buttons:
            btn = row[col_idx]
            new_val = 1 - int(btn.cget("text")) if op == "flip" else op
            btn.configure(
                text=str(new_val), fg_color="#1f538d" if new_val else "#333333"
            )

    def toggle(self, btn):
        new_val = 1 - int(btn.cget("text"))
        btn.configure(text=str(new_val), fg_color="#1f538d" if new_val else "#333333")


class KarnaughMapGrid(ctk.CTkFrame):
    def __init__(self, master, title, data, n):
        super().__init__(
            master,
            fg_color="#2b2b2b",
            border_width=2,
            border_color="#555",
            corner_radius=8,
        )
        ctk.CTkLabel(
            self, text=title.upper(), font=("Arial", 16, "bold"), text_color="#2ecc71"
        ).pack(pady=10)
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=10, pady=10)
        rh = ["0", "1"] if n < 4 else ["00", "01", "11", "10"]
        ch = (
            ["0", "1"]
            if n == 2
            else (["00", "01", "11", "10"] if n >= 3 else ["0", "1"])
        )
        for c, h in enumerate(ch):
            ctk.CTkLabel(inner, text=h, font=("Arial", 14)).grid(
                row=0, column=c + 1, padx=5, pady=5
            )
        for r, rh_val in enumerate(rh):
            ctk.CTkLabel(inner, text=rh_val, font=("Arial", 14)).grid(
                row=r + 1, column=0, padx=5, pady=5
            )
            for c, ch_val in enumerate(ch):
                bits = (
                    tuple(int(b) for b in (ch_val + rh_val))
                    if n >= 3
                    else (int(ch_val), int(rh_val))
                )
                val = data.get(bits[-n:], 0)
                box = ctk.CTkFrame(inner, width=50, height=50, fg_color="#333333")
                box.grid(row=r + 1, column=c + 1, padx=5, pady=5)
                ctk.CTkLabel(
                    box,
                    text=str(val),
                    text_color="#21b773" if val else "#a81f1f",
                    font=("Arial", 16, "bold"),
                ).place(relx=0.5, rely=0.5, anchor="center")


if __name__ == "__main__":
    App().mainloop()
