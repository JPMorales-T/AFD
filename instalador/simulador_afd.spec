import os

carpeta_proyecto = os.path.dirname(SPECPATH)

archivos_adicionales = [
    (os.path.join(carpeta_proyecto, "ejemplos"), "ejemplos"),
    (os.path.join(carpeta_proyecto, "recursos"), "recursos"),
]
ruta_manual_usuario = os.path.join(carpeta_proyecto, "documentacion", "Manual_de_usuario.pdf")
if os.path.exists(ruta_manual_usuario):
    archivos_adicionales.append((ruta_manual_usuario, "documentacion"))

modulos_excluidos = [
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineWidgets", "PySide6.QtMultimedia", "PySide6.Qt3DCore", "PySide6.QtCharts",
    "PySide6.QtDataVisualization", "PySide6.QtPdf", "PySide6.QtSql", "PySide6.QtTest", "tkinter",
]

analisis = Analysis(
    [os.path.join(carpeta_proyecto, "principal.py")],
    pathex=[carpeta_proyecto],
    datas=archivos_adicionales,
    excludes=modulos_excluidos,
)
codigo_empaquetado = PYZ(analisis.pure)

ejecutable = EXE(
    codigo_empaquetado,
    analisis.scripts,
    [],
    exclude_binaries=True,
    name="SimuladorAFD",
    icon=os.path.join(carpeta_proyecto, "recursos", "icono.ico"),
    console=False,
    upx=False,
)

carpeta_distribucion = COLLECT(
    ejecutable,
    analisis.binaries,
    analisis.datas,
    name="SimuladorAFD",
    upx=False,
)
