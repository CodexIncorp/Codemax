import tkinter as tk


class Deslizador(tk.Frame):
    """Deslizador para indicar las n-filas/columnas de la matriz"""

    def __init__(self, contenedor, maximo=10, inicial=None, **kwargs):
        super().__init__(contenedor, **kwargs)
        self.minimo = 1
        self.maximo = int(maximo)
        if self.maximo < self.minimo:
            self.maximo = self.minimo

        if inicial is None:
            inicial = self.minimo
        inicial = max(self.minimo, min(self.maximo, int(inicial)))
        self.valor_deslizador = tk.IntVar(value=int(inicial))

        # Layout: entrada a la izq. (col: 0), a la der. (col: 1) contenedor para barra + etiquetas de rango
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.texto_var = tk.StringVar(value=str(inicial))
        self.texto_var.trace_add("write", self._validar_texto)

        # Entrada
        self.entrada = tk.Entry(
            self, justify="center", textvariable=self.texto_var, width=6
        )
        self.entrada.grid(row=0, column=0, padx=(6, 8), pady=6, sticky="w")

        # Contenedor de la barra
        frame_barra = tk.Frame(self)
        frame_barra.grid(row=0, column=1, padx=(0, 6), pady=6, sticky="ew")
        frame_barra.columnconfigure(0, weight=1)

        # Slider sincronizado
        self.barra = tk.Scale(
            frame_barra,
            from_=self.minimo,
            to=self.maximo,
            resolution=1,
            orient="horizontal",
            showvalue=True,
            variable=self.valor_deslizador,
        )
        self.barra.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Etiquetas de rango
        self.lbl_min = tk.Label(frame_barra, text=str(self.minimo))
        self.lbl_min.grid(row=1, column=0, padx=(0, 2), sticky="w")
        self.lbl_max = tk.Label(frame_barra, text=str(self.maximo))
        self.lbl_max.grid(row=1, column=1, padx=(2, 0), sticky="e")

        # Bindings y sincronía
        self.entrada.bind("<Return>", lambda e: self._confirmar_entrada())
        self.entrada.bind("<FocusOut>", lambda e: self._confirmar_entrada())
        self.entrada.bind("<Up>", lambda e: self._ajustar_incremento(+1))
        self.entrada.bind("<Down>", lambda e: self._ajustar_incremento(-1))
        self.entrada.bind("<Right>", lambda e: self._ajustar_incremento(+1))
        self.entrada.bind("<Left>", lambda e: self._ajustar_incremento(-1))
        self.entrada.bind("<MouseWheel>", self._incremento_por_mouse)
        self.entrada.bind("<Button-4>", lambda e: self._ajustar_incremento(+1))
        self.entrada.bind("<Button-5>", lambda e: self._ajustar_incremento(-1))

        self.valor_deslizador.trace_add("write", lambda *a: self._actualizar_entrada())
        self._actualizar_entrada()

    def _validar_texto(self, *args):
        texto = self.texto_var.get()
        if texto == "":
            return
        try:
            v = int(texto)
        except ValueError:
            return
        v_clamp = max(self.minimo, min(self.maximo, v))
        if self.valor_deslizador.get() != v_clamp:
            self.valor_deslizador.set(v_clamp)

    def _actualizar_entrada(self):  
        texto = str(self.valor_deslizador.get())
        if self.texto_var.get() != texto:
            self.texto_var.set(texto)

    def _confirmar_entrada(self):
        texto = self.texto_var.get().strip()
        if texto == "":
            v = self.minimo
        else:
            try:
                v = int(texto)
            except ValueError:
                v = self.valor_deslizador.get()
        v = max(self.minimo, min(self.maximo, v))
        self.valor_deslizador.set(v)
        self._actualizar_entrada()

    def _ajustar_incremento(self, direccion):
        actual = int(self.valor_deslizador.get())
        nuevo = actual + direccion
        nuevo = max(self.minimo, min(self.maximo, nuevo))
        self.valor_deslizador.set(nuevo)

    def _incremento_por_mouse(self, event):
        delta = 1 if getattr(event, "delta", 0) > 0 else -1
        self._ajustar_incremento(delta)

    def _get_valor(self) -> int:
        return int(self.valor_deslizador.get())

    def _set_valor(self, v):
        v = int(v)
        v = max(self.minimo, min(self.maximo, v))
        self.valor_deslizador.set(v)
