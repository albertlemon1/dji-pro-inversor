@echo off
title Lanzador DJI Pro con Backup
cd /d "%~dp0"

echo [1/3] Activando entorno virtual...
call venv\Scripts\activate

echo [2/3] Iniciando Terminal de Inversion...
:: Ejecuta la app y espera a que la cierres
streamlit run dji_pro_tool.py

echo [3/3] Generando Copia de Seguridad...
:: Crea la carpeta si no existe
if not exist "Backups" mkdir Backups

:: Usa PowerShell para obtener una fecha limpia (AAAA-MM-DD_HHmm)
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd_HHmm'"') do set timestamp=%%i

:: Copia el archivo generado por Python a la carpeta de Backups
if exist "ultimo_analisis.csv" (
    copy "ultimo_analisis.csv" "Backups\backup_%timestamp%.csv" >nul
    echo.
    echo --------------------------------------------------
    echo SEGURIDAD: Backup creado como backup_%timestamp%.csv
    echo --------------------------------------------------
) else (
    echo No se encontro el archivo de datos para respaldar.
)

echo.
echo Proceso finalizado.
pause