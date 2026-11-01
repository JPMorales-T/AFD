from __future__ import annotations

import html

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from afd.simulacion import SimulacionPasoAPaso
from interfaz import estilos

INTERVALO_MINIMO_REPRODUCCION_MS = 150
INTERVALO_MAXIMO_REPRODUCCION_MS = 2000
INTERVALO_INICIAL_REPRODUCCION_MS = 800


def describir_resultado_final(simulacion: SimulacionPasoAPaso) -> tuple[str, str]:
    resultado = simulacion.resultado_completo
    estado_final = simulacion.obtener_estado_actual()
    if resultado.mensaje_error:
        return f"RECHAZADA: {resultado.mensaje_error}", estilos.COLOR_TEXTO_RECHAZADA
    if resultado.fue_aceptada:
        return f"ACEPTADA: {estado_final} es estado de aceptación", estilos.COLOR_TEXTO_ACEPTADA
    return f"RECHAZADA: {estado_final} no es estado de aceptación", estilos.COLOR_TEXTO_RECHAZADA


class ControlesSimulacion(QWidget):
    reiniciar_solicitado = Signal()
    paso_anterior_solicitado = Signal()
    paso_siguiente_solicitado = Signal()
    ir_al_final_solicitado = Signal()

    def __init__(self, padre=None):
        super().__init__(padre)
        self.simulacion_terminada = False
        self.temporizador_reproduccion = QTimer(self)
        self.crear_componentes()
        self.conectar_senales()
        self.mostrar_sin_simulacion()

    def crear_componentes(self) -> None:
        estilo_sistema = self.style()

        self.etiqueta_cadena = QLabel()
        self.etiqueta_cadena.setTextFormat(Qt.RichText)
        self.etiqueta_cadena.setAlignment(Qt.AlignCenter)
        fuente_cadena = QFont("Consolas", 18)
        self.etiqueta_cadena.setFont(fuente_cadena)

        self.etiqueta_estado = QLabel()
        self.etiqueta_estado.setTextFormat(Qt.RichText)
        self.etiqueta_estado.setAlignment(Qt.AlignCenter)
        self.etiqueta_estado.setWordWrap(True)

        self.boton_reiniciar = QPushButton(estilo_sistema.standardIcon(QStyle.SP_MediaSkipBackward), " Reiniciar")
        self.boton_paso_anterior = QPushButton(estilo_sistema.standardIcon(QStyle.SP_MediaSeekBackward), " Paso anterior")
        self.boton_paso_siguiente = QPushButton(estilo_sistema.standardIcon(QStyle.SP_MediaSeekForward), " Paso siguiente")
        self.boton_ir_al_final = QPushButton(estilo_sistema.standardIcon(QStyle.SP_MediaSkipForward), " Ir al final")
        self.boton_reproducir = QPushButton()
        self.mostrar_boton_como_reproducir()

        self.control_velocidad = QSlider(Qt.Horizontal)
        self.control_velocidad.setRange(INTERVALO_MINIMO_REPRODUCCION_MS, INTERVALO_MAXIMO_REPRODUCCION_MS)
        self.control_velocidad.setValue(INTERVALO_INICIAL_REPRODUCCION_MS)
        self.control_velocidad.setInvertedAppearance(True)
        self.control_velocidad.setFixedWidth(140)

        fila_botones = QHBoxLayout()
        fila_botones.addStretch(1)
        for boton in (
            self.boton_reiniciar,
            self.boton_paso_anterior,
            self.boton_paso_siguiente,
            self.boton_ir_al_final,
            self.boton_reproducir,
        ):
            fila_botones.addWidget(boton)
        fila_botones.addSpacing(16)
        fila_botones.addWidget(QLabel("Lento"))
        fila_botones.addWidget(self.control_velocidad)
        fila_botones.addWidget(QLabel("Rápido"))
        fila_botones.addStretch(1)

        distribucion = QVBoxLayout(self)
        distribucion.addWidget(self.etiqueta_cadena)
        distribucion.addWidget(self.etiqueta_estado)
        distribucion.addLayout(fila_botones)

    def conectar_senales(self) -> None:
        self.boton_reiniciar.clicked.connect(self.reiniciar_solicitado.emit)
        self.boton_paso_anterior.clicked.connect(self.paso_anterior_solicitado.emit)
        self.boton_paso_siguiente.clicked.connect(self.paso_siguiente_solicitado.emit)
        self.boton_ir_al_final.clicked.connect(self.ir_al_final_solicitado.emit)
        self.boton_reproducir.clicked.connect(self.alternar_reproduccion)
        self.temporizador_reproduccion.timeout.connect(self.paso_siguiente_solicitado.emit)
        self.control_velocidad.valueChanged.connect(self.temporizador_reproduccion.setInterval)

    def alternar_reproduccion(self) -> None:
        if self.temporizador_reproduccion.isActive():
            self.detener_reproduccion()
        else:
            self.iniciar_reproduccion()

    def iniciar_reproduccion(self) -> None:
        if self.simulacion_terminada:
            self.reiniciar_solicitado.emit()
        self.temporizador_reproduccion.start(self.control_velocidad.value())
        self.boton_reproducir.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.boton_reproducir.setText(" Pausar")

    def detener_reproduccion(self) -> None:
        self.temporizador_reproduccion.stop()
        self.mostrar_boton_como_reproducir()

    def mostrar_boton_como_reproducir(self) -> None:
        self.boton_reproducir.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.boton_reproducir.setText(" Reproducir")

    def mostrar_sin_simulacion(self) -> None:
        self.detener_reproduccion()
        self.etiqueta_cadena.setText("<i>—</i>")
        self.etiqueta_estado.setText("Cargue un autómata y seleccione una cadena para simular.")
        for boton in (
            self.boton_reiniciar,
            self.boton_paso_anterior,
            self.boton_paso_siguiente,
            self.boton_ir_al_final,
            self.boton_reproducir,
        ):
            boton.setEnabled(False)

    def mostrar_progreso(self, simulacion: SimulacionPasoAPaso) -> None:
        self.simulacion_terminada = simulacion.esta_terminada()
        self.etiqueta_cadena.setText(self.construir_html_cadena(simulacion))
        self.etiqueta_estado.setText(self.construir_html_estado(simulacion))

        self.boton_reiniciar.setEnabled(not simulacion.esta_al_inicio())
        self.boton_paso_anterior.setEnabled(not simulacion.esta_al_inicio())
        self.boton_paso_siguiente.setEnabled(not simulacion.esta_terminada())
        self.boton_ir_al_final.setEnabled(not simulacion.esta_terminada())
        self.boton_reproducir.setEnabled(True)
        if simulacion.esta_terminada():
            self.detener_reproduccion()

    @staticmethod
    def construir_html_cadena(simulacion: SimulacionPasoAPaso) -> str:
        if not simulacion.simbolos_cadena:
            return "<i>ε (palabra vacía)</i>"
        posicion_recien_leido = simulacion.cantidad_pasos_ejecutados - 1
        simbolos_html = []
        for posicion_simbolo, simbolo in enumerate(simulacion.simbolos_cadena):
            simbolo_escapado = html.escape(simbolo)
            if posicion_simbolo == posicion_recien_leido:
                simbolos_html.append(
                    f"<span style='color:{estilos.COLOR_SIMBOLO_RECIEN_LEIDO};"
                    f"background:{estilos.COLOR_FONDO_SIMBOLO_RECIEN_LEIDO};"
                    f"font-weight:bold;text-decoration:underline'>&nbsp;{simbolo_escapado}&nbsp;</span>"
                )
            elif posicion_simbolo < posicion_recien_leido:
                simbolos_html.append(f"<span style='color:{estilos.COLOR_SIMBOLO_YA_LEIDO}'>{simbolo_escapado}</span>")
            else:
                simbolos_html.append(f"<span style='color:{estilos.COLOR_SIMBOLO_PENDIENTE}'>{simbolo_escapado}</span>")
        return " ".join(simbolos_html)

    @staticmethod
    def construir_html_estado(simulacion: SimulacionPasoAPaso) -> str:
        partes_descripcion = [
            f"Paso <b>{simulacion.cantidad_pasos_ejecutados}</b> de {simulacion.obtener_total_pasos()}",
            f"Estado actual: <b>{html.escape(simulacion.obtener_estado_actual())}</b>",
        ]
        ultimo_paso = simulacion.obtener_ultimo_paso()
        if ultimo_paso is not None and ultimo_paso.estado_destino is not None:
            partes_descripcion.append(
                html.escape(f"δ({ultimo_paso.estado_origen}, {ultimo_paso.simbolo_leido}) = {ultimo_paso.estado_destino}")
            )
        if simulacion.esta_terminada():
            texto_resultado, color_resultado = describir_resultado_final(simulacion)
            partes_descripcion.append(
                f"<span style='color:{color_resultado};font-weight:bold'>{html.escape(texto_resultado)}</span>"
            )
        return " &nbsp;|&nbsp; ".join(partes_descripcion)


class HistorialRecorrido(QListWidget):
    def mostrar_recorrido(self, simulacion: SimulacionPasoAPaso) -> None:
        self.clear()
        self.addItem(f"Inicio en el estado {simulacion.automata.estado_inicial}")
        for numero_paso, paso in enumerate(simulacion.obtener_pasos_ejecutados(), start=1):
            if paso.estado_destino is None:
                descripcion_paso = (
                    f"{numero_paso}. Lee '{paso.simbolo_leido}': no pertenece al alfabeto, el autómata se detiene"
                )
            else:
                descripcion_paso = (
                    f"{numero_paso}. Lee '{paso.simbolo_leido}':  "
                    f"δ({paso.estado_origen}, {paso.simbolo_leido}) = {paso.estado_destino}"
                )
            self.addItem(descripcion_paso)

        if simulacion.esta_terminada():
            texto_resultado, color_resultado = describir_resultado_final(simulacion)
            elemento_resultado = QListWidgetItem(texto_resultado)
            elemento_resultado.setForeground(QBrush(QColor(color_resultado)))
            fuente_resultado = elemento_resultado.font()
            fuente_resultado.setBold(True)
            elemento_resultado.setFont(fuente_resultado)
            self.addItem(elemento_resultado)

        self.scrollToBottom()
