import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def mostrar_fases(contenedor, fases: list, coste_total: float):
    if not fases:
        messagebox.showinfo("Resultado", "No hay fases para mostrar.")
        return

    win = tk.Toplevel(contenedor)
    win.title("Visualizacion de iteraciones")
    win.geometry("900x640")

    # Top: Coste total
    top = ttk.Frame(win, padding=(10, 10))
    top.pack(fill="x")

    coste_frame = tk.Frame(top, bg="#f4cccc", bd=2, relief="groove")
    coste_frame.pack(side="left", padx=(0, 12))
    lbl_coste = tk.Label(
        coste_frame,
        text=f"Coste total: {coste_total:.4f}",
        font=("Segoe UI", 14, "bold"),
        bg="#f4cccc",
        padx=12,
        pady=8,
    )
    lbl_coste.pack()
