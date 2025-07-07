@echo off
REM DesafíoSaber - Script de Instalación para Windows
REM =================================================

echo 🎮 Instalando DesafíoSaber...

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instala Python 3.8 o superior.
    pause
    exit /b 1
)

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no está instalado. Por favor instala pip.
    pause
    exit /b 1
)

REM Instalar dependencias Python
echo 📦 Instalando dependencias de Python...
pip install -r requirements.txt

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Node.js no está instalado. El panel web no funcionará.
    echo    Instala Node.js desde https://nodejs.org/
) else (
    REM Instalar dependencias Node.js
    echo 📦 Instalando dependencias de Node.js...
    cd web_admin
    npm install
    cd ..
)

echo ✅ Instalación completada!
echo.
echo 🚀 Para iniciar el sistema:
echo    python start_system.py
echo.
echo 📖 Para más información, consulta README.md
pause
