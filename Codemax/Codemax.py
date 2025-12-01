import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
from Deslizador import Deslizador
from Matriz import Matriz
import Algoritmo as codemax
from Ventana_resultado import mostrar_fases
import random
from typing import Any, Dict
import math


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def crear_ventana():
    root = ctk.CTk()
    w_window = 950
    h_window = 600
    center_x_screen = (root.winfo_screenwidth() // 2) - (w_window // 2)
    center_y_screen = (root.winfo_screenheight() // 2) - (h_window // 2)
    root.geometry(f"{w_window}x{h_window}+{center_x_screen}+{center_y_screen}")
    root.title("CODEMAX")
    return root


def config_ventana(root):
    filas_var = tk.IntVar(value=3)
    cols_var = tk.IntVar(value=4)

    # Top bar
    top_bar = ctk.CTkFrame(root, corner_radius=8)
    top_bar.pack(fill="x", padx=18, pady=(14, 6))

    lbl_titulo = ctk.CTkLabel(top_bar, text="CODEMAX", font=("Seogue UI", 18, "bold"))
    lbl_titulo.pack(side="left", padx=10)

    bact_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
    bact_frame.pack(side="right")

    state: Dict[str, Any] = {"mtx": None}

    frame_mtx = ctk.CTkFrame(root, fg_color="transparent")
    frame_mtx.pack(fill="both", expand=True, padx=20, pady=20)

    def crear_mtx():
        mtx_old = state.get("mtx")
        if mtx_old is not None:
            try:
                mtx_old.limpiar_trazas()
            except Exception:
                pass
            try:
                mtx_old.destroy()
            except Exception:
                pass
        mtx = Matriz(frame_mtx, filas_var, cols_var)
        mtx.pack(fill="both", expand=True)
        state["mtx"] = mtx
        return mtx

    def limpiar():
        filas_var.set(3)
        cols_var.set(4)
        slider_ofer.set_valor(3)
        slider_dem.set_valor(4)
        crear_mtx()

    def aleatorio():
        filasr = random.randint(2, 10)
        colsr = random.randint(2, 10)
        mtx = crear_mtx()
        filas_var.set(filasr)
        cols_var.set(colsr)

        for s, v in ((slider_ofer, filasr), (slider_dem, colsr)):
            if hasattr(s, "set_valor"):
                try:
                    s.set_valor(v)
                except Exception:
                    pass

        root.after_idle(lambda: mtx.llenar_aleatorio(filas=filasr, cols=colsr))

    btn_aleatorio = ctk.CTkButton(bact_frame, text="Aleatorio", command=aleatorio)
    btn_limpiar = ctk.CTkButton(
        bact_frame,
        text="Limpiar",
        fg_color="#ff4d4d",
        hover_color="#ff6666",
        text_color="white",
        command=limpiar,
    )
    btn_aleatorio.pack(side="left", padx=6)
    btn_limpiar.pack(side="left", padx=6)

    # Sliders
    frame_sliders = ctk.CTkFrame(root)
    frame_sliders.pack(fill="x", padx=20, pady=(6, 8))
    frame_sliders.columnconfigure(0, weight=1)
    frame_sliders.columnconfigure(1, weight=1)

    # Frame para el deslizador de ofertas
    frame_ofer = ctk.CTkFrame(frame_sliders, fg_color="transparent")
    frame_ofer.grid(row=0, column=0, padx=(0, 6), sticky="ew")
    lbl_ofer = ctk.CTkLabel(frame_ofer, text="Filas (ofertas)")
    lbl_ofer.pack(anchor="w")
    slider_ofer = Deslizador(frame_ofer, inicial=filas_var.get())
    slider_ofer.pack(fill="x", pady=(4, 0))
    slider_ofer.set_valor(filas_var.get())
    slider_ofer.valor_deslizador.trace_add(
        "write", lambda *a: filas_var.set(slider_ofer.get_valor())
    )

    # Frame para el deslizador de demandas
    frame_dem = ctk.CTkFrame(frame_sliders, fg_color="transparent")
    frame_dem.grid(row=0, column=1, padx=(6, 0), sticky="ew")
    lbl_dem = ctk.CTkLabel(frame_dem, text="Columnas (demandas)")
    lbl_dem.pack(anchor="w")
    slider_dem = Deslizador(frame_dem, inicial=cols_var.get())
    slider_dem.pack(fill="x", pady=(4, 0))
    slider_dem.set_valor(cols_var.get())
    slider_dem.valor_deslizador.trace_add(
        "write", lambda *a: cols_var.set(slider_dem.get_valor())
    )

    crear_mtx()

    frame_botones = ctk.CTkFrame(root, fg_color="transparent")
    frame_botones.pack(fill="x", padx=12, pady=(6, 12))

    btn_calcular = ctk.CTkButton(
        frame_botones,
        text="Calcular",
        width=180,
        command=lambda: calcular(state["mtx"]),
    )
    btn_calcular.pack(pady=(6, 0))


def es_numero(text: str) -> bool:
    if text is None:
        return False
    s = str(text).strip()
    if s == "":
        return False
    try:
        n = float(s)
    except Exception:
        return False
    if math.isnan(n) or math.isinf(n):
        return False
    return True


def calcular(mtx: Matriz):
    try:
        for (i, j), e in list(mtx.celdas.items()):
            try:
                e.configure(fg_color="white")
            except Exception:
                try:
                    e.configure(bg="white")
                except Exception:
                    pass
        for j, e in list(mtx.ofertas.items()):
            try:
                e.configure(fg_color="white")
            except Exception:
                try:
                    e.configure(bg="white")
                except Exception:
                    pass
        for j, e in list(mtx.demandas.items()):
            try:
                e.configure(fg_color="white")
            except Exception:
                try:
                    e.configure(bg="white")
                except Exception:
                    pass
    except Exception:
        pass

    inv_celdas = []
    inv_of = []
    inv_dem = []

    for (i, j), e in list(mtx.celdas.items()):
        try:
            txt = e.get().strip()
        except Exception:
            txt = ""
        if not es_numero(txt):
            inv_celdas.append((i, j, txt))
            try:
                e.configure(fg_color="#ffc3c3")
            except Exception:
                try:
                    e.configure(bg="#ffc3c3")
                except Exception:
                    pass

    for j, e in list(mtx.ofertas.items()):
        try:
            txt = e.get().strip()
        except Exception:
            txt = ""
        if not es_numero(txt):
            inv_of.append((j, txt))
            try:
                e.configure(fg_color="#ffc3c3")
            except Exception:
                try:
                    e.configure(bg="#ffc3c3")
                except Exception:
                    pass

    for i, e in list(mtx.demandas.items()):
        try:
            txt = e.get().strip()
        except Exception:
            txt = ""
        if not es_numero(txt):
            inv_dem.append((i, txt))
            try:
                e.configure(fg_color="#ffc3c3")
            except Exception:
                try:
                    e.configure(bg="#ffc3c3")
                except Exception:
                    pass

    if inv_celdas or inv_of or inv_dem:
        messagebox.showerror(
            "Entradas invalidas", "Corrija las entradas resaltadas en rojo."
        )
        try:
            if inv_celdas:
                i, j, _ = inv_celdas[0]
                mtx.celdas[(i, j)].focus_set()
            elif inv_of:
                j, _ = inv_of[0]
                mtx.ofertas[j].focus_set()
            else:
                i, _ = inv_dem[0]
                mtx.demandas[i].focus_set()
        except Exception:
            pass
        return

    costos = mtx.obtener_costos()
    ofertas = mtx.obtener_ofertas()
    demandas = mtx.obtener_demandas()

    if not costos:
        messagebox.showerror("Error", "La matriz de costes esta vacia.")
        return

    try:
        fases, coste_total = codemax.resolver_transporte(costos, ofertas, demandas)
    except Exception as e:
        messagebox.showerror(
            "Error al resolver",
            f"Ocurrio un error no esperado al resolver el problema:\n{e}",
        )
        return
    try:
        mostrar_fases(mtx.master, fases, coste_total)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron mostrar las iteraciones:\n{e}")


def main():
    root = crear_ventana()
    config_ventana(root)
    root.mainloop()


if __name__ == "__main__":
    main()