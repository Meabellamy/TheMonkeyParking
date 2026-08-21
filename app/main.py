"""
The Monkey Parking - Layout visual (Python + Pygame)
---------------------------------------------------------------
Se conecta al Arduino por USB/Serie y dibuja en tiempo real:
  - Las plazas del estacionamiento (ocupadas/libres).
  - El contador digital de plazas disponibles.
  - El estado de la pluma (abierta/cerrada).
  - Un aviso de "LLENO" cuando corresponda.

Ejecutar con:  python main.py
"""

import sys

import pygame

import config
from serial_reader import EstadoEstacionamiento, LectorSerial

# ---------------------- COLORES ----------------------
NEGRO = (20, 20, 24)
BLANCO = (240, 240, 240)
GRIS = (70, 74, 84)
GRIS_CLARO = (110, 115, 128)
VERDE = (46, 204, 113)
ROJO = (231, 76, 60)
AMARILLO = (241, 196, 15)
AZUL = (52, 152, 219)


def dibujar_texto(pantalla, texto, tamano, color, centro, negrita=False):
    fuente = pygame.font.SysFont("consolas", tamano, bold=negrita)
    superficie = fuente.render(texto, True, color)
    rect = superficie.get_rect(center=centro)
    pantalla.blit(superficie, rect)
    return rect


def dibujar_plazas(pantalla, ocupados, capacidad, origen, ancho_total):
    """Dibuja los cajones de estacionamiento; los primeros 'ocupados' en rojo."""
    capacidad = max(capacidad, 1)
    margen = 12
    ancho_cajon = (ancho_total - margen * (capacidad - 1)) / capacidad
    alto_cajon = 120

    for i in range(capacidad):
        x = origen[0] + i * (ancho_cajon + margen)
        y = origen[1]
        rect = pygame.Rect(x, y, ancho_cajon, alto_cajon)

        ocupado = i < ocupados
        color = ROJO if ocupado else VERDE
        pygame.draw.rect(pantalla, color, rect, border_radius=8)
        pygame.draw.rect(pantalla, BLANCO, rect, width=2, border_radius=8)

        etiqueta = "OCUPADO" if ocupado else "LIBRE"
        dibujar_texto(pantalla, etiqueta, 14, NEGRO, rect.center)
        dibujar_texto(pantalla, f"P{i + 1}", 16, BLANCO, (rect.centerx, rect.top + 16), negrita=True)


def dibujar_pluma(pantalla, centro, abierta):
    base_x, base_y = centro
    pygame.draw.circle(pantalla, GRIS_CLARO, (base_x, base_y), 10)

    largo = 90
    if abierta:
        # Pluma vertical (levantada).
        extremo = (base_x, base_y - largo)
        color = VERDE
    else:
        # Pluma horizontal (bloqueando el paso).
        extremo = (base_x + largo, base_y)
        color = ROJO

    pygame.draw.line(pantalla, color, (base_x, base_y), extremo, 10)


def main():
    pygame.init()
    pygame.display.set_caption("The Monkey Parking")
    pantalla = pygame.display.set_mode((config.ANCHO_VENTANA, config.ALTO_VENTANA))
    reloj = pygame.time.Clock()

    estado = EstadoEstacionamiento()
    lector = LectorSerial(estado)
    lector.start()

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                ejecutando = False

        datos = estado.snapshot()
        disponibles = max(datos["capacidad"] - datos["ocupados"], 0)

        pantalla.fill(NEGRO)

        # --- Encabezado ---
        dibujar_texto(pantalla, "THE MONKEY PARKING", 30, BLANCO,
                       (config.ANCHO_VENTANA // 2, 40), negrita=True)

        # --- Contador digital ---
        color_contador = ROJO if datos["lleno"] else VERDE
        dibujar_texto(pantalla, f"{disponibles}", 90, color_contador,
                       (config.ANCHO_VENTANA // 2, 130), negrita=True)
        dibujar_texto(pantalla, f"Plazas disponibles de {datos['capacidad']}", 20, BLANCO,
                       (config.ANCHO_VENTANA // 2, 185))

        # --- Plazas ---
        dibujar_plazas(pantalla, datos["ocupados"], datos["capacidad"],
                        origen=(50, 230), ancho_total=config.ANCHO_VENTANA - 100)

        # --- Pluma ---
        dibujar_texto(pantalla, "Pluma", 18, BLANCO, (150, 400))
        dibujar_pluma(pantalla, (150, 440), datos["pluma_abierta"])
        estado_pluma_txt = "ABIERTA" if datos["pluma_abierta"] else "CERRADA"
        dibujar_texto(pantalla, estado_pluma_txt, 18,
                       VERDE if datos["pluma_abierta"] else ROJO, (150, 500))

        # --- Aviso de lleno ---
        if datos["lleno"]:
            banner = pygame.Rect(0, 520, config.ANCHO_VENTANA, 50)
            pygame.draw.rect(pantalla, ROJO, banner)
            dibujar_texto(pantalla, "ESTACIONAMIENTO LLENO - ENTRADA BLOQUEADA", 22, BLANCO,
                           banner.center, negrita=True)

        # --- Estado de conexion ---
        if datos["conectado"]:
            texto_conexion = f"Conectado en {datos['puerto']}"
            color_conexion = AZUL
        else:
            texto_conexion = datos["ultimo_error"] or "Buscando Arduino..."
            color_conexion = AMARILLO
        dibujar_texto(pantalla, texto_conexion, 16, color_conexion,
                       (config.ANCHO_VENTANA // 2, config.ALTO_VENTANA - 20))

        pygame.display.flip()
        reloj.tick(30)

    lector.detener()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
