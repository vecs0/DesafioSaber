#!/usr/bin/env python3
"""
Test Script: Category Sync Cleanup
=================================

Este script prueba que cuando se elimina una categoría desde el panel:
1. La categoría se elimina del archivo de categorías
2. La categoría no aparece en la API del juego
3. Las preguntas asociadas a esa categoría se manejan correctamente
4. No hay inconsistencias en el sistema

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
QUESTIONS_FILE = os.path.join(GAME_DATA_DIR, "questions.json")

SYNC_WAIT = 3  # segundos para esperar propagación

TEST_CATEGORY = f"TestCat_{datetime.now().strftime('%H%M%S')}"
TEST_QUESTION_TEXT = f"¿Pregunta test {datetime.now().strftime('%H%M%S')}?"

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

def create_test_category():
    data = {"name": TEST_CATEGORY}
    response = requests.post(f"{BASE_URL}/api/categories", json=data)
    return response.status_code == 200

def create_test_question():
    data = {
        "text": TEST_QUESTION_TEXT,
        "options": ["A", "B", "C", "D"],
        "correctAnswer": "A",
        "difficulty": "Fácil",
        "category": TEST_CATEGORY,
        "mode": "Clásico"
    }
    response = requests.post(f"{BASE_URL}/api/questions", json=data)
    return response.status_code == 201

def verify_category_exists():
    # Verificar en API
    response = requests.get(f"{BASE_URL}/api/categories")
    if response.status_code == 200:
        categories = response.json()
        if TEST_CATEGORY in categories:
            print_success(f"Categoría '{TEST_CATEGORY}' existe en API")
            return True
        else:
            print_error(f"Categoría '{TEST_CATEGORY}' NO existe en API")
            return False
    return False

def verify_question_exists():
    # Verificar en API
    response = requests.get(f"{BASE_URL}/api/questions")
    if response.status_code == 200:
        questions = response.json()
        for q in questions:
            if q.get('pregunta') == TEST_QUESTION_TEXT:
                print_success(f"Pregunta '{TEST_QUESTION_TEXT}' existe en API")
                return True
        print_error(f"Pregunta '{TEST_QUESTION_TEXT}' NO existe en API")
        return False
    return False

def delete_test_category():
    response = requests.delete(f"{BASE_URL}/api/categories/{TEST_CATEGORY}")
    return response.status_code == 200

def verify_category_deleted():
    # Verificar en API
    response = requests.get(f"{BASE_URL}/api/categories")
    if response.status_code == 200:
        categories = response.json()
        if TEST_CATEGORY not in categories:
            print_success(f"Categoría '{TEST_CATEGORY}' eliminada de API")
            return True
        else:
            print_error(f"Categoría '{TEST_CATEGORY}' aún existe en API")
            return False
    return False

def verify_question_handling():
    # Verificar que la pregunta se maneja correctamente después de eliminar la categoría
    response = requests.get(f"{BASE_URL}/api/questions")
    if response.status_code == 200:
        questions = response.json()
        orphaned_questions = []
        for q in questions:
            if q.get('categoria') == TEST_CATEGORY:
                orphaned_questions.append(q)
        
        if orphaned_questions:
            print_warning(f"Se encontraron {len(orphaned_questions)} preguntas huérfanas de la categoría eliminada")
            return False
        else:
            print_success("No se encontraron preguntas huérfanas")
            return True
    return False

def verify_file_consistency():
    # Verificar que el archivo de categorías está sincronizado
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            categories = json.load(f)
        
        if isinstance(categories, list) and TEST_CATEGORY not in categories:
            print_success("Archivo de categorías sincronizado correctamente")
            return True
        else:
            print_error("Archivo de categorías no está sincronizado")
            return False
    except Exception as e:
        print_error(f"Error leyendo archivo de categorías: {e}")
        return False

def main():
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 60)
    print("    TEST DE SINCRONIZACIÓN DE ELIMINACIÓN DE CATEGORÍAS")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print_info(f"Iniciando test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"URL del servidor: {BASE_URL}")
    print_info(f"Categoría de prueba: {TEST_CATEGORY}")
    
    test_results = []
    try:
        # PASO 1: Verificar conexión
        print_step(1, "Verificación de Conexión", "Comprobando que el servidor backend esté disponible")
        if not check_server_connection():
            print_error("No se puede continuar sin conexión al servidor")
            return False
        test_results.append(True)
        
        # PASO 2: Crear categoría de prueba
        print_step(2, "Crear Categoría", f"Creando categoría '{TEST_CATEGORY}' para pruebas")
        if create_test_category():
            time.sleep(SYNC_WAIT)
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se pudo crear la categoría de prueba")
            return False
        
        # PASO 3: Verificar que la categoría existe
        print_step(3, "Verificar Existencia", "Verificando que la categoría se creó correctamente")
        if verify_category_exists():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 4: Crear pregunta de prueba
        print_step(4, "Crear Pregunta", f"Creando pregunta asociada a la categoría '{TEST_CATEGORY}'")
        if create_test_question():
            time.sleep(SYNC_WAIT)
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se pudo crear la pregunta de prueba")
            return False
        
        # PASO 5: Verificar que la pregunta existe
        print_step(5, "Verificar Pregunta", "Verificando que la pregunta se creó correctamente")
        if verify_question_exists():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 6: Eliminar categoría
        print_step(6, "Eliminar Categoría", f"Eliminando categoría '{TEST_CATEGORY}' desde el panel")
        if delete_test_category():
            time.sleep(SYNC_WAIT)
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se pudo eliminar la categoría")
            return False
        
        # PASO 7: Verificar que la categoría fue eliminada
        print_step(7, "Verificar Eliminación", "Verificando que la categoría fue eliminada de la API")
        if verify_category_deleted():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 8: Verificar manejo de preguntas huérfanas
        print_step(8, "Verificar Preguntas", "Verificando manejo de preguntas asociadas a la categoría eliminada")
        if verify_question_handling():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 9: Verificar consistencia de archivos
        print_step(9, "Verificar Archivos", "Verificando sincronización de archivos")
        if verify_file_consistency():
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
            print_info("La sincronización de eliminación de categorías funciona correctamente")
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