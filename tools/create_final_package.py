#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DesafíoSaber - Script de Creación de Paquete Final
==================================================

Este script crea un paquete ZIP final del proyecto DesafíoSaber
incluyendo todos los archivos necesarios para la distribución.

Autor: Equipo DesafíoSaber
Versión: 1.0.0
"""

import os
import zipfile
import shutil
import json
from datetime import datetime
from pathlib import Path

def print_banner():
    """Imprime el banner del script"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                📦 DESAFÍO SABER - PAQUETE FINAL 📦          ║
    ║                                                              ║
    ║              Creando paquete de distribución...              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def get_project_info():
    """Obtiene información del proyecto"""
    try:
        with open('data/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return {
            'name': config.get('title', 'DesafíoSaber'),
            'version': config.get('version', '1.0.0'),
            'description': config.get('description', 'Juego de Conocimiento Interactivo')
        }
    except:
        return {
            'name': 'DesafíoSaber',
            'version': '1.0.0',
            'description': 'Juego de Conocimiento Interactivo'
        }

def create_file_list():
    """Crea la lista de archivos a incluir en el paquete"""
    include_patterns = [
        # Archivos principales
        'game/*.py',
        'web_admin/*.py',
        'web_admin/*.json',
        'web_admin/src/**/*',
        'web_admin/public/**/*',
        
        # Datos
        'data/*.json',
        
        # Assets
        'assets/**/*',
        'sounds/*.mp3',
        
        # Scripts y utilidades
        'scripts/*.py',
        'utils/*.py',
        
        # Pruebas
        'tests/*.py',
        
        # Documentación
        'docs/**/*',
        'README.md',
        'CHECKLIST_ENTREGA.md',
        'requirements.txt',
        'start_system.py',
        
        # Configuración
        'web_admin/package.json',
        'web_admin/requirements.txt',
        'web_admin/tailwind.config.js',
        'web_admin/postcss.config.js'
    ]
    
    exclude_patterns = [
        '**/__pycache__/**',
        '**/*.pyc',
        '**/node_modules/**',
        '**/.git/**',
        '**/.venv/**',
        '**/venv/**',
        '**/env/**',
        '**/*.log',
        '**/build/**',
        '**/dist/**',
        '**/.DS_Store',
        '**/Thumbs.db'
    ]
    
    return include_patterns, exclude_patterns

def should_include_file(file_path, exclude_patterns):
    """Verifica si un archivo debe ser incluido"""
    file_path_str = str(file_path)
    
    for pattern in exclude_patterns:
        if pattern.startswith('**/'):
            pattern = pattern[3:]
        if pattern.endswith('/**'):
            pattern = pattern[:-3]
        
        if pattern in file_path_str:
            return False
    
    return True

def get_all_files(base_path, include_patterns, exclude_patterns):
    """Obtiene todos los archivos que deben ser incluidos"""
    files = []
    base_path = Path(base_path)
    
    for pattern in include_patterns:
        if '**' in pattern:
            # Patrón con wildcard
            if pattern.startswith('**/'):
                pattern = pattern[3:]
            if pattern.endswith('/**'):
                pattern = pattern[:-3]
            
            for file_path in base_path.rglob(pattern):
                if file_path.is_file() and should_include_file(file_path, exclude_patterns):
                    files.append(file_path)
        else:
            # Patrón simple
            for file_path in base_path.glob(pattern):
                if file_path.is_file() and should_include_file(file_path, exclude_patterns):
                    files.append(file_path)
    
    return list(set(files))  # Eliminar duplicados

def create_zip_package(files, project_info):
    """Crea el paquete ZIP final"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"DesafioSaber_v{project_info['version']}_{timestamp}.zip"
    
    print(f"📦 Creando paquete: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files:
            try:
                # Calcular ruta relativa para el ZIP
                relative_path = file_path.relative_to(Path.cwd())
                
                print(f"   📄 Agregando: {relative_path}")
                
                # Agregar archivo al ZIP
                zipf.write(file_path, relative_path)
            except ValueError:
                # Si hay problemas con la ruta relativa, usar la ruta absoluta
                print(f"   📄 Agregando: {file_path.name}")
                zipf.write(file_path, file_path.name)
    
    return zip_name

def create_install_script():
    """Crea un script de instalación para el paquete"""
    install_script = """#!/bin/bash
# DesafíoSaber - Script de Instalación
# ====================================

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
echo "   python start_system.py"
echo ""
echo "📖 Para más información, consulta README.md"
"""
    
    with open('install.sh', 'w', encoding='utf-8') as f:
        f.write(install_script)

def create_windows_install_script():
    """Crea un script de instalación para Windows"""
    install_script = """@echo off
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
"""
    
    with open('install.bat', 'w', encoding='utf-8') as f:
        f.write(install_script)

def create_package_info(project_info, files, zip_name):
    """Crea un archivo de información del paquete"""
    info = {
        'package_info': {
            'name': project_info['name'],
            'version': project_info['version'],
            'description': project_info['description'],
            'created_at': datetime.now().isoformat(),
            'zip_file': zip_name,
            'total_files': len(files),
            'total_size_mb': round(os.path.getsize(zip_name) / (1024 * 1024), 2)
        },
        'file_structure': {
            'game_files': len([f for f in files if 'game' in str(f)]),
            'web_admin_files': len([f for f in files if 'web_admin' in str(f)]),
            'data_files': len([f for f in files if 'data' in str(f)]),
            'asset_files': len([f for f in files if 'assets' in str(f) or 'sounds' in str(f)]),
            'script_files': len([f for f in files if 'scripts' in str(f) or 'utils' in str(f)]),
            'test_files': len([f for f in files if 'tests' in str(f)]),
            'doc_files': len([f for f in files if 'docs' in str(f) or f.name.endswith('.md')])
        },
        'installation_instructions': {
            'python_version': '3.8+',
            'node_version': '16+',
            'main_script': 'start_system.py',
            'requirements': 'requirements.txt',
            'web_admin_requirements': 'web_admin/package.json'
        }
    }
    
    with open('package_info.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    return info

def main():
    """Función principal"""
    print_banner()
    
    # Obtener información del proyecto
    project_info = get_project_info()
    print(f"📋 Proyecto: {project_info['name']} v{project_info['version']}")
    print(f"📝 Descripción: {project_info['description']}")
    print()
    
    # Crear lista de archivos
    print("🔍 Analizando archivos del proyecto...")
    include_patterns, exclude_patterns = create_file_list()
    files = get_all_files('.', include_patterns, exclude_patterns)
    
    print(f"📄 Archivos encontrados: {len(files)}")
    print()
    
    # Crear scripts de instalación
    print("📝 Creando scripts de instalación...")
    create_install_script()
    create_windows_install_script()
    print("✅ Scripts de instalación creados")
    print()
    
    # Crear paquete ZIP
    print("📦 Creando paquete ZIP...")
    zip_name = create_zip_package(files, project_info)
    
    # Crear información del paquete
    print("📋 Creando información del paquete...")
    package_info = create_package_info(project_info, files, zip_name)
    
    # Mostrar resumen
    print()
    print("="*60)
    print("🎉 ¡PAQUETE CREADO EXITOSAMENTE!")
    print("="*60)
    print(f"📦 Archivo: {zip_name}")
    print(f"📊 Tamaño: {package_info['package_info']['total_size_mb']} MB")
    print(f"📄 Archivos incluidos: {package_info['package_info']['total_files']}")
    print()
    print("📁 Estructura del paquete:")
    print(f"   🎮 Archivos del juego: {package_info['file_structure']['game_files']}")
    print(f"   🌐 Archivos web: {package_info['file_structure']['web_admin_files']}")
    print(f"   📊 Archivos de datos: {package_info['file_structure']['data_files']}")
    print(f"   🎨 Archivos multimedia: {package_info['file_structure']['asset_files']}")
    print(f"   🔧 Scripts: {package_info['file_structure']['script_files']}")
    print(f"   🧪 Pruebas: {package_info['file_structure']['test_files']}")
    print(f"   📚 Documentación: {package_info['file_structure']['doc_files']}")
    print()
    print("🚀 Para instalar:")
    print("   Linux/Mac: ./install.sh")
    print("   Windows: install.bat")
    print()
    print("📖 Consulta README.md para más información")
    print("="*60)

if __name__ == "__main__":
    main() 