from config import *
import framebuf
import time
def abrir_icono(ruta):
    """
    Carga un archivo PBM binario (P4) y devuelve un FrameBuffer.
    Entradas : ruta – path del archivo .pbm
    Salidas  : (FrameBuffer, ancho, alto) o (None, 0, 0) si falla
    """
    try:
        with open(ruta, "rb") as f:
            if f.readline().strip() != b'P4':
                raise ValueError("No es PBM P4")
            linea = f.readline()
            while linea.startswith(b'#'):
                linea = f.readline()
            w, h  = [int(v) for v in linea.split()]
            datos = bytearray(f.read())
        return framebuf.FrameBuffer(datos, w, h, framebuf.MONO_HLSB), w, h
    except:
        return None, 0, 0

def mostrar_logo(fb, w, h, texto):
    """
    Muestra una imagen PBM centrada con texto inferior en la OLED.
    """
    oled.fill(0)
    oled.blit(fb, (WIDTH - w) // 2, 0)
    oled.hline(0, 50, WIDTH, 1)
    oled.text(texto, (WIDTH - len(texto) * 8) // 2, 54)
    oled.show()

def efecto_cambio():
    """
    Efecto de barrido vertical al limpiar pantalla entre logos.
    """
    for i in range(0, HEIGHT, 4):
        oled.fill_rect(0, i, WIDTH, 4, 0)
        oled.show()
        time.sleep(0.02)

# =========================================================
# SECUENCIA DE ARRANQUE – Logos
# =========================================================

def secuencia_inicio():
    """
    Muestra los logos de los integrantes al iniciar el sistema.
    Los archivos logf.pbm y leon.pbm deben estar en la raíz del FS.
    """
    fb1, w1, h1 = abrir_icono("logf.pbm")
    fb2, w2, h2 = abrir_icono("leon.pbm")

    if fb1:
        mostrar_logo(fb1, w1, h1, "Monse C.Alcon H.")
        time.sleep(2)
        efecto_cambio()

    if fb2:
        mostrar_logo(fb2, w2, h2, "Jose L. Poma T.")
        time.sleep(2)
        efecto_cambio()

    print("Sistema listo | btn_next=GP14 | btn_prev=GP15")
    print("Fourier serial: '1'=vertical  '0'=horizontal")