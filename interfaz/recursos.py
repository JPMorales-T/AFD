import os
import sys


def obtener_carpeta_base_aplicacion() -> str:
    carpeta_empaquetada = getattr(sys, "_MEIPASS", None)
    if carpeta_empaquetada:
        return carpeta_empaquetada
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def obtener_ruta_recurso(*partes_ruta: str) -> str:
    return os.path.join(obtener_carpeta_base_aplicacion(), *partes_ruta)
