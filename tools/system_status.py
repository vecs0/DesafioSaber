#!/usr/bin/env python3
"""
Script de Estado del Sistema DesafíoSaber
Muestra un resumen completo del estado de todos los componentes
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

class SystemStatus:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'UNKNOWN',
            'components': {},
            'recommendations': []
        }
        
    def print_banner(self):
        """Imprime el banner de estado del sistema"""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                📊 Estado del Sistema 📊                      ║
    ║                                                              ║
    ║  DesafíoSaber v2.0 - Análisis Completo                      ║
    ║  ========================================================    ║
    ║                                                              ║
    ║  Verificando todos los componentes del sistema              ║
    ║  Generando reporte detallado de estado                      ║
    ║  Proporcionando recomendaciones de optimización             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_file_structure(self):
        """Verifica la estructura de archivos del proyecto"""
        print("📁 Verificando estructura de archivos...")
        
        required_dirs = [
            ('game', 'Juego Principal'),
            ('web_admin', 'Panel Web'),
            ('data', 'Base de Datos'),
            ('assets', 'Recursos'),
            ('scripts', 'Scripts de Utilidad'),
            ('docs', 'Documentación'),
            ('backups', 'Backups'),
            ('tests', 'Pruebas')
        ]
        
        required_files = [
            ('game/main.py', 'Aplicación Principal'),
            ('web_admin/server.py', 'Servidor Backend'),
            ('web_admin/package.json', 'Configuración Node.js'),
            ('data/questions.json', 'Base de Preguntas'),
            ('data/users.json', 'Base de Usuarios'),
            ('data/ranking.json', 'Ranking'),
            ('scripts/test_connections.py', 'Script de Verificación'),
            ('README_FINAL.md', 'Documentación Principal')
        ]
        
        structure_status = {'directories': {}, 'files': {}, 'overall': True}
        
        # Verificar directorios
        for dir_path, dir_name in required_dirs:
            full_path = os.path.join(self.project_root, dir_path)
            if os.path.exists(full_path):
                structure_status['directories'][dir_path] = {
                    'status': True,
                    'name': dir_name,
                    'exists': True
                }
                print(f"   ✅ {dir_name}: Encontrado")
            else:
                structure_status['directories'][dir_path] = {
                    'status': False,
                    'name': dir_name,
                    'exists': False
                }
                structure_status['overall'] = False
                print(f"   ❌ {dir_name}: No encontrado")
        
        # Verificar archivos
        for file_path, file_name in required_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                structure_status['files'][file_path] = {
                    'status': True,
                    'name': file_name,
                    'exists': True,
                    'size': size
                }
                print(f"   ✅ {file_name}: Encontrado ({size} bytes)")
            else:
                structure_status['files'][file_path] = {
                    'status': False,
                    'name': file_name,
                    'exists': False
                }
                structure_status['overall'] = False
                print(f"   ❌ {file_name}: No encontrado")
        
        self.status['components']['file_structure'] = structure_status
        return structure_status['overall']
    
    def check_database_integrity(self):
        """Verifica la integridad de la base de datos"""
        print("\n💾 Verificando integridad de la base de datos...")
        
        db_files = [
            ('data/questions.json', 'Preguntas'),
            ('data/users.json', 'Usuarios'),
            ('data/ranking.json', 'Ranking'),
            ('data/config.json', 'Configuración'),
            ('data/categories.json', 'Categorías'),
            ('data/achievements.json', 'Logros'),
            ('data/user_stats.json', 'Estadísticas de Usuario'),
            ('data/game_history.json', 'Historial de Juegos')
        ]
        
        db_status = {'files': {}, 'overall': True, 'total_questions': 0, 'total_users': 0}
        
        for file_path, file_name in db_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Verificar que no esté vacío
                    if data:
                        if isinstance(data, list):
                            count = len(data)
                        elif isinstance(data, dict):
                            count = len(data.keys())
                        else:
                            count = 1
                        
                        db_status['files'][file_path] = {
                            'status': True,
                            'name': file_name,
                            'valid': True,
                            'count': count,
                            'size': os.path.getsize(full_path)
                        }
                        
                        # Contar preguntas y usuarios
                        if 'questions' in file_path.lower():
                            db_status['total_questions'] = count
                        elif 'users' in file_path.lower():
                            db_status['total_users'] = count
                        
                        print(f"   ✅ {file_name}: Válido ({count} elementos)")
                    else:
                        db_status['files'][file_path] = {
                            'status': False,
                            'name': file_name,
                            'valid': False,
                            'error': 'Archivo vacío'
                        }
                        db_status['overall'] = False
                        print(f"   ⚠️ {file_name}: Vacío")
                        
                except json.JSONDecodeError:
                    db_status['files'][file_path] = {
                        'status': False,
                        'name': file_name,
                        'valid': False,
                        'error': 'JSON inválido'
                    }
                    db_status['overall'] = False
                    print(f"   ❌ {file_name}: JSON inválido")
                except Exception as e:
                    db_status['files'][file_path] = {
                        'status': False,
                        'name': file_name,
                        'valid': False,
                        'error': str(e)
                    }
                    db_status['overall'] = False
                    print(f"   ❌ {file_name}: Error - {str(e)}")
            else:
                db_status['files'][file_path] = {
                    'status': False,
                    'name': file_name,
                    'valid': False,
                    'error': 'Archivo no encontrado'
                }
                db_status['overall'] = False
                print(f"   ❌ {file_name}: No encontrado")
        
        self.status['components']['database_integrity'] = db_status
        return db_status['overall']
    
    def check_service_connectivity(self):
        """Verifica la conectividad de los servicios"""
        print("\n🔌 Verificando conectividad de servicios...")
        
        services = [
            ('http://localhost:5000/api/config', 'Backend Flask'),
            ('http://localhost:3000', 'Frontend React')
        ]
        
        connectivity_status = {'services': {}, 'overall': True}
        
        for url, service_name in services:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    connectivity_status['services'][url] = {
                        'status': True,
                        'name': service_name,
                        'response_time': round(response_time, 3),
                        'code': response.status_code
                    }
                    print(f"   ✅ {service_name}: OK ({response_time:.3f}s)")
                else:
                    connectivity_status['services'][url] = {
                        'status': False,
                        'name': service_name,
                        'response_time': round(response_time, 3),
                        'code': response.status_code
                    }
                    connectivity_status['overall'] = False
                    print(f"   ⚠️ {service_name}: Código {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                connectivity_status['services'][url] = {
                    'status': False,
                    'name': service_name,
                    'error': 'No se pudo conectar'
                }
                connectivity_status['overall'] = False
                print(f"   ❌ {service_name}: No se pudo conectar")
            except requests.exceptions.Timeout:
                connectivity_status['services'][url] = {
                    'status': False,
                    'name': service_name,
                    'error': 'Timeout'
                }
                connectivity_status['overall'] = False
                print(f"   ❌ {service_name}: Timeout")
            except Exception as e:
                connectivity_status['services'][url] = {
                    'status': False,
                    'name': service_name,
                    'error': str(e)
                }
                connectivity_status['overall'] = False
                print(f"   ❌ {service_name}: Error - {str(e)}")
        
        self.status['components']['service_connectivity'] = connectivity_status
        return connectivity_status['overall']
    
    def check_dependencies(self):
        """Verifica las dependencias del sistema"""
        print("\n📦 Verificando dependencias...")
        
        python_deps = [
            'pygame', 'PIL', 'requests', 'matplotlib', 'numpy',
            'flask', 'flask_cors', 'flask_socketio', 'tkinter'
        ]
        
        node_deps = ['node', 'npm']
        
        deps_status = {'python': {}, 'node': {}, 'overall': True}
        
        # Verificar dependencias Python
        for dep in python_deps:
            try:
                __import__(dep.replace('-', '_'))
                deps_status['python'][dep] = {'status': True, 'installed': True}
                print(f"   ✅ Python {dep}: Instalado")
            except ImportError:
                deps_status['python'][dep] = {'status': False, 'installed': False}
                deps_status['overall'] = False
                print(f"   ❌ Python {dep}: No instalado")
        
        # Verificar Node.js
        try:
            import subprocess
            subprocess.run(['node', '--version'], check=True, capture_output=True)
            deps_status['node']['node'] = {'status': True, 'installed': True}
            print(f"   ✅ Node.js: Instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            deps_status['node']['node'] = {'status': False, 'installed': False}
            deps_status['overall'] = False
            print(f"   ❌ Node.js: No instalado")
        
        try:
            subprocess.run(['npm', '--version'], check=True, capture_output=True)
            deps_status['node']['npm'] = {'status': True, 'installed': True}
            print(f"   ✅ npm: Instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            deps_status['node']['npm'] = {'status': False, 'installed': False}
            deps_status['overall'] = False
            print(f"   ❌ npm: No instalado")
        
        self.status['components']['dependencies'] = deps_status
        return deps_status['overall']
    
    def check_performance_metrics(self):
        """Verifica métricas de rendimiento"""
        print("\n⚡ Verificando métricas de rendimiento...")
        
        perf_status = {'metrics': {}, 'overall': True}
        
        # Verificar tamaño de archivos críticos
        critical_files = [
            ('game/main.py', 'Juego Principal'),
            ('web_admin/server.py', 'Servidor Backend'),
            ('data/questions.json', 'Base de Preguntas')
        ]
        
        total_size = 0
        for file_path, file_name in critical_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                total_size += size
                perf_status['metrics'][file_path] = {
                    'name': file_name,
                    'size': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                }
        
        perf_status['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        perf_status['overall'] = True
        
        print(f"   📊 Tamaño total de archivos críticos: {perf_status['total_size_mb']} MB")
        
        # Verificar espacio en disco
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.project_root)
            free_gb = round(free / (1024**3), 2)
            perf_status['disk_space_gb'] = free_gb
            print(f"   💾 Espacio libre en disco: {free_gb} GB")
            
            if free_gb < 1:
                perf_status['overall'] = False
                self.status['recommendations'].append("⚠️ Espacio en disco bajo (< 1 GB)")
        except:
            pass
        
        self.status['components']['performance'] = perf_status
        return perf_status['overall']
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en el estado del sistema"""
        print("\n💡 Generando recomendaciones...")
        
        recommendations = []
        
        # Verificar estructura de archivos
        if not self.status['components']['file_structure']['overall']:
            recommendations.append("🔧 Revisar estructura de archivos faltantes")
        
        # Verificar base de datos
        if not self.status['components']['database_integrity']['overall']:
            recommendations.append("💾 Verificar integridad de la base de datos")
        
        # Verificar conectividad
        if not self.status['components']['service_connectivity']['overall']:
            recommendations.append("🔌 Iniciar servicios web (backend y frontend)")
        
        # Verificar dependencias
        if not self.status['components']['dependencies']['overall']:
            recommendations.append("📦 Instalar dependencias faltantes")
        
        # Verificar rendimiento
        if not self.status['components']['performance']['overall']:
            recommendations.append("⚡ Optimizar rendimiento del sistema")
        
        # Recomendaciones específicas
        db_status = self.status['components']['database_integrity']
        if db_status.get('total_questions', 0) < 50:
            recommendations.append("📝 Agregar más preguntas al juego")
        
        if db_status.get('total_users', 0) < 5:
            recommendations.append("👥 Registrar más usuarios de prueba")
        
        # Si todo está bien
        if not recommendations:
            recommendations.append("✅ Sistema funcionando correctamente")
            recommendations.append("🎮 Listo para usar y compilar")
        
        self.status['recommendations'] = recommendations
        
        for rec in recommendations:
            print(f"   {rec}")
    
    def calculate_overall_status(self):
        """Calcula el estado general del sistema"""
        components = self.status['components']
        
        if not components:
            self.status['overall_status'] = 'UNKNOWN'
            return
        
        # Contar componentes exitosos
        successful_components = 0
        total_components = len(components)
        
        for component_name, component_status in components.items():
            if component_status.get('overall', False):
                successful_components += 1
        
        success_rate = (successful_components / total_components) * 100
        
        if success_rate >= 90:
            self.status['overall_status'] = 'EXCELLENT'
        elif success_rate >= 75:
            self.status['overall_status'] = 'GOOD'
        elif success_rate >= 50:
            self.status['overall_status'] = 'FAIR'
        else:
            self.status['overall_status'] = 'POOR'
        
        self.status['success_rate'] = success_rate
        self.status['successful_components'] = successful_components
        self.status['total_components'] = total_components
    
    def save_report(self):
        """Guarda el reporte en un archivo"""
        report_file = os.path.join(self.project_root, 'data', 'system_status_report.json')
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.status, f, ensure_ascii=False, indent=2)
        
        return report_file
    
    def print_summary(self):
        """Imprime el resumen del estado del sistema"""
        print("\n" + "="*60)
        print("📋 RESUMEN DEL ESTADO DEL SISTEMA")
        print("="*60)
        
        status_emoji = {
            'EXCELLENT': '🟢',
            'GOOD': '🟡',
            'FAIR': '🟠',
            'POOR': '🔴',
            'UNKNOWN': '⚪'
        }
        
        emoji = status_emoji.get(self.status['overall_status'], '⚪')
        
        print(f"\n🎯 Estado General: {emoji} {self.status['overall_status']}")
        print(f"📊 Tasa de Éxito: {self.status.get('success_rate', 0):.1f}%")
        print(f"✅ Componentes Exitosos: {self.status.get('successful_components', 0)}/{self.status.get('total_components', 0)}")
        
        # Mostrar estado de cada componente
        print(f"\n🔧 Componentes:")
        for component_name, component_status in self.status['components'].items():
            status = "✅ OK" if component_status.get('overall', False) else "❌ PROBLEMA"
            print(f"   • {component_name.replace('_', ' ').title()}: {status}")
        
        # Mostrar recomendaciones
        print(f"\n💡 Recomendaciones:")
        for rec in self.status['recommendations']:
            print(f"   • {rec}")
        
        # Mostrar próximos pasos
        print(f"\n🚀 Próximos Pasos:")
        if self.status['overall_status'] in ['EXCELLENT', 'GOOD']:
            print("   1. 🎮 Probar el juego: python scripts/quick_start.py")
            print("   2. 🌐 Acceder al panel: http://localhost:3000")
            print("   3. 📦 Preparar .exe: python scripts/prepare_exe_build.py")
        else:
            print("   1. 🔧 Ejecutar: python scripts/fix_system.py")
            print("   2. 🔍 Verificar: python scripts/test_connections.py")
            print("   3. 📦 Instalar dependencias faltantes")
        
        # Guardar reporte
        report_file = self.save_report()
        print(f"\n📄 Reporte guardado en: {report_file}")
    
    def run_analysis(self):
        """Ejecuta el análisis completo del sistema"""
        self.print_banner()
        
        print("🚀 Iniciando análisis del sistema...")
        print("="*60)
        
        # Ejecutar todas las verificaciones
        self.check_file_structure()
        self.check_database_integrity()
        self.check_service_connectivity()
        self.check_dependencies()
        self.check_performance_metrics()
        
        # Generar recomendaciones
        self.generate_recommendations()
        
        # Calcular estado general
        self.calculate_overall_status()
        
        # Mostrar resumen
        self.print_summary()
        
        return self.status['overall_status'] in ['EXCELLENT', 'GOOD']

def main():
    """Función principal"""
    analyzer = SystemStatus()
    
    try:
        success = analyzer.run_analysis()
        
        if success:
            print("\n🎉 ¡Sistema en buen estado!")
            print("✅ Puedes proceder con confianza")
        else:
            print("\n⚠️ Se encontraron problemas en el sistema")
            print("🔧 Revisa las recomendaciones antes de continuar")
            
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        print("🔧 Contacta al soporte técnico")

if __name__ == "__main__":
    main() 