import tkinter as tk
from Deslizador import Deslizador

# Configuración de la ventana
root = tk.Tk()
root.update_idletasks()
w_window = 800
h_window = 500
center_x_screen = (root.winfo_screenwidth() // 2) - (w_window // 2)
center_y_screen = (root.winfo_screenheight() // 2) - (h_window // 2)
root.geometry(f"{w_window}x{h_window}+{center_x_screen}+{center_y_screen}")
root.title("CODEMAX")
frame_principal = tk.Frame(root)
frame_principal.pack()

# Frame para el deslizador de ofertas
frame_ofer = tk.LabelFrame(frame_principal, text="Filas (ofertas)")
frame_ofer.grid(row=0, column=0, padx=20)
slider_ofer = Deslizador(frame_ofer, inicial=5)
slider_ofer.pack(fill="x")

# Frame para el deslizador de demandas
frame_dem = tk.LabelFrame(frame_principal, text="Columnas (demandas)")
frame_dem.grid(row=0, column=1, padx=20)
slider_dem = Deslizador(frame_dem, inicial=5)
slider_dem.pack(fill="x")

root.mainloop()