from __future__ import annotations

import os

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QPushButton, QTextBrowser, QVBoxLayout

from interfaz.contenido_ayuda import CONTENIDO_AYUDA_HTML
from interfaz.recursos import obtener_ruta_recurso

RUTA_MANUAL_USUARIO = obtener_ruta_recurso("documentacion", "Manual_de_usuario.pdf")


class DialogoAyuda(QDialog):
    def __init__(self, ventana_padre=None):
        super().__init__(ventana_padre)
        self.setWindowTitle("Ayuda")
        self.resize(760, 680)

        visor_ayuda = QTextBrowser()
        visor_ayuda.setHtml(CONTENIDO_AYUDA_HTML)

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        boton_abrir_manual = QPushButton("Abrir manual de usuario (PDF)")
        boton_abrir_manual.clicked.connect(self.abrir_manual_usuario)
        if not os.path.exists(RUTA_MANUAL_USUARIO):
            boton_abrir_manual.setEnabled(False)
            boton_abrir_manual.setToolTip("No se encontró el manual de usuario.")
        botones.addButton(boton_abrir_manual, QDialogButtonBox.ActionRole)
        botones.rejected.connect(self.reject)

        distribucion = QVBoxLayout(self)
        distribucion.addWidget(visor_ayuda)
        distribucion.addWidget(botones)

    @staticmethod
    def abrir_manual_usuario() -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(RUTA_MANUAL_USUARIO))
