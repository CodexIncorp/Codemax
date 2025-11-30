import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk


def mostrar_fases(contenedor, fases: list, coste_total: float, eps: float = 1e-9):
    if not fases:
        messagebox.showinfo("Resultado", "Rellene todos los campos de la matriz.")
        return

    win = ctk.CTkToplevel(contenedor)
    win.title("Visualizacion de iteraciones")
    win.geometry("850x600")

    # Top: Coste total
    top = ctk.CTkFrame(win)
    top.pack(fill="x", padx=10, pady=10)

    coste_frame = ctk.CTkFrame(top, fg_color="#f4cccc", corner_radius=6)
    coste_frame.pack(side="left", padx=(0, 12))
    lbl_coste = ctk.CTkLabel(
        coste_frame,
        text=f"Coste total: {coste_total:.2f}",
        font=("Segoe UI", 14, "bold"),
        text_color="black",
    )
    lbl_coste.pack(padx=12, pady=8)

    lbl_fase = ctk.CTkLabel(top, text="", font=("Seogue UI", 11))
    lbl_fase.pack(side="left", anchor="n", pady=6)

    info_frame = ctk.CTkFrame(win)
    info_frame.pack(fill="x", pady=10, padx=8)

    def info_item(contenedor, color, text):
        box = ctk.CTkFrame(
            contenedor, width=18, height=18, fg_color=color, corner_radius=1
        )
        box.pack_propagate(False)
        box.pack(side="left", padx=(0, 6))
        lbl_text = ctk.CTkLabel(contenedor, text=text)
        lbl_text.pack(side="left", padx=(0, 12))
        return box, lbl_text

    iframe = ctk.CTkFrame(info_frame)
    iframe.pack(anchor="w")
    info_item(iframe, "#ffd966", "Celda seleccionada en la fase (antes de aplicar)")
    info_item(iframe, "#b6d7a8", "Asignacion aplicada en la fase")
    info_item(iframe, "#d9d9d9", "Fila/Columna ficticia")

    # Controles simples
    ctrl_frame = ctk.CTkFrame(top)
    ctrl_frame.pack(side="right")
    btn_ant = ctk.CTkButton(ctrl_frame, text="Anterior")
    btn_sig = ctk.CTkButton(ctrl_frame, text="Siguiente")
    btn_ant.grid(row=0, column=0, padx=4)
    btn_sig.grid(row=0, column=1, padx=4)

    # Area central con scroll para matriz
    canvas = tk.Canvas(win, bg="white", highlightthickness=0)
    canvas.pack(fill="both", expand=True, padx=8, pady=8)
    canvas_frame = ctk.CTkFrame(canvas)
    scroll_y = ctk.CTkScrollbar(win, orientation="vertical", command=canvas.yview)
    scroll_x = ctk.CTkScrollbar(win, orientation="horizontal", command=canvas.xview)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    canvas_wid = canvas.create_window((0, 0), window=canvas_frame, anchor="center")

    def configurar_canvas(event=None):
        canvas.update_idletasks()
        bbox = canvas.bbox(canvas_wid)
        if bbox is None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            return
        canvas.configure(scrollregion=canvas.bbox("all"))

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        cx = cw // 2
        cy = ch // 2
        canvas.coords(canvas_wid, cx, cy)

    canvas.bind("<Configure>", configurar_canvas)
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
        seleccionadas = fase.get("seleccionadas", [])
        aplicadas = fase.get("aplicadas", [])
        lote_min = fase.get("lote_min", None)

        # Determinar filas/columnas activas
        filas_activas = [i for i, v in enumerate(ofertas) if v > eps]
        cols_activas = [j for j, v in enumerate(demandas) if v > eps]

        if not filas_activas or not cols_activas:
            ctk.CTkLabel(
                canvas_frame,
                text="No quedan filas o columnas activas en esta iteracion.",
            ).pack(padx=8, pady=8)
            total_fases_aplicadas = sum(1 for p in fases if p.get("aplicadas"))
            if total_fases_aplicadas == 0:
                lbl_fase.configure(text=f"Iteracion {k+1} de {len(fases)}")
            else:
                aplicadas_hasta_k = sum(1 for p in fases[: k + 1] if p.get("aplicadas"))
                lbl_fase.configure(
                    text=f"Iteracion {aplicadas_hasta_k} de {total_fases_aplicadas}"
                )
            return

        # Encabezados de columnas
        ctk.CTkLabel(canvas_frame, text="").grid(row=0, column=0, padx=2, pady=2)
        for col_idx, j in enumerate(cols_activas):
            txt = f"D{j}={demandas[j]:.2f}"
            ctk.CTkLabel(canvas_frame, text=txt).grid(
                row=0, column=1 + col_idx, sticky="nsew", padx=1, pady=1
            )

        for row_idx, i in enumerate(filas_activas):
            ctk.CTkLabel(
                canvas_frame,
                text=f"O{i}={ofertas[i]:.2f}",
            ).grid(row=1 + row_idx, column=0, sticky="nsew", padx=1, pady=1)
            lbl_rows = []
            for col_idx, j in enumerate(cols_activas):
                cval = costos[i][j] if i < len(costos) and j < len(costos[i]) else 0.0
                lbl = ctk.CTkLabel(
                    canvas_frame,
                    text=f"{cval:.2f}",
                    width=80,
                    height=40,
                    fg_color="white",
                    corner_radius=4,
                )
                lbl.grid(
                    row=1 + row_idx, column=1 + col_idx, padx=1, pady=1, sticky="nsew"
                )
                lbl_rows.append(lbl)
            lbl_celdas.append(lbl_rows)

        # Pintar seleccionadas (amarillo)
        for isel, jsel, cant, cunit in seleccionadas:
            if isel in filas_activas and jsel in cols_activas:
                row_idx = filas_activas.index(isel)
                col_idx = cols_activas.index(jsel)
                lbl = lbl_celdas[row_idx][col_idx]
                lote = cant * cunit
                lbl.configure(
                    fg_color="#ffd966",
                    text=f"{cunit:.2f}\ncant = {cant:.2f}\nlote = {lote:.2f}",
                )

        # Pintar aplicadas (verde)
        for isel, jsel, cant, cunit in aplicadas:
            if isel in filas_activas and jsel in cols_activas:
                row_idx = filas_activas.index(isel)
                col_idx = cols_activas.index(jsel)
                lbl = lbl_celdas[row_idx][col_idx]
                lote = cant * cunit
                lbl.configure(
                    fg_color="#b6d7a8",
                    text=f"{cunit:.2f}\ncant = {cant:.2f}\nlote = {lote:.2f}",
                )

        # Marcar 'ficticia' en gris claro si no fue pintada
        for row_idx, i in enumerate(filas_activas):
            for col_idx, j in enumerate(cols_activas):
                cval = costos[i][j] if i < len(costos) and j < len(costos[i]) else 0.0
                lbl = lbl_celdas[row_idx][col_idx]
                if cval == 0.0 and lbl.cget("fg_color") == "white":
                    lbl.configure(fg_color="#d9d9d9", text=f"{cval:.2f}")

        aplicadas_hasta_k = sum(1 for p in fases[: k + 1] if p.get("aplicadas"))
        total_fases_aplicadas = sum(1 for p in fases if p.get("aplicadas"))

        if total_fases_aplicadas == 0:
            txt_fase = f"Iteracion {k+1} de {len(fases)}"
        else:
            if fases[k].get("aplicadas"):
                txt_fase = f"Iteracion {aplicadas_hasta_k+1} de {total_fases_aplicadas}"
            else:
                txt_fase = f"Fase de seleccion - Iteracion {aplicadas_hasta_k+1} de {total_fases_aplicadas}"

        if lote_min is not None:
            txt_fase += f"\nlote min. = {lote_min:.6g}"
        lbl_fase.configure(text=txt_fase)

    def sig():
        if idx["i"] < len(fases) - 1:
            idx["i"] += 1
            render_fase(idx["i"])

    def ant():
        if idx["i"] > 0:
            idx["i"] -= 1
            render_fase(idx["i"])

    btn_sig.configure(command=sig)
    btn_ant.configure(command=ant)
    render_fase(0)
    return win
