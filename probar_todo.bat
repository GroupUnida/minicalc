@echo off
REM Ejecuta Mini-Calc con todos los archivos de ejemplo y luego las pruebas automaticas.
REM Uso: doble clic sobre este archivo, o escribir probar_todo.bat en la consola.
chcp 65001 >nul
cd /d "%~dp0"

set PY=python
where python >nul 2>nul || set PY=py

for %%f in (ejemplos\*.calc) do (
    echo.
    echo ==================== %%f ====================
    %PY% minicalc.py "%%f"
)

echo.
echo ==================== PRUEBAS AUTOMATICAS ====================
%PY% -m unittest -v

echo.
pause
