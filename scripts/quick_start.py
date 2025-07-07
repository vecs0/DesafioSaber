#!/usr/bin/env python3
"""
Script de Inicio Rápido para DesafíoSaber
Permite iniciar y probar el sistema completo de manera fácil
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from datetime import datetime

class QuickStart:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.processes = []
        
    def print_banner(self):
        """Imprime el banner de inicio rápido"""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                ⚡ Inicio Rápido DesafíoSaber ⚡               ║
    ║                                                              ║
    ║  Sistema Completo de Gestión y Estadísticas                 ║
    ║  ========================================================    ║
    ║                                                              ║
    ║  🚀 Iniciando todos los servicios automáticamente           ║
    ║  🌐 Panel Web: http://localhost:3000                        ║
    ║  🔧 API Backend: http://localhost:5000                      ║
    ║  🎮 Juego: Se abrirá automáticamente                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_ports(self):
        """Verifica si los puertos están disponibles"""
        import socket
        
        ports_to_check = [3000, 5000]
        available_ports = []
        
        for port in ports_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result != 0:
                    available_ports.append(port)
                else:
                    print(f"⚠️ Puerto {port} ya está en uso")
            except:
                available_ports.append(port)
        
        return available_ports
    
    def start_backend(self):
        """Inicia el backend Flask"""
        print("🔧 Iniciando Backend Flask...")
        try:
            backend_dir = os.path.join(self.project_root, 'web_admin')
            os.chdir(backend_dir)
            
            # Verificar si Flask está instalado
            try:
                import flask
            except ImportError:
                print("📦 Instalando Flask...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors', 'flask-socketio'], 
                             check=True, capture_output=True)
            
            # Iniciar servidor Flask
            process = subprocess.Popen([
                sys.executable, 'server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('Backend Flask', process))
            print("✅ Backend Flask iniciado")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando backend: {e}")
            return False
    
    def start_frontend(self):
        """Inicia el frontend React"""
        print("🌐 Iniciando Frontend React...")
        try:
            frontend_dir = os.path.join(self.project_root, 'web_admin')
            os.chdir(frontend_dir)
            
            # Verificar si Node.js está instalado
            try:
                subprocess.run(['node', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ Node.js no está instalado. El frontend no se iniciará.")
                print("💡 Instala Node.js desde https://nodejs.org/")
                return False
            
            # Instalar dependencias si es necesario
            if not os.path.exists('node_modules'):
                print("📦 Instalando dependencias de React...")
                subprocess.run(['npm', 'install'], check=True, capture_output=True)
            
            # Iniciar servidor de desarrollo
            process = subprocess.Popen([
                'npm', 'start'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(('Frontend React', process))
            print("✅ Frontend React iniciado")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando frontend: {e}")
            return False
    
    def start_game(self):
        """Inicia el juego principal"""
        print("🎮 Iniciando Juego Principal...")
        try:
            game_dir = os.path.join(self.project_root, 'game')
            os.chdir(game_dir)
            
            # Verificar dependencias del juego
            try:
                import pygame
                import PIL
                import requests
            except ImportError as e:
                print(f"📦 Instalando dependencias faltantes: {e}")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pygame', 'pillow', 'requests'], 
                             check=True, capture_output=True)
            
            # Iniciar juego en un hilo separado
            def run_game():
                try:
                    subprocess.run([sys.executable, 'main.py'], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error en el juego: {e}")
                except KeyboardInterrupt:
                    print("👋 Juego detenido")
            
            game_thread = threading.Thread(target=run_game, daemon=True)
            game_thread.start()
            
            print("✅ Juego iniciado")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando juego: {e}")
            return False
    
    def open_browsers(self):
        """Abre los navegadores para los servicios web"""
        print("🌐 Abriendo navegadores...")
        
        # Esperar un poco para que los servicios se inicien
        time.sleep(3)
        
        try:
            # Panel de administración
            webbrowser.open('http://localhost:3000')
            print("✅ Panel de administración abierto")
        except Exception as e:
            print(f"❌ Error abriendo panel: {e}")
        
        try:
            # API de backend
            webbrowser.open('http://localhost:5000/api/config')
            print("✅ API de backend verificada")
        except Exception as e:
            print(f"❌ Error verificando API: {e}")
    
    def show_status(self):
        """Muestra el estado de los servicios"""
        print("\n" + "="*60)
        print("📊 ESTADO DE LOS SERVICIOS")
        print("="*60)
        
        services = [
            ("🌐 Panel Web", "http://localhost:3000"),
            ("🔧 API Backend", "http://localhost:5000"),
            ("🎮 Juego", "Ejecutándose en ventana separada"),
        ]
        
        for service_name, url in services:
            print(f"{service_name}: {url}")
        
        print("\n🎯 COMANDOS ÚTILES:")
        print("• Verificar conexiones: python scripts/test_connections.py")
        print("• Preparar .exe: python scripts/prepare_exe_build.py")
        print("• Detener servicios: Ctrl+C")
        
        print("\n💡 CONSEJOS:")
        print("• El panel web permite gestionar preguntas, usuarios y estadísticas")
        print("• El juego se ejecuta independientemente del panel web")
        print("• Los datos se sincronizan automáticamente entre ambos")
    
    def cleanup(self):
        """Limpia los procesos al salir"""
        print("\n🛑 Deteniendo servicios...")
        
        for service_name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {service_name} detenido")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ {service_name} forzado a detener")
            except Exception as e:
                print(f"❌ Error deteniendo {service_name}: {e}")
    
    def run(self):
        """Ejecuta el inicio rápido completo"""
        self.print_banner()
        
        # Verificar puertos
        print("🔍 Verificando puertos...")
        available_ports = self.check_ports()
        
        if not available_ports:
            print("❌ Los puertos necesarios no están disponibles")
            return False
        
        print("✅ Puertos disponibles")
        
        # Iniciar servicios
        print("\n🚀 Iniciando servicios...")
        print("="*40)
        
        services_started = 0
        
        if self.start_backend():
            services_started += 1
        
        if self.start_frontend():
            services_started += 1
        
        if self.start_game():
            services_started += 1
        
        # Abrir navegadores
        browser_thread = threading.Thread(target=self.open_browsers, daemon=True)
        browser_thread.start()
        
        # Mostrar estado
        self.show_status()
        
        print(f"\n✅ {services_started}/3 servicios iniciados")
        
        if services_started >= 2:
            print("🎉 ¡Sistema iniciado exitosamente!")
            print("🌐 Accede al panel web en: http://localhost:3000")
            print("🎮 El juego se abrirá automáticamente")
            
            try:
                # Mantener el script ejecutándose
                print("\n⏳ Presiona Ctrl+C para detener todos los servicios...")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Deteniendo sistema...")
                self.cleanup()
                print("✅ Sistema detenido correctamente")
        else:
            print("⚠️ Algunos servicios no se pudieron iniciar")
            print("🔧 Revisa los errores y vuelve a intentar")
            return False
        
        return True

def main():
    """Función principal"""
    quick_start = QuickStart()
    
    try:
        success = quick_start.run()
        if not success:
            print("\n🔧 ACCIONES RECOMENDADAS:")
            print("1. Verificar que Python y Node.js estén instalados")
            print("2. Ejecutar: python scripts/test_connections.py")
            print("3. Revisar los logs de error")
            print("4. Contactar al soporte técnico")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        quick_start.cleanup()

if __name__ == "__main__":
    main() 