#!/usr/bin/env python3
"""
Script de Verificación de Conexiones para DesafíoSaber
Verifica que todos los servicios estén funcionando correctamente
"""

import requests
import json
import time
import subprocess
import sys
import os
import threading
from datetime import datetime

class ConnectionTester:
    def __init__(self):
        self.results = {
            'backend': {'status': False, 'message': '', 'response_time': 0},
            'frontend': {'status': False, 'message': '', 'response_time': 0},
            'api_endpoints': {'status': False, 'message': '', 'details': {}},
            'game_files': {'status': False, 'message': '', 'details': {}},
            'database_files': {'status': False, 'message': '', 'details': {}}
        }
        
    def print_banner(self):
        """Imprime el banner de verificación"""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                🔍 Verificación de Conexiones 🔍               ║
    ║                                                              ║
    ║  DesafíoSaber v2.0 - Sistema Completo                       ║
    ║  ========================================================    ║
    ║                                                              ║
    ║  Verificando:                                                ║
    ║  • Backend Flask (Puerto 5000)                              ║
    ║  • Frontend React (Puerto 3000)                             ║
    ║  • Endpoints de la API                                      ║
    ║  • Archivos del juego                                       ║
    ║  • Base de datos local                                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def test_backend_connection(self):
        """Verifica la conexión al backend Flask"""
        print("🔧 Verificando Backend Flask (Puerto 5000)...")
        try:
            start_time = time.time()
            response = requests.get('http://localhost:5000/api/config', timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.results['backend']['status'] = True
                self.results['backend']['message'] = f"✅ Backend funcionando correctamente"
                self.results['backend']['response_time'] = round(response_time, 3)
                print(f"   ✅ Backend: OK (Respuesta en {response_time:.3f}s)")
                return True
            else:
                self.results['backend']['message'] = f"❌ Backend respondió con código {response.status_code}"
                print(f"   ❌ Backend: Error - Código {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.results['backend']['message'] = "❌ No se pudo conectar al backend"
            print("   ❌ Backend: No se pudo conectar")
            return False
        except requests.exceptions.Timeout:
            self.results['backend']['message'] = "❌ Timeout al conectar con el backend"
            print("   ❌ Backend: Timeout")
            return False
        except Exception as e:
            self.results['backend']['message'] = f"❌ Error inesperado: {str(e)}"
            print(f"   ❌ Backend: Error inesperado - {str(e)}")
            return False
    
    def test_frontend_connection(self):
        """Verifica la conexión al frontend React"""
        print("🌐 Verificando Frontend React (Puerto 3000)...")
        try:
            start_time = time.time()
            response = requests.get('http://localhost:3000', timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.results['frontend']['status'] = True
                self.results['frontend']['message'] = f"✅ Frontend funcionando correctamente"
                self.results['frontend']['response_time'] = round(response_time, 3)
                print(f"   ✅ Frontend: OK (Respuesta en {response_time:.3f}s)")
                return True
            else:
                self.results['frontend']['message'] = f"❌ Frontend respondió con código {response.status_code}"
                print(f"   ❌ Frontend: Error - Código {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.results['frontend']['message'] = "❌ No se pudo conectar al frontend"
            print("   ❌ Frontend: No se pudo conectar")
            return False
        except requests.exceptions.Timeout:
            self.results['frontend']['message'] = "❌ Timeout al conectar con el frontend"
            print("   ❌ Frontend: Timeout")
            return False
        except Exception as e:
            self.results['frontend']['message'] = f"❌ Error inesperado: {str(e)}"
            print(f"   ❌ Frontend: Error inesperado - {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Verifica los endpoints principales de la API"""
        print("🔌 Verificando Endpoints de la API...")
        endpoints = [
            ('/api/questions', 'Preguntas'),
            ('/api/categories', 'Categorías'),
            ('/api/ranking', 'Ranking'),
            ('/api/players', 'Jugadores'),
            ('/api/config', 'Configuración'),
            ('/api/game-modes', 'Modos de Juego'),
            ('/api/sounds', 'Sonidos'),
            ('/api/achievements', 'Logros'),
            ('/api/user_stats', 'Estadísticas de Usuario'),
            ('/api/category-colors', 'Colores de Categorías'),
            ('/api/button-styles', 'Estilos de Botones')
        ]
        
        working_endpoints = 0
        total_endpoints = len(endpoints)
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f'http://localhost:5000{endpoint}', timeout=3)
                if response.status_code in [200, 201]:
                    working_endpoints += 1
                    print(f"   ✅ {name}: OK")
                    self.results['api_endpoints']['details'][endpoint] = {
                        'status': True,
                        'name': name,
                        'code': response.status_code
                    }
                else:
                    print(f"   ⚠️ {name}: Código {response.status_code}")
                    self.results['api_endpoints']['details'][endpoint] = {
                        'status': False,
                        'name': name,
                        'code': response.status_code
                    }
            except Exception as e:
                print(f"   ❌ {name}: Error - {str(e)}")
                self.results['api_endpoints']['details'][endpoint] = {
                    'status': False,
                    'name': name,
                    'error': str(e)
                }
        
        success_rate = (working_endpoints / total_endpoints) * 100
        self.results['api_endpoints']['status'] = success_rate >= 80
        self.results['api_endpoints']['message'] = f"✅ {working_endpoints}/{total_endpoints} endpoints funcionando ({success_rate:.1f}%)"
        
        print(f"   📊 Resultado: {working_endpoints}/{total_endpoints} endpoints OK ({success_rate:.1f}%)")
        return success_rate >= 80
    
    def test_game_files(self):
        """Verifica que los archivos principales del juego existan"""
        print("🎮 Verificando Archivos del Juego...")
        game_files = [
            ('game/main.py', 'Juego Principal'),
            ('game/achievements.py', 'Sistema de Logros'),
            ('game/api_client.py', 'Cliente API'),
            ('game/cloud_sync.py', 'Sincronización en Nube'),
            ('game/user_registration.py', 'Registro de Usuarios'),
            ('game/wheel_animation.py', 'Animaciones'),
            ('assets/images/logo.png', 'Logo del Juego'),
            ('assets/sounds/acierto.mp3', 'Sonido Acierto'),
            ('assets/sounds/errado.mp3', 'Sonido Error'),
            ('assets/sounds/despliegue_opciones.mp3', 'Sonido Despliegue')
        ]
        
        existing_files = 0
        total_files = len(game_files)
        
        for file_path, name in game_files:
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            if os.path.exists(full_path):
                existing_files += 1
                print(f"   ✅ {name}: Encontrado")
                self.results['game_files']['details'][file_path] = {
                    'status': True,
                    'name': name,
                    'size': os.path.getsize(full_path)
                }
            else:
                print(f"   ❌ {name}: No encontrado")
                self.results['game_files']['details'][file_path] = {
                    'status': False,
                    'name': name
                }
        
        success_rate = (existing_files / total_files) * 100
        self.results['game_files']['status'] = success_rate >= 90
        self.results['game_files']['message'] = f"✅ {existing_files}/{total_files} archivos encontrados ({success_rate:.1f}%)"
        
        print(f"   📊 Resultado: {existing_files}/{total_files} archivos OK ({success_rate:.1f}%)")
        return success_rate >= 90
    
    def test_database_files(self):
        """Verifica que los archivos de base de datos existan y sean válidos"""
        print("💾 Verificando Archivos de Base de Datos...")
        db_files = [
            ('data/questions.json', 'Preguntas'),
            ('data/ranking.json', 'Ranking'),
            ('data/config.json', 'Configuración'),
            ('data/categories.json', 'Categorías'),
            ('data/usuarios.json', 'Usuarios'),
            ('data/user_stats.json', 'Estadísticas de Usuario'),
            ('data/achievements.json', 'Logros'),
            ('data/game_history.json', 'Historial de Juegos'),
            ('data/admins.json', 'Administradores'),
            ('data/button_styles.json', 'Estilos de Botones')
        ]
        
        valid_files = 0
        total_files = len(db_files)
        
        for file_path, name in db_files:
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Verificar que el archivo no esté vacío
                    if data:
                        valid_files += 1
                        print(f"   ✅ {name}: Válido ({len(data) if isinstance(data, list) else len(data.keys())} elementos)")
                        self.results['database_files']['details'][file_path] = {
                            'status': True,
                            'name': name,
                            'elements': len(data) if isinstance(data, list) else len(data.keys()),
                            'size': os.path.getsize(full_path)
                        }
                    else:
                        print(f"   ⚠️ {name}: Vacío")
                        self.results['database_files']['details'][file_path] = {
                            'status': False,
                            'name': name,
                            'error': 'Archivo vacío'
                        }
                except json.JSONDecodeError:
                    print(f"   ❌ {name}: JSON inválido")
                    self.results['database_files']['details'][file_path] = {
                        'status': False,
                        'name': name,
                        'error': 'JSON inválido'
                    }
                except Exception as e:
                    print(f"   ❌ {name}: Error - {str(e)}")
                    self.results['database_files']['details'][file_path] = {
                        'status': False,
                        'name': name,
                        'error': str(e)
                    }
            else:
                print(f"   ❌ {name}: No encontrado")
                self.results['database_files']['details'][file_path] = {
                    'status': False,
                    'name': name,
                    'error': 'Archivo no encontrado'
                }
        
        success_rate = (valid_files / total_files) * 100
        self.results['database_files']['status'] = success_rate >= 80
        self.results['database_files']['message'] = f"✅ {valid_files}/{total_files} archivos válidos ({success_rate:.1f}%)"
        
        print(f"   📊 Resultado: {valid_files}/{total_files} archivos válidos ({success_rate:.1f}%)")
        return success_rate >= 80
    
    def generate_report(self):
        """Genera un reporte completo de la verificación"""
        print("\n" + "="*60)
        print("📋 REPORTE DE VERIFICACIÓN")
        print("="*60)
        
        total_tests = 5
        passed_tests = sum([
            self.results['backend']['status'],
            self.results['frontend']['status'],
            self.results['api_endpoints']['status'],
            self.results['game_files']['status'],
            self.results['database_files']['status']
        ])
        
        overall_status = "✅ SISTEMA LISTO" if passed_tests >= 4 else "⚠️ SISTEMA CON PROBLEMAS"
        
        print(f"\n🎯 Estado General: {overall_status}")
        print(f"📊 Resultado: {passed_tests}/{total_tests} pruebas exitosas")
        
        print(f"\n🔧 Backend Flask:")
        print(f"   {self.results['backend']['message']}")
        if self.results['backend']['response_time'] > 0:
            print(f"   ⏱️ Tiempo de respuesta: {self.results['backend']['response_time']}s")
        
        print(f"\n🌐 Frontend React:")
        print(f"   {self.results['frontend']['message']}")
        if self.results['frontend']['response_time'] > 0:
            print(f"   ⏱️ Tiempo de respuesta: {self.results['frontend']['response_time']}s")
        
        print(f"\n🔌 API Endpoints:")
        print(f"   {self.results['api_endpoints']['message']}")
        
        print(f"\n🎮 Archivos del Juego:")
        print(f"   {self.results['game_files']['message']}")
        
        print(f"\n💾 Base de Datos:")
        print(f"   {self.results['database_files']['message']}")
        
        # Guardar reporte en archivo
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'results': self.results
        }
        
        report_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'connection_test_report.json')
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        
        return passed_tests >= 4
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas de verificación"""
        self.print_banner()
        
        print("🚀 Iniciando verificación de conexiones...")
        print("="*60)
        
        # Ejecutar pruebas
        self.test_backend_connection()
        print()
        
        self.test_frontend_connection()
        print()
        
        self.test_api_endpoints()
        print()
        
        self.test_game_files()
        print()
        
        self.test_database_files()
        print()
        
        # Generar reporte
        success = self.generate_report()
        
        if success:
            print("\n🎉 ¡Sistema verificado exitosamente!")
            print("✅ El juego está listo para compilación y uso")
        else:
            print("\n⚠️ Se encontraron problemas en el sistema")
            print("🔧 Revisa los errores antes de proceder")
        
        return success

def main():
    """Función principal"""
    tester = ConnectionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Ejecutar: python scripts/start/start_complete_system.py")
        print("2. Probar el juego: python game/main.py")
        print("3. Acceder al panel: http://localhost:3000")
        print("4. Verificar API: http://localhost:5000/api/config")
    else:
        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("1. Verificar que los servicios estén ejecutándose")
        print("2. Revisar los logs de error")
        print("3. Ejecutar: python scripts/fix_system.py")
        print("4. Volver a ejecutar este script")

if __name__ == "__main__":
    main() 