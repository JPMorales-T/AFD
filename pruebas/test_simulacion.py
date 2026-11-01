import unittest

from afd.automata import AutomataFinitoDeterminista
from afd.simulacion import SimulacionPasoAPaso
from pruebas.test_automata import DEFINICION_DEL_ENUNCIADO


def crear_simulacion(texto_cadena):
    automata = AutomataFinitoDeterminista.crear_desde_texto(DEFINICION_DEL_ENUNCIADO)
    return SimulacionPasoAPaso(automata, automata.interpretar_cadena_ingresada(texto_cadena))


class PruebasSimulacionPasoAPaso(unittest.TestCase):
    def test_avanza_por_los_estados_correctos(self):
        simulacion = crear_simulacion("1,0,0,1")
        estados_observados = [simulacion.obtener_estado_actual()]
        while simulacion.avanzar_un_paso():
            estados_observados.append(simulacion.obtener_estado_actual())
        self.assertEqual(estados_observados, ["Q0", "Q1", "Q3", "Q1", "Q0"])
        self.assertTrue(simulacion.esta_terminada())
        self.assertTrue(simulacion.obtener_resultado_final())

    def test_resultado_final_solo_se_conoce_al_terminar(self):
        simulacion = crear_simulacion("0,0,1,0,1")
        simulacion.avanzar_un_paso()
        self.assertIsNone(simulacion.obtener_resultado_final())
        simulacion.ejecutar_hasta_el_final()
        self.assertFalse(simulacion.obtener_resultado_final())

    def test_retroceder_y_reiniciar(self):
        simulacion = crear_simulacion("1,0,0,1")
        simulacion.avanzar_un_paso()
        simulacion.avanzar_un_paso()
        self.assertEqual(simulacion.obtener_estado_actual(), "Q3")
        simulacion.retroceder_un_paso()
        self.assertEqual(simulacion.obtener_estado_actual(), "Q1")
        simulacion.reiniciar()
        self.assertTrue(simulacion.esta_al_inicio())
        self.assertFalse(simulacion.retroceder_un_paso())
        self.assertIsNone(simulacion.obtener_ultimo_paso())

    def test_estados_visitados(self):
        simulacion = crear_simulacion("1,0")
        simulacion.ejecutar_hasta_el_final()
        self.assertEqual(simulacion.obtener_estados_visitados(), {"Q0", "Q1", "Q3"})

    def test_simbolo_invalido_detiene_el_automata(self):
        simulacion = crear_simulacion("1,5,0")
        simulacion.ejecutar_hasta_el_final()
        self.assertEqual(simulacion.obtener_total_pasos(), 2)
        self.assertEqual(simulacion.obtener_estado_actual(), "Q1")
        self.assertFalse(simulacion.obtener_resultado_final())

    def test_cadena_ingresada_sin_comas(self):
        simulacion = crear_simulacion("1001")
        self.assertEqual(simulacion.simbolos_cadena, ["1", "0", "0", "1"])


if __name__ == "__main__":
    unittest.main()
