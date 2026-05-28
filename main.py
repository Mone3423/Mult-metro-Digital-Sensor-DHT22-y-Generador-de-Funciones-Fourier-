from machine import Timer
from config import *
import globals as g
import utime

from interrupts import irq_next, irq_prev
from timers import timer_irq

from oled_utils import *
from modos import *
from logos import secuencia_inicio
from fourier import *

# IRQ botones
btn_next.irq(trigger=Pin.IRQ_FALLING, handler=irq_next)
btn_prev.irq(trigger=Pin.IRQ_FALLING, handler=irq_prev)

# Timer
timer = Timer()
timer.init(period=1000,
           mode=Timer.PERIODIC,
           callback=timer_irq)

# Inicio
secuencia_inicio()

barra_estado()
oled.show()

while True:

    if g.flag_cambio_modo or g.modo != g.modo_anterior:

        g.flag_cambio_modo = False
        g.modo_anterior = g.modo

        limpiar_area_modos()
        dibujar_nombre_modo()

    if g.flag_reloj:

        g.flag_reloj = False
        barra_estado()

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
        modo_fourier()

    oled.show()
    utime.sleep_ms(20)