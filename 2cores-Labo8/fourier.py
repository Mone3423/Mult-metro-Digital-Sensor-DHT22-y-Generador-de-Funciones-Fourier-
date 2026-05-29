from config import *
import globals as g

from oled_utils import texto_vertical
from dac_utils import dac_write

import math
import utime
import sys
import select

# =========================================================
# PARÁMETROS GENERALES
# =========================================================

_XMIN   = 0.0
_XMAX   = 4 * math.pi

_YMIN   = -2.0
_YMAX   =  4.0

_A0     = (1 + math.pi) / 2
_W0     = 0.5

_DELTA  = 0.1

_GRAF_H = HEIGHT - ZONA_MODOS_Y - 2


# =========================================================
# LECTURA SERIAL NO BLOQUEANTE
# =========================================================

def _leer_consola_fourier():
    """
    Lee comandos desde consola serial.

    1 -> orientación vertical
    0 -> orientación horizontal
    """

    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:

        cmd = sys.stdin.readline().strip()

        if cmd == "1":
            g.fourier_modo_orientacion = 1

        elif cmd == "0":
            g.fourier_modo_orientacion = 0


# =========================================================
# MODO FOURIER
# =========================================================

def modo_fourier():
    """
    Serie de Fourier visualizada en OLED
    + síntesis DAC R-2R de 8 bits.
    """

    _leer_consola_fourier()

    # -----------------------------------------------------
    # LIMPIAR ÁREA DE TRABAJO
    # -----------------------------------------------------

    oled.fill_rect(0, ZONA_MODOS_Y, WIDTH, _GRAF_H + 2, 0)

    xp_ant  = 0
    yp_ant  = 0
    primera = True

    # -----------------------------------------------------
    # RECORRIDO EN PIXELES
    # -----------------------------------------------------

    for xp_px in range(0, WIDTH, 2):

        # Mapear pixel -> dominio matemático
        x = _XMIN + (xp_px / WIDTH) * (_XMAX - _XMIN)

        suma = 0.0

        # -------------------------------------------------
        # SUMATORIA FOURIER
        # -------------------------------------------------

        for n in range(1, g.fourier_nmax + 1):

            an = (1 / (2 * math.pi)) * (
                ((math.sin(n * math.pi / 2)) / n) *
                (-2 + 4 * math.pi * math.cos(n * math.pi / 2))
                - ((8 / (n ** 2)) * math.cos(n * math.pi / 2))
                + ((4 / (n ** 2)) * (1 + ((-1) ** n)))
            )

            bn = (1 / (2 * math.pi)) * (
                ((2 * math.pi) / n) *
                (1 - math.cos(n * math.pi))
                + (2 / n) *
                (math.cos(n * math.pi) - math.cos(n * math.pi / 2))
                + ((8 / (n ** 2)) * math.sin(n * math.pi / 2)) *
                (math.cos(n * math.pi / 2) - 1)
            )

            # ---------------------------------------------
            # Ventana suavizada (reduce Gibbs)
            # ---------------------------------------------

            ventana = (1 - n / g.fourier_nmax) \
                if g.fourier_nmax > 1 else 1

            suma += (
                an * math.cos(n * _W0 * x) +
                bn * math.sin(n * _W0 * x)
            ) * ventana

        # -------------------------------------------------
        # FUNCIÓN FINAL
        # -------------------------------------------------

        fx = (_A0 / 2) + suma
        print(fx)
        # -------------------------------------------------
        # DAC R-2R
        # -------------------------------------------------

        valor_dac = int((fx + 2) * 50)

        valor_dac = max(0, min(255, valor_dac))

        dac_write(valor_dac)

        utime.sleep_us(10)

        # -------------------------------------------------
        # CONVERSIÓN A PIXELES OLED
        # -------------------------------------------------

        xp_draw = int(
            (x - _XMIN) /
            (_XMAX - _XMIN) *
            (WIDTH - 1)
        )

        yp_draw = int(
            (_YMAX - fx) /
            (_YMAX - _YMIN) *
            (_GRAF_H - 1)
        ) + ZONA_MODOS_Y

        # -------------------------------------------------
        # ROTACIÓN VERTICAL
        # -------------------------------------------------

        if g.fourier_modo_orientacion == 1:

            xp_draw, yp_draw = (
                int((yp_draw - ZONA_MODOS_Y) * 2),
                int(xp_draw / 2) + ZONA_MODOS_Y
            )

        # -------------------------------------------------
        # LIMITAR COORDENADAS
        # -------------------------------------------------

        xp_draw = max(0, min(WIDTH - 1, xp_draw))
        yp_draw = max(ZONA_MODOS_Y, min(HEIGHT - 1, yp_draw))

        # -------------------------------------------------
        # DIBUJAR LÍNEA
        # -------------------------------------------------

        if not primera:

            if (
                0 <= xp_draw < WIDTH and
                ZONA_MODOS_Y <= yp_draw < HEIGHT and
                0 <= xp_ant < WIDTH and
                ZONA_MODOS_Y <= yp_ant < HEIGHT
            ):

                oled.line(
                    xp_ant,
                    yp_ant,
                    xp_draw,
                    yp_draw,
                    1
                )

        else:
            primera = False

        xp_ant = xp_draw
        yp_ant = yp_draw

    # -----------------------------------------------------
    # ETIQUETAS
    # -----------------------------------------------------

    if g.fourier_modo_orientacion == 0:

        oled.hline(0, HEIGHT - 10, WIDTH, 1)

        etiqueta = "Funcion1"

        oled.text(etiqueta, 0, HEIGHT - 9)

    else:

        oled.vline(96, ZONA_MODOS_Y, _GRAF_H, 1)

        texto_vertical(
            "1noicnuF",
            98,
            ZONA_MODOS_Y + 4
        )

    # -----------------------------------------------------
    # ACTUALIZAR ARMÓNICOS
    # -----------------------------------------------------

    g.fourier_nmax += 1

    if g.fourier_nmax > 50:
        g.fourier_nmax = 1