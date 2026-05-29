from machine import Timer
from config import *
import globals as g
import utime
import _thread
import sys
import uselect

from interrupts import irq_next, irq_prev
from timers import timer_irq

from oled_utils import *
from modos import *
from logos import secuencia_inicio
from fourier import *

# =========================================================
# VARIABLES DUAL CORE
# =========================================================

fourier_core1_activo = False

# =========================================================
# IRQ BOTONES
# =========================================================

btn_next.irq(
    trigger=Pin.IRQ_FALLING,
    handler=irq_next
)

btn_prev.irq(
    trigger=Pin.IRQ_FALLING,
    handler=irq_prev
)

# =========================================================
# TIMER
# =========================================================

timer = Timer()

timer.init(
    period=1000,
    mode=Timer.PERIODIC,
    callback=timer_irq
)

# =========================================================
# CORE 1
# SOLO FOURIER
# =========================================================

def core1_task():

    global fourier_core1_activo

    while True:

        # Solo ejecutar Fourier si está habilitado
        if fourier_core1_activo and g.modo == 5:

            # Fourier en Core 1
            modo_fourier()

        utime.sleep_ms(10)

# =========================================================
# INICIAR CORE 1
# =========================================================

_thread.start_new_thread(core1_task, ())

# =========================================================
# CONSOLA SERIAL
# =========================================================

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

# =========================================================
# INICIO
# =========================================================

secuencia_inicio()

barra_estado()
oled.show()

# =========================================================
# LOOP PRINCIPAL
# =========================================================

while True:

    # =====================================================
    # LEER CONSOLA
    # =====================================================

    if poll.poll(0):

        comando = sys.stdin.read(1)

        # Activar Core 1 Fourier
        if comando == "1":

            fourier_core1_activo = True

            print("FOURIER CORE1 ACTIVADO")

        # Desactivar Core 1 Fourier
        elif comando == "0":

            fourier_core1_activo = False

            print("FOURIER CORE1 DESACTIVADO")

    # =====================================================
    # CAMBIO MODO
    # =====================================================

    if g.flag_cambio_modo or g.modo != g.modo_anterior:

        g.flag_cambio_modo = False
        g.modo_anterior = g.modo

        limpiar_area_modos()
        dibujar_nombre_modo()

    # =====================================================
    # RELOJ
    # =====================================================

    if g.flag_reloj:

        g.flag_reloj = False
        barra_estado()

    # =====================================================
    # MAQUINA DE ESTADOS
    # =====================================================

    if g.modo == 0:
        modo_voltimetro()

    elif g.modo == 1:
        modo_amperimetro()

    elif g.modo == 2:
        modo_ohmimetro()

    elif g.modo == 3:
        modo_dht22()

    elif g.modo == 4:
        modo_temp_vsys()

    elif g.modo == 5:

        # Si Core1 está apagado
        if not fourier_core1_activo:

            modo_fourier()

        else:

            oled.fill_rect(0, 16, 128, 48, 0)
            oled.text("FOURIER CORE1", 0, 25)

    # =====================================================
    # OLED
    # =====================================================

    oled.show()

    utime.sleep_ms(20)