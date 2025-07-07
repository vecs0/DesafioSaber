#!/usr/bin/env python3
"""
Script para iniciar todo el sistema DesafíoSaber
Inicia el servidor Flask y la aplicación React
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    # Verificar Python
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Verificar pip
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      capture_output=True, check=True)
        print("✅ pip disponible")
    except:
        print("❌ pip no disponible")
        return False
    
    # Verificar dependencias principales
    required_packages = ['flask', 'flask-cors', 'requests', 'pygame', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} no instalado")
            missing_packages.append(package)
    
    # Instalar dependencias faltantes
    if missing_packages:
        print(f"\n⚠️ Instalando dependencias faltantes: {', '.join(missing_packages)}")
        for package in missing_packages:
            if package == 'PIL':
                package = 'pillow'
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Instalado: {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Error instalando: {package}")
            return False
    
    return True

def start_flask_server():
    """Inicia el servidor Flask"""
    print("🚀 Iniciando servidor Flask...")
    try:
        # Cambiar al directorio web_admin
        os.chdir('web_admin')
        
        # Iniciar servidor Flask
        process = subprocess.Popen([
            sys.executable, 'server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Esperar un momento para que el servidor inicie
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Servidor Flask iniciado en http://localhost:5000")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Error iniciando servidor Flask:")
            print(stderr)
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando servidor Flask: {e}")
        return None

def start_react_app():
    """Inicia la aplicación React"""
    print("🌐 Iniciando aplicación React...")
    try:
        # Cambiar al directorio web_admin
        os.chdir('web_admin')
        
        # Verificar si node_modules existe
        if not os.path.exists('node_modules'):
            print("📦 Instalando dependencias de React...")
            subprocess.run(['npm', 'install'], check=True)
        
        # Iniciar aplicación React
        process = subprocess.Popen([
            'npm', 'start'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Esperar un momento para que la app inicie
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Aplicación React iniciada en http://localhost:3000")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Error iniciando aplicación React:")
            print(stderr)
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando aplicación React: {e}")
        return None

def open_browsers():
    """Abre el navegador con el panel de administración"""
    print("🌍 Abriendo panel de administración...")
    
    # Esperar un poco más para que todo esté listo
    time.sleep(3)
    
    try:
        # Abrir solo el panel de administración
        webbrowser.open('http://localhost:3000')
        print("✅ Panel de administración abierto en http://localhost:3000")
    except Exception as e:
        print(f"⚠️ No se pudo abrir el panel automáticamente: {e}")
        print("   Abre manualmente: http://localhost:3000")

def main():
    print("🎮 Iniciando Sistema DesafíoSaber")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("web_admin/server.py"):
        print("❌ Error: No se encontró web_admin/server.py")
        print("   Ejecuta este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ Faltan dependencias. Instálalas con:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n✅ Todas las dependencias están instaladas")
    
    # Guardar directorio original
    original_dir = os.getcwd()
    
    try:
        # Iniciar servidor Flask
        flask_process = start_flask_server()
        if not flask_process:
            print("❌ No se pudo iniciar el servidor Flask")
            sys.exit(1)
        
        # Iniciar aplicación React
        react_process = start_react_app()
        if not react_process:
            print("❌ No se pudo iniciar la aplicación React")
            flask_process.terminate()
            sys.exit(1)
        
        # Abrir navegadores
        open_browsers()
        
        print("\n🎉 ¡Sistema iniciado correctamente!")
        print("\n📋 Resumen:")
        print("   🌐 Panel de administración: http://localhost:3000")
        print("   🔌 API del servidor: http://localhost:5000/api/")
        print("   🎮 Para ejecutar el juego: python game/main.py")
        print("\n💡 Presiona Ctrl+C para detener el sistema")
        
        # Mantener el script ejecutándose
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo sistema...")
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
        
    finally:
        # Volver al directorio original
        os.chdir(original_dir)
        
        # Terminar procesos
        if 'flask_process' in locals() and flask_process:
            flask_process.terminate()
            print("✅ Servidor Flask detenido")
        
        if 'react_process' in locals() and react_process:
            react_process.terminate()
            print("✅ Aplicación React detenida")
        
        print("👋 Sistema detenido")

if __name__ == "__main__":
    main() 