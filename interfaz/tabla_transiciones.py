from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from afd.automata import AutomataFinitoDeterminista, PasoSimulacion
from interfaz import estilos

MARCA_ESTADO_INICIAL = "→"
MARCA_ESTADO_ACEPTACION = "*"


class TablaTransiciones(QTableWidget):
    def __init__(self, padre=None):
        super().__init__(padre)
        self.automata: AutomataFinitoDeterminista | None = None
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setToolTip(
            f"{MARCA_ESTADO_INICIAL} estado inicial     {MARCA_ESTADO_ACEPTACION} estado de aceptación"
        )

    def mostrar_automata(self, automata: AutomataFinitoDeterminista) -> None:
        self.automata = automata
        self.clear()
        self.setRowCount(len(automata.estados))
        self.setColumnCount(len(automata.simbolos))
        self.setHorizontalHeaderLabels(automata.simbolos)
        self.setVerticalHeaderLabels([self.crear_etiqueta_estado(estado) for estado in automata.estados])

        for numero_fila, estado_origen in enumerate(automata.estados):
            for numero_columna, simbolo in enumerate(automata.simbolos):
                celda_destino = QTableWidgetItem(automata.obtener_estado_destino(estado_origen, simbolo))
                celda_destino.setTextAlignment(Qt.AlignCenter)
                celda_destino.setForeground(QBrush(QColor(estilos.COLOR_TEXTO_NORMAL)))
                self.setItem(numero_fila, numero_columna, celda_destino)

        self.limpiar_resaltado()

    def crear_etiqueta_estado(self, estado: str) -> str:
        marcas = ""
        if estado == self.automata.estado_inicial:
            marcas += MARCA_ESTADO_INICIAL
        if self.automata.es_estado_aceptacion(estado):
            marcas += MARCA_ESTADO_ACEPTACION
        return f"{marcas} {estado}".strip()

    def aplicar_estilo_celda(self, numero_fila: int, numero_columna: int, color_fondo: str, en_negrita: bool) -> None:
        celda = self.item(numero_fila, numero_columna)
        if celda is None:
            return
        celda.setBackground(QBrush(QColor(color_fondo)))
        fuente_celda = celda.font()
        fuente_celda.setBold(en_negrita)
        celda.setFont(fuente_celda)

    def limpiar_resaltado(self) -> None:
        for numero_fila in range(self.rowCount()):
            for numero_columna in range(self.columnCount()):
                self.aplicar_estilo_celda(numero_fila, numero_columna, estilos.COLOR_CELDA_NORMAL, False)

    def mostrar_estado_simulacion(self, estado_actual: str, ultimo_paso: PasoSimulacion | None) -> None:
        self.limpiar_resaltado()
        if self.automata is None:
            return

        fila_estado_actual = self.automata.estados.index(estado_actual)
        for numero_columna in range(self.columnCount()):
            self.aplicar_estilo_celda(fila_estado_actual, numero_columna, estilos.COLOR_FILA_ESTADO_ACTUAL, False)

        if ultimo_paso is not None and ultimo_paso.simbolo_leido in self.automata.simbolos:
            fila_ultimo_paso = self.automata.estados.index(ultimo_paso.estado_origen)
            columna_ultimo_paso = self.automata.simbolos.index(ultimo_paso.simbolo_leido)
            self.aplicar_estilo_celda(
                fila_ultimo_paso, columna_ultimo_paso, estilos.COLOR_CELDA_TRANSICION_ACTIVA, True
            )
