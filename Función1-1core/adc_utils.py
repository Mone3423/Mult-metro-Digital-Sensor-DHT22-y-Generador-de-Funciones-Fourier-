from config import adc

def leer_adc_promedio():

    suma = 0

    for _ in range(300):
        suma += adc.read_u16()

    return suma / 300