import html
import os
import sys

CARPETA_DOCUMENTACION = os.path.dirname(os.path.abspath(__file__))
CARPETA_PROYECTO = os.path.dirname(CARPETA_DOCUMENTACION)
sys.path.insert(0, CARPETA_PROYECTO)

from PySide6.QtCore import QMarginsF, Qt, QUrl
from PySide6.QtGui import QImage, QPageLayout, QPageSize, QPdfWriter, QTextDocument
from PySide6.QtWidgets import QApplication, QWidget

from interfaz import datos_proyecto
from interfaz.contenido_ayuda import EXPLICACION_FORMATO_ARCHIVO_HTML
from interfaz.dialogo_acerca_de import DialogoAcercaDe
from interfaz.editor_definicion import PLANTILLA_NUEVO_AUTOMATA
from interfaz.ventana_principal import EJEMPLOS_INCLUIDOS, VentanaPrincipal
from principal import cargar_traduccion_espanol

CARPETA_CAPTURAS = os.path.join(CARPETA_DOCUMENTACION, "capturas")
RUTA_MANUAL_PDF = os.path.join(CARPETA_DOCUMENTACION, "Manual_de_usuario.pdf")
ANCHO_IMAGEN_COMPLETA = 520
ANCHO_IMAGEN_MEDIANA = 380
RESOLUCION_PDF_DPI = 300


def guardar_captura(componente: QWidget, nombre_captura: str) -> str:
    QApplication.processEvents()
    ruta_captura = os.path.join(CARPETA_CAPTURAS, nombre_captura)
    componente.grab().save(ruta_captura)
    return ruta_captura


def tomar_capturas() -> None:
    os.makedirs(CARPETA_CAPTURAS, exist_ok=True)
    ventana = VentanaPrincipal()
    ventana.resize(1300, 820)
    ventana.show()

    ventana.cargar_ejemplo(*EJEMPLOS_INCLUIDOS[0])
    guardar_captura(ventana, "ventana_inicio.png")

    ventana.avanzar_un_paso()
    ventana.avanzar_un_paso()
    guardar_captura(ventana, "ventana_paso_a_paso.png")
    guardar_captura(ventana.diagrama_automata, "diagrama_paso.png")
    guardar_captura(ventana.tabla_transiciones, "tabla_transiciones_paso.png")
    guardar_captura(ventana.controles_simulacion, "controles_simulacion.png")

    ventana.procesar_todas_las_cadenas()
    ventana.seleccionar_cadena(1)
    ventana.ir_al_final_de_la_cadena()
    guardar_captura(ventana, "ventana_rechazada.png")
    guardar_captura(ventana.panel_cadenas, "tabla_cadenas.png")

    ventana.cargar_ejemplo(*EJEMPLOS_INCLUIDOS[1])
    ventana.ir_al_final_de_la_cadena()
    guardar_captura(ventana.diagrama_automata, "diagrama_aceptada.png")

    ventana.crear_nuevo_automata()
    editor = ventana.editor_definicion
    editor.campo_texto.setPlainText(PLANTILLA_NUEVO_AUTOMATA.replace("Q1,Q0", "Q1,Q9"))
    editor.validar_definicion()
    guardar_captura(editor, "editor_con_error.png")
    editor.campo_texto.setPlainText(PLANTILLA_NUEVO_AUTOMATA)
    editor.validar_definicion()
    guardar_captura(editor, "editor_valido.png")
    editor.campo_texto.document().setModified(False)
    editor.reject()

    dialogo_acerca_de = DialogoAcercaDe(ventana)
    dialogo_acerca_de.show()
    guardar_captura(dialogo_acerca_de, "acerca_de.png")
    dialogo_acerca_de.close()
    ventana.close()


def imagen_html(nombre_captura: str, ancho: int, pie_de_imagen: str) -> str:
    return (
        f"<p align='center'><img src='{nombre_captura}' width='{ancho}'><br>"
        f"<i style='color:#555555'>{html.escape(pie_de_imagen)}</i></p>"
    )


def salto_de_pagina() -> str:
    return "<div style='page-break-before: always'></div>"


def construir_portada_html() -> str:
    filas_integrantes = "".join(
        f"<tr><td align='center'>{numero}</td><td>{html.escape(nombre)}</td><td>{html.escape(carne)}</td></tr>"
        for numero, (nombre, carne) in enumerate(datos_proyecto.INTEGRANTES_GRUPO, start=1)
    )
    linea_catedratico = (
        f"<br>Catedrático: {html.escape(datos_proyecto.NOMBRE_CATEDRATICO)}"
        if datos_proyecto.NOMBRE_CATEDRATICO.strip()
        else ""
    )
    return f"""
    <p align='center' style='font-size:15pt'>{html.escape(datos_proyecto.NOMBRE_UNIVERSIDAD)}<br>
    {html.escape(datos_proyecto.NOMBRE_FACULTAD)}<br>{html.escape(datos_proyecto.NOMBRE_CARRERA)}</p>
    <p align='center'>{html.escape(datos_proyecto.NOMBRE_CURSO)} — Sección {html.escape(datos_proyecto.SECCION_CURSO)}{linea_catedratico}</p>
    <br><br>
    <p align='center'><img src='icono.png' width='110'></p>
    <h1 align='center' style='font-size:26pt'>Manual de usuario</h1>
    <h2 align='center'>{html.escape(datos_proyecto.NOMBRE_APLICACION)}</h2>
    <p align='center'>Versión {html.escape(datos_proyecto.VERSION_APLICACION)}</p>
    <br>
    <table align='center' border='1' cellspacing='0' cellpadding='5' width='75%'>
      <tr style='background:#DCEBFA'><th>No.</th><th>Nombre</th><th>Carné</th></tr>
      {filas_integrantes}
    </table>
    <br>
    <p align='center'>{html.escape(datos_proyecto.FECHA_ENTREGA)}</p>
    """


def construir_contenido_html() -> str:
    return f"""
    <html><body style='font-family:"Segoe UI"; font-size:11pt'>
    {construir_portada_html()}
    {salto_de_pagina()}

    <h2>Contenido</h2>
    <ol>
      <li>Introducción</li>
      <li>Instalación y desinstalación</li>
      <li>La ventana principal</li>
      <li>Menú Archivo</li>
      <li>Menú Ejemplos</li>
      <li>Formato del archivo de entrada</li>
      <li>Simulación paso a paso</li>
      <li>Tabla de cadenas y resultados</li>
      <li>Significado de los colores</li>
      <li>Menú Acerca de</li>
      <li>Mensajes de error frecuentes</li>
    </ol>

    <h2>1. Introducción</h2>
    <p>El <b>{html.escape(datos_proyecto.NOMBRE_APLICACION)}</b> permite definir un Autómata Finito
    Determinista (AFD) en un archivo de texto y observar, símbolo por símbolo, cómo procesa cada cadena:
    por qué estados pasa, qué transición utiliza en cada paso y si la cadena es aceptada o rechazada.</p>
    <p>Un AFD se define por un conjunto de <b>símbolos</b> (alfabeto), un conjunto de <b>estados</b>,
    un <b>estado inicial</b>, un conjunto de <b>estados de aceptación</b> y una <b>función de transición</b>
    δ(estado, símbolo) = estado siguiente. Una cadena es aceptada si, después de leer todos sus símbolos
    desde el estado inicial, el autómata termina en un estado de aceptación.</p>

    <h2>2. Instalación y desinstalación</h2>
    <h3>Requisitos</h3>
    <ul><li>Windows 10 u 11 de 64 bits.</li>
        <li>No requiere instalar Python, Java ni Graphviz: todo va incluido en el instalador.</li></ul>
    <h3>Instalación</h3>
    <ol>
      <li>Ejecute <b>Instalador_SimuladorAFD.exe</b>.</li>
      <li>Elija la carpeta de instalación (o deje la sugerida) y presione <i>Siguiente</i>.</li>
      <li>Opcionalmente marque <i>Crear un acceso directo en el escritorio</i>.</li>
      <li>Presione <i>Instalar</i> y luego <i>Finalizar</i>. La aplicación puede abrirse al terminar.</li>
    </ol>
    <p>El programa queda disponible en el menú Inicio como <b>Simulador AFD</b>, junto con este manual
    y la carpeta de ejemplos.</p>
    <h3>Desinstalación</h3>
    <p>Desde <i>Configuración → Aplicaciones → Aplicaciones instaladas</i>, busque <b>Simulador AFD</b>
    y elija <i>Desinstalar</i>, o use el acceso <i>Desinstalar Simulador AFD</i> del menú Inicio.</p>

    {salto_de_pagina()}
    <h2>3. La ventana principal</h2>
    {imagen_html("ventana_paso_a_paso.png", ANCHO_IMAGEN_COMPLETA, "Figura 1. Ventana principal durante la simulación de la cadena 1,0,0,1")}
    <p>La ventana se divide en cinco zonas:</p>
    <table border='1' cellspacing='0' cellpadding='5' width='100%'>
      <tr style='background:#DCEBFA'><th>Zona</th><th>Descripción</th></tr>
      <tr><td><b>Diagrama del AFD</b><br>(izquierda)</td><td>Dibujo del autómata. La flecha <i>inicio</i> señala
        el estado inicial y el doble círculo los estados de aceptación. Las flechas muestran las transiciones con
        los símbolos que las producen. Durante la simulación se resaltan el estado actual y la última transición.</td></tr>
      <tr><td><b>Tabla de transiciones</b><br>(arriba a la derecha)</td><td>Filas = estados, columnas = símbolos,
        cada celda = estado destino. El estado inicial se marca con <b>→</b> y los de aceptación con <b>*</b>.</td></tr>
      <tr><td><b>Cadenas a analizar</b></td><td>Lista de cadenas del archivo con su recorrido y resultado.
        Al hacer clic en una cadena se prepara su simulación.</td></tr>
      <tr><td><b>Recorrido paso a paso</b></td><td>Historial de las transiciones aplicadas a la cadena actual.</td></tr>
      <tr><td><b>Simulación paso a paso</b><br>(abajo)</td><td>Cadena actual, estado actual y botones para
        controlar la simulación.</td></tr>
    </table>
    <p>Los separadores entre zonas pueden arrastrarse con el ratón para cambiar su tamaño.</p>

    <h2>4. Menú Archivo</h2>
    <table border='1' cellspacing='0' cellpadding='5' width='100%'>
      <tr style='background:#DCEBFA'><th>Opción</th><th>Atajo</th><th>Descripción</th></tr>
      <tr><td>Nuevo</td><td>Ctrl+N</td><td>Abre el editor con una plantilla para definir un AFD nuevo.</td></tr>
      <tr><td>Abrir</td><td>Ctrl+O</td><td>Abre el explorador de archivos para cargar una definición (.txt).</td></tr>
      <tr><td>Editar autómata actual</td><td>Ctrl+E</td><td>Abre en el editor el autómata que se está simulando.</td></tr>
      <tr><td>Guardar</td><td>Ctrl+S</td><td>Si el editor está abierto guarda su contenido; si no, guarda el autómata
        actual junto con las cadenas agregadas. Si aún no tiene archivo, pregunta dónde guardarlo.</td></tr>
      <tr><td>Guardar como</td><td>Ctrl+Shift+S</td><td>Guarda en un archivo nuevo.</td></tr>
      <tr><td>Salir</td><td>Ctrl+Q</td><td>Cierra la aplicación (pregunta si hay cambios sin guardar en el editor).</td></tr>
    </table>
    <h3>El editor de definiciones</h3>
    <p>El editor muestra a la izquierda el texto de la definición y a la derecha una explicación del formato.
    Mientras se escribe, la parte inferior indica si la definición es válida o cuál es el error.
    El botón <b>Cargar en el simulador</b> (habilitado solo cuando la definición es válida) muestra el
    autómata en la ventana principal.</p>
    {imagen_html("editor_valido.png", ANCHO_IMAGEN_MEDIANA, "Figura 2. Editor con una definición válida")}
    {imagen_html("editor_con_error.png", ANCHO_IMAGEN_MEDIANA, "Figura 3. El editor señala el error: el estado Q9 no existe")}

    <h2>5. Menú Ejemplos</h2>
    <p>Carga directamente uno de los autómatas incluidos, sin necesidad de buscar un archivo:</p>
    <table border='1' cellspacing='0' cellpadding='5' width='100%'>
      <tr style='background:#DCEBFA'><th>Ejemplo</th><th>Lenguaje que reconoce</th></tr>
      <tr><td>1. Cantidad par de 0s y de 1s</td><td>Cadenas sobre {{0, 1}} con un número par de ceros y un número
        par de unos (es el ejemplo del enunciado del proyecto).</td></tr>
      <tr><td>2. Terminan en «ab»</td><td>Cadenas sobre {{a, b}} cuyos dos últimos símbolos son <i>a</i> y <i>b</i>.</td></tr>
      <tr><td>3. Binarios divisibles entre 3</td><td>Números escritos en binario cuyo valor es múltiplo de 3.
        Cada estado R0, R1, R2 representa el residuo de la división entre 3.</td></tr>
    </table>
    <p>Para guardar una copia modificada de un ejemplo use <i>Archivo → Guardar como</i>.</p>

    <h2>6. Formato del archivo de entrada</h2>
    {EXPLICACION_FORMATO_ARCHIVO_HTML}
    <p>Los encabezados pueden escribirse con o sin tilde (<i>aceptación</i> / <i>aceptacion</i>) y se ignoran
    las líneas en blanco.</p>

    {salto_de_pagina()}
    <h2>7. Simulación paso a paso</h2>
    <ol>
      <li>Seleccione una cadena en la tabla <b>Cadenas a analizar</b>. El autómata se coloca en el estado inicial.</li>
      <li>Use los controles de la parte inferior:</li>
    </ol>
    {imagen_html("controles_simulacion.png", ANCHO_IMAGEN_COMPLETA, "Figura 4. Controles de simulación")}
    <table border='1' cellspacing='0' cellpadding='5' width='100%'>
      <tr style='background:#DCEBFA'><th>Botón</th><th>Acción</th></tr>
      <tr><td>Reiniciar</td><td>Vuelve al estado inicial, sin símbolos leídos.</td></tr>
      <tr><td>Paso anterior</td><td>Deshace la lectura del último símbolo.</td></tr>
      <tr><td>Paso siguiente</td><td>Lee el siguiente símbolo y aplica la transición correspondiente.</td></tr>
      <tr><td>Ir al final</td><td>Lee todos los símbolos restantes de una vez.</td></tr>
      <tr><td>Reproducir / Pausar</td><td>Avanza automáticamente un paso a la vez. La barra
        <i>Lento — Rápido</i> ajusta la velocidad.</td></tr>
    </table>
    <p>Sobre los botones se muestra la cadena: los símbolos ya leídos en gris, el <b>símbolo recién leído
    resaltado</b> y los pendientes en negro. Debajo se indica el número de paso, el estado actual y la
    transición aplicada, por ejemplo <i>δ(Q1, 0) = Q3</i>.</p>
    <p>En cada paso, el <b>diagrama</b> y la <b>tabla de transiciones</b> se actualizan:</p>
    {imagen_html("diagrama_paso.png", ANCHO_IMAGEN_MEDIANA, "Figura 5. Diagrama tras leer 1 y 0: el autómata pasó de Q1 a Q3")}
    {imagen_html("tabla_transiciones_paso.png", ANCHO_IMAGEN_MEDIANA, "Figura 6. Tabla: en rojo la celda δ(Q1,0) usada; en amarillo la fila del estado actual Q3")}

    <h2>8. Tabla de cadenas y resultados</h2>
    <p>Cuando una cadena termina de leerse, su fila muestra el <b>recorrido de estados</b> y el resultado
    <span style='color:#1B5E20'><b>✔ Aceptada</b></span> o <span style='color:#B71C1C'><b>✘ Rechazada</b></span>.
    El botón <b>Procesar todas</b> calcula el resultado de todas las cadenas de una vez.</p>
    <p>Para analizar una cadena que no está en el archivo, escríbala en el campo inferior y presione
    <b>Agregar</b> (o Enter). Puede escribirse con comas (<i>1,0,1</i>) o, si los símbolos son de un
    solo carácter, sin ellas (<i>101</i>).</p>
    {imagen_html("tabla_cadenas.png", ANCHO_IMAGEN_COMPLETA * 0.8, "Figura 7. Resultados de las cadenas del ejemplo 1")}
    <p>Al final de la simulación el estado final se colorea en el diagrama: verde si la cadena fue aceptada y
    rojo si fue rechazada. El panel <i>Recorrido paso a paso</i> explica el motivo.</p>
    {imagen_html("diagrama_aceptada.png", ANCHO_IMAGEN_MEDIANA, "Figura 8. Cadena a,b del ejemplo 2 aceptada en q2")}

    <h2>9. Significado de los colores</h2>
    <table border='1' cellspacing='0' cellpadding='5' width='100%'>
      <tr style='background:#DCEBFA'><th>Color</th><th>Dónde</th><th>Significado</th></tr>
      <tr><td style='background:#FFD54F'>&nbsp;</td><td>Diagrama</td><td>Estado actual.</td></tr>
      <tr><td style='background:#DCEBFA'>&nbsp;</td><td>Diagrama</td><td>Estados ya visitados.</td></tr>
      <tr><td style='background:#D32F2F'>&nbsp;</td><td>Diagrama</td><td>Última transición utilizada.</td></tr>
      <tr><td style='background:#81C784'>&nbsp;</td><td>Diagrama</td><td>Estado final de una cadena aceptada.</td></tr>
      <tr><td style='background:#E57373'>&nbsp;</td><td>Diagrama</td><td>Estado final de una cadena rechazada.</td></tr>
      <tr><td style='background:#FFF3C4'>&nbsp;</td><td>Tabla de transiciones</td><td>Fila del estado actual.</td></tr>
      <tr><td style='background:#FFCDD2'>&nbsp;</td><td>Tabla de transiciones</td><td>Celda de la última transición.</td></tr>
      <tr><td style='background:#C8E6C9'>&nbsp;</td><td>Tabla de cadenas</td><td>Cadena aceptada.</td></tr>
      <tr><td style='background:#FFCDD2'>&nbsp;</td><td>Tabla de cadenas</td><td>Cadena rechazada.</td></tr>
    </table>

    <h2>10. Menú Acerca de</h2>
    <ul>
      <li><b>Acerca de</b>: muestra la universidad, el curso, la fecha y los integrantes del grupo.</li>
      <li><b>Ayuda</b> (F1): muestra las instrucciones de uso dentro de la aplicación y permite abrir este manual.</li>
    </ul>
    {imagen_html("acerca_de.png", ANCHO_IMAGEN_MEDIANA * 0.85, "Figura 9. Ventana Acerca de")}

    <h2>11. Mensajes de error frecuentes</h2>
    <table border='1' cellspacing='0' cellpadding='5' width='100%'>
      <tr style='background:#DCEBFA'><th>Mensaje</th><th>Causa y solución</th></tr>
      <tr><td>Falta la sección 'X:'</td><td>No se escribió uno de los encabezados obligatorios
        (Simbolos, Estados, Estado inicial, Estados de aceptación, Transiciones).</td></tr>
      <tr><td>Se esperaban N filas de transiciones</td><td>Debe haber exactamente una fila de transiciones por
        cada estado, en el mismo orden de la lista de estados.</td></tr>
      <tr><td>La fila de transiciones de Q debe tener N destinos</td><td>Cada fila necesita un destino por cada
        símbolo del alfabeto.</td></tr>
      <tr><td>Transición δ(Q, s) = 'X': ese estado no existe</td><td>Un destino no aparece en la lista de estados
        (revise mayúsculas y minúsculas).</td></tr>
      <tr><td>El estado inicial / de aceptación 'X' no está en la lista de estados</td><td>Corrija el nombre del
        estado o agréguelo a <i>Estados</i>.</td></tr>
      <tr><td>Debe haber exactamente un estado inicial</td><td>Un AFD tiene un único estado inicial.</td></tr>
      <tr><td>El símbolo 'x' no pertenece al alfabeto</td><td>Aparece al simular: la cadena contiene un símbolo que
        no está en <i>Simbolos</i>. El autómata se detiene y la cadena se rechaza.</td></tr>
    </table>
    </body></html>
    """


def crear_documento_manual() -> QTextDocument:
    documento = QTextDocument()
    for nombre_captura in os.listdir(CARPETA_CAPTURAS):
        documento.addResource(
            QTextDocument.ImageResource,
            QUrl(nombre_captura),
            QImage(os.path.join(CARPETA_CAPTURAS, nombre_captura)),
        )
    documento.addResource(
        QTextDocument.ImageResource,
        QUrl("icono.png"),
        QImage(os.path.join(CARPETA_PROYECTO, "recursos", "icono.png")),
    )
    documento.setHtml(construir_contenido_html())
    return documento


def exportar_pdf(documento: QTextDocument) -> None:
    escritor_pdf = QPdfWriter(RUTA_MANUAL_PDF)
    escritor_pdf.setResolution(RESOLUCION_PDF_DPI)
    escritor_pdf.setTitle(f"Manual de usuario — {datos_proyecto.NOMBRE_APLICACION}")
    escritor_pdf.setPageLayout(
        QPageLayout(QPageSize(QPageSize.Letter), QPageLayout.Portrait, QMarginsF(18, 18, 18, 18), QPageLayout.Millimeter)
    )
    documento.print_(escritor_pdf)


def generar_manual() -> None:
    aplicacion = QApplication(sys.argv)
    cargar_traduccion_espanol(aplicacion)
    aplicacion.setStyle("Fusion")
    aplicacion.styleHints().setColorScheme(Qt.ColorScheme.Light)

    tomar_capturas()
    exportar_pdf(crear_documento_manual())
    print(f"Manual generado en {RUTA_MANUAL_PDF}")


if __name__ == "__main__":
    generar_manual()
