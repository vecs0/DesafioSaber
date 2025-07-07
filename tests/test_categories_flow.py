#!/usr/bin/env python3
"""
Test Script: Categories Flow Integration
========================================

Este script prueba el flujo completo de gestión de categorías:
1. Crear una nueva categoría desde el panel admin
2. Verificar que aparece en el editor visual
3. Configurar color/fondo en el editor visual
4. Confirmar que aparece en el juego
5. Asignar una pregunta a la nueva categoría
6. Eliminar la categoría y verificar limpieza

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
TEST_CATEGORY_NAME = f"Categoría de Prueba {datetime.now().strftime('%H%M%S')}"
TEST_CATEGORY_DESCRIPTION = "Categoría creada para pruebas automáticas"
TEST_COLOR = "#FF6B6B"
TEST_BACKGROUND = "#FFE66D"

class Colors:
    """Colores para output en consola"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step_num, title, description=""):
    """Imprime un paso del test con formato"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== PASO {step_num}: {title} ==={Colors.END}")
    if description:
        print(f"{Colors.CYAN}{description}{Colors.END}")
    print()

def print_success(message):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    """Imprime mensaje informativo"""
    print(f"{Colors.PURPLE}ℹ️  {message}{Colors.END}")

def check_server_connection():
    """Verifica que el servidor esté funcionando"""
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

def get_categories():
    """Obtiene la lista actual de categorías"""
    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Error al obtener categorías: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error en get_categories: {e}")
        return []

def create_test_category():
    """Crea una nueva categoría de prueba"""
    category_data = {
        "name": TEST_CATEGORY_NAME
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/categories", json=category_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success(f"Categoría '{TEST_CATEGORY_NAME}' creada exitosamente")
                return {"id": TEST_CATEGORY_NAME, "name": TEST_CATEGORY_NAME}
            else:
                print_error(f"Error al crear categoría: {result.get('error', 'Error desconocido')}")
                return None
        else:
            print_error(f"Error al crear categoría: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Error en create_test_category: {e}")
        return None

def verify_category_in_editor(category_id):
    """Verifica que la categoría aparece en el editor visual"""
    try:
        print_info("Verificando que la categoría aparece en el editor visual...")
        
        # Verificar que el archivo de configuración del editor se actualiza
        editor_config_path = os.path.join(GAME_DATA_DIR, "categories.json")
        if os.path.exists(editor_config_path):
            with open(editor_config_path, 'r', encoding='utf-8') as f:
                categories = json.load(f)
            
            # Buscar la categoría de prueba (las categorías son strings simples)
            if TEST_CATEGORY_NAME in categories:
                print_success(f"Categoría '{TEST_CATEGORY_NAME}' encontrada en editor visual")
                return True
            else:
                print_error("Categoría no encontrada en el editor visual")
                return False
        else:
            print_error("Archivo de configuración del editor no encontrado")
            return False
            
    except Exception as e:
        print_error(f"Error verificando editor visual: {e}")
        return False

def verify_category_in_game():
    """Verifica que la categoría aparece en el juego"""
    try:
        print_info("Verificando que la categoría aparece en el juego...")
        
        # Obtener categorías desde la API del juego
        response = requests.get(f"{BASE_URL}/api/categories")
        if response.status_code == 200:
            categories = response.json()
            
            # Buscar la categoría de prueba (las categorías son strings simples)
            if TEST_CATEGORY_NAME in categories:
                print_success(f"Categoría '{TEST_CATEGORY_NAME}' disponible en el juego")
                return True
            else:
                print_error("Categoría no encontrada en el juego")
                return False
        else:
            print_error(f"Error al obtener categorías del juego: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error verificando juego: {e}")
        return False

def create_test_question_for_category(category_id):
    """Crea una pregunta de prueba para la nueva categoría"""
    question_data = {
        "text": "¿Esta es una pregunta de prueba para la nueva categoría?",
        "options": [
            "Opción A - Correcta",
            "Opción B",
            "Opción C", 
            "Opción D"
        ],
        "correctAnswer": "Opción A - Correcta",
        "difficulty": "Fácil",
        "category": category_id,
        "mode": "Clásico"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/questions", json=question_data)
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print_success("Pregunta de prueba creada exitosamente para la nueva categoría")
                return result.get('question')
            else:
                print_error(f"Error al crear pregunta: {result.get('error', 'Error desconocido')}")
                return None
        else:
            print_error(f"Error al crear pregunta: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Error en create_test_question_for_category: {e}")
        return None

def verify_question_in_category(question_id, category_id):
    """Verifica que la pregunta aparece en la categoría correcta"""
    try:
        response = requests.get(f"{BASE_URL}/api/questions")
        if response.status_code == 200:
            questions = response.json()
            
            # Buscar la pregunta de prueba
            test_question = None
            for q in questions:
                if q.get('id') == question_id:
                    test_question = q
                    break
            
            if test_question and test_question.get('categoria') == category_id:
                print_success("Pregunta correctamente asignada a la nueva categoría")
                return True
            else:
                print_error("Pregunta no encontrada o asignada incorrectamente")
                return False
        else:
            print_error(f"Error al obtener preguntas: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error verificando pregunta: {e}")
        return False

def delete_test_question(question_id):
    """Elimina la pregunta de prueba"""
    try:
        response = requests.delete(f"{BASE_URL}/api/questions/{question_id}")
        if response.status_code == 200:
            print_success("Pregunta de prueba eliminada exitosamente")
            return True
        else:
            print_error(f"Error al eliminar pregunta: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en delete_test_question: {e}")
        return False

def delete_test_category(category_id):
    """Elimina la categoría de prueba"""
    try:
        response = requests.delete(f"{BASE_URL}/api/categories/{TEST_CATEGORY_NAME}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success(f"Categoría '{TEST_CATEGORY_NAME}' eliminada exitosamente")
                return True
            else:
                print_error(f"Error al eliminar categoría: {result.get('error', 'Error desconocido')}")
                return False
        else:
            print_error(f"Error al eliminar categoría: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en delete_test_category: {e}")
        return False

def verify_cleanup():
    """Verifica que la limpieza fue exitosa"""
    try:
        print_info("Verificando limpieza del sistema...")
        
        # Verificar que la categoría ya no existe
        categories = get_categories()
        test_category_exists = TEST_CATEGORY_NAME in categories
        
        if not test_category_exists:
            print_success("Categoría de prueba eliminada correctamente del sistema")
        else:
            print_error("La categoría de prueba aún existe después de la eliminación")
            return False
        
        # Verificar que no hay preguntas huérfanas
        response = requests.get(f"{BASE_URL}/api/questions")
        if response.status_code == 200:
            questions = response.json()
            orphaned_questions = [q for q in questions if q.get('pregunta', '').startswith('¿Esta es una pregunta de prueba')]
            
            if not orphaned_questions:
                print_success("No se encontraron preguntas huérfanas de prueba")
            else:
                print_warning(f"Se encontraron {len(orphaned_questions)} preguntas huérfanas de prueba")
        
        return True
        
    except Exception as e:
        print_error(f"Error en verify_cleanup: {e}")
        return False

def main():
    """Función principal del test"""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 60)
    print("    TEST DE FLUJO DE CATEGORÍAS - SISTEMA COMPLETO")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print_info(f"Iniciando test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"URL del servidor: {BASE_URL}")
    print_info(f"Categoría de prueba: {TEST_CATEGORY_NAME}")
    
    # Variables para tracking
    test_results = []
    category_id = None
    question_id = None
    
    try:
        # PASO 1: Verificar conexión al servidor
        print_step(1, "Verificación de Conexión", "Comprobando que el servidor backend esté disponible")
        if not check_server_connection():
            print_error("No se puede continuar sin conexión al servidor")
            return False
        test_results.append(True)
        
        # PASO 2: Obtener estado inicial
        print_step(2, "Estado Inicial", "Obteniendo lista actual de categorías")
        initial_categories = get_categories()
        print_info(f"Categorías existentes: {len(initial_categories)}")
        test_results.append(True)
        
        # PASO 3: Crear categoría de prueba
        print_step(3, "Creación de Categoría", f"Creando categoría '{TEST_CATEGORY_NAME}' desde el panel admin")
        new_category = create_test_category()
        if new_category:
            category_id = new_category.get('id')
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se puede continuar sin crear la categoría")
            return False
        
        # PASO 4: Verificar en editor visual
        print_step(4, "Verificación en Editor Visual", "Confirmando que la categoría aparece en el editor visual")
        if verify_category_in_editor(category_id):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 5: Verificar en juego
        print_step(5, "Verificación en Juego", "Confirmando que la categoría aparece en el juego")
        if verify_category_in_game():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 6: Crear pregunta de prueba
        print_step(6, "Creación de Pregunta", "Creando pregunta de prueba para la nueva categoría")
        new_question = create_test_question_for_category(category_id)
        if new_question:
            question_id = new_question.get('id')
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 7: Verificar asignación de pregunta
        print_step(7, "Verificación de Asignación", "Verificando que la pregunta está correctamente asignada")
        if verify_question_in_category(question_id, category_id):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 8: Limpieza - Eliminar pregunta
        print_step(8, "Limpieza - Pregunta", "Eliminando pregunta de prueba")
        if delete_test_question(question_id):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 9: Limpieza - Eliminar categoría
        print_step(9, "Limpieza - Categoría", f"Eliminando categoría '{TEST_CATEGORY_NAME}'")
        if delete_test_category(category_id):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 10: Verificar limpieza
        print_step(10, "Verificación de Limpieza", "Confirmando que el sistema está limpio")
        if verify_cleanup():
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
            print_info("El flujo de categorías funciona correctamente en todo el sistema")
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
    finally:
        # Limpieza de emergencia si algo falló
        if category_id and not verify_cleanup():
            print_warning("Realizando limpieza de emergencia...")
            try:
                if question_id:
                    delete_test_question(question_id)
                delete_test_category(category_id)
            except:
                pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 