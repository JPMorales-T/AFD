from __future__ import annotations

import itertools
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView

from afd.automata import AutomataFinitoDeterminista, PasoSimulacion
from interfaz import estilos

RADIO_ESTADO = 28.0
SEPARACION_CIRCULO_ACEPTACION = 5.0
ALTURA_CURVA_TRANSICIONES_OPUESTAS = 28.0
SEPARACION_ETIQUETA_TRANSICION = 12.0
TAMANO_PUNTA_FLECHA = 12.0
LONGITUD_FLECHA_INICIAL = 45.0
DISTANCIA_MINIMA_ENTRE_ESTADOS_VECINOS = RADIO_ESTADO * 4.5
RADIO_MINIMO_DISTRIBUCION = 130.0
MAXIMO_ESTADOS_PARA_OPTIMIZAR_ORDEN = 7
PENALIZACION_POR_CRUCE = 10
ESCALA_MAXIMA_VISTA = 1.6
MARGEN_VISTA = 30.0

GROSOR_TRANSICION_NORMAL = 1.6
GROSOR_TRANSICION_ACTIVA = 3.5
GROSOR_BORDE_ESTADO_NORMAL = 2.0
GROSOR_BORDE_ESTADO_ACTUAL = 3.5

CAPA_TRANSICIONES = 0
CAPA_ETIQUETAS = 2
CAPA_ESTADOS = 4

FUENTE_NOMBRE_ESTADO = QFont("Segoe UI", 11, QFont.Bold)
FUENTE_ETIQUETA_TRANSICION = QFont("Segoe UI", 10)


def calcular_vector_unitario(punto_inicio: QPointF, punto_fin: QPointF) -> QPointF:
    diferencia_x = punto_fin.x() - punto_inicio.x()
    diferencia_y = punto_fin.y() - punto_inicio.y()
    longitud = math.hypot(diferencia_x, diferencia_y)
    if longitud == 0:
        return QPointF(1.0, 0.0)
    return QPointF(diferencia_x / longitud, diferencia_y / longitud)


def calcular_punto_en_direccion(centro: QPointF, angulo_radianes: float, distancia: float) -> QPointF:
    return QPointF(
        centro.x() + math.cos(angulo_radianes) * distancia,
        centro.y() + math.sin(angulo_radianes) * distancia,
    )


def crear_poligono_punta_flecha(punta: QPointF, direccion_unitaria: QPointF) -> QPolygonF:
    perpendicular = QPointF(-direccion_unitaria.y(), direccion_unitaria.x())
    base_punta = punta - direccion_unitaria * TAMANO_PUNTA_FLECHA
    media_anchura = TAMANO_PUNTA_FLECHA * 0.5
    return QPolygonF(
        [punta, base_punta + perpendicular * media_anchura, base_punta - perpendicular * media_anchura]
    )


def calcular_costo_distribucion(orden_estados: list[str], pares_conectados: set[frozenset]) -> int:
    cantidad_estados = len(orden_estados)
    posicion_en_circulo = {estado: indice for indice, estado in enumerate(orden_estados)}
    cuerdas = [sorted(posicion_en_circulo[estado] for estado in par) for par in pares_conectados]

    cantidad_cruces = 0
    for indice_cuerda, (inicio_a, fin_a) in enumerate(cuerdas):
        for inicio_b, fin_b in cuerdas[indice_cuerda + 1 :]:
            if (inicio_a < inicio_b < fin_a) != (inicio_a < fin_b < fin_a) and len({inicio_a, fin_a, inicio_b, fin_b}) == 4:
                cantidad_cruces += 1

    distancia_total = sum(
        min(fin - inicio, cantidad_estados - (fin - inicio)) for inicio, fin in cuerdas
    )
    return cantidad_cruces * PENALIZACION_POR_CRUCE + distancia_total


def centrar_texto_en_punto(elemento_texto: QGraphicsSimpleTextItem, punto: QPointF) -> None:
    rectangulo_texto = elemento_texto.boundingRect()
    elemento_texto.setPos(
        punto.x() - rectangulo_texto.width() / 2, punto.y() - rectangulo_texto.height() / 2
    )


class EstadoGrafico:
    def __init__(self, escena: QGraphicsScene, nombre_estado: str, centro: QPointF, es_aceptacion: bool):
        self.centro = centro
        rectangulo_circulo = QRectF(
            centro.x() - RADIO_ESTADO, centro.y() - RADIO_ESTADO, 2 * RADIO_ESTADO, 2 * RADIO_ESTADO
        )
        self.circulo_exterior = escena.addEllipse(rectangulo_circulo)
        self.circulo_exterior.setZValue(CAPA_ESTADOS)

        self.circulo_interior = None
        if es_aceptacion:
            separacion = SEPARACION_CIRCULO_ACEPTACION
            self.circulo_interior = escena.addEllipse(
                rectangulo_circulo.adjusted(separacion, separacion, -separacion, -separacion)
            )
            self.circulo_interior.setZValue(CAPA_ESTADOS + 1)

        self.texto_nombre = escena.addSimpleText(nombre_estado, FUENTE_NOMBRE_ESTADO)
        self.texto_nombre.setBrush(QBrush(QColor(estilos.COLOR_TEXTO_NORMAL)))
        centrar_texto_en_punto(self.texto_nombre, centro)
        self.texto_nombre.setZValue(CAPA_ESTADOS + 2)

        self.aplicar_estilo_normal()

    def aplicar_estilo(self, color_relleno: str, color_borde: str, grosor_borde: float) -> None:
        self.circulo_exterior.setPen(QPen(QColor(color_borde), grosor_borde))
        self.circulo_exterior.setBrush(QBrush(QColor(color_relleno)))
        if self.circulo_interior is not None:
            self.circulo_interior.setPen(QPen(QColor(color_borde), max(1.5, grosor_borde * 0.6)))

    def aplicar_estilo_normal(self) -> None:
        self.aplicar_estilo(
            estilos.COLOR_ESTADO_NORMAL, estilos.COLOR_LINEA_NORMAL, GROSOR_BORDE_ESTADO_NORMAL
        )


class TransicionGrafica:
    def __init__(
        self,
        escena: QGraphicsScene,
        trazo: QPainterPath,
        punta: QPointF,
        direccion_punta: QPointF,
        posicion_etiqueta: QPointF,
        texto_etiqueta: str,
    ):
        self.linea = escena.addPath(trazo)
        self.linea.setZValue(CAPA_TRANSICIONES)

        self.punta_flecha = escena.addPolygon(crear_poligono_punta_flecha(punta, direccion_punta))
        self.punta_flecha.setZValue(CAPA_TRANSICIONES + 1)

        self.etiqueta = escena.addSimpleText(texto_etiqueta, FUENTE_ETIQUETA_TRANSICION)
        centrar_texto_en_punto(self.etiqueta, posicion_etiqueta)
        self.etiqueta.setZValue(CAPA_ETIQUETAS + 1)

        self.fondo_etiqueta = escena.addRect(
            self.etiqueta.sceneBoundingRect().adjusted(-3, -1, 3, 1),
            QPen(Qt.NoPen),
            QBrush(QColor(estilos.COLOR_FONDO_DIAGRAMA)),
        )
        self.fondo_etiqueta.setZValue(CAPA_ETIQUETAS)

        self.aplicar_estilo_normal()

    def aplicar_estilo(self, color: str, grosor: float) -> None:
        color_qt = QColor(color)
        lapiz_linea = QPen(color_qt, grosor)
        lapiz_linea.setCapStyle(Qt.RoundCap)
        self.linea.setPen(lapiz_linea)
        self.punta_flecha.setPen(QPen(color_qt, 1))
        self.punta_flecha.setBrush(QBrush(color_qt))
        self.etiqueta.setBrush(QBrush(color_qt))

    def aplicar_estilo_normal(self) -> None:
        self.aplicar_estilo(estilos.COLOR_LINEA_NORMAL, GROSOR_TRANSICION_NORMAL)


class DiagramaAutomata(QGraphicsView):
    def __init__(self, padre=None):
        super().__init__(padre)
        self.escena = QGraphicsScene(self)
        self.setScene(self.escena)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setBackgroundBrush(QBrush(QColor(estilos.COLOR_FONDO_DIAGRAMA)))
        self.setMinimumSize(360, 300)

        self.automata: AutomataFinitoDeterminista | None = None
        self.centro_distribucion = QPointF(0.0, 0.0)
        self.estados_graficos: dict[str, EstadoGrafico] = {}
        self.transiciones_graficas: dict[tuple[str, str], TransicionGrafica] = {}

    def mostrar_automata(self, automata: AutomataFinitoDeterminista) -> None:
        self.automata = automata
        self.escena.clear()
        self.estados_graficos.clear()
        self.transiciones_graficas.clear()

        posiciones_estados = self.calcular_posiciones_estados(automata)
        for estado in automata.estados:
            self.estados_graficos[estado] = EstadoGrafico(
                self.escena, estado, posiciones_estados[estado], automata.es_estado_aceptacion(estado)
            )

        simbolos_por_par_de_estados = self.agrupar_simbolos_por_par_de_estados(automata)
        for (estado_origen, estado_destino), simbolos in simbolos_por_par_de_estados.items():
            texto_etiqueta = ", ".join(simbolos)
            if estado_origen == estado_destino:
                transicion_grafica = self.crear_bucle(estado_origen, texto_etiqueta)
            else:
                existe_transicion_opuesta = (estado_destino, estado_origen) in simbolos_por_par_de_estados
                transicion_grafica = self.crear_transicion_entre_estados(
                    estado_origen, estado_destino, texto_etiqueta, existe_transicion_opuesta
                )
            self.transiciones_graficas[(estado_origen, estado_destino)] = transicion_grafica

        self.dibujar_flecha_estado_inicial(automata.estado_inicial)
        self.ajustar_vista_al_contenido()

    def calcular_posiciones_estados(self, automata: AutomataFinitoDeterminista) -> dict[str, QPointF]:
        estados = automata.estados
        cantidad_estados = len(estados)
        if cantidad_estados == 1:
            return {estados[0]: self.centro_distribucion}

        estados_ordenados = self.elegir_orden_con_menos_cruces(automata)

        radio_distribucion = max(
            RADIO_MINIMO_DISTRIBUCION,
            DISTANCIA_MINIMA_ENTRE_ESTADOS_VECINOS / (2 * math.sin(math.pi / cantidad_estados)),
        )
        posiciones_estados = {}
        for indice_estado, estado in enumerate(estados_ordenados):
            angulo = math.pi + 2 * math.pi * indice_estado / cantidad_estados
            posiciones_estados[estado] = calcular_punto_en_direccion(
                self.centro_distribucion, angulo, radio_distribucion
            )
        return posiciones_estados

    @staticmethod
    def elegir_orden_con_menos_cruces(automata: AutomataFinitoDeterminista) -> list[str]:
        estados_sin_inicial = [estado for estado in automata.estados if estado != automata.estado_inicial]
        if len(automata.estados) > MAXIMO_ESTADOS_PARA_OPTIMIZAR_ORDEN:
            return [automata.estado_inicial] + estados_sin_inicial

        pares_conectados = {
            frozenset((estado_origen, automata.obtener_estado_destino(estado_origen, simbolo)))
            for estado_origen in automata.estados
            for simbolo in automata.simbolos
            if automata.obtener_estado_destino(estado_origen, simbolo) != estado_origen
        }
        mejor_orden, menor_costo = None, None
        for permutacion in itertools.permutations(estados_sin_inicial):
            orden_candidato = [automata.estado_inicial, *permutacion]
            costo_candidato = calcular_costo_distribucion(orden_candidato, pares_conectados)
            if menor_costo is None or costo_candidato < menor_costo:
                mejor_orden, menor_costo = orden_candidato, costo_candidato
        return mejor_orden

    @staticmethod
    def agrupar_simbolos_por_par_de_estados(
        automata: AutomataFinitoDeterminista,
    ) -> dict[tuple[str, str], list[str]]:
        simbolos_por_par_de_estados: dict[tuple[str, str], list[str]] = {}
        for estado_origen in automata.estados:
            for simbolo in automata.simbolos:
                estado_destino = automata.obtener_estado_destino(estado_origen, simbolo)
                simbolos_por_par_de_estados.setdefault((estado_origen, estado_destino), []).append(simbolo)
        return simbolos_por_par_de_estados

    def crear_transicion_entre_estados(
        self, estado_origen: str, estado_destino: str, texto_etiqueta: str, existe_transicion_opuesta: bool
    ) -> TransicionGrafica:
        centro_origen = self.estados_graficos[estado_origen].centro
        centro_destino = self.estados_graficos[estado_destino].centro
        direccion = calcular_vector_unitario(centro_origen, centro_destino)
        perpendicular = QPointF(direccion.y(), -direccion.x())
        punto_medio = (centro_origen + centro_destino) * 0.5

        altura_curva = ALTURA_CURVA_TRANSICIONES_OPUESTAS if existe_transicion_opuesta else 0.0
        punto_control = punto_medio + perpendicular * (altura_curva * 2)

        punto_salida = centro_origen + calcular_vector_unitario(centro_origen, punto_control) * RADIO_ESTADO
        punto_llegada = centro_destino + calcular_vector_unitario(centro_destino, punto_control) * RADIO_ESTADO

        trazo = QPainterPath(punto_salida)
        trazo.quadTo(punto_control, punto_llegada)

        punto_medio_curva = punto_salida * 0.25 + punto_control * 0.5 + punto_llegada * 0.25
        posicion_etiqueta = punto_medio_curva + perpendicular * SEPARACION_ETIQUETA_TRANSICION
        return TransicionGrafica(
            self.escena,
            trazo,
            punto_llegada,
            calcular_vector_unitario(punto_control, punto_llegada),
            posicion_etiqueta,
            texto_etiqueta,
        )

    def crear_bucle(self, estado: str, texto_etiqueta: str) -> TransicionGrafica:
        centro = self.estados_graficos[estado].centro
        angulo_bucle = self.calcular_angulo_bucle(estado, centro)
        apertura = math.radians(28)

        punto_salida = calcular_punto_en_direccion(centro, angulo_bucle - apertura, RADIO_ESTADO)
        punto_llegada = calcular_punto_en_direccion(centro, angulo_bucle + apertura, RADIO_ESTADO)
        control_salida = calcular_punto_en_direccion(centro, angulo_bucle - apertura * 1.8, RADIO_ESTADO * 3.2)
        control_llegada = calcular_punto_en_direccion(centro, angulo_bucle + apertura * 1.8, RADIO_ESTADO * 3.2)

        trazo = QPainterPath(punto_salida)
        trazo.cubicTo(control_salida, control_llegada, punto_llegada)

        posicion_etiqueta = calcular_punto_en_direccion(centro, angulo_bucle, RADIO_ESTADO * 2.25)
        return TransicionGrafica(
            self.escena,
            trazo,
            punto_llegada,
            calcular_vector_unitario(control_llegada, punto_llegada),
            posicion_etiqueta,
            texto_etiqueta,
        )

    def calcular_angulo_bucle(self, estado: str, centro: QPointF) -> float:
        angulo_hacia_arriba = -math.pi / 2
        if estado == self.automata.estado_inicial or centro == self.centro_distribucion:
            return angulo_hacia_arriba
        return math.atan2(
            centro.y() - self.centro_distribucion.y(), centro.x() - self.centro_distribucion.x()
        )

    def dibujar_flecha_estado_inicial(self, estado_inicial: str) -> None:
        centro = self.estados_graficos[estado_inicial].centro
        punta = QPointF(centro.x() - RADIO_ESTADO, centro.y())
        inicio = QPointF(punta.x() - LONGITUD_FLECHA_INICIAL, punta.y())
        color_linea = QColor(estilos.COLOR_LINEA_NORMAL)

        self.escena.addLine(inicio.x(), inicio.y(), punta.x(), punta.y(), QPen(color_linea, 2))
        self.escena.addPolygon(
            crear_poligono_punta_flecha(punta, QPointF(1.0, 0.0)), QPen(color_linea, 1), QBrush(color_linea)
        )
        texto_inicio = self.escena.addSimpleText("inicio", FUENTE_ETIQUETA_TRANSICION)
        texto_inicio.setBrush(QBrush(color_linea))
        centrar_texto_en_punto(texto_inicio, QPointF(inicio.x() + LONGITUD_FLECHA_INICIAL / 2 - 6, inicio.y() - 12))

    def limpiar_resaltado(self) -> None:
        for estado_grafico in self.estados_graficos.values():
            estado_grafico.aplicar_estilo_normal()
        for transicion_grafica in self.transiciones_graficas.values():
            transicion_grafica.aplicar_estilo_normal()

    def mostrar_estado_simulacion(
        self,
        estado_actual: str,
        estados_visitados: set[str],
        ultimo_paso: PasoSimulacion | None,
        resultado_final: bool | None,
    ) -> None:
        self.limpiar_resaltado()

        for estado_visitado in estados_visitados:
            self.estados_graficos[estado_visitado].aplicar_estilo(
                estilos.COLOR_ESTADO_VISITADO, estilos.COLOR_LINEA_NORMAL, GROSOR_BORDE_ESTADO_NORMAL
            )

        if ultimo_paso is not None and ultimo_paso.estado_destino is not None:
            par_estados_ultimo_paso = (ultimo_paso.estado_origen, ultimo_paso.estado_destino)
            self.transiciones_graficas[par_estados_ultimo_paso].aplicar_estilo(
                estilos.COLOR_TRANSICION_ACTIVA, GROSOR_TRANSICION_ACTIVA
            )

        if resultado_final is None:
            color_estado_actual = estilos.COLOR_ESTADO_ACTUAL
        elif resultado_final:
            color_estado_actual = estilos.COLOR_ESTADO_FINAL_ACEPTADO
        else:
            color_estado_actual = estilos.COLOR_ESTADO_FINAL_RECHAZADO
        self.estados_graficos[estado_actual].aplicar_estilo(
            color_estado_actual, estilos.COLOR_BORDE_ESTADO_ACTUAL, GROSOR_BORDE_ESTADO_ACTUAL
        )

    def ajustar_vista_al_contenido(self) -> None:
        if not self.escena.items():
            return
        rectangulo_contenido = self.escena.itemsBoundingRect().adjusted(
            -MARGEN_VISTA, -MARGEN_VISTA, MARGEN_VISTA, MARGEN_VISTA
        )
        self.escena.setSceneRect(rectangulo_contenido)
        self.fitInView(rectangulo_contenido, Qt.KeepAspectRatio)
        if self.transform().m11() > ESCALA_MAXIMA_VISTA:
            self.resetTransform()
            self.scale(ESCALA_MAXIMA_VISTA, ESCALA_MAXIMA_VISTA)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.ajustar_vista_al_contenido()
