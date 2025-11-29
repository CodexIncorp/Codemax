import tkinter as tk
from tkinter import ttk, messagebox
from Deslizador import Deslizador
from Matriz import Matriz
import Algoritmo as codemax
from Ventana_resultado import mostrar_fases
import random
from typing import Any, Dict

BG = "#f7f8fb"
CARD = "#ffffff"
ACCENT = "#2b7be9"
ACCENT_HOVER = "#1a5fd6"
TEXT = "#222222"
MUTED = "#6b7280"
RED = "#ff4e4e"
RED_HOVER = "#ff3030"


def _crear_ventana():
    root = tk.Tk()
    root.update_idletasks()
    w_window = 900
    h_window = 560
    center_x_screen = (root.winfo_screenwidth() // 2) - (w_window // 2)
    center_y_screen = (root.winfo_screenheight() // 2) - (h_window // 2)
    root.geometry(f"{w_window}x{h_window}+{center_x_screen}+{center_y_screen}")
    root.title("CODEMAX")
    root.configure(bg=BG)

    estilo = ttk.Style(root)
    try:
        estilo.theme_use("clam")
    except Exception:
        pass
    return root


def _config_ventana(root):
    filas_var = tk.IntVar(value=3)
    cols_var = tk.IntVar(value=4)

    # Top bar
    top_bar = ttk.Frame(root)
    top_bar.pack(fill="x", padx=18, pady=(14, 6))

    titulo_frame = ttk.Frame(top_bar)
    titulo_frame.pack(side="left", anchor="w")
    lbl_titulo = ttk.Label(titulo_frame, text="CODEMAX", font=("Seogue UI", 14, "bold"))
    lbl_titulo.pack(anchor="w")
    lbl_sub = ttk.Label(titulo_frame, text="Transporte por lotes", foreground=MUTED)
    lbl_sub.pack(anchor="w")

    bact_frame = ttk.Frame(top_bar)
    bact_frame.pack(side="right", anchor="e")

    def estilo_btn(btn: tk.Button, color: str, color_hover: str):
        btn.configure(borderwidth=0, relief="flat", padx=10, pady=6, fg="white")

        def enter(e):
            try:
                btn.configure(bg=color_hover)
            except Exception:
                pass

        def leave(e):
            try:
                btn.configure(bg=color)
            except Exception:
                pass

        btn.bind("<Enter>", enter)
        btn.bind("<Leave>", leave)

    state: Dict[str, Any] = {"mtx": None}

    def crear_mtx(contenedor, filas, cols):
        if state["mtx"] is not None:
            try:
                state["mtx"].destroy()
            except Exception:
                pass
        mtx = Matriz(contenedor, filas, cols)
        mtx.pack(fill="both", expand=True, padx=20, pady=(6, 12))
        state["mtx"] = mtx
        return mtx

    def limpiar():
        filas = 3
        cols = 4
        filas_var.set(filas)
        cols_var.set(cols)

        slider_ofer._set_valor(filas)
        slider_dem._set_valor(cols)
        crear_mtx(root, filas_var, cols_var)

    def aleatorio():
        filasr = random.randint(2, 10)
        colsr = random.randint(2, 10)
        filas_var.set(filasr)
        cols_var.set(colsr)

        slider_ofer._set_valor(filasr)
        slider_dem._set_valor(colsr)

        mtx = state["mtx"]
        if mtx is None:
            return
        mtx.llenar_aleatorio(
            filas=filasr,
            cols=colsr,
        )

    btn_limpiar = tk.Button(bact_frame, text="Limpiar", bg=RED, command=limpiar)
    btn_aleatorio = tk.Button(
        bact_frame, text="Aleatorio", bg=ACCENT, command=aleatorio
    )

    estilo_btn(btn_limpiar, RED, RED_HOVER)
    estilo_btn(btn_aleatorio, ACCENT, ACCENT_HOVER)

    btn_limpiar.pack(side="right", padx=(0, 6))
    btn_aleatorio.pack(side="right", padx=(0, 6))

    # Sliders
    frame_sliders = ttk.Frame(root)
    frame_sliders.pack(fill="x", padx=20, pady=(6, 8))
    frame_sliders.columnconfigure(0, weight=1)
    frame_sliders.columnconfigure(1, weight=1)

    # Frame para el deslizador de ofertas
    frame_ofer = ttk.LabelFrame(frame_sliders)
    frame_ofer.grid(row=0, column=0, padx=(0, 6), sticky="ew")
    lbl_ofer = ttk.Label(frame_ofer, text="Filas (ofertas)", foreground=TEXT)
    lbl_ofer.pack(anchor="w")
    slider_ofer = Deslizador(frame_ofer, inicial=filas_var.get())
    slider_ofer.pack(fill="x", pady=(4, 0))
    slider_ofer._set_valor(filas_var.get())
    slider_ofer.valor_deslizador.trace_add(
        "write", lambda *a: filas_var.set(slider_ofer._get_valor())
    )

    # Frame para el deslizador de demandas
    frame_dem = ttk.LabelFrame(frame_sliders)
    frame_dem.grid(row=0, column=1, padx=(6, 0), sticky="ew")
    lbl_dem = ttk.Label(frame_dem, text="Columnas (demandas)", foreground=TEXT)
    lbl_dem.pack(anchor="w")
    slider_dem = Deslizador(frame_dem, inicial=cols_var.get())
    slider_dem.pack(fill="x", pady=(4, 0))
    slider_dem._set_valor(cols_var.get())
    slider_dem.valor_deslizador.trace_add(
        "write", lambda *a: cols_var.set(slider_dem._get_valor())
    )

    mtxwd = crear_mtx(root, filas_var, cols_var)

    frame_botones = ttk.Frame(root)
    frame_botones.pack(fill="x", padx=12, pady=(6, 12))
    frame_botones.columnconfigure(0, weight=1)

    btn_calcular = tk.Button(
        frame_botones,
        text="Calcular",
        width=18,
        bg=ACCENT,
        fg="white",
        activebackground=ACCENT_HOVER,
        command=lambda: calcular(state["mtx"]),
    )

    estilo_btn(btn_calcular, ACCENT, ACCENT_HOVER)
    btn_calcular.pack(side="top", pady=(6, 0))

    state["slider_ofer"] = slider_ofer
    state["slider_dem"] = slider_dem
    state["btn_calcular"] = btn_calcular


def calcular(mtx: Matriz):
    costos = mtx.obtener_costos()
    ofertas = mtx.obtener_ofertas()
    demandas = mtx.obtener_demandas()

    if not costos:
        messagebox.showwarning("Calcular", "La matriz de costes esta vacia.")
        return
    fases, coste_total = codemax.resolver_transporte(costos, ofertas, demandas)
    mostrar_fases(mtx.master, fases, coste_total)


def main():
    root = _crear_ventana()
    _config_ventana(root)
    root.mainloop()


if __name__ == "__main__":
    main()