import os
import sys

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QImage, QPainter, QPainterPath, QPen, QPolygonF

CARPETA_RECURSOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recursos")
RUTA_ICONO = os.path.join(CARPETA_RECURSOS, "icono.ico")
RUTA_ICONO_PNG = os.path.join(CARPETA_RECURSOS, "icono.png")
TAMANO_ICONO = 256

COLOR_FONDO = QColor("#1E5AA8")
COLOR_TRAZO = QColor("#FFFFFF")
COLOR_ESTADO_ACEPTACION = QColor("#FFD54F")


def dibujar_icono(tamano: int) -> QImage:
    imagen = QImage(tamano, tamano, QImage.Format_ARGB32)
    imagen.fill(Qt.transparent)
    pintor = QPainter(imagen)
    pintor.setRenderHint(QPainter.Antialiasing)
    pintor.scale(tamano / 256, tamano / 256)

    pintor.setPen(Qt.NoPen)
    pintor.setBrush(QBrush(COLOR_FONDO))
    pintor.drawRoundedRect(QRectF(8, 8, 240, 240), 48, 48)

    lapiz_trazo = QPen(COLOR_TRAZO, 12)
    lapiz_trazo.setCapStyle(Qt.RoundCap)
    radio_estado = 38
    centro_estado_inicial = QPointF(78, 150)
    centro_estado_aceptacion = QPointF(182, 150)

    trazo_transicion = QPainterPath(QPointF(100, 116))
    trazo_transicion.quadTo(QPointF(130, 60), QPointF(160, 112))
    pintor.setPen(lapiz_trazo)
    pintor.setBrush(Qt.NoBrush)
    pintor.drawPath(trazo_transicion)
    pintor.setPen(Qt.NoPen)
    pintor.setBrush(QBrush(COLOR_TRAZO))
    pintor.drawPolygon(QPolygonF([QPointF(170, 124), QPointF(146, 112), QPointF(168, 96)]))

    pintor.setPen(lapiz_trazo)
    pintor.setBrush(Qt.NoBrush)
    pintor.drawEllipse(centro_estado_inicial, radio_estado, radio_estado)
    pintor.setBrush(QBrush(COLOR_ESTADO_ACEPTACION))
    pintor.drawEllipse(centro_estado_aceptacion, radio_estado, radio_estado)
    pintor.setPen(QPen(COLOR_FONDO, 8))
    pintor.setBrush(Qt.NoBrush)
    pintor.drawEllipse(centro_estado_aceptacion, radio_estado - 14, radio_estado - 14)

    pintor.end()
    return imagen


def generar_icono() -> None:
    os.makedirs(CARPETA_RECURSOS, exist_ok=True)
    imagen_icono = dibujar_icono(TAMANO_ICONO)
    if not imagen_icono.save(RUTA_ICONO, "ICO") or not imagen_icono.save(RUTA_ICONO_PNG, "PNG"):
        sys.exit("No se pudo guardar el ícono.")
    print(f"Ícono generado en {RUTA_ICONO}")


if __name__ == "__main__":
    aplicacion = QGuiApplication(sys.argv)
    generar_icono()
