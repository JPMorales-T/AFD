import sys

from PySide6.QtCore import QLibraryInfo, QLocale, Qt, QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from interfaz.recursos import obtener_ruta_recurso
from interfaz.ventana_principal import TITULO_APLICACION, VentanaPrincipal


def cargar_traduccion_espanol(aplicacion: QApplication) -> QTranslator:
    traductor_qt = QTranslator(aplicacion)
    carpeta_traducciones = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
    if traductor_qt.load(QLocale(QLocale.Spanish), "qtbase", "_", carpeta_traducciones):
        aplicacion.installTranslator(traductor_qt)
    return traductor_qt


def iniciar_aplicacion() -> None:
    aplicacion = QApplication(sys.argv)
    cargar_traduccion_espanol(aplicacion)
    aplicacion.setApplicationName(TITULO_APLICACION)
    aplicacion.setWindowIcon(QIcon(obtener_ruta_recurso("recursos", "icono.png")))
    aplicacion.setStyle("Fusion")
    aplicacion.styleHints().setColorScheme(Qt.ColorScheme.Light)

    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    sys.exit(aplicacion.exec())


if __name__ == "__main__":
    iniciar_aplicacion()
