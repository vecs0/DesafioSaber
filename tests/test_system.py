#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del sistema Desafío Saber
"""

import os
import sys
import json
import requests
import subprocess
import time
from pathlib import Path

def test_file_structure():
    """Prueba la estructura de archivos"""
    print("📁 Verificando estructura de archivos...")
    
    required_files = [
        "game/main.py",
        "game/achievements.py", 
        "game/wheel_animation.py",
        "game/api_client.py",
        "web_admin/server.py",
        "web_admin/requirements.txt",
        "data/questions.json",
        "data/ranking.json",
        "data/config.json",
        "requirements.txt",
        "start_system.py",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Archivos faltantes: {missing_files}")
        return False
    
    print("✅ Estructura de archivos correcta")
    return True

def test_dependencies():
    """Prueba las dependencias de Python"""
    print("\n📦 Verificando dependencias...")
    
    required_packages = [
        'flask', 'flask_cors', 'requests', 'pygame', 'PIL', 'tkinter'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANTE")
    
    if missing_packages:
        print(f"\n⚠️  Instala las dependencias faltantes:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def test_json_files():
    """Prueba que los archivos JSON sean válidos"""
    print("\n📄 Verificando archivos JSON...")
    
    json_files = [
        "data/questions.json",
        "data/ranking.json", 
        "data/config.json"
    ]
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ {json_file} - Válido")
        except Exception as e:
            print(f"❌ {json_file} - Error: {e}")
            return False
    
    print("✅ Todos los archivos JSON son válidos")
    return True

def test_server_connection():
    """Prueba la conexión al servidor"""
    print("\n🌐 Verificando servidor...")
    
    try:
        # Intentar iniciar el servidor
        server_process = subprocess.Popen([
            sys.executable, "web_admin/server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar a que inicie
        time.sleep(3)
        
        if server_process.poll() is None:
            # Servidor está ejecutándose
            try:
                response = requests.get("http://localhost:5000/api/stats", timeout=5)
                if response.status_code == 200:
                    print("✅ Servidor API funcionando")
                    server_process.terminate()
                    return True
                else:
                    print(f"❌ Servidor respondió con código {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error conectando al servidor: {e}")
        else:
            print("❌ Servidor no pudo iniciarse")
        
        server_process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error probando servidor: {e}")
        return False

def test_game_files():
    """Prueba que el juego pueda ejecutarse"""
    print("\n🎮 Verificando archivos del juego...")
    
    game_files = [
        "game/main.py",
        "sounds/acierto.mp3",
        "sounds/errado.mp3",
        "assets/images/logo.png"
    ]
    
    for file_path in game_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"⚠️  {file_path} - No encontrado (opcional)")
    
    # Verificar que el juego principal existe
    if Path("game/main.py").exists():
        print("✅ Archivo principal del juego encontrado")
        return True
    else:
        print("❌ Archivo principal del juego no encontrado")
        return False

def test_api_client():
    """Prueba el cliente API"""
    print("\n🔌 Verificando cliente API...")
    
    try:
        # Importar el cliente API
        sys.path.append('game')
        from api_client import APIClient
        
        client = APIClient()
        
        # Probar métodos básicos
        if hasattr(client, 'is_server_available'):
            print("✅ Cliente API importado correctamente")
            return True
        else:
            print("❌ Cliente API no tiene métodos esperados")
            return False
            
    except Exception as e:
        print(f"❌ Error importando cliente API: {e}")
        return False

def test_web_admin_structure():
    """Prueba la estructura de la web de administración"""
    print("\n🌐 Verificando estructura web...")
    
    web_files = [
        "web_admin/src/App.js",
        "web_admin/src/components/QuestionsManagement.js",
        "web_admin/src/components/RankingDisplay.js",
        "web_admin/package.json"
    ]
    
    missing_files = []
    for file_path in web_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - FALTANTE")
    
    if missing_files:
        print(f"⚠️  Algunos archivos web faltan: {missing_files}")
        return False
    
    print("✅ Estructura web correcta")
    return True

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA DESAFÍO SABER")
    print("=" * 60)
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Dependencias", test_dependencies),
        ("Archivos JSON", test_json_files),
        ("Cliente API", test_api_client),
        ("Archivos del juego", test_game_files),
        ("Estructura web", test_web_admin_structure),
        ("Servidor", test_server_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name.upper()}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en prueba {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo.")
        print("\n🚀 Para iniciar el sistema:")
        print("   python start_system.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("\n🔧 Para instalar dependencias:")
        print("   pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 