from machine import Pin, ADC, I2C
from ssd1306 import SSD1306_I2C
import dht

WIDTH = 128
HEIGHT = 64

ZONA_BARRA_H = 12
ZONA_MODOS_Y = 13

# OLED
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# ADC
adc = ADC(26)
sensor_temp = ADC(4)
vsys_adc = ADC(29)

# DHT22
dht_sensor = dht.DHT22(Pin(16))

# Botones
btn_next = Pin(19, Pin.IN, Pin.PULL_UP)
btn_prev = Pin(18, Pin.IN, Pin.PULL_UP)

VREF   = 3.26
factor = VREF / 65535