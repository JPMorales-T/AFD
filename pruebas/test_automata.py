import os
import tempfile
import unittest

from afd.automata import AutomataFinitoDeterminista, ErrorDefinicionAutomata

CARPETA_EJEMPLOS = os.path.join(os.path.dirname(__file__), "..", "ejemplos")

DEFINICION_DEL_ENUNCIADO = """Simbolos: 0,1
Estados: Q0,Q1,Q2,Q3
Estado inicial: Q0
Estados de aceptación: Q0
Transiciones:
Q2,Q1
Q3,Q0
Q0,Q3
Q1,Q2
Cadenas a analizar:
1,0,0,1
0,0,1,0,1
"""


def cargar_ejemplo(nombre_archivo):
    return AutomataFinitoDeterminista.crear_desde_archivo(
        os.path.join(CARPETA_EJEMPLOS, nombre_archivo)
    )


def automata_acepta(automata, texto_cadena):
    simbolos_cadena = AutomataFinitoDeterminista.separar_simbolos_cadena(texto_cadena)
    return automata.simular_cadena(simbolos_cadena).fue_aceptada


class PruebasLecturaArchivo(unittest.TestCase):
    def test_lee_archivo_del_enunciado(self):
        automata = AutomataFinitoDeterminista.crear_desde_texto(DEFINICION_DEL_ENUNCIADO)
        self.assertEqual(automata.simbolos, ["0", "1"])
        self.assertEqual(automata.estados, ["Q0", "Q1", "Q2", "Q3"])
        self.assertEqual(automata.estado_inicial, "Q0")
        self.assertEqual(automata.estados_aceptacion, {"Q0"})
        self.assertEqual(automata.obtener_estado_destino("Q0", "0"), "Q2")
        self.assertEqual(automata.obtener_estado_destino("Q0", "1"), "Q1")
        self.assertEqual(automata.obtener_estado_destino("Q3", "1"), "Q2")
        self.assertEqual(len(automata.cadenas_a_analizar), 2)

    def test_acepta_encabezados_sin_tildes(self):
        texto_sin_tildes = DEFINICION_DEL_ENUNCIADO.replace("aceptación", "aceptacion")
        automata = AutomataFinitoDeterminista.crear_desde_texto(texto_sin_tildes)
        self.assertEqual(automata.estados_aceptacion, {"Q0"})

    def test_lee_archivos_ansi_y_utf16(self):
        texto_con_mayusculas_acentuadas = DEFINICION_DEL_ENUNCIADO.replace("Simbolos", "SÍMBOLOS")
        for codificacion in ("cp1252", "utf-16", "utf-8", "utf-8-sig"):
            with self.subTest(codificacion=codificacion):
                with tempfile.TemporaryDirectory() as carpeta_temporal:
                    ruta_archivo = os.path.join(carpeta_temporal, "automata.txt")
                    with open(ruta_archivo, "w", encoding=codificacion) as archivo:
                        archivo.write(texto_con_mayusculas_acentuadas)
                    automata = AutomataFinitoDeterminista.crear_desde_archivo(ruta_archivo)
                self.assertEqual(automata.estados_aceptacion, {"Q0"})
                self.assertEqual(automata.simbolos, ["0", "1"])

    def test_guardar_y_volver_a_leer_conserva_transiciones(self):
        automata_original = AutomataFinitoDeterminista.crear_desde_texto(DEFINICION_DEL_ENUNCIADO)
        automata_releido = AutomataFinitoDeterminista.crear_desde_texto(
            automata_original.convertir_a_texto()
        )
        self.assertEqual(automata_releido.tabla_transiciones, automata_original.tabla_transiciones)

    def test_detecta_definiciones_invalidas(self):
        definiciones_invalidas = {
            "estado inicial inexistente": DEFINICION_DEL_ENUNCIADO.replace(
                "Estado inicial: Q0", "Estado inicial: Q9"
            ),
            "falta una fila de transiciones": DEFINICION_DEL_ENUNCIADO.replace("Q1,Q2\n", ""),
            "fila de transiciones incompleta": DEFINICION_DEL_ENUNCIADO.replace("Q3,Q0", "Q3"),
            "estado destino inexistente": DEFINICION_DEL_ENUNCIADO.replace("Q0,Q3", "Q0,Q7"),
            "falta la sección de símbolos": DEFINICION_DEL_ENUNCIADO.replace("Simbolos: 0,1\n", ""),
        }
        for descripcion_caso, definicion in definiciones_invalidas.items():
            with self.subTest(descripcion_caso), self.assertRaises(ErrorDefinicionAutomata):
                AutomataFinitoDeterminista.crear_desde_texto(definicion)


class PruebasSimulacion(unittest.TestCase):
    def test_cadenas_del_enunciado(self):
        automata = AutomataFinitoDeterminista.crear_desde_texto(DEFINICION_DEL_ENUNCIADO)
        resultado_primera_cadena = automata.simular_cadena(automata.cadenas_a_analizar[0])
        self.assertTrue(resultado_primera_cadena.fue_aceptada)
        self.assertEqual(
            resultado_primera_cadena.obtener_estados_recorridos(), ["Q0", "Q1", "Q3", "Q1", "Q0"]
        )
        self.assertFalse(automata.simular_cadena(automata.cadenas_a_analizar[1]).fue_aceptada)

    def test_rechaza_simbolo_fuera_del_alfabeto(self):
        automata = AutomataFinitoDeterminista.crear_desde_texto(DEFINICION_DEL_ENUNCIADO)
        resultado = automata.simular_cadena(["1", "2"])
        self.assertFalse(resultado.fue_aceptada)
        self.assertIsNotNone(resultado.mensaje_error)

    def test_palabra_vacia_se_acepta_si_inicial_es_de_aceptacion(self):
        automata = AutomataFinitoDeterminista.crear_desde_texto(DEFINICION_DEL_ENUNCIADO)
        self.assertTrue(automata.simular_cadena([]).fue_aceptada)

    def test_ejemplo1_cantidad_par_de_ceros_y_unos(self):
        automata = cargar_ejemplo("ejemplo1_pares.txt")
        for cadena_aceptada in ["1,0,0,1", "1,1,0,0", "1,1"]:
            self.assertTrue(automata_acepta(automata, cadena_aceptada), cadena_aceptada)
        for cadena_rechazada in ["0,0,1,0,1", "0,1,0"]:
            self.assertFalse(automata_acepta(automata, cadena_rechazada), cadena_rechazada)

    def test_ejemplo2_cadenas_que_terminan_en_ab(self):
        automata = cargar_ejemplo("ejemplo2_termina_ab.txt")
        for cadena_aceptada in ["a,b", "b,a,a,b", "a,a,b,a,b"]:
            self.assertTrue(automata_acepta(automata, cadena_aceptada), cadena_aceptada)
        for cadena_rechazada in ["a,b,a", "b,b,b"]:
            self.assertFalse(automata_acepta(automata, cadena_rechazada), cadena_rechazada)

    def test_ejemplo3_binarios_divisibles_entre_tres(self):
        automata = cargar_ejemplo("ejemplo3_divisible3.txt")
        for numero in range(64):
            cadena_binaria = ",".join(bin(numero)[2:])
            self.assertEqual(automata_acepta(automata, cadena_binaria), numero % 3 == 0, cadena_binaria)


if __name__ == "__main__":
    unittest.main()
