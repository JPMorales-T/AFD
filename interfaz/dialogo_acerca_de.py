from __future__ import annotations

import html

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from interfaz import datos_proyecto

TITULOS_COLUMNAS_INTEGRANTES = ["No.", "Nombre", "Carné"]


class DialogoAcercaDe(QDialog):
    def __init__(self, ventana_padre=None):
        super().__init__(ventana_padre)
        self.setWindowTitle("Acerca de")
        self.resize(560, 520)

        encabezado = QLabel(self.construir_html_encabezado())
        encabezado.setTextFormat(Qt.RichText)
        encabezado.setAlignment(Qt.AlignCenter)
        encabezado.setWordWrap(True)

        distribucion = QVBoxLayout(self)
        distribucion.addWidget(encabezado)
        distribucion.addWidget(QLabel("<b>Integrantes del grupo</b>"))
        distribucion.addWidget(self.crear_tabla_integrantes())

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)
        distribucion.addWidget(botones)

    @staticmethod
    def construir_html_encabezado() -> str:
        datos_institucionales = [
            ("Universidad", datos_proyecto.NOMBRE_UNIVERSIDAD),
            ("Facultad", datos_proyecto.NOMBRE_FACULTAD),
            ("Carrera", datos_proyecto.NOMBRE_CARRERA),
            ("Curso", datos_proyecto.NOMBRE_CURSO),
            ("Sección", datos_proyecto.SECCION_CURSO),
            ("Catedrático", datos_proyecto.NOMBRE_CATEDRATICO),
            ("Fecha", datos_proyecto.FECHA_ENTREGA),
        ]
        filas_html = "".join(
            f"<tr><td align='right'><b>{html.escape(titulo)}:</b></td><td>{html.escape(valor)}</td></tr>"
            for titulo, valor in datos_institucionales
            if valor.strip()
        )
        return (
            f"<h2>{html.escape(datos_proyecto.NOMBRE_APLICACION)}</h2>"
            f"<p>Versión {html.escape(datos_proyecto.VERSION_APLICACION)}</p>"
            f"<table align='center' cellspacing='4'>{filas_html}</table>"
        )

    @staticmethod
    def crear_tabla_integrantes() -> QTableWidget:
        integrantes = datos_proyecto.INTEGRANTES_GRUPO
        tabla_integrantes = QTableWidget(len(integrantes), len(TITULOS_COLUMNAS_INTEGRANTES))
        tabla_integrantes.setHorizontalHeaderLabels(TITULOS_COLUMNAS_INTEGRANTES)
        tabla_integrantes.verticalHeader().setVisible(False)
        tabla_integrantes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabla_integrantes.setSelectionMode(QAbstractItemView.NoSelection)
        encabezado = tabla_integrantes.horizontalHeader()
        encabezado.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        encabezado.setSectionResizeMode(1, QHeaderView.Stretch)
        encabezado.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        for numero_fila, (nombre_integrante, carne_integrante) in enumerate(integrantes):
            celda_numero = QTableWidgetItem(str(numero_fila + 1))
            celda_numero.setTextAlignment(Qt.AlignCenter)
            tabla_integrantes.setItem(numero_fila, 0, celda_numero)
            tabla_integrantes.setItem(numero_fila, 1, QTableWidgetItem(nombre_integrante))
            tabla_integrantes.setItem(numero_fila, 2, QTableWidgetItem(carne_integrante))
        return tabla_integrantes
