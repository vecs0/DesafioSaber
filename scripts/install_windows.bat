@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo.
echo ========================================
echo    INSTALADOR DESAFÍO SABER - WINDOWS
echo ========================================
echo.

echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
) else (
    echo ✅ Python encontrado
)

echo.
echo 🔍 Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no encontrado. Instalando...
    python -m ensurepip --upgrade
) else (
    echo ✅ pip encontrado
)

echo.
echo 📦 Instalando dependencias de Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Error instalando dependencias de Python
    pause
    exit /b 1
) else (
    echo ✅ Dependencias de Python instaladas
)

echo.
echo 🔍 Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js no encontrado. Por favor instala Node.js desde https://nodejs.org
    echo    Después ejecuta este script nuevamente.
    pause
    exit /b 1
) else (
    echo ✅ Node.js encontrado
)

echo.
echo 📦 Instalando dependencias de Node.js...
cd web_admin
npm install
if errorlevel 1 (
    echo ❌ Error instalando dependencias de Node.js
    cd ..
    pause
    exit /b 1
) else (
    echo ✅ Dependencias de Node.js instaladas
)
cd ..



echo.
echo ========================================
echo           INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo 🚀 Para iniciar el sistema:
echo    python scripts\start_all.py
echo.
echo 🌐 Panel de administración: http://localhost:3000
echo 🎮 Para ejecutar solo el juego: python game/main.py
echo.
echo 🧪 Para correr los tests: python -m pytest tests
echo.
pause 