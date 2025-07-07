#!/usr/bin/env python3
"""
Script de prueba completa del sistema DesafíoSaber
Verifica que todos los componentes funcionen correctamente
"""

import os
import sys
import json
import subprocess
import time
import requests
import threading
from pathlib import Path

class SystemTester:
    def __init__(self):
        self.test_results = {}
        self.flask_process = None
        self.react_process = None
        
    def log(self, message, status="INFO"):
        """Registra un mensaje con timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        status_icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }
        icon = status_icons.get(status, "ℹ️")
        print(f"[{timestamp}] {icon} {message}")
    
    def test_file_structure(self):
        """Prueba la estructura de archivos"""
        self.log("Verificando estructura de archivos...")
        
        required_files = [
            'game/main.py',
            'web_admin/server.py',
            'web_admin/package.json',
            'data/questions.json',
            'data/config.json',
            'data/ranking.json',
            'requirements.txt',
            'start_system.py',
            'fix_system.py'
        ]
        
        required_dirs = [
            'game',
            'web_admin',
            'data',
            'assets/images',
            'assets/sounds',
            'sounds',
            'uploads'
        ]
        
        all_good = True
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log(f"Archivo encontrado: {file_path}", "SUCCESS")
            else:
                self.log(f"Archivo faltante: {file_path}", "ERROR")
                all_good = False
        
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                self.log(f"Directorio encontrado: {dir_path}", "SUCCESS")
            else:
                self.log(f"Directorio faltante: {dir_path}", "ERROR")
                all_good = False
        
        self.test_results['file_structure'] = all_good
        return all_good
    
    def test_dependencies(self):
        """Prueba las dependencias de Python"""
        self.log("Verificando dependencias de Python...")
        
        required_packages = [
            'flask',
            'flask_cors',
            'requests',
            'pygame',
            'PIL',
            'tkinter'
        ]
        
        all_good = True
        
        for package in required_packages:
            try:
                if package == 'PIL':
                    import PIL
                elif package == 'tkinter':
                    import tkinter
                else:
                    __import__(package.replace('-', '_'))
                self.log(f"Dependencia instalada: {package}", "SUCCESS")
            except ImportError:
                self.log(f"Dependencia faltante: {package}", "ERROR")
                all_good = False
        
        self.test_results['dependencies'] = all_good
        return all_good
    
    def test_data_files(self):
        """Prueba los archivos de datos JSON"""
        self.log("Verificando archivos de datos...")
        
        data_files = [
            ('data/questions.json', list),
            ('data/config.json', dict),
            ('data/ranking.json', list),
            ('usuarios.json', dict)
        ]
        
        all_good = True
        
        for file_path, expected_type in data_files:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, expected_type):
                        self.log(f"Archivo válido: {file_path}", "SUCCESS")
                    else:
                        self.log(f"Tipo incorrecto en {file_path}: esperado {expected_type}, obtenido {type(data)}", "ERROR")
                        all_good = False
                else:
                    self.log(f"Archivo no encontrado: {file_path}", "ERROR")
                    all_good = False
            except json.JSONDecodeError as e:
                self.log(f"JSON inválido en {file_path}: {e}", "ERROR")
                all_good = False
            except Exception as e:
                self.log(f"Error leyendo {file_path}: {e}", "ERROR")
                all_good = False
        
        self.test_results['data_files'] = all_good
        return all_good
    
    def test_flask_server(self):
        """Prueba el servidor Flask"""
        self.log("Iniciando servidor Flask...")
        
        try:
            # Cambiar al directorio web_admin
            original_dir = os.getcwd()
            os.chdir('web_admin')
            
            # Iniciar servidor Flask
            self.flask_process = subprocess.Popen([
                sys.executable, 'server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Esperar a que el servidor inicie
            time.sleep(3)
            
            if self.flask_process.poll() is None:
                # Probar la API
                try:
                    response = requests.get('http://localhost:5000/api/questions', timeout=5)
                    if response.status_code == 200:
                        self.log("Servidor Flask funcionando correctamente", "SUCCESS")
                        self.test_results['flask_server'] = True
                        return True
                    else:
                        self.log(f"Error en API Flask: {response.status_code}", "ERROR")
                        self.test_results['flask_server'] = False
                        return False
                except requests.exceptions.RequestException as e:
                    self.log(f"Error conectando a Flask: {e}", "ERROR")
                    self.test_results['flask_server'] = False
                    return False
            else:
                stdout, stderr = self.flask_process.communicate()
                self.log(f"Error iniciando Flask: {stderr}", "ERROR")
                self.test_results['flask_server'] = False
                return False
                
        except Exception as e:
            self.log(f"Error en prueba Flask: {e}", "ERROR")
            self.test_results['flask_server'] = False
            return False
        finally:
            # Volver al directorio original
            os.chdir(original_dir)
    
    def test_react_app(self):
        """Prueba la aplicación React"""
        self.log("Verificando aplicación React...")
        
        try:
            # Verificar que node_modules existe
            if not os.path.exists('web_admin/node_modules'):
                self.log("node_modules no encontrado, instalando dependencias...", "WARNING")
                os.chdir('web_admin')
                subprocess.run(['npm', 'install'], check=True, capture_output=True)
                os.chdir('..')
            
            # Verificar package.json
            package_json_path = 'web_admin/package.json'
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                if 'dependencies' in package_data and 'react' in package_data['dependencies']:
                    self.log("Aplicación React configurada correctamente", "SUCCESS")
                    self.test_results['react_app'] = True
                    return True
                else:
                    self.log("package.json inválido o faltan dependencias", "ERROR")
                    self.test_results['react_app'] = False
                    return False
            else:
                self.log("package.json no encontrado", "ERROR")
                self.test_results['react_app'] = False
                return False
                
        except Exception as e:
            self.log(f"Error verificando React: {e}", "ERROR")
            self.test_results['react_app'] = False
            return False
    
    def test_game_imports(self):
        """Prueba las importaciones del juego"""
        self.log("Verificando importaciones del juego...")
        
        try:
            # Agregar el directorio del juego al path
            sys.path.insert(0, os.path.join(os.getcwd(), 'game'))
            
            # Intentar importar la clase principal del juego
            from main import DesafioSaberApp
            
            self.log("Importaciones del juego funcionando", "SUCCESS")
            self.test_results['game_imports'] = True
            return True
            
        except ImportError as e:
            self.log(f"Error importando juego: {e}", "ERROR")
            self.test_results['game_imports'] = False
            return False
        except Exception as e:
            self.log(f"Error inesperado en juego: {e}", "ERROR")
            self.test_results['game_imports'] = False
            return False
    
    def test_assets(self):
        """Prueba los archivos de assets"""
        self.log("Verificando archivos de assets...")
        
        required_assets = [
            'assets/images/logo.png',
            'assets/images/menu_background.png',
            'sounds/acierto.mp3',
            'sounds/errado.mp3',
            'sounds/despliegue_opciones.mp3',
            'sounds/intro_music.mp3'
        ]
        
        all_good = True
        
        for asset in required_assets:
            if os.path.exists(asset):
                file_size = os.path.getsize(asset)
                if file_size > 0:
                    self.log(f"Asset válido: {asset} ({file_size} bytes)", "SUCCESS")
                else:
                    self.log(f"Asset vacío: {asset}", "WARNING")
            else:
                self.log(f"Asset faltante: {asset}", "ERROR")
                all_good = False
        
        self.test_results['assets'] = all_good
        return all_good
    
    def cleanup(self):
        """Limpia los procesos iniciados"""
        if self.flask_process:
            self.flask_process.terminate()
            self.log("Servidor Flask detenido")
        
        if self.react_process:
            self.react_process.terminate()
            self.log("Aplicación React detenida")
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        self.log("🧪 Iniciando pruebas completas del sistema DesafíoSaber")
        self.log("=" * 60)
        
        tests = [
            ("Estructura de archivos", self.test_file_structure),
            ("Dependencias de Python", self.test_dependencies),
            ("Archivos de datos", self.test_data_files),
            ("Assets", self.test_assets),
            ("Importaciones del juego", self.test_game_imports),
            ("Servidor Flask", self.test_flask_server),
            ("Aplicación React", self.test_react_app)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            self.log(f"\n🔍 Ejecutando: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                self.log(f"Error en prueba {test_name}: {e}", "ERROR")
                results[test_name] = False
        
        # Mostrar resumen
        self.log("\n" + "=" * 60)
        self.log("📊 RESUMEN DE PRUEBAS")
        self.log("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            self.log(f"{test_name}: {status}")
            if result:
                passed += 1
        
        self.log(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
        
        if passed == total:
            self.log("🎉 ¡Todas las pruebas pasaron! El sistema está listo.", "SUCCESS")
        else:
            self.log("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.", "WARNING")
        
        return passed == total

def main():
    """Función principal"""
    tester = SystemTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🚀 El sistema está listo para usar!")
            print("Para iniciar:")
            print("  python launch.py")
            print("  o")
            print("  python start_system.py")
        else:
            print("\n🔧 Ejecuta 'python fix_system.py' para corregir problemas")
        
    except KeyboardInterrupt:
        print("\n🛑 Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 