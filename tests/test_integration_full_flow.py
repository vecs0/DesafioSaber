#!/usr/bin/env python3
"""
Test de Integración Completa del Sistema
Valida el flujo completo desde la creación de datos hasta el juego,
incluyendo todas las funcionalidades del sistema integradas.
"""

import requests
import json
import time
import os
import sys
import subprocess
import threading
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000/api"
GAME_PY = "main.py"

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

def wait_for_server(url, timeout=30):
    """Esperar a que el servidor esté disponible"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/config", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def test_integration_full_flow():
    """Test completo de integración del sistema"""
    
    print("🚀 INICIANDO TEST DE INTEGRACIÓN COMPLETA DEL SISTEMA")
    print(f"📡 Conectando a: {BASE_URL}")
    
    # Verificar que el servidor esté corriendo
    if not wait_for_server(BASE_URL):
        print_error("Servidor no está disponible")
        return False
    
    print_success("Servidor conectado correctamente")
    
    # PASO 1: Preparar datos de prueba
    print_step(1, "PREPARAR DATOS DE PRUEBA")
    
    # Crear categorías de prueba
    test_categories = [
        "Historia_Test",
        "Ciencia_Test", 
        "Geografía_Test"
    ]
    
    created_categories = []
    for category in test_categories:
        try:
            response = requests.post(f"{BASE_URL}/categories", json={"name": category})
            if response.status_code == 200:
                created_categories.append(category)
                print_success(f"Categoría creada: {category}")
            else:
                print_error(f"Error creando categoría {category}: {response.text}")
                return False
        except Exception as e:
            print_error(f"Excepción creando categoría {category}: {e}")
            return False
    
    # Crear preguntas de prueba
    test_questions = [
        {
            "pregunta": "¿En qué año comenzó la Primera Guerra Mundial?",
            "opciones": ["1914", "1915", "1916", "1917"],
            "respuesta_correcta": 0,
            "categoria": "Historia_Test",
            "dificultad": "media"
        },
        {
            "pregunta": "¿Cuál es el planeta más grande del sistema solar?",
            "opciones": ["Tierra", "Marte", "Júpiter", "Saturno"],
            "respuesta_correcta": 2,
            "categoria": "Ciencia_Test",
            "dificultad": "fácil"
        },
        {
            "pregunta": "¿Cuál es la capital de Francia?",
            "opciones": ["Londres", "Berlín", "París", "Madrid"],
            "respuesta_correcta": 2,
            "categoria": "Geografía_Test",
            "dificultad": "fácil"
        }
    ]
    
    created_questions = []
    for question_data in test_questions:
        try:
            response = requests.post(f"{BASE_URL}/questions", json=question_data)
            if response.status_code == 200:
                question_result = response.json()
                question_id = question_result.get('question', {}).get('id')
                created_questions.append(question_id)
                print_success(f"Pregunta creada: ID {question_id}")
            else:
                print_error(f"Error creando pregunta: {response.text}")
                return False
        except Exception as e:
            print_error(f"Excepción creando pregunta: {e}")
            return False
    
    # Crear usuario de prueba
    test_user = {
        "username": "test_integration_user",
        "fullName": "Usuario Integración",
        "password": "password123",
        "email": "integration@test.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/players", json=test_user)
        if response.status_code == 201:
            created_user = response.json()['player']
            user_id = created_user['id']
            print_success(f"Usuario creado: {created_user['username']} (ID: {user_id})")
        else:
            print_error(f"Error creando usuario: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción creando usuario: {e}")
        return False
    
    # PASO 2: Configurar modos de juego
    print_step(2, "CONFIGURAR MODOS DE JUEGO")
    
    test_modes = {
        "modos": {
            "Clásico": {
                "tiempo_limite": 300,
                "preguntas_por_ronda": 10,
                "puntos_por_respuesta": 100,
                "bonus_tiempo": 10
            },
            "Contrarreloj": {
                "tiempo_limite": 180,
                "preguntas_por_ronda": 15,
                "puntos_por_respuesta": 150,
                "bonus_tiempo": 5
            },
            "Supervivencia": {
                "tiempo_limite": 0,
                "preguntas_por_ronda": 999,
                "puntos_por_respuesta": 200,
                "bonus_tiempo": 0
            }
        }
    }
    
    try:
        response = requests.put(f"{BASE_URL}/game-modes", json=test_modes)
        if response.status_code == 200:
            print_success("Modos de juego configurados")
        else:
            print_error(f"Error configurando modos de juego: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción configurando modos: {e}")
        return False
    
    # PASO 3: Verificar sincronización de datos
    print_step(3, "VERIFICAR SINCRONIZACIÓN DE DATOS")
    
    # Verificar categorías
    try:
        response = requests.get(f"{BASE_URL}/categories")
        if response.status_code == 200:
            categories = response.json()
            found_categories = [c for c in categories if c in created_categories]
            if len(found_categories) == len(created_categories):
                print_success(f"Categorías sincronizadas: {len(found_categories)}")
            else:
                print_error("Faltan categorías en la sincronización")
                return False
        else:
            print_error(f"Error obteniendo categorías: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando categorías: {e}")
        return False
    
    # Verificar preguntas
    try:
        response = requests.get(f"{BASE_URL}/questions")
        if response.status_code == 200:
            questions = response.json()
            found_questions = [q for q in questions if q.get('id') in created_questions]
            if len(found_questions) == len(created_questions):
                print_success(f"Preguntas sincronizadas: {len(found_questions)}")
            else:
                print_error("Faltan preguntas en la sincronización")
                return False
        else:
            print_error(f"Error obteniendo preguntas: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando preguntas: {e}")
        return False
    
    # PASO 4: Simular partidas y puntuaciones
    print_step(4, "SIMULAR PARTIDAS Y PUNTUACIONES")
    
    test_scores = [
        {
            "username": test_user["username"],
            "score": 1500,
            "mode": "Clásico",
            "categoria": "Historia_Test",
            "correctas": 15,
            "incorrectas": 5,
            "tiempo": 300
        },
        {
            "username": test_user["username"],
            "score": 2000,
            "mode": "Contrarreloj",
            "categoria": "Ciencia_Test",
            "correctas": 20,
            "incorrectas": 0,
            "tiempo": 180
        }
    ]
    
    for i, score_data in enumerate(test_scores, 1):
        try:
            response = requests.post(f"{BASE_URL}/ranking", json=score_data)
            if response.status_code == 200:
                print_success(f"Puntuación {i} agregada: {score_data['score']} puntos")
            else:
                print_error(f"Error agregando puntuación {i}: {response.text}")
                return False
        except Exception as e:
            print_error(f"Excepción agregando puntuación {i}: {e}")
            return False
    
    # PASO 5: Verificar ranking y estadísticas
    print_step(5, "VERIFICAR RANKING Y ESTADÍSTICAS")
    
    # Verificar ranking
    try:
        response = requests.get(f"{BASE_URL}/ranking")
        if response.status_code == 200:
            ranking = response.json()
            user_scores = [r for r in ranking if r.get('username') == test_user['username']]
            if len(user_scores) >= len(test_scores):
                print_success(f"Ranking actualizado: {len(user_scores)} puntuaciones")
            else:
                print_error("Faltan puntuaciones en ranking")
                return False
        else:
            print_error(f"Error obteniendo ranking: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando ranking: {e}")
        return False
    
    # Verificar estadísticas
    try:
        response = requests.get(f"{BASE_URL}/user_stats")
        if response.status_code == 200:
            stats = response.json()
            user_stats = [s for s in stats if s.get('username') == test_user['username']]
            if user_stats:
                print_success("Estadísticas de usuario generadas")
            else:
                print_warning("No se encontraron estadísticas específicas del usuario")
        else:
            print_error(f"Error obteniendo estadísticas: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando estadísticas: {e}")
        return False
    
    # PASO 6: Probar eliminación de categoría con preguntas
    print_step(6, "PROBAR ELIMINACIÓN DE CATEGORÍA CON PREGUNTAS")
    
    # Verificar preguntas antes de eliminar categoría
    try:
        response = requests.get(f"{BASE_URL}/questions")
        if response.status_code == 200:
            questions_before = response.json()
            questions_in_category = [q for q in questions_before if q.get('categoria') == test_categories[0]]
            print_info(f"Preguntas en categoría {test_categories[0]}: {len(questions_in_category)}")
        else:
            print_error(f"Error obteniendo preguntas: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción contando preguntas: {e}")
        return False
    
    # Eliminar categoría
    try:
        response = requests.delete(f"{BASE_URL}/categories/{test_categories[0]}")
        if response.status_code == 200:
            print_success(f"Categoría eliminada: {test_categories[0]}")
        else:
            print_error(f"Error eliminando categoría: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción eliminando categoría: {e}")
        return False
    
    # Verificar que las preguntas se eliminaron
    try:
        response = requests.get(f"{BASE_URL}/questions")
        if response.status_code == 200:
            questions_after = response.json()
            questions_in_deleted_category = [q for q in questions_after if q.get('categoria') == test_categories[0]]
            if len(questions_in_deleted_category) == 0:
                print_success("Preguntas huérfanas eliminadas correctamente")
            else:
                print_error(f"Quedan {len(questions_in_deleted_category)} preguntas huérfanas")
                return False
        else:
            print_error(f"Error verificando preguntas después de eliminar: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando preguntas después de eliminar: {e}")
        return False
    
    # PASO 7: Probar carga de recursos
    print_step(7, "PROBAR CARGA DE RECURSOS")
    
    # Verificar sonidos
    try:
        response = requests.get(f"{BASE_URL}/sounds")
        if response.status_code == 200:
            sounds = response.json()
            print_success(f"Sonidos cargados: {len(sounds)} archivos")
        else:
            print_error(f"Error obteniendo sonidos: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción obteniendo sonidos: {e}")
        return False
    
    # Verificar configuración
    try:
        response = requests.get(f"{BASE_URL}/config")
        if response.status_code == 200:
            config = response.json()
            print_success("Configuración cargada correctamente")
        else:
            print_error(f"Error obteniendo configuración: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción obteniendo configuración: {e}")
        return False
    
    # PASO 8: Probar robustez del sistema
    print_step(8, "PROBAR ROBUSTEZ DEL SISTEMA")
    
    # Probar múltiples requests simultáneos
    print_info("Probando múltiples requests simultáneos...")
    
    import concurrent.futures
    
    def make_request(endpoint):
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            return f"{endpoint}: {response.status_code}"
        except Exception as e:
            return f"{endpoint}: Error - {e}"
    
    endpoints = ["/questions", "/categories", "/ranking", "/players", "/config", "/sounds"]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(make_request, endpoints))
    
    successful_requests = [r for r in results if "200" in r]
    if len(successful_requests) == len(endpoints):
        print_success("Todos los endpoints respondieron correctamente bajo carga")
    else:
        print_warning(f"Algunos endpoints fallaron: {len(successful_requests)}/{len(endpoints)}")
    
    for result in results:
        print_info(f"  - {result}")
    
    # PASO 9: Verificar integridad de datos
    print_step(9, "VERIFICAR INTEGRIDAD DE DATOS")
    
    # Verificar que no hay datos corruptos
    critical_endpoints = [
        ("/questions", "Preguntas"),
        ("/categories", "Categorías"),
        ("/ranking", "Ranking"),
        ("/players", "Jugadores"),
        ("/config", "Configuración")
    ]
    
    for endpoint, description in critical_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (list, dict)):
                    print_success(f"{description}: Datos válidos")
                else:
                    print_error(f"{description}: Formato de datos inválido")
                    return False
            else:
                print_error(f"Error obteniendo {description}: {response.text}")
                return False
        except json.JSONDecodeError as e:
            print_error(f"{description}: Datos JSON corruptos - {e}")
            return False
        except Exception as e:
            print_error(f"Excepción verificando {description}: {e}")
            return False
    
    # PASO 10: Limpiar datos de prueba
    print_step(10, "LIMPIAR DATOS DE PRUEBA")
    
    # Eliminar preguntas restantes
    for question_id in created_questions:
        try:
            response = requests.delete(f"{BASE_URL}/questions/{question_id}")
            if response.status_code == 200:
                print_success(f"Pregunta eliminada: ID {question_id}")
            else:
                print_error(f"Error eliminando pregunta {question_id}: {response.text}")
        except Exception as e:
            print_error(f"Excepción eliminando pregunta {question_id}: {e}")
    
    # Eliminar categorías restantes
    for category in created_categories[1:]:  # La primera ya se eliminó
        try:
            response = requests.delete(f"{BASE_URL}/categories/{category}")
            if response.status_code == 200:
                print_success(f"Categoría eliminada: {category}")
            else:
                print_error(f"Error eliminando categoría {category}: {response.text}")
        except Exception as e:
            print_error(f"Excepción eliminando categoría {category}: {e}")
    
    # Eliminar usuario de prueba
    try:
        response = requests.delete(f"{BASE_URL}/players/{user_id}")
        if response.status_code == 200:
            print_success(f"Usuario eliminado: {test_user['username']}")
        else:
            print_error(f"Error eliminando usuario: {response.text}")
    except Exception as e:
        print_error(f"Excepción eliminando usuario: {e}")
    
    print_success("🚀 TEST DE INTEGRACIÓN COMPLETA DEL SISTEMA COMPLETADO EXITOSAMENTE")
    return True

if __name__ == "__main__":
    success = test_integration_full_flow()
    sys.exit(0 if success else 1) 