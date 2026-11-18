#!/usr/bin/env python3
"""
Script de Preparación para Compilación .exe
Prepara el juego DesafíoSaber para compilación con PyInstaller
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime

class ExeBuilder:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.game_dir = os.path.join(self.project_root, 'game')
        self.build_dir = os.path.join(self.project_root, 'build')
        self.dist_dir = os.path.join(self.project_root, 'dist')
        self.spec_file = os.path.join(self.project_root, 'DesafioSaber.spec')
        
    def print_banner(self):
        """Imprime el banner de preparación"""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                🚀 Preparación para .exe 🚀                   ║
    ║                                                              ║
    ║  DesafíoSaber v2.0 - Compilación a Ejecutable               ║
    ║  ========================================================    ║
    ║                                                              ║
    ║  Preparando:                                                 ║
    ║  • Verificación de dependencias                             ║
    ║  • Optimización de archivos                                 ║
    ║  • Configuración de PyInstaller                             ║
    ║  • Generación de archivo .spec                              ║
    ║  • Preparación de recursos                                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_dependencies(self):
        """Verifica que las dependencias necesarias estén instaladas"""
        print("📦 Verificando dependencias...")
        
        required_packages = [
            'pyinstaller',
            'requests',
            'pygame',
            'pillow',
            'matplotlib',
            'numpy',
            'flask',
            'flask-cors',
            'flask-socketio',
            'python-socketio'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"   ✅ {package}: Instalado")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}: No instalado")
        
        if missing_packages:
            print(f"\n⚠️ Faltan dependencias: {', '.join(missing_packages)}")
            print("🔧 Instalando dependencias faltantes...")
            
            for package in missing_packages:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                 check=True, capture_output=True)
                    print(f"   ✅ {package}: Instalado correctamente")
                except subprocess.CalledProcessError:
                    print(f"   ❌ {package}: Error en la instalación")
                    return False
        
        print("✅ Todas las dependencias están instaladas")
        return True
    
    def create_spec_file(self):
        """Crea el archivo .spec para PyInstaller"""
        print("📄 Creando archivo .spec...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Archivos de datos
datas = [
    ('../data', 'data'),
    ('../assets', 'assets'),
    ('../sounds', 'sounds'),
    ('../fonts', 'fonts'),
    ('../backups', 'backups'),
]

# Archivos ocultos
hiddenimports = [
    'pygame',
    'PIL',
    'PIL._tkinter_finder',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',
    'numpy',
    'requests',
    'flask',
    'flask_cors',
    'flask_socketio',
    'socketio',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'json',
    'threading',
    'datetime',
    'random',
    'time',
    'os',
    'sys',
    'webbrowser',
    'subprocess',
    'sqlite3',
    'werkzeug',
    'werkzeug.utils',
    'werkzeug.datastructures',
    'werkzeug.exceptions',
    'werkzeug.security',
    'werkzeug.wrappers',
    'werkzeug.wsgi',
    'werkzeug.local',
    'werkzeug.middleware',
    'werkzeug.middleware.proxy_fix',
    'werkzeug.middleware.shared_data',
    'werkzeug.middleware.dispatcher',
    'werkzeug.middleware.http_proxy',
    'werkzeug.middleware.lint',
    'werkzeug.middleware.profiler',
    'werkzeug.middleware.proxy_fix',
    'werkzeug.middleware.shared_data',
    'werkzeug.middleware.dispatcher',
    'werkzeug.middleware.http_proxy',
    'werkzeug.middleware.lint',
    'werkzeug.middleware.profiler',
]

# Configuración de la aplicación
a = Analysis(
    ['main.py'],
    pathex=['{self.game_dir}'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DesafioSaber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola para aplicación GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../assets/images/logo.ico' if os.path.exists('../assets/images/logo.ico') else None,
)
'''
        
        try:
            with open(self.spec_file, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            print("✅ Archivo .spec creado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error creando archivo .spec: {e}")
            return False
    
    def optimize_game_files(self):
        """Optimiza los archivos del juego para la compilación"""
        print("🔧 Optimizando archivos del juego...")
        
        # Verificar que el archivo principal existe
        main_file = os.path.join(self.game_dir, 'main.py')
        if not os.path.exists(main_file):
            print("❌ No se encontró el archivo main.py")
            return False
        
        # Crear directorio de build si no existe
        os.makedirs(self.build_dir, exist_ok=True)
        
        # Copiar archivos necesarios al directorio de build
        files_to_copy = [
            ('../data', 'data'),
            ('../assets', 'assets'),
            ('../sounds', 'sounds'),
            ('../fonts', 'fonts'),
            ('../backups', 'backups'),
        ]
        
        for src, dst in files_to_copy:
            src_path = os.path.join(self.project_root, src)
            dst_path = os.path.join(self.build_dir, dst)
            
            if os.path.exists(src_path):
                try:
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dst_path)
                    print(f"   ✅ Copiado: {src} -> {dst}")
                except Exception as e:
                    print(f"   ❌ Error copiando {src}: {e}")
            else:
                print(f"   ⚠️ No encontrado: {src}")
        
        print("✅ Archivos optimizados")
        return True
    
    def create_launcher_script(self):
        """Crea un script de lanzamiento para el ejecutable"""
        print("🚀 Creando script de lanzamiento...")
        
        launcher_content = '''#!/usr/bin/env python3
"""
Lanzador para DesafíoSaber
Inicia el juego y verifica las dependencias
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Verifica que las dependencias estén disponibles"""
    try:
        import pygame
        import PIL
        import requests
        return True
    except ImportError as e:
        return False

def show_error_dialog(message):
    """Muestra un diálogo de error"""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error - DesafíoSaber", message)
    root.destroy()

def main():
    """Función principal del lanzador"""
    try:
        # Verificar dependencias
        if not check_dependencies():
            show_error_dialog("Error: Faltan dependencias necesarias.\\n\\nPor favor, reinstala el juego.")
            return
        
        # Cambiar al directorio del juego
        game_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(game_dir)
        
        # Importar y ejecutar el juego
        from main import DesafioSaberApp
        import tkinter as tk
        
        root = tk.Tk()
        app = DesafioSaberApp(root)
        root.mainloop()
        
    except Exception as e:
        show_error_dialog(f"Error al iniciar el juego:\\n\\n{str(e)}\\n\\nPor favor, contacta al soporte técnico.")

if __name__ == "__main__":
    main()
'''
        
        launcher_file = os.path.join(self.build_dir, 'launcher.py')
        try:
            with open(launcher_file, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            print("✅ Script de lanzamiento creado")
            return True
        except Exception as e:
            print(f"❌ Error creando script de lanzamiento: {e}")
            return False
    
    def create_requirements_file(self):
        """Crea un archivo requirements.txt para la compilación"""
        print("📋 Creando archivo requirements.txt...")
        
        requirements = [
            'pyinstaller>=5.0',
            'requests>=2.25.0',
            'pygame>=2.0.0',
            'pillow>=8.0.0',
            'matplotlib>=3.3.0',
            'numpy>=1.19.0',
            'flask>=2.0.0',
            'flask-cors>=3.0.0',
            'flask-socketio>=5.0.0',
            'python-socketio>=5.0.0',
            'werkzeug>=2.0.0'
        ]
        
        requirements_file = os.path.join(self.build_dir, 'requirements.txt')
        try:
            with open(requirements_file, 'w', encoding='utf-8') as f:
                for req in requirements:
                    f.write(req + '\n')
            print("✅ Archivo requirements.txt creado")
            return True
        except Exception as e:
            print(f"❌ Error creando requirements.txt: {e}")
            return False
    
    def create_build_script(self):
        """Crea un script para ejecutar la compilación"""
        print("🔨 Creando script de compilación...")
        
        build_script_content = '''#!/usr/bin/env python3
"""
Script de Compilación para DesafíoSaber
Ejecuta PyInstaller para crear el ejecutable
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def main():
    print("🚀 Iniciando compilación de DesafíoSaber...")
    print("="*50)
    
    # Cambiar al directorio de build
    build_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(build_dir)
    
    # Limpiar compilaciones anteriores
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Ejecutar PyInstaller
    print("🔨 Ejecutando PyInstaller...")
    try:
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name=DesafioSaber",
            "--distpath=dist",
            "--workpath=build",
            "--specpath=.",
            "launcher.py"
        ], check=True)
        
        print(f"✅ Compilación completada exitosamente!")
        print(f"📁 Ejecutable creado en: {os.path.join(build_dir, 'dist', 'DesafioSaber.exe')}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en la compilación: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
'''
        
        build_script_file = os.path.join(self.build_dir, 'build_exe.py')
        try:
            with open(build_script_file, 'w', encoding='utf-8') as f:
                f.write(build_script_content)
            print("✅ Script de compilación creado")
            return True
        except Exception as e:
            print(f"❌ Error creando script de compilación: {e}")
            return False
    
    def create_readme(self):
        """Crea un archivo README para la compilación"""
        print("📖 Creando archivo README...")
        
        readme_content = '''# DesafíoSaber - Compilación a Ejecutable

## Instrucciones de Compilación

### Requisitos Previos
- Python 3.8 o superior
- PyInstaller instalado: `pip install pyinstaller`
- Todas las dependencias del proyecto instaladas

### Pasos para Compilar

1. **Verificar dependencias:**
   ```bash
   python scripts/test_connections.py
   ```

2. **Preparar la compilación:**
   ```bash
   python scripts/prepare_exe_build.py
   ```

3. **Ejecutar la compilación:**
   ```bash
   cd build
   python build_exe.py
   ```

4. **Encontrar el ejecutable:**
   El archivo `DesafioSaber.exe` se creará en la carpeta `build/dist/`

### Estructura del Ejecutable

El ejecutable incluye:
- Juego principal con interfaz Tkinter
- Todos los recursos (imágenes, sonidos, fuentes)
- Base de datos local
- Sistema de logros y estadísticas
- Panel de administración web (requiere servidor separado)

### Notas Importantes

- El ejecutable es independiente y no requiere Python instalado
- El tamaño del archivo puede ser grande debido a las dependencias incluidas
- Para usar el panel de administración, ejecuta el servidor web por separado
- Los datos se guardan localmente en la carpeta del ejecutable

### Solución de Problemas

Si el ejecutable no funciona:
1. Verifica que todas las dependencias estén instaladas
2. Ejecuta el script de verificación de conexiones
3. Revisa los logs de error
4. Contacta al soporte técnico

### Versión
DesafíoSaber v2.0
Fecha de compilación: ''' + datetime.now().strftime("%d/%m/%Y %H:%M") + '''

---
Desarrollado con ❤️ por el equipo DesafíoSaber
'''
        
        readme_file = os.path.join(self.build_dir, 'README_COMPILACION.md')
        try:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print("✅ Archivo README creado")
            return True
        except Exception as e:
            print(f"❌ Error creando README: {e}")
            return False
    
    def run_preparation(self):
        """Ejecuta todo el proceso de preparación"""
        self.print_banner()
        
        print("🚀 Iniciando preparación para compilación...")
        print("="*60)
        
        steps = [
            ("Verificando dependencias", self.check_dependencies),
            ("Creando archivo .spec", self.create_spec_file),
            ("Optimizando archivos", self.optimize_game_files),
            ("Creando script de lanzamiento", self.create_launcher_script),
            ("Creando requirements.txt", self.create_requirements_file),
            ("Creando script de compilación", self.create_build_script),
            ("Creando README", self.create_readme)
        ]
        
        success_count = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if step_func():
                success_count += 1
                print(f"✅ {step_name} completado")
            else:
                print(f"❌ {step_name} falló")
        
        print("\n" + "="*60)
        print("📋 RESUMEN DE PREPARACIÓN")
        print("="*60)
        
        if success_count == total_steps:
            print("🎉 ¡Preparación completada exitosamente!")
            print("✅ El proyecto está listo para compilación")
            
            print("\n🎯 PRÓXIMOS PASOS:")
            print("1. cd build")
            print("2. python build_exe.py")
            print("3. El ejecutable se creará en build/dist/")
            
            return True
        else:
            print(f"⚠️ Preparación incompleta: {success_count}/{total_steps} pasos exitosos")
            print("🔧 Revisa los errores antes de proceder")
            return False

def main():
    """Función principal"""
    builder = ExeBuilder()
    success = builder.run_preparation()
    
    if success:
        print("\n🎉 ¡Sistema preparado para compilación!")
        print("✅ Puedes proceder con la compilación del .exe")
    else:
        print("\n⚠️ Hubo problemas en la preparación")
        print("🔧 Revisa los errores antes de continuar")

if __name__ == "__main__":
    main() 