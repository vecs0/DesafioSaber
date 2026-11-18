#!/bin/bash
# DesafíoSaber - Script de Instalación
# ====================================

cd "$(dirname "$0")/.." || exit 1
echo "🎮 Instalando DesafíoSaber..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instala Python 3.8 o superior."
    exit 1
fi

# Verificar pip
if ! command -v pip &> /dev/null; then
    echo "❌ pip no está instalado. Por favor instala pip."
    exit 1
fi

# Instalar dependencias Python
echo "📦 Instalando dependencias de Python..."
pip install -r requirements.txt

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️ Node.js no está instalado. El panel web no funcionará."
    echo "   Instala Node.js desde https://nodejs.org/"
else
    # Instalar dependencias Node.js
    echo "📦 Instalando dependencias de Node.js..."
    cd web_admin
    npm install
    cd ..
fi

echo "✅ Instalación completada!"
echo ""
echo "🚀 Para iniciar el sistema:"
echo "   python3 scripts/start_all.py"
echo ""
echo "📖 Para más información, consulta README.md"
