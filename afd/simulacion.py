from __future__ import annotations

from afd.automata import AutomataFinitoDeterminista, PasoSimulacion


class SimulacionPasoAPaso:
    def __init__(self, automata: AutomataFinitoDeterminista, simbolos_cadena: list[str]):
        self.automata = automata
        self.simbolos_cadena = simbolos_cadena
        self.resultado_completo = automata.simular_cadena(simbolos_cadena)
        self.cantidad_pasos_ejecutados = 0

    def avanzar_un_paso(self) -> bool:
        if self.esta_terminada():
            return False
        self.cantidad_pasos_ejecutados += 1
        return True

    def retroceder_un_paso(self) -> bool:
        if self.cantidad_pasos_ejecutados == 0:
            return False
        self.cantidad_pasos_ejecutados -= 1
        return True

    def reiniciar(self) -> None:
        self.cantidad_pasos_ejecutados = 0

    def ejecutar_hasta_el_final(self) -> None:
        self.cantidad_pasos_ejecutados = self.obtener_total_pasos()

    def obtener_total_pasos(self) -> int:
        return len(self.resultado_completo.pasos)

    def esta_terminada(self) -> bool:
        return self.cantidad_pasos_ejecutados == self.obtener_total_pasos()

    def esta_al_inicio(self) -> bool:
        return self.cantidad_pasos_ejecutados == 0

    def obtener_pasos_ejecutados(self) -> list[PasoSimulacion]:
        return self.resultado_completo.pasos[: self.cantidad_pasos_ejecutados]

    def obtener_ultimo_paso(self) -> PasoSimulacion | None:
        if self.cantidad_pasos_ejecutados == 0:
            return None
        return self.resultado_completo.pasos[self.cantidad_pasos_ejecutados - 1]

    def obtener_estado_actual(self) -> str:
        ultimo_paso = self.obtener_ultimo_paso()
        if ultimo_paso is None:
            return self.automata.estado_inicial
        if ultimo_paso.estado_destino is None:
            return ultimo_paso.estado_origen
        return ultimo_paso.estado_destino

    def obtener_estados_visitados(self) -> set[str]:
        estados_visitados = {self.automata.estado_inicial}
        for paso in self.obtener_pasos_ejecutados():
            if paso.estado_destino is not None:
                estados_visitados.add(paso.estado_destino)
        return estados_visitados

    def obtener_resultado_final(self) -> bool | None:
        if not self.esta_terminada():
            return None
        return self.resultado_completo.fue_aceptada
