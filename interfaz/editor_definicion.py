from __future__ import annotations

import html
import os

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
)

from afd.automata import AutomataFinitoDeterminista, ErrorDefinicionAutomata
from interfaz import estilos
from interfaz.contenido_ayuda import EXPLICACION_FORMATO_ARCHIVO_HTML
from interfaz.dialogos_archivo import escribir_texto_en_archivo, pedir_ruta_para_guardar

TITULO_EDITOR = "Editor de definición del AFD"
TITULO_DOCUMENTO_SIN_GUARDAR = "Sin título"
ESPERA_ANTES_DE_VALIDAR_MS = 400

PLANTILLA_NUEVO_AUTOMATA = """Simbolos: 0,1
Estados: Q0,Q1
Estado inicial: Q0
Estados de aceptación: Q1
Transiciones:
Q0,Q1
Q1,Q0
Cadenas a analizar:
1
1,0,1
1,1
"""


class EditorDefinicion(QDialog):
    automata_listo_para_cargar = Signal(object, object)

    def __init__(self, ventana_padre=None):
        super().__init__(ventana_padre)
        self.ruta_archivo_editado: str | None = None
        self.temporizador_validacion = QTimer(self)
        self.temporizador_validacion.setSingleShot(True)
        self.temporizador_validacion.setInterval(ESPERA_ANTES_DE_VALIDAR_MS)
        self.resize(900, 600)
        self.crear_componentes()
        self.conectar_senales()

    def crear_componentes(self) -> None:
        self.campo_texto = QPlainTextEdit()
        self.campo_texto.setFont(QFont("Consolas", 12))
        self.campo_texto.setLineWrapMode(QPlainTextEdit.NoWrap)

        explicacion_formato = QLabel(EXPLICACION_FORMATO_ARCHIVO_HTML)
        explicacion_formato.setTextFormat(Qt.RichText)
        explicacion_formato.setWordWrap(True)
        explicacion_formato.setAlignment(Qt.AlignTop)
        explicacion_formato.setMargin(8)
        panel_explicacion = QScrollArea()
        panel_explicacion.setWidget(explicacion_formato)
        panel_explicacion.setWidgetResizable(True)

        self.etiqueta_validacion = QLabel()
        self.etiqueta_validacion.setTextFormat(Qt.RichText)
        self.etiqueta_validacion.setWordWrap(True)

        self.boton_cargar_en_simulador = QPushButton("Cargar en el simulador")
        self.boton_cargar_en_simulador.setDefault(True)
        self.boton_guardar = QPushButton("Guardar")
        self.boton_guardar_como = QPushButton("Guardar como...")
        self.boton_cerrar = QPushButton("Cerrar")

        fila_contenido = QHBoxLayout()
        fila_contenido.addWidget(self.campo_texto, 3)
        fila_contenido.addWidget(panel_explicacion, 2)

        fila_botones = QHBoxLayout()
        fila_botones.addWidget(self.boton_cargar_en_simulador)
        fila_botones.addStretch(1)
        fila_botones.addWidget(self.boton_guardar)
        fila_botones.addWidget(self.boton_guardar_como)
        fila_botones.addWidget(self.boton_cerrar)

        distribucion = QVBoxLayout(self)
        distribucion.addLayout(fila_contenido, 1)
        distribucion.addWidget(self.etiqueta_validacion)
        distribucion.addLayout(fila_botones)

    def conectar_senales(self) -> None:
        self.campo_texto.textChanged.connect(self.temporizador_validacion.start)
        self.campo_texto.modificationChanged.connect(self.actualizar_titulo)
        self.temporizador_validacion.timeout.connect(self.validar_definicion)
        self.boton_cargar_en_simulador.clicked.connect(self.cargar_en_simulador)
        self.boton_guardar.clicked.connect(self.guardar)
        self.boton_guardar_como.clicked.connect(self.guardar_como)
        self.boton_cerrar.clicked.connect(self.reject)

    def editar_definicion(self, texto_definicion: str, ruta_archivo: str | None) -> None:
        if self.isVisible() and not self.confirmar_descartar_cambios():
            return
        self.campo_texto.setPlainText(texto_definicion)
        self.campo_texto.document().setModified(False)
        self.ruta_archivo_editado = ruta_archivo
        self.actualizar_titulo()
        self.validar_definicion()
        self.show()
        self.raise_()
        self.activateWindow()

    def editar_nuevo_automata(self) -> None:
        self.editar_definicion(PLANTILLA_NUEVO_AUTOMATA, None)

    def validar_definicion(self) -> AutomataFinitoDeterminista | None:
        try:
            automata = AutomataFinitoDeterminista.crear_desde_texto(self.campo_texto.toPlainText())
        except ErrorDefinicionAutomata as error:
            self.etiqueta_validacion.setText(
                f"<span style='color:{estilos.COLOR_TEXTO_RECHAZADA}'><b>✘ Definición inválida:</b> "
                f"{html.escape(str(error))}</span>"
            )
            self.boton_cargar_en_simulador.setEnabled(False)
            return None

        self.etiqueta_validacion.setText(
            f"<span style='color:{estilos.COLOR_TEXTO_ACEPTADA}'><b>✔ Definición válida:</b> "
            f"{len(automata.estados)} estados, {len(automata.simbolos)} símbolos, "
            f"{len(automata.cadenas_a_analizar)} cadenas a analizar.</span>"
        )
        self.boton_cargar_en_simulador.setEnabled(True)
        return automata

    def cargar_en_simulador(self) -> None:
        automata = self.validar_definicion()
        if automata is not None:
            self.automata_listo_para_cargar.emit(automata, self.ruta_archivo_editado)

    def guardar(self) -> bool:
        if self.ruta_archivo_editado is None:
            return self.guardar_como()
        return self.guardar_en_ruta(self.ruta_archivo_editado)

    def guardar_como(self) -> bool:
        ruta_elegida = pedir_ruta_para_guardar(self, self.ruta_archivo_editado)
        if ruta_elegida is None:
            return False
        return self.guardar_en_ruta(ruta_elegida)

    def guardar_en_ruta(self, ruta_archivo: str) -> bool:
        if self.validar_definicion() is None:
            respuesta = QMessageBox.warning(
                self,
                "Definición inválida",
                "La definición tiene errores y no podrá abrirse en el simulador hasta corregirlos.\n\n"
                "¿Desea guardarla de todas formas?",
                QMessageBox.Save | QMessageBox.Cancel,
            )
            if respuesta != QMessageBox.Save:
                return False
        if not escribir_texto_en_archivo(self, ruta_archivo, self.campo_texto.toPlainText()):
            return False
        self.ruta_archivo_editado = ruta_archivo
        self.campo_texto.document().setModified(False)
        self.actualizar_titulo()
        return True

    def tiene_cambios_sin_guardar(self) -> bool:
        return self.campo_texto.document().isModified()

    def confirmar_descartar_cambios(self) -> bool:
        if not self.tiene_cambios_sin_guardar():
            return True
        respuesta = QMessageBox.question(
            self,
            "Cambios sin guardar",
            "La definición del editor tiene cambios sin guardar.\n¿Desea guardarlos?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )
        if respuesta == QMessageBox.Save:
            return self.guardar()
        return respuesta == QMessageBox.Discard

    def actualizar_titulo(self) -> None:
        nombre_documento = (
            os.path.basename(self.ruta_archivo_editado) if self.ruta_archivo_editado else TITULO_DOCUMENTO_SIN_GUARDAR
        )
        marca_modificado = " *" if self.tiene_cambios_sin_guardar() else ""
        self.setWindowTitle(f"{TITULO_EDITOR} — {nombre_documento}{marca_modificado}")

    def reject(self) -> None:
        if self.confirmar_descartar_cambios():
            self.campo_texto.document().setModified(False)
            super().reject()
