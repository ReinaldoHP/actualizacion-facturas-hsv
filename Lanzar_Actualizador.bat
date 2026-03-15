@echo off
title Lanzador Actualizador de Facturas
echo Iniciando el Actualizador de Facturas...
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Ocurrio un error al iniciar la aplicacion.
    echo Asegurate de tener instalado ttkbootstrap y de estar usando el interprete correcto.
    pause
)
