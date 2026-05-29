from machine import Pin

_DAC_PINES = [2,3,4,5,6,7,8,9]

dac_pins = [Pin(p, Pin.OUT) for p in _DAC_PINES]
def dac_write(valor):

    mascara = 1

    for gpio in dac_pins:
        gpio.value(1 if (valor & mascara) else 0)
        mascara <<= 1