@echo off
where py >nul 2>nul
if errorlevel 1 (
  python -B "%~dp0..\modulo_nube\subir_nube.py"
) else (
  py -3 -B "%~dp0..\modulo_nube\subir_nube.py"
)
if errorlevel 1 pause
