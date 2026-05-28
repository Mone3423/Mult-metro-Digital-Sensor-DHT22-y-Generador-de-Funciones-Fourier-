from config import (
    oled,
    WIDTH,
    vsys_adc,
    factor,
    ZONA_BARRA_H,
    ZONA_MODOS_Y
)

import globals as g
import framebuf


_cache_barra = {}
_cache_modos = {}

def limpiar_area_modos():
    g.display_dirty = True
    oled.fill_rect(0, 13, WIDTH, 51, 0)

    _cache_modos.clear()

def texto_si_cambio(clave, nuevo_texto, x, y, cache):
    """
    Dibuja texto en la OLED solo si difiere del valor en caché.
    Borra el área exacta del string anterior antes de redibujar,
    eliminando el parpadeo causado por fill_rect completo.

    Entradas : clave       – identificador único de la zona
               nuevo_texto – string a mostrar
               x, y        – posición OLED
               cache       – diccionario de caché a usar
    Salidas  : True si hubo redibujado, False si no cambió
    """
    g.display_dirty = True
    if cache.get(clave) == nuevo_texto:
        return False
    # Borrar solo el área del texto anterior (8px por carácter, 8px alto)
    ancho_borrado = max(
        len(cache.get(clave, "")),
        len(nuevo_texto)
    ) * 8
    oled.fill_rect(x, y, ancho_borrado, 8, 0)
    oled.text(nuevo_texto, x, y, 1)
    cache[clave] = nuevo_texto
    return True

def barra_estado():
    """
    Refresca la barra de estado superior (filas 0 a ZONA_BARRA_H).
    Solo redibuja los campos que cambiaron desde la última vez,
    aplicando la técnica de refresco selectivo de strings para
    eliminar el parpadeo (flickering).
    Entradas : ninguna (usa globales hora, minuto, segundo, vsys_adc)
    Salidas  : ninguna
    """
    # --- Reloj ---
    reloj_str = "{:02}:{:02}:{:02}".format(
        g.hora,
        g.minuto,
        g.segundo
    )
    texto_si_cambio("reloj", reloj_str, 0, 2, _cache_barra)

    # --- Batería (VSYS) ---
    lectura_vsys  = vsys_adc.read_u16()
    voltaje_vsys  = lectura_vsys * factor * 3          # divisor ×3 interno Pico W
    porcentaje    = int(((voltaje_vsys - 3.0) / (4.2 - 3.0)) * 100)
    porcentaje    = max(0, min(100, porcentaje))
    bat_str       = "{}%".format(porcentaje)
    texto_si_cambio("bat", bat_str, 90, 2, _cache_barra)

    # --- Línea separadora (se dibuja una sola vez) ---
    if _cache_barra.get("sep") != 1:
        oled.hline(0, ZONA_BARRA_H, WIDTH, 1)
        _cache_barra["sep"] = 1

def texto_vertical(texto, x, y):
    """
    Dibuja texto rotado 90° en la OLED usando FrameBuffer.
    Entradas : texto – cadena a dibujar
               x, y  – esquina superior izquierda del bloque rotado
    Salidas  : ninguna
    """
    for i, char in enumerate(texto):
        fb_c = framebuf.FrameBuffer(bytearray(8 * 8), 8, 8, framebuf.MONO_HLSB)
        fb_c.fill(0)
        fb_c.text(char, 0, 0, 1)
        for px in range(8):
            for py in range(8):
                if fb_c.pixel(px, py):
                    oled.pixel(x + py, y + i * 8 + (7 - px), 1)
_NOMBRES_MODO = [
    "VOLTIMETRO",
    "AMPERIMETRO",
    "OHMIMETRO",
    "DHT22",
    "TEMP-VSYS",
    "FOURIER DAC"
]

def dibujar_nombre_modo():
    """
    Dibuja el nombre del modo activo en la primera línea del área de trabajo.
    Se llama solo cuando cambia el modo (flag_cambio_modo).
    """
    nombre = _NOMBRES_MODO[g.modo]
    oled.fill_rect(0, ZONA_MODOS_Y, WIDTH, 10, 0)
    oled.text(nombre, 0, ZONA_MODOS_Y + 1, 1)