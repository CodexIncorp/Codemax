import tkinter as tk
from Deslizador import Deslizador
from Matriz import Matriz


def _crear_ventana():
    root = tk.Tk()
    root.update_idletasks()
    w_window = 800
    h_window = 500
    center_x_screen = (root.winfo_screenwidth() // 2) - (w_window // 2)
    center_y_screen = (root.winfo_screenheight() // 2) - (h_window // 2)
    root.geometry(f"{w_window}x{h_window}+{center_x_screen}+{center_y_screen}")
    root.title("CODEMAX")
    return root


def _config_ventana(root):
    filas_var = tk.IntVar(value=3)
    cols_var = tk.IntVar(value=4)

    frame_sliders = tk.Frame(root)
    frame_sliders.pack(fill="x", padx=20, pady=20)
    frame_sliders.columnconfigure(0, weight=1)
    frame_sliders.columnconfigure(1, weight=1)

    # Frame para el deslizador de ofertas
    frame_ofer = tk.LabelFrame(frame_sliders, text="Filas (ofertas)")
    frame_ofer.grid(row=0, column=0, padx=(0, 6), sticky="ew")
    slider_ofer = Deslizador(frame_ofer, inicial=filas_var.get())
    slider_ofer.pack(fill="x")

    slider_ofer._set_valor(filas_var.get())
    slider_ofer.valor_deslizador.trace_add(
        "write", lambda *a: filas_var.set(slider_ofer._get_valor())
    )

    # Frame para el deslizador de demandas
    frame_dem = tk.LabelFrame(frame_sliders, text="Columnas (demandas)")
    frame_dem.grid(row=0, column=1, padx=(6, 0), sticky="ew")
    slider_dem = Deslizador(frame_dem, inicial=cols_var.get())
    slider_dem.pack(fill="x")

    slider_dem._set_valor(cols_var.get())
    slider_dem.valor_deslizador.trace_add(
        "write", lambda *a: cols_var.set(slider_dem._get_valor())
    )

    matriz = Matriz(root, filas_var, cols_var)
    matriz.pack(fill="both", expand=True, padx=20, pady=20)

    frame_botones = tk.Frame(root)
    frame_botones.pack(fill="x", padx=12, pady=12)
    frame_botones.columnconfigure(0, weight=1)
    frame_botones.columnconfigure(1, weight=0)
    frame_botones.columnconfigure(2, weight=1)

    btn_calcular = tk.Button(
        frame_botones,
        text="Calcular",
        width=16,
        bg="#2b7be9",
        fg="white",
        activebackground="#1a5fd6",
    )
    btn_calcular.grid(row=0, column=0, columnspan=3, pady=(0, 8))

    frame_botones.rowconfigure(1, weight=0)
    frame_botones.columnconfigure(0, weight=1)
    frame_botones.columnconfigure(1, weight=1)
    frame_botones.columnconfigure(2, weight=0)

    btn_salir = tk.Button(
        frame_botones,
        text="Salir",
        command=root.destroy,
        width=12,
        bg="#c13b3b",
        fg="white",
        activebackground="#a02f2f",
    )
    btn_salir.grid(row=1, column=2, sticky="e")


def main():
    root = _crear_ventana()
    _config_ventana(root)
    root.mainloop()


if __name__ == "__main__":
    main()