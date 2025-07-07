#!/usr/bin/env python3
"""
Script de Inicio Completo para DesafíoSaber
Inicia todos los servicios: servidor de estadísticas, panel web y juego
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from datetime import datetime

def print_banner():
    """Imprime el banner de inicio"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎮 DesafíoSaber v2.0 🎮                    ║
    ║                                                              ║
    ║  Sistema Completo de Gestión y Estadísticas                 ║
    ║  ========================================================    ║
    ║                                                              ║
    ║  🚀 Servidor de Estadísticas (Puerto 5001)                  ║
    ║  🌐 Panel Web de Administración (Puerto 3000)               ║
    ║  🎯 Juego Principal (Tkinter)                                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def start_stats_server():
    """Inicia el servidor de estadísticas"""
    print("🚀 Iniciando Servidor de Estadísticas...")
    try:
        subprocess.run([sys.executable, "start_stats_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando servidor de estadísticas: {e}")
    except KeyboardInterrupt:
        print("👋 Servidor de estadísticas detenido")

def start_web_admin():
    """Inicia el panel web de administración"""
    print("🌐 Iniciando Panel Web de Administración...")
    web_admin_dir = os.path.join(os.path.dirname(__file__), 'web_admin')
    
    if not os.path.exists(web_admin_dir):
        print("❌ Directorio web_admin no encontrado")
        return
    
    try:
        # Cambiar al directorio del panel web
        os.chdir(web_admin_dir)
        
        # Instalar dependencias si es necesario
        print("📦 Verificando dependencias del panel web...")
        subprocess.run(["npm", "install"], check=True, capture_output=True)
        
        # Iniciar el servidor de desarrollo
        print("🌐 Iniciando servidor de desarrollo...")
        subprocess.run(["npm", "start"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando panel web: {e}")
    except KeyboardInterrupt:
        print("👋 Panel web detenido")
    finally:
        # Volver al directorio original
        os.chdir(os.path.dirname(__file__))

def start_game():
    """Inicia el juego principal"""
    print("🎮 Iniciando Juego Principal...")
    try:
        game_dir = os.path.join(os.path.dirname(__file__), 'game')
        os.chdir(game_dir)
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando juego: {e}")
    except KeyboardInterrupt:
        print("👋 Juego detenido")
    finally:
        os.chdir(os.path.dirname(__file__))

def open_browsers():
    """Abre los navegadores para los servicios web"""
    time.sleep(5)  # Esperar a que los servicios se inicien
    
    print("🌐 Abriendo navegadores...")
    
    # Panel de administración
    try:
        webbrowser.open('http://localhost:3000')
        print("✅ Panel de administración abierto en http://localhost:3000")
    except Exception as e:
        print(f"❌ Error abriendo panel de administración: {e}")
    
    # API de estadísticas
    try:
        webbrowser.open('http://localhost:5001/api/health')
        print("✅ API de estadísticas verificada en http://localhost:5001/api/health")
    except Exception as e:
        print(f"❌ Error verificando API de estadísticas: {e}")

def main():
    """Función principal"""
    print_banner()
    
    print("🔄 Iniciando todos los servicios...")
    print("=" * 60)
    
    # Iniciar servidor de estadísticas en un hilo
    stats_thread = threading.Thread(target=start_stats_server, daemon=True)
    stats_thread.start()
    
    # Iniciar panel web en un hilo
    web_thread = threading.Thread(target=start_web_admin, daemon=True)
    web_thread.start()
    
    # Abrir navegadores en un hilo
    browser_thread = threading.Thread(target=open_browsers, daemon=True)
    browser_thread.start()
    
    # Iniciar juego en el hilo principal
    try:
        start_game()
    except KeyboardInterrupt:
        print("\n👋 Sistema detenido por el usuario")
    except Exception as e:
        print(f"❌ Error en el sistema: {e}")

if __name__ == "__main__":
    main() 