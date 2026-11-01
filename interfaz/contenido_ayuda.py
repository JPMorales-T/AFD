EXPLICACION_FORMATO_ARCHIVO_HTML = """
<p>El archivo de texto tiene estas secciones, en este orden:</p>
<pre style="background:#F5F5F5; padding:6px">Simbolos: 0,1
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
0,0,1,0,1</pre>
<ul>
  <li><b>Simbolos</b> y <b>Estados</b>: listas separadas por comas.</li>
  <li><b>Estado inicial</b>: un solo estado.</li>
  <li><b>Estados de aceptación</b>: uno o varios, separados por comas.</li>
  <li><b>Transiciones</b>: una línea por cada estado, <u>en el mismo orden</u> de la lista de estados.
      Cada línea tiene un destino por símbolo, <u>en el mismo orden</u> de la lista de símbolos.
      En el ejemplo, la primera línea <code>Q2,Q1</code> indica δ(Q0,0)=Q2 y δ(Q0,1)=Q1.</li>
  <li><b>Cadenas a analizar</b>: una cadena por línea, con los símbolos separados por comas.
      La palabra vacía se escribe <code>ε</code>.</li>
</ul>
"""

CONTENIDO_AYUDA_HTML = f"""
<h2>Cómo usar el simulador</h2>

<h3>1. Cargar un autómata</h3>
<ul>
  <li><b>Archivo → Abrir</b> (Ctrl+O): carga un archivo de texto con la definición del AFD.</li>
  <li><b>Ejemplos</b>: carga uno de los tres autómatas incluidos.</li>
  <li><b>Archivo → Nuevo</b> (Ctrl+N): abre el editor con una plantilla para escribir un AFD nuevo.
      El editor indica si la definición es válida mientras se escribe; con
      <i>Cargar en el simulador</i> se muestra el autómata en la ventana principal.</li>
  <li><b>Archivo → Editar autómata actual</b> (Ctrl+E): abre en el editor el autómata que se está simulando.</li>
</ul>

<h3>2. Formato del archivo</h3>
{EXPLICACION_FORMATO_ARCHIVO_HTML}

<h3>3. Simular una cadena paso a paso</h3>
<ol>
  <li>Seleccione una cadena en la tabla <b>Cadenas a analizar</b>
      (o escriba una nueva, por ejemplo <code>1,0,1</code> o <code>101</code>, y presione <i>Agregar</i>).</li>
  <li>Use los controles de <b>Simulación paso a paso</b>:
    <ul>
      <li><b>Paso siguiente</b>: lee el siguiente símbolo.</li>
      <li><b>Paso anterior</b>: deshace el último símbolo leído.</li>
      <li><b>Reiniciar</b>: vuelve al estado inicial.</li>
      <li><b>Ir al final</b>: lee toda la cadena de una vez.</li>
      <li><b>Reproducir / Pausar</b>: avanza automáticamente; la barra ajusta la velocidad.</li>
    </ul>
  </li>
  <li>Al terminar de leer la cadena, la tabla de cadenas muestra el recorrido y si fue
      <span style="color:#1B5E20"><b>Aceptada</b></span> o
      <span style="color:#B71C1C"><b>Rechazada</b></span>.</li>
  <li><b>Procesar todas</b> calcula el resultado de todas las cadenas de una vez.</li>
</ol>

<h3>4. Significado de los colores</h3>
<table border="1" cellspacing="0" cellpadding="4">
  <tr><td style="background:#FFD54F">&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Estado actual del autómata.</td></tr>
  <tr><td style="background:#DCEBFA">&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Estados ya visitados.</td></tr>
  <tr><td style="background:#D32F2F">&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Última transición utilizada (diagrama).</td></tr>
  <tr><td style="background:#FFCDD2">&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Celda de la última transición utilizada (tabla).</td></tr>
  <tr><td style="background:#FFF3C4">&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Fila del estado actual (tabla).</td></tr>
  <tr><td style="background:#81C784">&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Cadena aceptada: terminó en un estado de aceptación.</td></tr>
  <tr><td style="background:#E57373">&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Cadena rechazada.</td></tr>
</table>
<p>En el diagrama, la flecha <i>inicio</i> señala el estado inicial y el doble círculo
los estados de aceptación. En la tabla de transiciones se marcan con → y * respectivamente.</p>

<h3>5. Guardar</h3>
<ul>
  <li><b>Archivo → Guardar</b> (Ctrl+S): si el editor está abierto guarda su contenido;
      si no, guarda el autómata actual junto con las cadenas agregadas.</li>
  <li><b>Archivo → Guardar como</b> (Ctrl+Shift+S): guarda en un archivo nuevo.</li>
</ul>
"""
