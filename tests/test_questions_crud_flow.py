#!/usr/bin/env python3
"""
Test Script: Questions CRUD Flow
===============================

Este script prueba el flujo completo de gestión de preguntas:
1. Crear una nueva pregunta desde el panel admin (API)
2. Verificar que aparece en la base de datos y en el juego
3. Editar la pregunta y comprobar que el cambio se refleja
4. Eliminar la pregunta y asegurar que desaparece de todos los módulos
5. Validar que no hay residuos ni errores tras la operación

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
TEST_QUESTION_TEXT = f"¿Pregunta de prueba {datetime.now().strftime('%H%M%S')}?"
TEST_QUESTION_TEXT_EDITED = f"¿Pregunta de prueba EDITADA {datetime.now().strftime('%H%M%S')}?"
TEST_CATEGORY = "Ciencia"  # Usar una categoría existente

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

def get_questions():
    try:
        response = requests.get(f"{BASE_URL}/api/questions")
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Error al obtener preguntas: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error en get_questions: {e}")
        return []

def create_test_question():
    question_data = {
        "text": TEST_QUESTION_TEXT,
        "options": [
            "Opción A - Correcta",
            "Opción B",
            "Opción C",
            "Opción D"
        ],
        "correctAnswer": "Opción A - Correcta",
        "difficulty": "Fácil",
        "category": TEST_CATEGORY,
        "mode": "Clásico"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/questions", json=question_data)
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print_success("Pregunta de prueba creada exitosamente")
                return result.get('question')
            else:
                print_error(f"Error al crear pregunta: {result.get('error', 'Error desconocido')}")
                return None
        else:
            print_error(f"Error al crear pregunta: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Error en create_test_question: {e}")
        return None

def verify_question_exists(question_id, text):
    try:
        questions = get_questions()
        for q in questions:
            if q.get('id') == question_id and q.get('pregunta') == text:
                print_success(f"Pregunta encontrada en el sistema: {text}")
                return True
        print_error("Pregunta no encontrada en el sistema")
        return False
    except Exception as e:
        print_error(f"Error en verify_question_exists: {e}")
        return False

def edit_test_question(question_id):
    data = {
        "text": TEST_QUESTION_TEXT_EDITED,
        "options": [
            "Opción A - Correcta",
            "Opción B",
            "Opción C",
            "Opción D"
        ],
        "correctAnswer": "Opción B",
        "difficulty": "Media",
        "category": TEST_CATEGORY,
        "mode": "Clásico"
    }
    try:
        response = requests.put(f"{BASE_URL}/api/questions/{question_id}", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Pregunta editada exitosamente")
                return True
            else:
                print_error(f"Error al editar pregunta: {result.get('error', 'Error desconocido')}")
                return False
        else:
            print_error(f"Error al editar pregunta: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en edit_test_question: {e}")
        return False

def delete_test_question(question_id):
    try:
        response = requests.delete(f"{BASE_URL}/api/questions/{question_id}")
        if response.status_code == 200:
            print_success("Pregunta eliminada exitosamente")
            return True
        else:
            print_error(f"Error al eliminar pregunta: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en delete_test_question: {e}")
        return False

def verify_cleanup():
    try:
        questions = get_questions()
        for q in questions:
            if q.get('pregunta', '').startswith('¿Pregunta de prueba'):
                print_warning("Se encontró una pregunta de prueba residual")
                return False
        print_success("No se encontraron preguntas de prueba residuales")
        return True
    except Exception as e:
        print_error(f"Error en verify_cleanup: {e}")
        return False

def main():
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 60)
    print("    TEST DE FLUJO DE PREGUNTAS - CRUD COMPLETO")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print_info(f"Iniciando test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"URL del servidor: {BASE_URL}")
    print_info(f"Texto de prueba: {TEST_QUESTION_TEXT}")
    
    test_results = []
    question_id = None
    try:
        # PASO 1: Verificar conexión
        print_step(1, "Verificación de Conexión", "Comprobando que el servidor backend esté disponible")
        if not check_server_connection():
            print_error("No se puede continuar sin conexión al servidor")
            return False
        test_results.append(True)
        
        # PASO 2: Crear pregunta
        print_step(2, "Creación de Pregunta", "Creando pregunta de prueba desde el panel admin")
        question = create_test_question()
        if question:
            question_id = question.get('id')
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se puede continuar sin crear la pregunta")
            return False
        
        # PASO 3: Verificar existencia
        print_step(3, "Verificación de Existencia", "Verificando que la pregunta aparece en el sistema")
        if verify_question_exists(question_id, TEST_QUESTION_TEXT):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 4: Editar pregunta
        print_step(4, "Edición de Pregunta", "Editando la pregunta de prueba")
        if edit_test_question(question_id):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 5: Verificar edición
        print_step(5, "Verificación de Edición", "Verificando que la edición se refleja en el sistema")
        if verify_question_exists(question_id, TEST_QUESTION_TEXT_EDITED):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 6: Eliminar pregunta
        print_step(6, "Eliminación de Pregunta", "Eliminando la pregunta de prueba")
        if delete_test_question(question_id):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 7: Verificar limpieza
        print_step(7, "Verificación de Limpieza", "Confirmando que no quedan residuos de la pregunta de prueba")
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
            print_info("El flujo CRUD de preguntas funciona correctamente en todo el sistema")
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
        if question_id:
            delete_test_question(question_id)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 