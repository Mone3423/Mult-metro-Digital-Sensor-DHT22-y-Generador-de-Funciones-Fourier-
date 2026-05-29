from config import *
import globals as g

from oled_utils import (
    texto_si_cambio,
    _cache_modos
)

from adc_utils import leer_adc_promedio

# =========================================================
# VOLTÍMETRO – calibración
# =========================================================

voltaje_filtrado_v = 0.0
VALOR_REAL_V = 0.148
VALOR_PICO_V = 0.174
K_VOLT             = VALOR_REAL_V / VALOR_PICO_V

# =========================================================
# AMPERÍMETRO – calibración
# =========================================================

voltaje_filtrado_a = 0.0
R_SHUNT      = 10.0
VALOR_REAL_I = 0.0257
VALOR_PICO_I = 0.045 
K_AMP              = VALOR_REAL_I / VALOR_PICO_I

# =========================================================
# OHMÍMETRO – calibración
# =========================================================

voltaje_filtrado_r = 0.0
R7     = 1000
RAMP   = 10
R_REAL = 4590
K_OHM  = R_REAL / 5260

def modo_voltimetro():
    """
    Muestra el voltaje medido en GP26 con filtro IIR y error porcentual.
    Aplica refresco selectivo para evitar flickering en los valores.
    """
    global voltaje_filtrado_v

    texto_si_cambio("titulo", "VOLTIMETRO", 0, ZONA_MODOS_Y + 2, _cache_modos)

    lectura = leer_adc_promedio()
    if lectura < 100:
        texto_si_cambio("v1", "Voltaje = 0.000V", 0, ZONA_MODOS_Y + 18, _cache_modos)
        texto_si_cambio("v2", "", 0, ZONA_MODOS_Y + 32, _cache_modos)
    else:
        v_sin = round(lectura * factor, 3)
        voltaje_raw = lectura * factor * K_VOLT
        voltaje_filtrado_v = round(0.9 * voltaje_filtrado_v + 0.1 * voltaje_raw,3)

        error = abs((VALOR_REAL_V - voltaje_filtrado_v) / VALOR_REAL_V) * 100

        texto_si_cambio(
            "v1",
            "V:{:.3f}V".format(voltaje_filtrado_v),
            0, ZONA_MODOS_Y + 18, _cache_modos
        )
        texto_si_cambio(
            "v2",
            "E:{:.2f}%".format(error),
            0, ZONA_MODOS_Y + 32, _cache_modos
        )
        #print("V_sin={:.3f}   V_patron={:.3f}  V_cal={:.3f}  err={:.2f}%".format(v_sin,VALOR_REAL_V, voltaje_filtrado_v, error))

def modo_amperimetro():
    """
    Muestra la corriente calculada a partir de la caída en R_SHUNT.
    Filtro IIR + refresco selectivo anti-flickering.
    """
    global voltaje_filtrado_a

    texto_si_cambio("titulo", "AMPERIMETRO", 0, ZONA_MODOS_Y + 2, _cache_modos)

    lectura = leer_adc_promedio()

    if lectura < 100:
        texto_si_cambio("a1", "I = 0.00 mA", 0, ZONA_MODOS_Y + 18, _cache_modos)
    else:
        v_sin_a = round(lectura * factor, 3)
        voltaje_raw        = lectura * factor * K_AMP
        voltaje_filtrado_a = round(0.9 * voltaje_filtrado_a + 0.1 * voltaje_raw,3)
        corriente          = (voltaje_filtrado_a / R_SHUNT) * 1000
        error_a   = round(abs((VALOR_REAL_I - voltaje_filtrado_a) / VALOR_REAL_I) * 100, 2)
        texto_si_cambio(
            "a1",
            "I:{:.2f}mA".format(corriente),
            0, ZONA_MODOS_Y + 18, _cache_modos
        )
        texto_si_cambio(
            "a2",
            "E:{:.2f}%".format(error_a),
            0, ZONA_MODOS_Y + 32, _cache_modos
        )
        #print("Vsin={:.3f} Vpatron={:.3f}  Vcal={:.4f}  I={:.2f}mA  err={:.2f}%".format(v_sin_a, VALOR_REAL_I,voltaje_filtrado_a,corriente, error_a))

def modo_ohmimetro():
    """
    Mide resistencia desconocida mediante divisor de tensión + ADC.
    Filtro IIR + refresco selectivo anti-flickering.
    """
    global voltaje_filtrado_r

    texto_si_cambio("titulo", "OHMIMETRO", 0, ZONA_MODOS_Y + 2, _cache_modos)

    lectura = leer_adc_promedio()

    if lectura < 100:
        texto_si_cambio("r1", "R = 0 Ohm", 0, ZONA_MODOS_Y + 18, _cache_modos)
    else:
        v_sin = round(lectura * factor, 3)
        voltaje_r          = lectura * factor * 0.0055 / 0.048
        voltaje_filtrado_r = 0.9 * voltaje_filtrado_r + 0.1 * voltaje_r
        corriente_r        = voltaje_filtrado_r / RAMP

        if corriente_r > 0:
            r_sin = (VREF / corriente_r) - R7 - RAMP
            
            r_cal = r_sin * K_OHM
            err   = round(abs((R_REAL - r_cal) / R_REAL) * 100, 2)
            texto_si_cambio(
                "r1",
                "R:{:.2f}K".format(r_cal / 1000),
                0, ZONA_MODOS_Y + 18, _cache_modos
            )
            texto_si_cambio(
                "a2",
                "E:{:.2f}%".format(err),
                0, ZONA_MODOS_Y + 32, _cache_modos
            )
            #print("V={:.4f}   Vsh={:.4f}   Rpatron={:.2f}K  Rcal={:.2f}K  err={:.2f}%".format(v_sin,
                  #voltaje_filtrado_r, R_REAL/1000,r_cal / 1000, err))
def modo_dht22():
    """
    Lee y muestra temperatura y humedad del sensor DHT22.
    Refresco selectivo anti-flickering sobre los valores.
    """
    texto_si_cambio("titulo", "DHT22", 0, ZONA_MODOS_Y + 2, _cache_modos)

    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum  = dht_sensor.humidity()

        texto_si_cambio(
            "d1",
            "T:{:.1f}C".format(temp),
            0, ZONA_MODOS_Y + 18, _cache_modos
        )
        texto_si_cambio(
            "d2",
            "H:{:.1f}%".format(hum),
            0, ZONA_MODOS_Y + 32, _cache_modos
        )
    except:
        texto_si_cambio("d1", "Error DHT22", 0, ZONA_MODOS_Y + 18, _cache_modos)

def modo_temp_vsys():
    """
    Muestra la temperatura interna del chip RP2040/RP2350
    y el voltaje de alimentación VSYS leído por el ADC interno.

    Fórmula temperatura interna (datasheet RP2040):
        T = 27 - (V_adc - 0.706) / 0.001721

    Fórmula VSYS (divisor ×3 interno en Pico W):
        V_sys = lectura_raw * (VREF / 65535) * 3

    Refresco selectivo anti-flickering sobre cada valor.
    Entradas : ninguna (usa globales sensor_temp, vsys_adc, factor)
    Salidas  : ninguna
    """
    texto_si_cambio("titulo", "TEMP + VSYS", 0, ZONA_MODOS_Y + 2, _cache_modos)

    # --- Temperatura interna ---
    lectura_t  = sensor_temp.read_u16()
    voltaje_t  = lectura_t * factor
    temp_chip  = 27.0 - ((voltaje_t - 0.706) / 0.001721)

    texto_si_cambio(
        "tv1",
        "Tint:{:.1f}C".format(temp_chip),
        0, ZONA_MODOS_Y + 18, _cache_modos
    )

    # --- VSYS (con divisor ×3) ---
    lectura_vs = vsys_adc.read_u16()
    voltaje_vs = lectura_vs * factor * 3          # divisor ×3 circuito Pico W
    porcentaje = int(((voltaje_vs - 3.0) / (4.2 - 3.0)) * 100)
    porcentaje = max(0, min(100, porcentaje))

    texto_si_cambio(
        "tv2",
        "VSYS:{:.2f}V".format(voltaje_vs),
        0, ZONA_MODOS_Y + 32, _cache_modos
    )
