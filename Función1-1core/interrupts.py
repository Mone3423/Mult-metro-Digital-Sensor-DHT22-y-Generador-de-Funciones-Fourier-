import utime
import globals as g

def irq_next(pin):

    ahora = utime.ticks_ms()

    if utime.ticks_diff(ahora, g.ultimo_boton) > g.DEBOUNCE_MS:
        g.modo = (g.modo + 1) % 6
        g.flag_cambio_modo = True
        g.ultimo_boton = ahora


def irq_prev(pin):

    ahora = utime.ticks_ms()

    if utime.ticks_diff(ahora, g.ultimo_boton) > g.DEBOUNCE_MS:
        g.modo = (g.modo - 1) % 6
        g.flag_cambio_modo = True
        g.ultimo_boton = ahora