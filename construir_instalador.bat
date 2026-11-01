@echo off
rem Genera el instalador completo: icono, manual PDF, ejecutable (PyInstaller) e instalador (Inno Setup).
rem Resultado: salida_instalador\Instalador_SimuladorAFD.exe
setlocal
cd /d "%~dp0"

set "PYTHON_PROYECTO=.venv\Scripts\python.exe"
set "COMPILADOR_INNO=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%COMPILADOR_INNO%" set "COMPILADOR_INNO=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"

if not exist "%PYTHON_PROYECTO%" (
    echo No se encontro el entorno virtual .venv. Creelo con:  python -m venv .venv
    exit /b 1
)
if not exist "%COMPILADOR_INNO%" (
    echo No se encontro Inno Setup 6. Instalelo con:  winget install JRSoftware.InnoSetup
    exit /b 1
)

echo [1/5] Ejecutando pruebas...
"%PYTHON_PROYECTO%" -m unittest discover -s pruebas -t . || goto error

echo [2/5] Generando icono...
"%PYTHON_PROYECTO%" instalador\generar_icono.py || goto error

echo [3/5] Generando manual de usuario...
"%PYTHON_PROYECTO%" documentacion\generar_manual.py || goto error

echo [4/5] Empaquetando la aplicacion con PyInstaller...
"%PYTHON_PROYECTO%" -m PyInstaller --noconfirm --distpath dist --workpath build instalador\simulador_afd.spec || goto error

echo [5/5] Compilando el instalador con Inno Setup...
"%COMPILADOR_INNO%" /Q instalador\instalador.iss || goto error

echo.
echo Listo: salida_instalador\Instalador_SimuladorAFD.exe
exit /b 0

:error
echo.
echo *** La construccion fallo en el paso anterior. ***
exit /b 1
