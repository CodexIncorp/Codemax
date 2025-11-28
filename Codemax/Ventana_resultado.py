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
        text=f"Coste total: {coste_total:.2f}",
        font=("Segoe UI", 14, "bold"),
        bg="#f4cccc",
        padx=12,
        pady=8,
    )
    lbl_coste.pack()

    lbl_fase = ttk.Label(top, text="", font=("Seogue UI", 11))
    lbl_fase.pack(side="left", anchor="n", pady=6)

    info_frame = ttk.Frame(win, padding=(8, 6))
    info_frame.pack(fill="x", pady=10)

    def info_item(contenedor, color, text):
        box = tk.Frame(contenedor, width=18, height=18, bg=color, bd=1, relief="solid")
        box.pack_propagate(False)
        lbl_box = box
        lbl_box.pack(side="left", padx=(0, 6))
        lbl_text = ttk.Label(contenedor, text=text)
        lbl_text.pack(side="left", padx=(0, 12))
        return box, lbl_text

    iframe = ttk.Frame(info_frame)
    iframe.pack(anchor="w")
    info_item(iframe, "#ffd966", "Celda seleccionada en la fase (antes de aplicar)")
    info_item(iframe, "#b6d7a8", "Asignacion aplicada en la fase")
    info_item(iframe, "#d9d9d9", "Fila/Columna ficticia")

    # Controles simples
    ctrl_frame = ttk.Frame(top)
    ctrl_frame.pack(side="right")
    btn_ant = ttk.Button(ctrl_frame, text="Anterior")
    btn_sig = ttk.Button(ctrl_frame, text="Siguiente")
    btn_ant.grid(row=0, column=0, padx=4)
    btn_sig.grid(row=0, column=1, padx=4)

    # Area central con scroll para matriz
    canvas = tk.Canvas(win)
    canvas.pack(fill="both", expand=True, padx=8, pady=8)
    canvas_frame = ttk.Frame(canvas)
    scroll_y = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scroll_x = ttk.Scrollbar(win, orient="horizontal", command=canvas.xview)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

    def configurar_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    canvas_frame.bind("<Configure>", configurar_canvas)

    # Estado
    idx = {"i": 0}
    lbl_celdas = []

    def render_fase(k: int):
        for ch in canvas_frame.winfo_children():
            ch.destroy()
        lbl_celdas.clear()

        fase = fases[k]
        costos = fase["costos"]
        ofertas = fase["ofertas"]
        demandas = fase["demandas"]
        seleccionadas = fase.get("selecionadas", [])
        aplicadas = fase.get("aplicadas", [])
        lote_min = fase.get("lote_min", None)

        m = len(costos)
        n = len(costos[0]) if m > 0 else 0

        # Encabezados de columnas
        ttk.Label(canvas_frame, text="").grid(row=0, column=0, padx=2, pady=2)
        for j in range(n):
            txt = f"J{j}\nD={demandas[j]:.2f}"
            ttk.Label(
                canvas_frame, text=txt, anchor="center", relief="ridge", padding=4
            ).grid(row=0, column=1 + j, sticky="nsew", padx=1, pady=1)

        for i in range(m):
            ttk.Label(
                canvas_frame,
                text=f"I{i}\nO={ofertas[i]:.2f}",
                anchor="center",
                relief="ridge",
                padding=4,
            ).grid(row=1 + i, column=0, sticky="nsew", padx=1, pady=1)
            lbl_rows = []
            for j in range(n):
                txt = f"{costos[i][j]:.2f}"
                bg = "white"
                lbl = tk.Label(
                    canvas_frame,
                    text=txt,
                    borderwidth=1,
                    relief="solid",
                    width=12,
                    height=3,
                    bg=bg,
                    justify="center",
                )
                lbl.grid(row=1 + i, column=1 + j, padx=1, pady=1, sticky="nsew")
                lbl_rows.append(lbl)
            lbl_celdas.append(lbl_rows)

        for isel, jsel, cant, cunit in seleccionadas:
            if 0 <= isel < len(lbl_celdas) and 0 <= jsel < len(lbl_celdas[isel]):
                lbl = lbl_celdas[isel][jsel]
                lote = cant * cunit
                lbl.config(bg="#ffd966")
                lbl.config(text=f"{cunit:.2f}\ncant={cant:.2f}\nlote={lote:.2f}")

        for isel, jsel, cant, cunit in aplicadas:
            if 0 <= isel < len(lbl_celdas) and 0 <= jsel < len(lbl_celdas[isel]):
                lbl = lbl_celdas[isel][jsel]
                lote = cant * cunit
                lbl.config(bg="#b6d7a8")
                lbl.config(text=f"{cunit:.2f}\ncant={cant:.2f}\nlote={lote:.2f}")

        for i in range(len(costos)):
            for j in range(len(costos[i]) if costos else 0):
                if costos[i][j] == 0.0:
                    lbl = lbl_celdas[i][j]
                    if lbl.cget("bg") == "white":
                        lbl.config(bg="#d9d9d9")
                        lbl.config(text=f"{costos[i][j]:.2f}")

        txt_fase = f"Iteracion {k+1} de {len(fases)}"
        if lote_min is not None:
            txt_fase += f"    /   lote min. = {lote_min:.6g}"
        lbl_fase.config(text=txt_fase)

    def sig():
        if idx["i"] < len(fases) - 1:
            idx["i"] += 1
            render_fase(idx["i"])

    def ant():
        if idx["i"] > 0:
            idx["i"] -= 1
            render_fase(idx["i"])

    btn_sig.config(command=sig)
    btn_ant.config(command=ant)
    render_fase(0)
    return win
