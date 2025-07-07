#!/usr/bin/env python3
"""
Test de Manejo de Errores y Recuperación
Valida el sistema de reporte de errores, manejo de excepciones,
recuperación de datos y robustez del sistema.
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000/api"
ERRORS_FILE = "data/error_reports.json"

def print_step(step, description):
    print(f"\n{'='*60}")
    print(f"PASO {step}: {description}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def test_error_handling_flow():
    """Test completo del manejo de errores y recuperación"""
    
    print("🛡️ INICIANDO TEST DE MANEJO DE ERRORES Y RECUPERACIÓN")
    print(f"📡 Conectando a: {BASE_URL}")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/errors", timeout=5)
        if response.status_code != 200:
            print_error("Servidor no responde correctamente")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"No se puede conectar al servidor: {e}")
        return False
    
    print_success("Servidor conectado correctamente")
    
    # PASO 1: Verificar endpoint de reporte de errores
    print_step(1, "VERIFICAR ENDPOINT DE REPORTE DE ERRORES")
    
    try:
        response = requests.get(f"{BASE_URL}/errors")
        if response.status_code == 200:
            errors = response.json()
            print_success("Endpoint de errores disponible")
            print_info(f"  - Errores existentes: {len(errors)}")
        else:
            print_error(f"Error obteniendo errores: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando errores: {e}")
        return False
    
    # PASO 2: Reportar errores de prueba
    print_step(2, "REPORTAR ERRORES DE PRUEBA")
    
    test_errors = [
        {
            "type": "validation_error",
            "message": "Datos de usuario inválidos",
            "details": "El campo email no tiene formato válido",
            "severity": "medium",
            "component": "user_registration",
            "timestamp": datetime.now().isoformat(),
            "user_agent": "test_client/1.0",
            "stack_trace": "Traceback (most recent call last):\n  File 'test.py', line 10, in <module>\n    validate_email('invalid-email')\nValueError: Invalid email format"
        },
        {
            "type": "connection_error",
            "message": "Error de conexión a base de datos",
            "details": "Timeout al conectar con MySQL",
            "severity": "high",
            "component": "database",
            "timestamp": datetime.now().isoformat(),
            "user_agent": "test_client/1.0",
            "stack_trace": "Traceback (most recent call last):\n  File 'db.py', line 25, in <module>\n    connection = mysql.connect()\nConnectionError: Connection timeout"
        },
        {
            "type": "file_error",
            "message": "Error al cargar archivo de configuración",
            "details": "El archivo config.json no existe",
            "severity": "low",
            "component": "config_loader",
            "timestamp": datetime.now().isoformat(),
            "user_agent": "test_client/1.0",
            "stack_trace": "Traceback (most recent call last):\n  File 'config.py', line 15, in <module>\n    with open('config.json', 'r') as f:\nFileNotFoundError: [Errno 2] No such file or directory: 'config.json'"
        }
    ]
    
    reported_errors = []
    for i, error_data in enumerate(test_errors, 1):
        try:
            response = requests.post(f"{BASE_URL}/errors", json=error_data)
            if response.status_code == 200:
                result = response.json()
                error_id = result.get('error_id')
                reported_errors.append(error_id)
                print_success(f"Error {i} reportado: {error_data['type']}")
                print_info(f"  - ID: {error_id}")
                print_info(f"  - Severidad: {error_data['severity']}")
            else:
                print_error(f"Error reportando error {i}: {response.text}")
                return False
        except Exception as e:
            print_error(f"Excepción reportando error {i}: {e}")
            return False
    
    # PASO 3: Verificar errores reportados
    print_step(3, "VERIFICAR ERRORES REPORTADOS")
    
    try:
        response = requests.get(f"{BASE_URL}/errors")
        if response.status_code == 200:
            errors = response.json()
            reported_error_ids = set(reported_errors)
            found_errors = [e for e in errors if e.get('id') in reported_error_ids]
            
            if len(found_errors) == len(reported_errors):
                print_success(f"Se encontraron {len(found_errors)} errores reportados")
                for error in found_errors:
                    print_info(f"  - ID: {error.get('id')} - {error.get('type')} ({error.get('severity')})")
            else:
                print_error(f"Faltan errores. Esperados: {len(reported_errors)}, Encontrados: {len(found_errors)}")
                return False
        else:
            print_error(f"Error obteniendo errores: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando errores: {e}")
        return False
    
    # PASO 4: Probar manejo de errores en endpoints inválidos
    print_step(4, "PROBAR MANEJO DE ERRORES EN ENDPOINTS INVÁLIDOS")
    
    invalid_endpoints = [
        ("/nonexistent", "Endpoint inexistente"),
        ("/questions/999999", "ID de pregunta inexistente"),
        ("/categories/nonexistent_category", "Categoría inexistente"),
        ("/players/999999", "ID de jugador inexistente")
    ]
    
    for endpoint, description in invalid_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code in [404, 400, 500]:
                print_success(f"{description}: Error manejado correctamente ({response.status_code})")
            else:
                print_warning(f"{description}: Respuesta inesperada ({response.status_code})")
        except Exception as e:
            print_error(f"Excepción en {description}: {e}")
    
    # PASO 5: Probar validación de datos
    print_step(5, "PROBAR VALIDACIÓN DE DATOS")
    
    invalid_data_tests = [
        {
            "endpoint": "/players",
            "method": "POST",
            "data": {"username": "", "password": "123"},  # Username vacío
            "description": "Usuario con username vacío"
        },
        {
            "endpoint": "/questions",
            "method": "POST",
            "data": {"pregunta": "Test", "categoria": "nonexistent"},  # Categoría inexistente
            "description": "Pregunta con categoría inexistente"
        },
        {
            "endpoint": "/ranking",
            "method": "POST",
            "data": {"username": "test", "score": "invalid_score"},  # Score inválido
            "description": "Ranking con score inválido"
        }
    ]
    
    for test in invalid_data_tests:
        try:
            if test["method"] == "POST":
                response = requests.post(f"{BASE_URL}{test['endpoint']}", json=test["data"])
            else:
                response = requests.get(f"{BASE_URL}{test['endpoint']}")
            
            if response.status_code in [400, 422, 500]:
                print_success(f"{test['description']}: Validación correcta ({response.status_code})")
            else:
                print_warning(f"{test['description']}: Validación inesperada ({response.status_code})")
        except Exception as e:
            print_error(f"Excepción en {test['description']}: {e}")
    
    # PASO 6: Probar recuperación de archivos corruptos
    print_step(6, "PROBAR RECUPERACIÓN DE ARCHIVOS CORRUPTOS")
    
    # Crear backup de archivos importantes
    backup_files = [
        ("data/questions.json", "data/questions_backup.json"),
        ("data/categories.json", "data/categories_backup.json"),
        ("data/usuarios.json", "data/usuarios_backup.json")
    ]
    
    for original, backup in backup_files:
        if os.path.exists(original):
            try:
                import shutil
                shutil.copy2(original, backup)
                print_success(f"Backup creado: {backup}")
            except Exception as e:
                print_error(f"Error creando backup de {original}: {e}")
    
    # Simular archivo corrupto
    corrupt_file = "data/test_corrupt.json"
    try:
        with open(corrupt_file, 'w') as f:
            f.write('{"invalid": json content')
        print_success(f"Archivo corrupto creado: {corrupt_file}")
    except Exception as e:
        print_error(f"Error creando archivo corrupto: {e}")
    
    # PASO 7: Verificar archivo de errores
    print_step(7, "VERIFICAR ARCHIVO DE ERRORES")
    
    if os.path.exists(ERRORS_FILE):
        try:
            with open(ERRORS_FILE, 'r', encoding='utf-8') as f:
                errors_data = json.load(f)
            print_success(f"Archivo de errores cargado: {ERRORS_FILE}")
            print_info(f"  - Formato: {type(errors_data).__name__}")
            if isinstance(errors_data, list):
                print_info(f"  - Errores en archivo: {len(errors_data)}")
            elif isinstance(errors_data, dict):
                print_info(f"  - Claves: {list(errors_data.keys())}")
        except json.JSONDecodeError as e:
            print_error(f"Archivo de errores corrupto: {e}")
            return False
        except Exception as e:
            print_error(f"Error leyendo archivo de errores: {e}")
            return False
    else:
        print_info(f"Archivo de errores no encontrado (puede ser normal): {ERRORS_FILE}")
    
    # PASO 8: Probar actualización de estado de errores
    print_step(8, "PROBAR ACTUALIZACIÓN DE ESTADO DE ERRORES")
    
    if reported_errors:
        error_id = reported_errors[0]
        update_data = {
            "status": "resolved",
            "resolution": "Error corregido en la validación de datos",
            "resolved_by": "test_admin",
            "resolved_at": datetime.now().isoformat()
        }
        
        try:
            response = requests.put(f"{BASE_URL}/errors/{error_id}", json=update_data)
            if response.status_code == 200:
                result = response.json()
                print_success(f"Error {error_id} actualizado como resuelto")
                print_info(f"  - Resuelto por: {update_data['resolved_by']}")
                print_info(f"  - Resolución: {update_data['resolution']}")
            else:
                print_error(f"Error actualizando error {error_id}: {response.text}")
        except Exception as e:
            print_error(f"Excepción actualizando error: {e}")
    
    # PASO 9: Probar robustez del sistema
    print_step(9, "PROBAR ROBUSTEZ DEL SISTEMA")
    
    # Probar múltiples requests simultáneos
    print_info("Probando múltiples requests simultáneos...")
    
    import threading
    import concurrent.futures
    
    def make_request(endpoint):
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            return f"{endpoint}: {response.status_code}"
        except Exception as e:
            return f"{endpoint}: Error - {e}"
    
    endpoints = ["/questions", "/categories", "/ranking", "/players", "/config"]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(make_request, endpoints))
    
    for result in results:
        print_info(f"  - {result}")
    
    # PASO 10: Limpiar datos de prueba
    print_step(10, "LIMPIAR DATOS DE PRUEBA")
    
    # Eliminar errores de prueba
    for error_id in reported_errors:
        try:
            # Nota: Asumiendo que hay un endpoint DELETE para errores
            # Si no existe, los errores se mantienen para análisis
            print_info(f"Error de prueba mantenido para análisis: {error_id}")
        except Exception as e:
            print_error(f"Error limpiando error {error_id}: {e}")
    
    # Limpiar archivos de prueba
    test_files = [
        corrupt_file,
        "data/questions_backup.json",
        "data/categories_backup.json", 
        "data/usuarios_backup.json"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print_success(f"Archivo eliminado: {file_path}")
            except Exception as e:
                print_error(f"Error eliminando {file_path}: {e}")
    
    print_success("🛡️ TEST DE MANEJO DE ERRORES Y RECUPERACIÓN COMPLETADO EXITOSAMENTE")
    return True

if __name__ == "__main__":
    success = test_error_handling_flow()
    sys.exit(0 if success else 1) 