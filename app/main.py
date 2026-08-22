"""
The Monkey Parking - Layout visual (Python + Tkinter)
---------------------------------------------------------------
Se conecta al Arduino por USB/Serie y dibuja en tiempo real:
  - Las plazas del estacionamiento (ocupadas/libres).
  - El contador digital de plazas disponibles.
  - El estado de la pluma (abierta/cerrada).
  - Un aviso de "LLENO" cuando corresponda.

Se usa Tkinter (incluido de fabrica con Python) en vez de una libreria
grafica externa, para que no haga falta instalar nada mas alla de
"pyserial" y para evitar problemas con antivirus / Smart App Control de
Windows bloqueando DLLs de terceros.

Ejecutar con:  python main.py
"""

import tkinter as tk

import config
from serial_reader import EstadoEstacionamiento, LectorSerial

# ---------------------- COLORES ----------------------
NEGRO = "#141418"
BLANCO = "#f0f0f0"
GRIS_CLARO = "#6e7380"
VERDE = "#2ecc71"
ROJO = "#e74c3c"
AMARILLO = "#f1c40f"
AZUL = "#3498db"


class AppEstacionamiento:
    def __init__(self, raiz, estado: EstadoEstacionamiento):
        self.raiz = raiz
        self.estado = estado

        raiz.title("The Monkey Parking")
        raiz.configure(bg=NEGRO)
        raiz.geometry(f"{config.ANCHO_VENTANA}x{config.ALTO_VENTANA}")
        raiz.bind("<Escape>", lambda _evento: raiz.destroy())

        self.canvas = tk.Canvas(
            raiz,
            width=config.ANCHO_VENTANA,
            height=config.ALTO_VENTANA,
            bg=NEGRO,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self._actualizar()

    def _texto(self, x, y, texto, tamano, color, negrita=False, ancla="center"):
        fuente = ("Consolas", tamano, "bold" if negrita else "normal")
        self.canvas.create_text(x, y, text=texto, fill=color, font=fuente, anchor=ancla)

    def _dibujar_plazas(self, ocupados, capacidad, origen_x, origen_y, ancho_total):
        capacidad = max(capacidad, 1)
        margen = 12
        alto_cajon = 120
        ancho_cajon = (ancho_total - margen * (capacidad - 1)) / capacidad

        for i in range(capacidad):
            x0 = origen_x + i * (ancho_cajon + margen)
            y0 = origen_y
            x1 = x0 + ancho_cajon
            y1 = y0 + alto_cajon

            ocupado = i < ocupados
            color = ROJO if ocupado else VERDE
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=BLANCO, width=2)

            etiqueta = "OCUPADO" if ocupado else "LIBRE"
            self._texto((x0 + x1) / 2, (y0 + y1) / 2, etiqueta, 11, NEGRO)
            self._texto((x0 + x1) / 2, y0 + 16, f"P{i + 1}", 13, BLANCO, negrita=True)

    def _dibujar_pluma(self, x, y, abierta):
        self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=GRIS_CLARO, outline="")

        largo = 90
        if abierta:
            extremo = (x, y - largo)
            color = VERDE
        else:
            extremo = (x + largo, y)
            color = ROJO

        self.canvas.create_line(x, y, extremo[0], extremo[1], fill=color, width=10, capstyle="round")

    def _actualizar(self):
        self.canvas.delete("all")

        datos = self.estado.snapshot()
        disponibles = max(datos["capacidad"] - datos["ocupados"], 0)
        ancho = config.ANCHO_VENTANA

        # --- Encabezado ---
        self._texto(ancho // 2, 40, "THE MONKEY PARKING", 24, BLANCO, negrita=True)

        # --- Contador digital ---
        color_contador = ROJO if datos["lleno"] else VERDE
        self._texto(ancho // 2, 110, f"{disponibles}", 70, color_contador, negrita=True)
        self._texto(ancho // 2, 170, f"Plazas disponibles de {datos['capacidad']}", 16, BLANCO)

        # --- Plazas ---
        self._dibujar_plazas(datos["ocupados"], datos["capacidad"], 50, 210, ancho - 100)

        # --- Pluma ---
        self._texto(150, 380, "Pluma", 14, BLANCO)
        self._dibujar_pluma(150, 420, datos["pluma_abierta"])
        estado_pluma_txt = "ABIERTA" if datos["pluma_abierta"] else "CERRADA"
        self._texto(150, 480, estado_pluma_txt, 14, VERDE if datos["pluma_abierta"] else ROJO)

        # --- Aviso de lleno ---
        if datos["lleno"]:
            self.canvas.create_rectangle(0, 500, ancho, 550, fill=ROJO, outline="")
            self._texto(ancho // 2, 525, "ESTACIONAMIENTO LLENO - ENTRADA BLOQUEADA", 18, BLANCO, negrita=True)

        # --- Estado de conexion ---
        if datos["conectado"]:
            texto_conexion = f"Conectado en {datos['puerto']}"
            color_conexion = AZUL
        else:
            texto_conexion = datos["ultimo_error"] or "Buscando Arduino..."
            color_conexion = AMARILLO
        self._texto(ancho // 2, config.ALTO_VENTANA - 20, texto_conexion, 13, color_conexion)

        self.raiz.after(100, self._actualizar)


def main():
    estado = EstadoEstacionamiento()
    lector = LectorSerial(estado)
    lector.start()

    raiz = tk.Tk()
    AppEstacionamiento(raiz, estado)

    try:
        raiz.mainloop()
    finally:
        lector.detener()


if __name__ == "__main__":
    main()
