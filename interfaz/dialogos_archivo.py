from __future__ import annotations

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

FILTRO_ARCHIVOS_DEFINICION = "Archivos de texto (*.txt);;Todos los archivos (*)"
NOMBRE_ARCHIVO_SUGERIDO = "automata.txt"


def pedir_ruta_para_abrir(ventana_padre: QWidget) -> str | None:
    ruta_elegida, _filtro_elegido = QFileDialog.getOpenFileName(
        ventana_padre, "Abrir definición de AFD", "", FILTRO_ARCHIVOS_DEFINICION
    )
    return ruta_elegida or None


def pedir_ruta_para_guardar(ventana_padre: QWidget, ruta_sugerida: str | None) -> str | None:
    ruta_elegida, _filtro_elegido = QFileDialog.getSaveFileName(
        ventana_padre,
        "Guardar definición de AFD",
        ruta_sugerida or NOMBRE_ARCHIVO_SUGERIDO,
        FILTRO_ARCHIVOS_DEFINICION,
    )
    return ruta_elegida or None


def escribir_texto_en_archivo(ventana_padre: QWidget, ruta_archivo: str, texto: str) -> bool:
    try:
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(texto)
    except OSError as error:
        QMessageBox.critical(ventana_padre, "No se pudo guardar", f"Archivo: {ruta_archivo}\n\n{error}")
        return False
    return True
