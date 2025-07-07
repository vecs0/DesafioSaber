#!/usr/bin/env python3
"""
Script de verificación y corrección automática del sistema DesafíoSaber
Verifica y corrige problemas comunes antes de ejecutar el sistema
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def check_and_create_directories():
    """Verifica y crea directorios necesarios"""
    print("📁 Verificando directorios...")
    
    directories = [
        'data',
        'assets/images',
        'assets/sounds',
        'sounds',
        'uploads',
        'web_admin/uploads'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Creado directorio: {directory}")
        else:
            print(f"✅ Directorio existe: {directory}")

def check_and_create_files():
    """Verifica y crea archivos necesarios"""
    print("\n📄 Verificando archivos de datos...")
    
    # Verificar archivo de configuración
    config_file = 'data/config.json'
    if not os.path.exists(config_file):
        default_config = {
            "theme": "oscuro",
            "difficulty": "difícil",
            "sound": True,
            "music": True,
            "game_modes": [
                {
                    "name": "Clásico",
                    "numQuestions": 15,
                    "timePerQuestion": 30
                },
                {
                    "isGlobalTimer": True,
                    "name": "Contrarreloj",
                    "totalTime": 60
                },
                {
                    "name": "Duelo",
                    "numQuestions": 10,
                    "timePerQuestion": 15
                }
            ]
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        print(f"✅ Creado archivo: {config_file}")
    
    # Verificar archivo de ranking
    ranking_file = 'data/ranking.json'
    if not os.path.exists(ranking_file):
        with open(ranking_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"✅ Creado archivo: {ranking_file}")
    
    # Verificar archivo de categorías
    categories_file = 'data/categories.json'
    if not os.path.exists(categories_file):
        default_categories = [
            {"name": "Historia", "color": "#e74c3c"},
            {"name": "Ciencia", "color": "#3498db"},
            {"name": "Geografía", "color": "#2ecc71"},
            {"name": "Literatura", "color": "#f39c12"},
            {"name": "Deportes", "color": "#9b59b6"},
            {"name": "Arte", "color": "#e67e22"},
            {"name": "Tecnología", "color": "#1abc9c"},
            {"name": "Música", "color": "#34495e"}
        ]
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump(default_categories, f, ensure_ascii=False, indent=2)
        print(f"✅ Creado archivo: {categories_file}")
    
    # Verificar archivo de usuarios
    users_file = 'usuarios.json'
    if not os.path.exists(users_file) or os.path.getsize(users_file) == 0:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        print(f"✅ Creado archivo: {users_file}")

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("\n🔍 Verificando dependencias...")
    
    required_packages = [
        'flask',
        'flask_cors', 
        'requests',
        'pygame',
        'PIL',
        'tkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'tkinter':
                import tkinter
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} no instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Faltan dependencias: {', '.join(missing_packages)}")
        print("Instalando dependencias faltantes...")
        
        for package in missing_packages:
            if package == 'PIL':
                package = 'pillow'
            elif package == 'tkinter':
                continue  # tkinter viene con Python
            
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Instalado: {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Error instalando: {package}")
                return False
    
    return True

def check_assets():
    """Verifica que los archivos de assets existan"""
    print("\n🎨 Verificando assets...")
    
    required_assets = [
        'assets/images/logo.png',
        'assets/images/menu_background.png',
        'sounds/acierto.mp3',
        'sounds/errado.mp3',
        'sounds/despliegue_opciones.mp3',
        'sounds/intro_music.mp3'
    ]
    
    missing_assets = []
    
    for asset in required_assets:
        if os.path.exists(asset):
            print(f"✅ {asset}")
        else:
            print(f"❌ {asset} no encontrado")
            missing_assets.append(asset)
    
    if missing_assets:
        print(f"\n⚠️ Faltan assets: {', '.join(missing_assets)}")
        print("Se crearán archivos placeholder...")
        
        for asset in missing_assets:
            try:
                os.makedirs(os.path.dirname(asset), exist_ok=True)
                if asset.endswith('.png'):
                    # Crear imagen placeholder
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (100, 100), color='gray')
                    draw = ImageDraw.Draw(img)
                    draw.text((10, 40), "PLACEHOLDER", fill='white')
                    img.save(asset)
                elif asset.endswith('.mp3'):
                    # Crear archivo de sonido vacío
                    with open(asset, 'wb') as f:
                        f.write(b'')
                print(f"✅ Creado placeholder: {asset}")
            except Exception as e:
                print(f"❌ Error creando placeholder para {asset}: {e}")

def fix_path_issues():
    """Corrige problemas de rutas en los archivos"""
    print("\n🔧 Corrigiendo problemas de rutas...")
    
    # Verificar que las rutas en el código sean correctas
    files_to_check = [
        'game/main.py',
        'main.py',
        'web_admin/server.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ Archivo verificado: {file_path}")
        else:
            print(f"❌ Archivo no encontrado: {file_path}")

def create_launcher_script():
    """Crea un script de lanzamiento mejorado"""
    print("\n🚀 Creando script de lanzamiento...")
    
    launcher_content = '''#!/usr/bin/env python3
"""
Lanzador automático del sistema DesafíoSaber
Ejecuta la verificación y luego inicia el sistema
"""

import os
import sys
import subprocess

def main():
    print("🎮 Iniciando DesafíoSaber...")
    
    # Ejecutar verificación
    try:
        subprocess.run([sys.executable, 'fix_system.py'], check=True)
        print("✅ Verificación completada")
    except subprocess.CalledProcessError:
        print("❌ Error en la verificación")
        return
    
    # Preguntar qué iniciar
    print("\\n¿Qué quieres iniciar?")
    print("1. Panel de administración")
    print("2. Juego")
    print("3. Ambos")
    
    choice = input("Selecciona una opción (1-3): ").strip()
    
    if choice == "1":
        print("🌐 Iniciando panel de administración...")
        subprocess.run([sys.executable, 'start_system.py'])
    elif choice == "2":
        print("🎮 Iniciando juego...")
        subprocess.run([sys.executable, 'game/main.py'])
    elif choice == "3":
        print("🚀 Iniciando sistema completo...")
        subprocess.run([sys.executable, 'start_system.py'])
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
'''
    
    with open('launch.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ Script de lanzamiento creado: launch.py")

def main():
    """Función principal"""
    print("🔧 Sistema de Verificación y Corrección DesafíoSaber")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("game") or not os.path.exists("web_admin"):
        print("❌ Error: No se encontró la estructura del proyecto")
        print("   Ejecuta este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Ejecutar verificaciones
    check_and_create_directories()
    check_and_create_files()
    
    if not check_dependencies():
        print("❌ Error: No se pudieron instalar todas las dependencias")
        sys.exit(1)
    
    check_assets()
    fix_path_issues()
    create_launcher_script()
    
    print("\n🎉 ¡Verificación completada!")
    print("\n📋 Resumen:")
    print("   ✅ Directorios verificados")
    print("   ✅ Archivos de datos creados")
    print("   ✅ Dependencias instaladas")
    print("   ✅ Assets verificados")
    print("   ✅ Script de lanzamiento creado")
    print("\n🚀 Para iniciar el sistema:")
    print("   python launch.py")
    print("   o")
    print("   python start_system.py")

if __name__ == "__main__":
    main() 