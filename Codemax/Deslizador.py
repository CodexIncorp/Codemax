import tkinter as tk
import customtkinter as ctk


class Deslizador(ctk.CTkFrame):
    """Deslizador para indicar las n-filas/columnas de la matriz"""

    def __init__(self, contenedor, maximo=10, inicial=None, **kwargs):
        super().__init__(contenedor, **kwargs)
        self.minimo = 2
        self.maximo = int(maximo)
        if self.maximo < self.minimo:
            self.maximo = self.minimo

        if inicial is None:
            inicial = self.minimo
        inicial = max(self.minimo, min(self.maximo, int(inicial)))
        self.valor_deslizador = tk.IntVar(value=int(inicial))

        self.columnconfigure(0,weight=0)
        self.columnconfigure(1,weight=1)

        self.texto_var = tk.StringVar(value=str(inicial))
        self.texto_var.trace_add("write",self.validar_texto)

        self.entrada = ctk.CTkEntry(
            self, justify="center", textvariable=self.texto_var, width=60
        )
        self.entrada.grid(row=0, column=0, padx=(6, 8), pady=6, sticky="w")

        # Slider sincronizado
        self.barra = ctk.CTkSlider(
            self,
            from_=self.minimo,
            to=self.maximo,
            number_of_steps=self.maximo - self.minimo,
            variable=self.valor_deslizador,
            width=200,
        )
        self.barra.grid(row=0, column=1, padx=(0, 6), pady=6, sticky="ew")

        # Etiquetas de rango
        self.lbl_min = ctk.CTkLabel(self, text=str(self.minimo))
        self.lbl_min.grid(row=1, column=0, sticky="w")
        self.lbl_max = ctk.CTkLabel(self, text=str(self.maximo))
        self.lbl_max.grid(row=1, column=1, sticky="e")

        # Bindings y sincronía
        self.entrada.bind("<Return>", lambda e: self.confirmar_entrada())
        self.entrada.bind("<FocusOut>", lambda e: self.confirmar_entrada())
        self.entrada.bind("<Up>", lambda e: self.ajustar_incremento(+1))
        self.entrada.bind("<Down>", lambda e: self.ajustar_incremento(-1))
        self.entrada.bind("<Right>", lambda e: self.ajustar_incremento(+1))
        self.entrada.bind("<Left>", lambda e: self.ajustar_incremento(-1))
        self.entrada.bind("<MouseWheel>", self.incremento_por_mouse)
        
        self.valor_deslizador.trace_add("write", lambda *a: self.actualizar_entrada())
        self.actualizar_entrada()

    def validar_texto(self, *args):
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

    def actualizar_entrada(self):
        texto = str(self.valor_deslizador.get())
        if self.texto_var.get() != texto:
            self.texto_var.set(texto)

    def confirmar_entrada(self):
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
        self.actualizar_entrada()

    def ajustar_incremento(self, direccion):
        actual = int(self.valor_deslizador.get())
        nuevo = actual + direccion
        nuevo = max(self.minimo, min(self.maximo, nuevo))
        self.valor_deslizador.set(nuevo)

    def incremento_por_mouse(self, event):
        delta = 1 if getattr(event, "delta", 0) > 0 else -1
        self.ajustar_incremento(delta)

    def get_valor(self) -> int:
        return int(self.valor_deslizador.get())

    def set_valor(self, v):
        v = int(v)
        v = max(self.minimo, min(self.maximo, v))
        self.valor_deslizador.set(v)
