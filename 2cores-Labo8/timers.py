import globals as g

def timer_irq(timer):

    g.segundo += 1

    if g.segundo >= 60:
        g.segundo = 0
        g.minuto += 1

    if g.minuto >= 60:
        g.minuto = 0
        g.hora += 1

    if g.hora >= 24:
        g.hora = 0

    g.flag_reloj = True