#!/usr/bin/env python3
"""
Script para iniciar solo el panel de administración de DesafíoSaber
Garantiza que solo se abra una ventana del navegador
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
import signal
import psutil
import socket

def check_ports():
    """Verifica si los puertos están ocupados"""
    ports_to_check = [3000, 5000]
    occupied_ports = []
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            occupied_ports.append(port)
    
    return occupied_ports

def kill_process_on_port(port):
    """Mata el proceso que está usando un puerto específico"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.laddr.port == port:
                        proc.terminate()
                        proc.wait(timeout=3)
                        print(f"✅ Proceso en puerto {port} terminado")
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
    except Exception as e:
        print(f"⚠️ Error terminando proceso en puerto {port}: {e}")
    
    return False

def is_browser_already_open():
    """Verifica si ya hay un navegador abierto con la aplicación"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if any('localhost:3000' in str(arg) for arg in cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    return False

def start_flask_server():
    """Inicia el servidor Flask"""
    print("🚀 Iniciando servidor Flask...")
    try:
        # Cambiar al directorio web_admin
        original_dir = os.getcwd()
        os.chdir('web_admin')
        
        # Iniciar servidor Flask en segundo plano
        process = subprocess.Popen([
            sys.executable, 'server.py'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Volver al directorio original
        os.chdir(original_dir)
        
        # Esperar a que el servidor inicie
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Servidor Flask iniciado en http://localhost:5000")
            return process
        else:
            print("❌ Error iniciando servidor Flask")
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando servidor Flask: {e}")
        return None

def start_react_app():
    """Inicia la aplicación React"""
    print("🌐 Iniciando aplicación React...")
    try:
        # Cambiar al directorio web_admin
        original_dir = os.getcwd()
        os.chdir('web_admin')
        
        # Verificar si node_modules existe
        if not os.path.exists('node_modules'):
            print("📦 Instalando dependencias de React...")
            subprocess.run(['npm', 'install'], check=True, capture_output=True)
        
        # Usar npm.cmd en Windows
        npm_command = 'npm.cmd' if os.name == 'nt' else 'npm'
        # Iniciar aplicación React en segundo plano
        process = subprocess.Popen([
            npm_command, 'start'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Volver al directorio original
        os.chdir(original_dir)
        
        # Esperar a que la app inicie
        time.sleep(8)
        
        if process.poll() is None:
            print("✅ Aplicación React iniciada en http://localhost:3000")
            return process
        else:
            print("❌ Error iniciando aplicación React")
            return None
            
    except Exception as e:
        print(f"❌ Error iniciando aplicación React: {e}")
        return None

def open_admin_panel():
    """Abre el panel de administración en el navegador (solo una vez)"""
    print("🌍 Verificando si ya está abierto...")
    
    # Esperar un poco más para que todo esté listo
    time.sleep(3)
    
    try:
        # Verificar si ya hay un navegador abierto con la aplicación
        if is_browser_already_open():
            print("✅ El panel ya está abierto en el navegador")
            return
        
        # Verificar si hay navegadores abiertos
        browser_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if any(browser in proc.info['name'].lower() for browser in ['chrome', 'firefox', 'edge', 'msedge']):
                    browser_processes.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Abrir el panel de administración
        if not browser_processes:
            # No hay navegadores abiertos, abrir uno nuevo
            webbrowser.open('http://localhost:3000')
            print("✅ Panel de administración abierto en nueva ventana: http://localhost:3000")
        else:
            # Hay navegadores abiertos, usar nueva pestaña
            webbrowser.open_new_tab('http://localhost:3000')
            print("✅ Panel de administración abierto en nueva pestaña: http://localhost:3000")
            
    except Exception as e:
        print(f"⚠️ No se pudo abrir automáticamente: {e}")
        print("   Abre manualmente: http://localhost:3000")

def signal_handler(signum, frame):
    """Maneja la señal de interrupción"""
    print("\n🛑 Deteniendo panel de administración...")
    sys.exit(0)

def main():
    print("🎮 Iniciando Panel de Administración DesafíoSaber")
    print("=" * 55)
    
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("web_admin/server.py"):
        print("❌ Error: No se encontró web_admin/server.py")
        print("   Ejecuta este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Verificar puertos ocupados
    occupied_ports = check_ports()
    if occupied_ports:
        print(f"⚠️ Puertos ocupados detectados: {occupied_ports}")
        response = input("¿Deseas terminar los procesos en estos puertos? (s/n): ").lower()
        if response == 's':
            for port in occupied_ports:
                kill_process_on_port(port)
        else:
            print("❌ No se pueden iniciar los servicios con puertos ocupados")
            sys.exit(1)
    
    # Guardar directorio original
    original_dir = os.getcwd()
    
    flask_process = None
    react_process = None
    
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
            if flask_process:
                flask_process.terminate()
            sys.exit(1)
        
        # Abrir panel de administración (solo una vez)
        open_admin_panel()
        
        print("\n🎉 ¡Panel de administración iniciado correctamente!")
        print("\n📋 Información:")
        print("   🌐 Panel de administración: http://localhost:3000")
        print("   🔌 API del servidor: http://localhost:5000/api/")
        print("   🎮 Para ejecutar el juego: python game/main.py")
        print("\n💡 Presiona Ctrl+C para detener el panel")
        print("💡 La sesión se mantendrá al refrescar la página")
        
        # Mantener el script ejecutándose
        try:
            while True:
                time.sleep(1)
                # Verificar que los procesos sigan ejecutándose
                if flask_process and flask_process.poll() is not None:
                    print("❌ Servidor Flask se detuvo inesperadamente")
                    break
                if react_process and react_process.poll() is not None:
                    print("❌ Aplicación React se detuvo inesperadamente")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo panel de administración...")
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo panel de administración...")
        
    finally:
        # Volver al directorio original
        os.chdir(original_dir)
        
        # Terminar procesos
        if flask_process:
            try:
                flask_process.terminate()
                flask_process.wait(timeout=5)
                print("✅ Servidor Flask detenido")
            except:
                flask_process.kill()
        
        if react_process:
            try:
                react_process.terminate()
                react_process.wait(timeout=5)
                print("✅ Aplicación React detenida")
            except:
                react_process.kill()
        
        print("👋 Panel de administración detenido")

if __name__ == "__main__":
    main() 