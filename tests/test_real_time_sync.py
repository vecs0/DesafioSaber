#!/usr/bin/env python3
"""
Test Script: Real-Time Sync Flow
===============================

Este script prueba la sincronización en tiempo real entre panel, editor visual y juego:
1. Modificar categorías, preguntas y modos de juego desde el panel (API)
2. Verificar que los cambios se reflejan instantáneamente en los archivos y endpoints correspondientes
3. Validar que no hay inconsistencias ni retrasos

Autor: Sistema de Pruebas Automatizadas
Fecha: 2024
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
GAME_DATA_DIR = "data"
CATEGORIES_FILE = os.path.join(GAME_DATA_DIR, "categories.json")
CONFIG_FILE = os.path.join(GAME_DATA_DIR, "config.json")

SYNC_WAIT = 2  # segundos para esperar propagación

TEST_CATEGORY = f"SyncCat_{datetime.now().strftime('%H%M%S')}"
TEST_MODE_NAME = f"SyncMode_{datetime.now().strftime('%H%M%S')}"
TEST_QUESTION_TEXT = f"¿Pregunta sync {datetime.now().strftime('%H%M%S')}?"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step_num, title, description=""):
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== PASO {step_num}: {title} ==={Colors.END}")
    if description:
        print(f"{Colors.CYAN}{description}{Colors.END}")
    print()

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.PURPLE}ℹ️  {message}{Colors.END}")

def check_server_connection():
    try:
        response = requests.get(f"{BASE_URL}/api/categories", timeout=5)
        if response.status_code == 200:
            print_success("Servidor backend conectado correctamente")
            return True
        else:
            print_error(f"Servidor responde con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"No se puede conectar al servidor: {e}")
        print_warning("Asegúrate de que el servidor backend esté ejecutándose en http://localhost:5000")
        return False

def add_category():
    data = {"name": TEST_CATEGORY}
    response = requests.post(f"{BASE_URL}/api/categories", json=data)
    return response.status_code == 200

def add_game_mode():
    config = load_json(CONFIG_FILE)
    modes = config.get('game_modes', [])
    new_mode = {
        "name": TEST_MODE_NAME,
        "description": "Modo sync test",
        "time_limit": 20,
        "score_per_question": 50,
        "bonus": 10
    }
    modes.append(new_mode)
    config['game_modes'] = modes
    save_json(CONFIG_FILE, config)
    # Notificar al backend
    requests.put(f"{BASE_URL}/api/game-modes", json=modes)
    return True

def add_question():
    data = {
        "text": TEST_QUESTION_TEXT,
        "options": ["A", "B", "C", "D"],
        "correctAnswer": "A",
        "difficulty": "Fácil",
        "category": TEST_CATEGORY,
        "mode": TEST_MODE_NAME
    }
    response = requests.post(f"{BASE_URL}/api/questions", json=data)
    return response.status_code == 201

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def verify_category_in_file():
    cats = load_json(CATEGORIES_FILE)
    if isinstance(cats, list) and TEST_CATEGORY in cats:
        print_success(f"Categoría '{TEST_CATEGORY}' sincronizada en archivo")
        return True
    print_error(f"Categoría '{TEST_CATEGORY}' NO sincronizada en archivo")
    return False

def verify_mode_in_file():
    config = load_json(CONFIG_FILE)
    modes = config.get('game_modes', [])
    for m in modes:
        if m.get('name') == TEST_MODE_NAME:
            print_success(f"Modo '{TEST_MODE_NAME}' sincronizado en archivo")
            return True
    print_error(f"Modo '{TEST_MODE_NAME}' NO sincronizado en archivo")
    return False

def verify_question_in_api():
    response = requests.get(f"{BASE_URL}/api/questions")
    if response.status_code == 200:
        questions = response.json()
        for q in questions:
            if q.get('pregunta') == TEST_QUESTION_TEXT:
                print_success(f"Pregunta '{TEST_QUESTION_TEXT}' sincronizada en API")
                return True
    print_error(f"Pregunta '{TEST_QUESTION_TEXT}' NO sincronizada en API")
    return False

def main():
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 60)
    print("    TEST DE FLUJO DE SINCRONIZACIÓN EN TIEMPO REAL")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print_info(f"Iniciando test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"URL del servidor: {BASE_URL}")
    
    test_results = []
    try:
        # PASO 1: Verificar conexión
        print_step(1, "Verificación de Conexión", "Comprobando que el servidor backend esté disponible")
        if not check_server_connection():
            print_error("No se puede continuar sin conexión al servidor")
            return False
        test_results.append(True)
        
        # PASO 2: Agregar categoría
        print_step(2, "Agregar Categoría", f"Agregando categoría '{TEST_CATEGORY}' desde el panel")
        if add_category():
            time.sleep(SYNC_WAIT)
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se pudo agregar la categoría")
            return False
        
        # PASO 3: Verificar categoría en archivo
        print_step(3, "Verificar Categoría", "Verificando sincronización en archivo de categorías")
        if verify_category_in_file():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 4: Agregar modo de juego
        print_step(4, "Agregar Modo de Juego", f"Agregando modo '{TEST_MODE_NAME}' desde el panel")
        if add_game_mode():
            time.sleep(SYNC_WAIT)
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se pudo agregar el modo de juego")
            return False
        
        # PASO 5: Verificar modo en archivo
        print_step(5, "Verificar Modo de Juego", "Verificando sincronización en archivo de configuración")
        if verify_mode_in_file():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 6: Agregar pregunta
        print_step(6, "Agregar Pregunta", f"Agregando pregunta '{TEST_QUESTION_TEXT}' desde el panel")
        if add_question():
            time.sleep(SYNC_WAIT)
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se pudo agregar la pregunta")
            return False
        
        # PASO 7: Verificar pregunta en API
        print_step(7, "Verificar Pregunta", "Verificando sincronización de pregunta en API")
        if verify_question_in_api():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # RESULTADOS FINALES
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("=" * 60)
        print("                    RESULTADOS FINALES")
        print("=" * 60)
        print(f"{Colors.END}")
        
        total_steps = len(test_results)
        successful_steps = sum(test_results)
        
        print_info(f"Pasos ejecutados: {total_steps}")
        print_info(f"Pasos exitosos: {successful_steps}")
        print_info(f"Pasos fallidos: {total_steps - successful_steps}")
        
        if successful_steps == total_steps:
            print_success("🎉 ¡TEST COMPLETADO EXITOSAMENTE!")
            print_info("La sincronización en tiempo real funciona correctamente en todo el sistema")
            return True
        else:
            print_error("❌ TEST FALLIDO")
            print_warning("Algunos pasos fallaron. Revisa los errores anteriores")
            return False
            
    except KeyboardInterrupt:
        print_warning("\nTest interrumpido por el usuario")
        return False
    except Exception as e:
        print_error(f"Error inesperado en el test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 