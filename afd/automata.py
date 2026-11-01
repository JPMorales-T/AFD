from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field


ENCABEZADOS_RECONOCIDOS = {
    "simbolos": "simbolos",
    "estados": "estados",
    "estado inicial": "estado_inicial",
    "estados de aceptacion": "estados_aceptacion",
    "estados finales": "estados_aceptacion",
    "transiciones": "transiciones",
    "cadenas a analizar": "cadenas",
    "cadenas": "cadenas",
}

SECCIONES_OBLIGATORIAS = {
    "simbolos": "Simbolos",
    "estados": "Estados",
    "estado_inicial": "Estado inicial",
    "estados_aceptacion": "Estados de aceptación",
    "transiciones": "Transiciones",
}

REPRESENTACIONES_PALABRA_VACIA = ("", "ε", "λ")


class ErrorDefinicionAutomata(Exception):
    pass


def normalizar_texto(texto: str) -> str:
    texto_descompuesto = unicodedata.normalize("NFD", texto)
    texto_sin_tildes = "".join(
        caracter for caracter in texto_descompuesto if unicodedata.category(caracter) != "Mn"
    )
    return " ".join(texto_sin_tildes.lower().split())


def separar_por_comas(texto: str) -> list[str]:
    return [elemento.strip() for elemento in texto.split(",") if elemento.strip()]


def leer_texto_de_archivo(ruta_archivo: str) -> str:
    with open(ruta_archivo, "rb") as archivo:
        contenido_en_bytes = archivo.read()

    if contenido_en_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
        codificaciones_a_probar = ["utf-16"]
    else:
        codificaciones_a_probar = ["utf-8-sig", "cp1252", "latin-1"]

    for codificacion in codificaciones_a_probar:
        try:
            return contenido_en_bytes.decode(codificacion)
        except UnicodeDecodeError:
            continue
    raise ErrorDefinicionAutomata(
        "No se pudo leer el archivo: su codificación no es reconocida. Guárdelo como texto UTF-8."
    )


def buscar_elementos_repetidos(elementos: list[str]) -> set[str]:
    return {elemento for elemento in elementos if elementos.count(elemento) > 1}


@dataclass
class PasoSimulacion:
    posicion_simbolo: int
    estado_origen: str
    simbolo_leido: str
    estado_destino: str | None


@dataclass
class ResultadoSimulacion:
    simbolos_cadena: list[str]
    pasos: list[PasoSimulacion]
    fue_aceptada: bool
    mensaje_error: str | None = None

    def obtener_estados_recorridos(self) -> list[str]:
        if not self.pasos:
            return []
        estados_recorridos = [self.pasos[0].estado_origen]
        estados_recorridos += [
            paso.estado_destino for paso in self.pasos if paso.estado_destino is not None
        ]
        return estados_recorridos


@dataclass
class AutomataFinitoDeterminista:
    simbolos: list[str]
    estados: list[str]
    estado_inicial: str
    estados_aceptacion: set[str]
    tabla_transiciones: dict[tuple[str, str], str]
    cadenas_a_analizar: list[list[str]] = field(default_factory=list)

    @classmethod
    def crear_desde_archivo(cls, ruta_archivo: str) -> "AutomataFinitoDeterminista":
        return cls.crear_desde_texto(leer_texto_de_archivo(ruta_archivo))

    @classmethod
    def crear_desde_texto(cls, texto_definicion: str) -> "AutomataFinitoDeterminista":
        lineas_por_seccion = cls.agrupar_lineas_por_seccion(texto_definicion)
        cls.validar_secciones_obligatorias(lineas_por_seccion)

        simbolos = separar_por_comas(",".join(lineas_por_seccion["simbolos"]))
        estados = separar_por_comas(",".join(lineas_por_seccion["estados"]))
        estados_iniciales = separar_por_comas(",".join(lineas_por_seccion["estado_inicial"]))
        estados_aceptacion = separar_por_comas(",".join(lineas_por_seccion["estados_aceptacion"]))

        cls.validar_simbolos_y_estados(simbolos, estados, estados_iniciales, estados_aceptacion)
        tabla_transiciones = cls.construir_tabla_transiciones(
            simbolos, estados, lineas_por_seccion["transiciones"]
        )
        cadenas_a_analizar = [
            cls.separar_simbolos_cadena(linea_cadena)
            for linea_cadena in lineas_por_seccion.get("cadenas", [])
        ]

        return cls(
            simbolos=simbolos,
            estados=estados,
            estado_inicial=estados_iniciales[0],
            estados_aceptacion=set(estados_aceptacion),
            tabla_transiciones=tabla_transiciones,
            cadenas_a_analizar=cadenas_a_analizar,
        )

    @staticmethod
    def agrupar_lineas_por_seccion(texto_definicion: str) -> dict[str, list[str]]:
        lineas_por_seccion: dict[str, list[str]] = {}
        seccion_actual: str | None = None

        for numero_linea, linea in enumerate(texto_definicion.splitlines(), start=1):
            linea = linea.strip()
            if not linea:
                continue
            nombre_seccion, contenido_en_misma_linea = (
                AutomataFinitoDeterminista.identificar_encabezado(linea)
            )
            if nombre_seccion is not None:
                seccion_actual = nombre_seccion
                lineas_por_seccion.setdefault(seccion_actual, [])
                if contenido_en_misma_linea:
                    lineas_por_seccion[seccion_actual].append(contenido_en_misma_linea)
            elif seccion_actual is None:
                raise ErrorDefinicionAutomata(
                    f"Línea {numero_linea}: se esperaba un encabezado, se encontró '{linea}'."
                )
            else:
                lineas_por_seccion[seccion_actual].append(linea)

        return lineas_por_seccion

    @staticmethod
    def identificar_encabezado(linea: str) -> tuple[str | None, str]:
        if ":" not in linea:
            return None, ""
        texto_encabezado, contenido = linea.split(":", 1)
        nombre_seccion = ENCABEZADOS_RECONOCIDOS.get(normalizar_texto(texto_encabezado))
        return nombre_seccion, contenido.strip()

    @staticmethod
    def validar_secciones_obligatorias(lineas_por_seccion: dict[str, list[str]]) -> None:
        for nombre_interno, nombre_visible in SECCIONES_OBLIGATORIAS.items():
            if nombre_interno not in lineas_por_seccion:
                raise ErrorDefinicionAutomata(f"Falta la sección '{nombre_visible}:'.")

    @staticmethod
    def validar_simbolos_y_estados(
        simbolos: list[str],
        estados: list[str],
        estados_iniciales: list[str],
        estados_aceptacion: list[str],
    ) -> None:
        if not simbolos:
            raise ErrorDefinicionAutomata("No se definieron símbolos.")
        if not estados:
            raise ErrorDefinicionAutomata("No se definieron estados.")

        simbolos_repetidos = buscar_elementos_repetidos(simbolos)
        if simbolos_repetidos:
            raise ErrorDefinicionAutomata(
                f"Hay símbolos repetidos: {', '.join(sorted(simbolos_repetidos))}."
            )
        estados_repetidos = buscar_elementos_repetidos(estados)
        if estados_repetidos:
            raise ErrorDefinicionAutomata(
                f"Hay estados repetidos: {', '.join(sorted(estados_repetidos))}."
            )

        if len(estados_iniciales) != 1:
            raise ErrorDefinicionAutomata("Debe haber exactamente un estado inicial.")
        if estados_iniciales[0] not in estados:
            raise ErrorDefinicionAutomata(
                f"El estado inicial '{estados_iniciales[0]}' no está en la lista de estados."
            )
        for estado_aceptacion in estados_aceptacion:
            if estado_aceptacion not in estados:
                raise ErrorDefinicionAutomata(
                    f"El estado de aceptación '{estado_aceptacion}' no está en la lista de estados."
                )

    @staticmethod
    def construir_tabla_transiciones(
        simbolos: list[str], estados: list[str], filas_transiciones: list[str]
    ) -> dict[tuple[str, str], str]:
        if len(filas_transiciones) != len(estados):
            raise ErrorDefinicionAutomata(
                f"Se esperaban {len(estados)} filas de transiciones (una por estado) "
                f"y se encontraron {len(filas_transiciones)}."
            )

        tabla_transiciones: dict[tuple[str, str], str] = {}
        for estado_origen, fila_transiciones in zip(estados, filas_transiciones):
            estados_destino = separar_por_comas(fila_transiciones)
            if len(estados_destino) != len(simbolos):
                raise ErrorDefinicionAutomata(
                    f"La fila de transiciones de {estado_origen} ('{fila_transiciones}') debe tener "
                    f"{len(simbolos)} destinos, uno por símbolo."
                )
            for simbolo, estado_destino in zip(simbolos, estados_destino):
                if estado_destino not in estados:
                    raise ErrorDefinicionAutomata(
                        f"Transición δ({estado_origen}, {simbolo}) = '{estado_destino}': "
                        f"ese estado no existe."
                    )
                tabla_transiciones[(estado_origen, simbolo)] = estado_destino
        return tabla_transiciones

    @staticmethod
    def separar_simbolos_cadena(texto_cadena: str) -> list[str]:
        texto_cadena = texto_cadena.strip()
        if texto_cadena in REPRESENTACIONES_PALABRA_VACIA:
            return []
        return [simbolo.strip() for simbolo in texto_cadena.split(",")]

    @staticmethod
    def formatear_simbolos_cadena(simbolos_cadena: list[str]) -> str:
        return ",".join(simbolos_cadena) if simbolos_cadena else "ε"

    def interpretar_cadena_ingresada(self, texto_ingresado: str) -> list[str]:
        texto_ingresado = texto_ingresado.strip()
        if "," in texto_ingresado or texto_ingresado in REPRESENTACIONES_PALABRA_VACIA:
            return self.separar_simbolos_cadena(texto_ingresado)
        if texto_ingresado in self.simbolos:
            return [texto_ingresado]
        return list(texto_ingresado)

    def obtener_estado_destino(self, estado_origen: str, simbolo: str) -> str | None:
        return self.tabla_transiciones.get((estado_origen, simbolo))

    def es_estado_aceptacion(self, estado: str) -> bool:
        return estado in self.estados_aceptacion

    def simular_cadena(self, simbolos_cadena: list[str]) -> ResultadoSimulacion:
        estado_actual = self.estado_inicial
        pasos_realizados: list[PasoSimulacion] = []

        for posicion_simbolo, simbolo_leido in enumerate(simbolos_cadena):
            estado_siguiente = self.obtener_estado_destino(estado_actual, simbolo_leido)
            pasos_realizados.append(
                PasoSimulacion(posicion_simbolo, estado_actual, simbolo_leido, estado_siguiente)
            )
            if estado_siguiente is None:
                return ResultadoSimulacion(
                    simbolos_cadena,
                    pasos_realizados,
                    fue_aceptada=False,
                    mensaje_error=f"El símbolo '{simbolo_leido}' no pertenece al alfabeto.",
                )
            estado_actual = estado_siguiente

        return ResultadoSimulacion(
            simbolos_cadena, pasos_realizados, fue_aceptada=self.es_estado_aceptacion(estado_actual)
        )

    def convertir_a_texto(self) -> str:
        estados_aceptacion_ordenados = [
            estado for estado in self.estados if self.es_estado_aceptacion(estado)
        ]
        lineas_archivo = [
            "Simbolos: " + ",".join(self.simbolos),
            "Estados: " + ",".join(self.estados),
            "Estado inicial: " + self.estado_inicial,
            "Estados de aceptación: " + ",".join(estados_aceptacion_ordenados),
            "Transiciones:",
        ]
        for estado_origen in self.estados:
            estados_destino = [
                self.tabla_transiciones[(estado_origen, simbolo)] for simbolo in self.simbolos
            ]
            lineas_archivo.append(",".join(estados_destino))

        lineas_archivo.append("Cadenas a analizar:")
        for simbolos_cadena in self.cadenas_a_analizar:
            lineas_archivo.append(self.formatear_simbolos_cadena(simbolos_cadena))
        return "\n".join(lineas_archivo) + "\n"
