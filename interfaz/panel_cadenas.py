from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from afd.automata import AutomataFinitoDeterminista, ResultadoSimulacion
from interfaz import estilos

COLUMNA_CADENA = 0
COLUMNA_RECORRIDO = 1
COLUMNA_RESULTADO = 2
TITULOS_COLUMNAS = ["Cadena", "Recorrido de estados", "Resultado"]

TEXTO_PENDIENTE = "Pendiente"
TEXTO_ACEPTADA = "✔ Aceptada"
TEXTO_RECHAZADA = "✘ Rechazada"


class PanelCadenas(QWidget):
    cadena_seleccionada = Signal(int)
    agregar_cadena_solicitada = Signal(str)
    procesar_todas_solicitado = Signal()

    def __init__(self, padre=None):
        super().__init__(padre)
        self.crear_componentes()
        self.conectar_senales()

    def crear_componentes(self) -> None:
        self.tabla_cadenas = QTableWidget(0, len(TITULOS_COLUMNAS))
        self.tabla_cadenas.setHorizontalHeaderLabels(TITULOS_COLUMNAS)
        self.tabla_cadenas.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_cadenas.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_cadenas.setSelectionMode(QAbstractItemView.SingleSelection)
        encabezado = self.tabla_cadenas.horizontalHeader()
        encabezado.setSectionResizeMode(COLUMNA_CADENA, QHeaderView.ResizeToContents)
        encabezado.setSectionResizeMode(COLUMNA_RECORRIDO, QHeaderView.Stretch)
        encabezado.setSectionResizeMode(COLUMNA_RESULTADO, QHeaderView.ResizeToContents)

        self.campo_nueva_cadena = QLineEdit()
        self.campo_nueva_cadena.setPlaceholderText("Nueva cadena, ej. 1,0,1 o 101")
        self.boton_agregar_cadena = QPushButton("Agregar")
        self.boton_procesar_todas = QPushButton("Procesar todas")

        fila_botones = QHBoxLayout()
        fila_botones.addWidget(self.campo_nueva_cadena, 1)
        fila_botones.addWidget(self.boton_agregar_cadena)
        fila_botones.addWidget(self.boton_procesar_todas)

        distribucion = QVBoxLayout(self)
        distribucion.setContentsMargins(0, 0, 0, 0)
        distribucion.addWidget(self.tabla_cadenas)
        distribucion.addLayout(fila_botones)

    def conectar_senales(self) -> None:
        self.tabla_cadenas.currentCellChanged.connect(self.notificar_cambio_de_fila)
        self.boton_agregar_cadena.clicked.connect(self.solicitar_agregar_cadena)
        self.campo_nueva_cadena.returnPressed.connect(self.solicitar_agregar_cadena)
        self.boton_procesar_todas.clicked.connect(self.procesar_todas_solicitado.emit)

    def notificar_cambio_de_fila(self, fila_actual: int, _columna_actual: int, fila_anterior: int, _columna_anterior: int) -> None:
        if fila_actual >= 0 and fila_actual != fila_anterior:
            self.cadena_seleccionada.emit(fila_actual)

    def solicitar_agregar_cadena(self) -> None:
        texto_ingresado = self.campo_nueva_cadena.text().strip()
        if texto_ingresado:
            self.agregar_cadena_solicitada.emit(texto_ingresado)
            self.campo_nueva_cadena.clear()

    def mostrar_cadenas(self, cadenas_a_analizar: list[list[str]]) -> None:
        self.tabla_cadenas.blockSignals(True)
        self.tabla_cadenas.setRowCount(0)
        for simbolos_cadena in cadenas_a_analizar:
            self.agregar_fila_cadena(simbolos_cadena)
        self.tabla_cadenas.blockSignals(False)

    def agregar_fila_cadena(self, simbolos_cadena: list[str]) -> int:
        numero_fila = self.tabla_cadenas.rowCount()
        self.tabla_cadenas.insertRow(numero_fila)
        texto_cadena = AutomataFinitoDeterminista.formatear_simbolos_cadena(simbolos_cadena)
        self.tabla_cadenas.setItem(numero_fila, COLUMNA_CADENA, QTableWidgetItem(texto_cadena))
        self.tabla_cadenas.setItem(numero_fila, COLUMNA_RECORRIDO, QTableWidgetItem(""))
        self.tabla_cadenas.setItem(numero_fila, COLUMNA_RESULTADO, self.crear_celda_resultado(None))
        return numero_fila

    def marcar_fila_seleccionada(self, numero_fila: int) -> None:
        self.tabla_cadenas.blockSignals(True)
        self.tabla_cadenas.selectRow(numero_fila)
        self.tabla_cadenas.blockSignals(False)

    def mostrar_resultado(self, numero_fila: int, resultado: ResultadoSimulacion) -> None:
        texto_recorrido = " → ".join(resultado.obtener_estados_recorridos())
        if resultado.mensaje_error:
            texto_recorrido += f"  ({resultado.mensaje_error})"
        self.tabla_cadenas.item(numero_fila, COLUMNA_RECORRIDO).setText(texto_recorrido)
        self.tabla_cadenas.setItem(numero_fila, COLUMNA_RESULTADO, self.crear_celda_resultado(resultado.fue_aceptada))

    @staticmethod
    def crear_celda_resultado(fue_aceptada: bool | None) -> QTableWidgetItem:
        if fue_aceptada is None:
            texto, color_fondo, color_texto = TEXTO_PENDIENTE, estilos.COLOR_FONDO_PENDIENTE, estilos.COLOR_TEXTO_NORMAL
        elif fue_aceptada:
            texto, color_fondo, color_texto = TEXTO_ACEPTADA, estilos.COLOR_FONDO_ACEPTADA, estilos.COLOR_TEXTO_ACEPTADA
        else:
            texto, color_fondo, color_texto = TEXTO_RECHAZADA, estilos.COLOR_FONDO_RECHAZADA, estilos.COLOR_TEXTO_RECHAZADA
        celda_resultado = QTableWidgetItem(texto)
        celda_resultado.setTextAlignment(Qt.AlignCenter)
        celda_resultado.setBackground(QBrush(QColor(color_fondo)))
        celda_resultado.setForeground(QBrush(QColor(color_texto)))
        fuente_celda = celda_resultado.font()
        fuente_celda.setBold(fue_aceptada is not None)
        celda_resultado.setFont(fuente_celda)
        return celda_resultado
