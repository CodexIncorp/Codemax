import tkinter as tk
import random
from typing import Optional, List


class Matriz(tk.Frame):
    """Matriz de costos unitarios"""

    def __init__(
        self,
        contenedor,
        filas: tk.IntVar,
        columnas: tk.IntVar,
        ancho_celdas=8,
        **kwargs,
    ):
        super().__init__(contenedor, **kwargs)
        self.filas = filas
        self.columnas = columnas
        self.ancho_celdas = ancho_celdas
        self.celdas = {}
        self.ofertas = {}
        self.demandas = {}
        # OP.
        self.lbl_fc = {}

        self.filas.trace_add("write", lambda *a: self._reconstruir())
        self.columnas.trace_add("write", lambda *a: self._reconstruir())
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(fill="both", expand=True)

        self._reconstruir()

    def _reconstruir(self):
        fils = max(1, int(self.filas.get()))
        cols = max(1, int(self.columnas.get()))

        valores_prev = {}
        for (i, j), entry in self.celdas.items():
            valores_prev[(i, j)] = entry.get()
        ofertas_prev = {j: e.get() for j, e in self.ofertas.items()}
        demandas_prev = {i: e.get() for i, e in self.demandas.items()}

        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.celdas.clear()
        self.ofertas.clear()
        self.demandas.clear()
        self.lbl_fc.clear()

        # OP.
        encabezado = tk.Label(self.grid_frame, text="")
        encabezado.grid(row=0, column=0, padx=2, pady=2)

        for j in range(cols):
            lbl_c = tk.Label(self.grid_frame, text=f"D{j+1}")
            lbl_c.grid(row=0, column=1 + j, padx=2, pady=2)
            self.lbl_fc[("col", j)] = lbl_c

        lbl_of = tk.Label(self.grid_frame, text="Oferta")
        lbl_of.grid(row=0, column=1 + cols, padx=6, pady=2)

        for i in range(fils):
            lbl_f = tk.Label(self.grid_frame, text=f"O{i+1}")
            lbl_f.grid(row=1 + i, column=0, padx=2, pady=2)
            self.lbl_fc[("row", i)] = lbl_f

            for j in range(cols):
                e = tk.Entry(self.grid_frame, width=self.ancho_celdas, justify="center")
                # restaurar valor si existía
                if (i, j) in valores_prev:
                    e.insert(0, valores_prev[(i, j)])
                else:
                    e.insert(0, "")  # vacío por defecto
                e.grid(row=1 + i, column=1 + j, padx=2, pady=2, sticky="ew")
                self.celdas[(i, j)] = e

            ed = tk.Entry(self.grid_frame, width=self.ancho_celdas, justify="center")
            if i in demandas_prev:
                ed.insert(0, demandas_prev[i])
            else:
                ed.insert(0, "")
            ed.grid(row=1 + i, column=1 + cols, padx=(8, 2), pady=2)
            self.demandas[i] = ed

        lbl_dem = tk.Label(self.grid_frame, text="Demanda")
        lbl_dem.grid(row=1 + fils, column=0, padx=2, pady=2)

        for j in range(cols):
            eo = tk.Entry(self.grid_frame, width=self.ancho_celdas, justify="center")
            if j in ofertas_prev:
                eo.insert(0, ofertas_prev[j])
            else:
                eo.insert(0, "")
            eo.grid(row=1 + fils, column=1 + j, padx=2, pady=(2, 8))
            self.ofertas[j] = eo

        suma_lbl = tk.Label(self.grid_frame, text="")
        suma_lbl.grid(row=1 + fils, column=1 + cols, padx=2, pady=2)

        for c in range(1 + cols + 1):
            self.grid_frame.columnconfigure(c, weight=1 if (1 <= c <= cols) else 0)

    def obtener_costos(self):
        fils = int(self.filas.get())
        cols = int(self.columnas.get())
        costos = [[0.0 for _ in range(cols)] for _ in range(fils)]
        for i in range(fils):
            for j in range(cols):
                texto = self.celdas[(i, j)].get().strip()
                try:
                    costos[i][j] = float(texto) if texto != "" else 0.0
                except ValueError:
                    costos[i][j] = 0.0
        return costos

    def obtener_demandas(self):
        cols = int(self.columnas.get())
        ofertas = [0.0] * cols
        for j in range(cols):
            texto = self.ofertas[j].get().strip()
            try:
                ofertas[j] = float(texto) if texto != "" else 0.0
            except ValueError:
                ofertas[j] = 0.0
        return ofertas

    def obtener_ofertas(self):
        fils = int(self.filas.get())
        demandas = [0.0] * fils
        for i in range(fils):
            texto = self.demandas[i].get().strip()
            try:
                demandas[i] = float(texto) if texto != "" else 0.0
            except ValueError:
                demandas[i] = 0.0
        return demandas

    def fijar_costos(self, matriz):
        fils = len(matriz)
        cols = len(matriz[0]) if fils else 0
        # actualizar vars si cambia tamaño
        if self.filas.get() != fils:
            self.filas.set(fils)
        if self.columnas.get() != cols:
            self.columnas.set(cols)
        # tras reconstrucción, rellenar
        for i in range(fils):
            for j in range(cols):
                self.celdas[(i, j)].delete(0, "end")
                self.celdas[(i, j)].insert(0, str(matriz[i][j]))

    def fijar_ofertas(self, ofertas):
        if self.columnas.get() != len(ofertas):
            self.columnas.set(len(ofertas))
        for j, val in enumerate(ofertas):
            self.ofertas[j].delete(0, "end")
            self.ofertas[j].insert(0, str(val))

    def fijar_demandas(self, demandas):
        if self.filas.get() != len(demandas):
            self.filas.set(len(demandas))
        for i, val in enumerate(demandas):
            self.demandas[i].delete(0, "end")
            self.demandas[i].insert(0, str(val))

    def part_random(self, total: int, parts: int) -> List[int]:
        if parts <= 0:
            return []
        if parts == 1:
            return [total]

        cortes = sorted(random.sample(range(1, total), parts - 1))
        valores = []
        prev = 0
        for c in cortes:
            valores.append(c - prev)
            prev = c
        valores.append(total - prev)
        return valores

    def llenar_aleatorio(
        self,
        filas: Optional[int] = None,
        cols: Optional[int] = None,
        coste_min: int = 1,
        coste_max: int = 99,
        demanda_min: int = 1,
        demanda_max: int = 20,
    ):
        if filas is not None:
            self.filas.set(max(1, int(filas)))
        if cols is not None:
            self.columnas.set(max(1, int(cols)))
        self.update_idletasks()

        m = max(1, int(self.filas.get()))
        n = max(1, int(self.columnas.get()))

        mtx_costos=[[random.randint(coste_min,coste_max)for _ in range(n)]for _ in range(m)]
        demandas=[random.randint(demanda_min,demanda_max)for _ in range(m)]
        sum_dem=sum(demandas)
        if sum_dem<=0:
            demandas=[1]*m
            sum_dem=m

        ofertas=self.part_random(sum_dem,n)
        self.update_idletasks()
        for i in range(m):
            for j in range(n):
                if(i,j)in self.celdas:
                    e=self.celdas[(i,j)]
                    e.delete(0,"end")
                    e.insert(0,str(mtx_costos[i][j]))
                else:
                    pass

        for i,val in enumerate(demandas):
            if i in self.demandas:
                ed=self.demandas[i]
                ed.delete(0,"end")
                ed.insert(0,str(val))

        for j,val in enumerate(ofertas):
            if j in self.ofertas:
                eo=self.ofertas[j]
                eo.delete(0,"end")
                eo.insert(0,str(val))

        self.update_idletasks()
