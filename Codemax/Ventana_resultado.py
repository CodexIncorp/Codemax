import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import List

ctk.set_appearance_mode("system")


def mostrar_fases(contenedor, fases: list, coste_total: float, eps: float = 1e-9):
    if not fases:
        messagebox.showinfo("Resultado", "Rellene todos los campos de la matriz.")
        return

    win = ctk.CTkToplevel(contenedor)
    win.title("Visualizacion de iteraciones")
    win.geometry("950x640")

    # Top: Coste total
    top = ctk.CTkFrame(win)
    top.pack(fill="x", padx=10, pady=8)

    coste_frame = ctk.CTkFrame(top, fg_color="#f4cccc", corner_radius=6)
    coste_frame.pack(side="left", padx=(0, 12))
    lbl_coste = ctk.CTkLabel(
        coste_frame,
        text=f"Coste total: {coste_total:.2f}",
        font=("Segoe UI", 16, "bold"),
        text_color="black",
        corner_radius=6,
    )
    lbl_coste.pack(padx=12, pady=8)

    lbl_fase = ctk.CTkLabel(top, text="", font=("Seogue UI", 11))
    lbl_fase.pack(side="left", anchor="n", pady=6)

    info_frame = ctk.CTkFrame(win)
    info_frame.pack(fill="x", pady=(6, 10), padx=8)

    def info_item(contenedor, color, text):
        box = ctk.CTkFrame(
            contenedor, width=18, height=18, fg_color=color, corner_radius=3
        )
        box.pack_propagate(False)
        box.pack(side="left", padx=(0, 6))
        lbl_text = ctk.CTkLabel(contenedor, text=text)
        lbl_text.pack(side="left", padx=(0, 12))
        return box, lbl_text

    iframe = ctk.CTkFrame(info_frame, fg_color="transparent")
    iframe.pack(anchor="w")
    info_item(iframe, "#ffd966", "Celda seleccionada en la fase (antes de aplicar)")
    info_item(iframe, "#b6d7a8", "Asignacion aplicada en la fase")
    info_item(iframe, "#d9d9d9", "Fila/Columna ficticia")

    # Controles simples
    ctrl_frame = ctk.CTkFrame(top)
    ctrl_frame.pack(side="right")
    btn_ant = ctk.CTkButton(ctrl_frame, text="Anterior")
    btn_sig = ctk.CTkButton(ctrl_frame, text="Siguiente")
    btn_ant.grid(row=0, column=0, padx=6)
    btn_sig.grid(row=0, column=1, padx=6)

    scroll_area = ctk.CTkScrollableFrame(win, orientation="vertical", corner_radius=0)
    scroll_area.pack(fill="both", expand=True, padx=8, pady=8)

    center_frame = ctk.CTkFrame(scroll_area, fg_color="transparent")
    center_frame.pack(fill="both", expand=True)

    def crear_grid_center(contenedor):
        gc = ctk.CTkFrame(contenedor, fg_color="transparent")
        gc.place(relx=0.5, rely=0.5, anchor="center")
        return gc

    # Estado
    idx = {"i": 0}
    lbl_celdas: List[List[ctk.CTkLabel]] = []

    def render_fase_sync(k: int):
        for ch in center_frame.winfo_children():
            try:
                ch.destroy()
            except Exception:
                pass
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
                center_frame,
                text="No quedan filas o columnas activas en esta iteracion.",
            ).pack(padx=8, pady=8)
            return

        grid_center = crear_grid_center(center_frame)
        for c in range(0, 1 + len(cols_activas)):
            grid_center.grid_columnconfigure(c, weight=1)
        for r in range(0, 1 + len(filas_activas)):
            grid_center.grid_rowconfigure(r, weight=1)

        center_frame.update_idletasks()
        dw = center_frame.winfo_width() or center_frame.winfo_reqwidth()
        dh = center_frame.winfo_height() or center_frame.winfo_reqheight()
        rw = 90
        rh = 80
        ncols = max(1, len(cols_activas))
        nrows = max(1, len(filas_activas))
        maxw_celda = max(40, (dw - rw) // ncols - 4)
        maxh_celda = max(24, (dh - rh) // nrows)
        maxh_celda = min(maxh_celda, 90)

        for r in range(0, 1 + nrows):
            grid_center.grid_rowconfigure(r, minsize=maxh_celda)

        # Encabezados de columnas
        ctk.CTkLabel(
            grid_center,
            text="",
            width=maxw_celda,
        ).grid(row=0, column=0, padx=2, pady=2, ipady=2)
        for col_idx, j in enumerate(cols_activas):
            txt = f"D{j} = {demandas[j]:.2f}"
            ctk.CTkLabel(
                grid_center,
                text=txt,
                anchor="center",
                width=maxw_celda,
                fg_color="#8896ff",
                corner_radius=6,
            ).grid(row=0, column=1 + col_idx, sticky="nsew", padx=1, pady=1, ipady=2)

        # Filas y celdas
        for row_idx, i in enumerate(filas_activas):
            ctk.CTkLabel(
                grid_center,
                text=f"O{i} = {ofertas[i]:.2f}",
                fg_color="#8896ff",
                corner_radius=6,
            ).grid(row=1 + row_idx, column=0, sticky="nsew", padx=1, pady=1, ipady=2)
            lbl_rows: List[ctk.CTkLabel] = []
            for col_idx, j in enumerate(cols_activas):
                cval = costos[i][j] if i < len(costos) and j < len(costos[i]) else 0.0
                lbl = ctk.CTkLabel(
                    grid_center,
                    text=f"{cval:.2f}",
                    fg_color="white",
                    corner_radius=6,
                    width=maxw_celda,
                )
                lbl.grid(
                    row=1 + row_idx,
                    column=1 + col_idx,
                    padx=1,
                    pady=1,
                    ipady=2,
                    sticky="nsew",
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
                try:
                    color_actual = lbl.cget("fg_color")
                except Exception:
                    color_actual = None
                if cval == 0.0 and (
                    color_actual is None or color_actual in ("white", "#ffffff")
                ):
                    lbl.configure(fg_color="#d9d9d9", text=f"{cval:.2f}")

        grid_center.update_idletasks()
        gw = grid_center.winfo_reqwidth()
        gh = grid_center.winfo_reqheight()

        center_frame.update_idletasks()
        cfw = center_frame.winfo_width() or center_frame.winfo_reqwidth()
        cfh = center_frame.winfo_height() or center_frame.winfo_reqheight()

        w = min(gw + 20, max(100, cfw - 20))
        h = min(gh + 20, max(100, cfh - 20))

        try:
            grid_center.place(relx=0.5, rely=0.5, anchor="center", width=w, height=h)
        except Exception:
            try:
                grid_center.pack(expand=True)
            except Exception:
                pass

        try:
            scroll_area.update_idletasks()
        except Exception:
            pass

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
            txt_fase += f"\nLote minimo = {lote_min:.6g}"
        lbl_fase.configure(text=txt_fase)

    def render_fase(k: int):
        try:
            win.after_idle(lambda: render_fase_sync(k))
        except Exception:
            render_fase_sync(k)

    def sig():
        if idx["i"] < len(fases) - 1:
            idx["i"] += 1
            render_fase_sync(idx["i"])

    def ant():
        if idx["i"] > 0:
            idx["i"] -= 1
            render_fase_sync(idx["i"])

    btn_sig.configure(command=sig)
    btn_ant.configure(command=ant)

    def cerrar():
        try:
            win.destroy()
        except Exception:
            pass

    win.protocol("WM_DELETE_WINDOW", cerrar)
    render_fase(0)
    return win
