#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DesafíoSaber - Script de Inicio del Sistema
============================================

Este script inicia todos los componentes del sistema DesafíoSaber:
- Servidor Flask (Backend API)
- Panel de Administración Web (React)
- Juego Principal (Tkinter)

Autor: Equipo DesafíoSaber
Versión: 1.0.0
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Imprime el banner de inicio"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎮 DESAFÍO SABER 🎮                      ║
    ║                                                              ║
    ║              Sistema de Juego Educativo Interactivo          ║
    ║                                                              ║
    ║  🚀 Iniciando todos los componentes del sistema...          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    try:
        import flask
        import requests
        import pygame
        from PIL import Image
        import tkinter
        print("✅ Todas las dependencias de Python están instaladas")
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    return True

def start_flask_server():
    """Inicia el servidor Flask"""
    print("🌐 Iniciando servidor Flask...")
    
    try:
        # Cambiar al directorio del servidor
        os.chdir("web_admin")
        
        # Iniciar servidor Flask
        server_process = subprocess.Popen([
            sys.executable, "server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un momento para que el servidor inicie
        time.sleep(3)
        
        # Verificar si el servidor está funcionando
        try:
            import requests
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor Flask iniciado correctamente")
                return server_process
            else:
                print("⚠️ Servidor Flask iniciado pero no responde correctamente")
                return server_process
        except:
            print("⚠️ Servidor Flask iniciado pero no se pudo verificar")
            return server_process
            
    except Exception as e:
        print(f"❌ Error iniciando servidor Flask: {e}")
        return None

def start_react_app():
    """Inicia la aplicación React"""
    print("⚛️ Iniciando aplicación React...")
    
    try:
        # Cambiar al directorio de React
        os.chdir("web_admin")
        
        # Verificar si node_modules existe
        if not os.path.exists("node_modules"):
            print("📦 Instalando dependencias de React...")
            subprocess.run(["npm", "install"], check=True)
        
        # Iniciar aplicación React
        react_process = subprocess.Popen([
            "npm", "start"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un momento para que React inicie
        time.sleep(5)
        
        print("✅ Aplicación React iniciada correctamente")
        return react_process
        
    except Exception as e:
        print(f"❌ Error iniciando aplicación React: {e}")
        return None

def start_game():
    """Inicia el juego principal"""
    print("🎮 Iniciando juego principal...")
    
    try:
        # Cambiar al directorio del juego
        os.chdir("game")
        
        # Iniciar juego
        game_process = subprocess.Popen([
            sys.executable, "main.py"
        ])
        
        print("✅ Juego principal iniciado correctamente")
        return game_process
        
    except Exception as e:
        print(f"❌ Error iniciando juego: {e}")
        return None

def open_browsers():
    """Abre los navegadores para las aplicaciones web"""
    print("🌐 Abriendo navegadores...")
    
    try:
        # Abrir panel de administración
        webbrowser.open("http://localhost:3000")
        print("✅ Panel de administración abierto")
        
        # Abrir API docs (si existe)
        webbrowser.open("http://localhost:5000/api")
        print("✅ Documentación de API abierta")
        
    except Exception as e:
        print(f"⚠️ Error abriendo navegadores: {e}")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar dependencias
    if not check_dependencies():
        return
    
    # Obtener directorio raíz
    root_dir = Path(__file__).parent
    os.chdir(root_dir)
    
    processes = []
    
    try:
        # Iniciar servidor Flask
        flask_process = start_flask_server()
        if flask_process:
            processes.append(flask_process)
        
        # Iniciar aplicación React
        react_process = start_react_app()
        if react_process:
            processes.append(react_process)
        
        # Esperar un momento para que los servicios web inicien
        time.sleep(2)
        
        # Abrir navegadores
        open_browsers()
        
        # Iniciar juego principal
        game_process = start_game()
        if game_process:
            processes.append(game_process)
        
        print("\n" + "="*60)
        print("🎉 ¡Sistema DesafíoSaber iniciado completamente!")
        print("="*60)
        print("\n📋 Componentes activos:")
        print("   🌐 Servidor Flask: http://localhost:5000")
        print("   ⚛️ Panel React: http://localhost:3000")
        print("   🎮 Juego Tkinter: Ejecutándose")
        print("\n💡 Para detener el sistema, presiona Ctrl+C")
        print("="*60)
        
        # Mantener el script ejecutándose
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo sistema...")
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
    except Exception as e:
        print(f"❌ Error en el sistema: {e}")
    finally:
        # Detener todos los procesos
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        print("✅ Sistema detenido correctamente")

if __name__ == "__main__":
    main() 