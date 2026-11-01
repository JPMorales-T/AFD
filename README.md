# Simulador de Autómatas Finitos Deterministas (AFD)

Aplicación de escritorio para Windows que simula un AFD paso a paso. Lee la definición del autómata desde un archivo de texto, dibuja su diagrama y su tabla de transiciones, y muestra el recorrido de cada cadena hasta indicar si es aceptada o rechazada.

Proyecto del curso **Autómatas y Lenguajes Formales**, sección A, de la carrera de Ingeniería en Sistemas de Información y Ciencias de la Computación, Universidad Mariano Gálvez de Guatemala.

## Funciones

- Carga de autómatas desde archivos `.txt` en UTF-8, UTF-16 o ANSI, con validación y mensajes de error.
- Diagrama y tabla de transiciones que resaltan el estado y la transición de cada paso.
- Tabla de cadenas con su resultado: aceptada o rechazada.
- Controles para reiniciar, retroceder, avanzar, ir al final y reproducir automáticamente con velocidad ajustable.
- Editor integrado para crear o modificar autómatas, con validación mientras se escribe.
- Tres ejemplos incluidos y manual de usuario en PDF.

## Ejecutar desde el código

Requiere Windows y Python. El proyecto se desarrolló y probó con Python 3.15.

```bat
git clone https://github.com/JPMorales-T/AFD.git
cd AFD
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python principal.py
```

## Formato del archivo de entrada

```text
Simbolos: 0,1
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
```

En `Transiciones` va una fila por estado, en el mismo orden de `Estados`, y una columna por símbolo, en el mismo orden de `Simbolos`. En este ejemplo, desde `Q0` se pasa a `Q2` con `0` y a `Q1` con `1`.

Hay más ejemplos en la carpeta [ejemplos](ejemplos).

## Pruebas

```bat
python -m unittest discover -s pruebas -t .
```

## Generar el instalador

Además de lo necesario para ejecutar desde el código, requiere PyInstaller e Inno Setup 6:

```bat
pip install pyinstaller
winget install JRSoftware.InnoSetup
construir_instalador.bat
```

El resultado es `salida_instalador\Instalador_SimuladorAFD.exe`. Quien lo instale no necesita tener Python.

## Estructura

| Carpeta o archivo | Contenido |
|---|---|
| `principal.py` | Punto de entrada de la aplicación |
| `afd/` | Lógica del autómata y de la simulación, sin interfaz gráfica |
| `interfaz/` | Ventanas, diagrama, tablas y controles (PySide6) |
| `pruebas/` | Pruebas automáticas de la lógica |
| `ejemplos/` | Autómatas de ejemplo |
| `recursos/` | Icono de la aplicación |
| `documentacion/` | Manual de usuario en PDF y su generador |
| `instalador/` | Configuración de PyInstaller e Inno Setup |

## Integrantes

| Nombre | Carné |
|---|---|
| José Eduardo Pineda Morales | 1890-24-19328 |
| Diego Alessandro Colindres Márquez | 1890-24-22584 |
| Oliver Eduardo Garcia Ramos | 1890-24-22693 |
| Luis Angel Elias Lima | 1890-24-16963 |
| Esmeralda Nataly Véliz Urbina | 1890-24-22807 |
| Joseph Raul Sánchez Portillo | 1890-24-20912 |
