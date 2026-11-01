from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QGroupBox,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from afd.automata import AutomataFinitoDeterminista, ErrorDefinicionAutomata
from afd.simulacion import SimulacionPasoAPaso
from interfaz.controles_simulacion import ControlesSimulacion, HistorialRecorrido
from interfaz.datos_proyecto import NOMBRE_APLICACION
from interfaz.diagrama_automata import DiagramaAutomata
from interfaz.dialogo_acerca_de import DialogoAcercaDe
from interfaz.dialogo_ayuda import DialogoAyuda
from interfaz.dialogos_archivo import escribir_texto_en_archivo, pedir_ruta_para_abrir, pedir_ruta_para_guardar
from interfaz.editor_definicion import EditorDefinicion
from interfaz.panel_cadenas import PanelCadenas
from interfaz.recursos import obtener_ruta_recurso
from interfaz.tabla_transiciones import TablaTransiciones

TITULO_APLICACION = NOMBRE_APLICACION
DESCRIPCION_AUTOMATA_SIN_GUARDAR = "autómata sin guardar"

EJEMPLOS_INCLUIDOS = [
    ("Ejemplo 1: cantidad par de 0s y de 1s", "ejemplo1_pares.txt"),
    ("Ejemplo 2: cadenas sobre {a, b} que terminan en «ab»", "ejemplo2_termina_ab.txt"),
    ("Ejemplo 3: números binarios divisibles entre 3", "ejemplo3_divisible3.txt"),
]


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.automata_actual: AutomataFinitoDeterminista | None = None
        self.simulacion_actual: SimulacionPasoAPaso | None = None
        self.indice_cadena_actual: int | None = None
        self.ruta_archivo_actual: str | None = None

        self.setWindowTitle(TITULO_APLICACION)
        self.resize(1300, 820)
        self.crear_componentes()
        self.crear_menus()
        self.conectar_senales()
        self.cargar_ejemplo(*EJEMPLOS_INCLUIDOS[0])

    def crear_componentes(self) -> None:
        self.diagrama_automata = DiagramaAutomata()
        self.tabla_transiciones = TablaTransiciones()
        self.panel_cadenas = PanelCadenas()
        self.historial_recorrido = HistorialRecorrido()
        self.controles_simulacion = ControlesSimulacion()
        self.editor_definicion = EditorDefinicion(self)

        divisor_derecho = QSplitter(Qt.Vertical)
        divisor_derecho.addWidget(
            self.crear_grupo("Tabla de transiciones  (→ inicial,  * aceptación)", self.tabla_transiciones)
        )
        divisor_derecho.addWidget(self.crear_grupo("Cadenas a analizar", self.panel_cadenas))
        divisor_derecho.addWidget(self.crear_grupo("Recorrido paso a paso", self.historial_recorrido))
        divisor_derecho.setSizes([220, 280, 200])

        divisor_principal = QSplitter(Qt.Horizontal)
        divisor_principal.addWidget(self.crear_grupo("Diagrama del AFD", self.diagrama_automata))
        divisor_principal.addWidget(divisor_derecho)
        divisor_principal.setSizes([720, 580])

        contenedor_central = QWidget()
        distribucion_central = QVBoxLayout(contenedor_central)
        distribucion_central.addWidget(divisor_principal, 1)
        distribucion_central.addWidget(self.crear_grupo("Simulación paso a paso", self.controles_simulacion))
        self.setCentralWidget(contenedor_central)

    @staticmethod
    def crear_grupo(titulo: str, contenido: QWidget) -> QGroupBox:
        grupo = QGroupBox(titulo)
        distribucion_grupo = QVBoxLayout(grupo)
        distribucion_grupo.addWidget(contenido)
        return grupo

    def crear_menus(self) -> None:
        menu_archivo = self.menuBar().addMenu("&Archivo")
        self.agregar_accion_menu(menu_archivo, "&Nuevo...", QKeySequence.New, self.crear_nuevo_automata)
        self.agregar_accion_menu(menu_archivo, "&Abrir...", QKeySequence.Open, self.abrir_archivo)
        self.agregar_accion_menu(
            menu_archivo, "&Editar autómata actual...", QKeySequence("Ctrl+E"), self.editar_automata_actual
        )
        menu_archivo.addSeparator()
        self.agregar_accion_menu(menu_archivo, "&Guardar", QKeySequence.Save, self.guardar_archivo)
        self.agregar_accion_menu(
            menu_archivo, "Guardar &como...", QKeySequence("Ctrl+Shift+S"), self.guardar_archivo_como
        )
        menu_archivo.addSeparator()
        self.agregar_accion_menu(menu_archivo, "&Salir", QKeySequence("Ctrl+Q"), self.close)

        menu_ejemplos = self.menuBar().addMenu("&Ejemplos")
        for titulo_ejemplo, nombre_archivo_ejemplo in EJEMPLOS_INCLUIDOS:
            accion_ejemplo = menu_ejemplos.addAction(titulo_ejemplo)
            accion_ejemplo.triggered.connect(
                lambda _marcada=False, titulo=titulo_ejemplo, archivo=nombre_archivo_ejemplo: self.cargar_ejemplo(
                    titulo, archivo
                )
            )

        menu_acerca_de = self.menuBar().addMenu("A&cerca de...")
        self.agregar_accion_menu(menu_acerca_de, "&Acerca de", None, self.mostrar_acerca_de)
        self.agregar_accion_menu(menu_acerca_de, "A&yuda", QKeySequence.HelpContents, self.mostrar_ayuda)

    def agregar_accion_menu(self, menu, texto_opcion: str, atajo_teclado, funcion_a_ejecutar) -> None:
        accion = menu.addAction(texto_opcion)
        if atajo_teclado is not None:
            accion.setShortcut(atajo_teclado)
        accion.triggered.connect(funcion_a_ejecutar)

    def conectar_senales(self) -> None:
        self.editor_definicion.automata_listo_para_cargar.connect(self.cargar_automata_desde_editor)

        self.panel_cadenas.cadena_seleccionada.connect(self.seleccionar_cadena)
        self.panel_cadenas.agregar_cadena_solicitada.connect(self.agregar_cadena)
        self.panel_cadenas.procesar_todas_solicitado.connect(self.procesar_todas_las_cadenas)

        self.controles_simulacion.reiniciar_solicitado.connect(self.reiniciar_simulacion)
        self.controles_simulacion.paso_anterior_solicitado.connect(self.retroceder_un_paso)
        self.controles_simulacion.paso_siguiente_solicitado.connect(self.avanzar_un_paso)
        self.controles_simulacion.ir_al_final_solicitado.connect(self.ir_al_final_de_la_cadena)

    def crear_nuevo_automata(self) -> None:
        self.editor_definicion.editar_nuevo_automata()

    def editar_automata_actual(self) -> None:
        if self.automata_actual is None:
            self.crear_nuevo_automata()
            return
        self.editor_definicion.editar_definicion(self.automata_actual.convertir_a_texto(), self.ruta_archivo_actual)

    def abrir_archivo(self) -> None:
        ruta_archivo = pedir_ruta_para_abrir(self)
        if ruta_archivo is not None:
            self.cargar_automata_desde_archivo(ruta_archivo)

    def cargar_ejemplo(self, titulo_ejemplo: str, nombre_archivo_ejemplo: str) -> None:
        ruta_ejemplo = obtener_ruta_recurso("ejemplos", nombre_archivo_ejemplo)
        self.cargar_automata_desde_archivo(ruta_ejemplo, descripcion_automata=titulo_ejemplo, recordar_ruta=False)

    def cargar_automata_desde_archivo(
        self, ruta_archivo: str, descripcion_automata: str | None = None, recordar_ruta: bool = True
    ) -> None:
        try:
            automata = AutomataFinitoDeterminista.crear_desde_archivo(ruta_archivo)
        except (OSError, ValueError, ErrorDefinicionAutomata) as error:
            QMessageBox.critical(
                self, "No se pudo cargar el autómata", f"Archivo: {ruta_archivo}\n\n{error}"
            )
            return
        self.ruta_archivo_actual = ruta_archivo if recordar_ruta else None
        self.mostrar_automata(automata, descripcion_automata or os.path.basename(ruta_archivo))

    def cargar_automata_desde_editor(self, automata: AutomataFinitoDeterminista, ruta_archivo: str | None) -> None:
        self.ruta_archivo_actual = ruta_archivo
        descripcion_automata = os.path.basename(ruta_archivo) if ruta_archivo else DESCRIPCION_AUTOMATA_SIN_GUARDAR
        self.mostrar_automata(automata, descripcion_automata)

    def guardar_archivo(self) -> None:
        if self.editor_definicion.isVisible():
            self.editor_definicion.guardar()
        elif self.ruta_archivo_actual is None:
            self.guardar_archivo_como()
        else:
            self.guardar_automata_actual_en(self.ruta_archivo_actual)

    def guardar_archivo_como(self) -> None:
        if self.editor_definicion.isVisible():
            self.editor_definicion.guardar_como()
            return
        ruta_elegida = pedir_ruta_para_guardar(self, self.ruta_archivo_actual)
        if ruta_elegida is not None:
            self.guardar_automata_actual_en(ruta_elegida)

    def guardar_automata_actual_en(self, ruta_archivo: str) -> None:
        if self.automata_actual is None:
            return
        if escribir_texto_en_archivo(self, ruta_archivo, self.automata_actual.convertir_a_texto()):
            self.ruta_archivo_actual = ruta_archivo
            nombre_archivo = os.path.basename(ruta_archivo)
            self.setWindowTitle(f"{TITULO_APLICACION} — {nombre_archivo}")
            self.statusBar().showMessage(f"Autómata guardado en {ruta_archivo}")

    def mostrar_acerca_de(self) -> None:
        DialogoAcercaDe(self).exec()

    def mostrar_ayuda(self) -> None:
        DialogoAyuda(self).exec()

    def closeEvent(self, evento):
        if self.editor_definicion.isVisible() and not self.editor_definicion.confirmar_descartar_cambios():
            evento.ignore()
            return
        self.controles_simulacion.detener_reproduccion()
        evento.accept()

    def mostrar_automata(self, automata: AutomataFinitoDeterminista, descripcion_automata: str) -> None:
        self.controles_simulacion.detener_reproduccion()
        self.automata_actual = automata
        self.diagrama_automata.mostrar_automata(automata)
        self.tabla_transiciones.mostrar_automata(automata)
        self.panel_cadenas.mostrar_cadenas(automata.cadenas_a_analizar)
        self.setWindowTitle(f"{TITULO_APLICACION} — {descripcion_automata}")
        self.statusBar().showMessage(
            f"Autómata cargado: {len(automata.estados)} estados, {len(automata.simbolos)} símbolos, "
            f"{len(automata.cadenas_a_analizar)} cadenas a analizar."
        )

        if automata.cadenas_a_analizar:
            self.panel_cadenas.marcar_fila_seleccionada(0)
            self.seleccionar_cadena(0)
        else:
            self.simulacion_actual = None
            self.indice_cadena_actual = None
            self.actualizar_vista_simulacion()

    def seleccionar_cadena(self, indice_cadena: int) -> None:
        if self.automata_actual is None or not 0 <= indice_cadena < len(self.automata_actual.cadenas_a_analizar):
            return
        self.controles_simulacion.detener_reproduccion()
        self.indice_cadena_actual = indice_cadena
        self.simulacion_actual = SimulacionPasoAPaso(
            self.automata_actual, self.automata_actual.cadenas_a_analizar[indice_cadena]
        )
        self.actualizar_vista_simulacion()

    def agregar_cadena(self, texto_ingresado: str) -> None:
        if self.automata_actual is None:
            return
        simbolos_cadena = self.automata_actual.interpretar_cadena_ingresada(texto_ingresado)
        self.automata_actual.cadenas_a_analizar.append(simbolos_cadena)
        indice_nueva_cadena = self.panel_cadenas.agregar_fila_cadena(simbolos_cadena)
        self.panel_cadenas.marcar_fila_seleccionada(indice_nueva_cadena)
        self.seleccionar_cadena(indice_nueva_cadena)

    def procesar_todas_las_cadenas(self) -> None:
        if self.automata_actual is None:
            return
        cantidad_aceptadas = 0
        for indice_cadena, simbolos_cadena in enumerate(self.automata_actual.cadenas_a_analizar):
            resultado = self.automata_actual.simular_cadena(simbolos_cadena)
            self.panel_cadenas.mostrar_resultado(indice_cadena, resultado)
            cantidad_aceptadas += resultado.fue_aceptada
        cantidad_rechazadas = len(self.automata_actual.cadenas_a_analizar) - cantidad_aceptadas
        self.statusBar().showMessage(
            f"Cadenas procesadas: {cantidad_aceptadas} aceptadas, {cantidad_rechazadas} rechazadas."
        )

    def avanzar_un_paso(self) -> None:
        if self.simulacion_actual is not None:
            self.simulacion_actual.avanzar_un_paso()
            self.actualizar_vista_simulacion()

    def retroceder_un_paso(self) -> None:
        if self.simulacion_actual is not None:
            self.simulacion_actual.retroceder_un_paso()
            self.actualizar_vista_simulacion()

    def reiniciar_simulacion(self) -> None:
        if self.simulacion_actual is not None:
            self.simulacion_actual.reiniciar()
            self.actualizar_vista_simulacion()

    def ir_al_final_de_la_cadena(self) -> None:
        if self.simulacion_actual is not None:
            self.simulacion_actual.ejecutar_hasta_el_final()
            self.actualizar_vista_simulacion()

    def actualizar_vista_simulacion(self) -> None:
        simulacion = self.simulacion_actual
        if simulacion is None:
            self.diagrama_automata.limpiar_resaltado()
            self.tabla_transiciones.limpiar_resaltado()
            self.historial_recorrido.clear()
            self.controles_simulacion.mostrar_sin_simulacion()
            return

        estado_actual = simulacion.obtener_estado_actual()
        ultimo_paso = simulacion.obtener_ultimo_paso()
        self.diagrama_automata.mostrar_estado_simulacion(
            estado_actual,
            simulacion.obtener_estados_visitados(),
            ultimo_paso,
            simulacion.obtener_resultado_final(),
        )
        self.tabla_transiciones.mostrar_estado_simulacion(estado_actual, ultimo_paso)
        self.historial_recorrido.mostrar_recorrido(simulacion)
        self.controles_simulacion.mostrar_progreso(simulacion)

        if simulacion.esta_terminada():
            self.panel_cadenas.mostrar_resultado(self.indice_cadena_actual, simulacion.resultado_completo)
