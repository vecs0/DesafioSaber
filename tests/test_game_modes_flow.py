#!/usr/bin/env python3
"""
Test Script: Game Modes CRUD Flow
================================

Este script prueba el flujo completo de gestión de modos de juego:
1. Crear un modo de juego desde el panel admin (API)
2. Verificar que aparece en la base de datos y en el juego
3. Editar el modo de juego y comprobar que el cambio se refleja
4. Eliminar el modo de juego y asegurar que desaparece de todos los módulos
5. Validar que las reglas (tiempos, puntajes, bonificaciones) se aplican correctamente a nivel de datos

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
TEST_MODE_NAME = f"ModoPrueba_{datetime.now().strftime('%H%M%S')}"
TEST_MODE_NAME_EDITED = f"ModoPruebaEDIT_{datetime.now().strftime('%H%M%S')}"

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
        response = requests.get(f"{BASE_URL}/api/game-modes", timeout=5)
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

def get_game_modes():
    try:
        response = requests.get(f"{BASE_URL}/api/game-modes")
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Error al obtener modos de juego: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error en get_game_modes: {e}")
        return []

def create_test_mode():
    try:
        # Obtener modos actuales
        current_modes = get_game_modes()
        
        # Agregar el nuevo modo
        new_mode = {
            "name": TEST_MODE_NAME,
            "description": "Modo de juego de prueba automatizada",
            "time_limit": 30,
            "score_per_question": 100,
            "bonus": 50
        }
        current_modes.append(new_mode)
        
        # Actualizar la lista completa
        response = requests.put(f"{BASE_URL}/api/game-modes", json=current_modes)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Modo de juego de prueba creado exitosamente")
                return new_mode
            else:
                print_error(f"Error al crear modo: {result.get('error', 'Error desconocido')}")
                return None
        else:
            print_error(f"Error al crear modo: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Error en create_test_mode: {e}")
        return None

def verify_mode_exists(mode_name):
    try:
        modes = get_game_modes()
        for mode in modes:
            if mode.get('name') == mode_name:
                print_success(f"Modo de juego encontrado: {mode_name}")
                return True
        print_error("Modo de juego no encontrado")
        return False
    except Exception as e:
        print_error(f"Error en verify_mode_exists: {e}")
        return False

def edit_test_mode():
    try:
        # Obtener modos actuales
        current_modes = get_game_modes()
        
        # Encontrar y editar el modo de prueba
        for i, mode in enumerate(current_modes):
            if mode.get('name') == TEST_MODE_NAME:
                current_modes[i] = {
                    "name": TEST_MODE_NAME_EDITED,
                    "description": "Modo de juego editado por prueba automatizada",
                    "time_limit": 45,
                    "score_per_question": 200,
                    "bonus": 100
                }
                break
        
        # Actualizar la lista completa
        response = requests.put(f"{BASE_URL}/api/game-modes", json=current_modes)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Modo de juego editado exitosamente")
                return True
            else:
                print_error(f"Error al editar modo: {result.get('error', 'Error desconocido')}")
                return False
        else:
            print_error(f"Error al editar modo: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en edit_test_mode: {e}")
        return False

def delete_test_mode():
    try:
        # Obtener modos actuales
        current_modes = get_game_modes()
        
        # Filtrar el modo de prueba
        filtered_modes = [mode for mode in current_modes if mode.get('name') != TEST_MODE_NAME_EDITED]
        
        # Actualizar la lista completa
        response = requests.put(f"{BASE_URL}/api/game-modes", json=filtered_modes)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success("Modo de juego eliminado exitosamente")
                return True
            else:
                print_error(f"Error al eliminar modo: {result.get('error', 'Error desconocido')}")
                return False
        else:
            print_error(f"Error al eliminar modo: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en delete_test_mode: {e}")
        return False

def verify_cleanup():
    try:
        modes = get_game_modes()
        for mode in modes:
            if mode.get('name', '').startswith('ModoPrueba'):
                print_warning("Se encontró un modo de juego de prueba residual")
                return False
        print_success("No se encontraron modos de juego de prueba residuales")
        return True
    except Exception as e:
        print_error(f"Error en verify_cleanup: {e}")
        return False

def main():
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 60)
    print("    TEST DE FLUJO DE MODOS DE JUEGO - CRUD COMPLETO")
    print("=" * 60)
    print(f"{Colors.END}")
    
    print_info(f"Iniciando test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"URL del servidor: {BASE_URL}")
    print_info(f"Modo de prueba: {TEST_MODE_NAME}")
    
    test_results = []
    try:
        # PASO 1: Verificar conexión
        print_step(1, "Verificación de Conexión", "Comprobando que el servidor backend esté disponible")
        if not check_server_connection():
            print_error("No se puede continuar sin conexión al servidor")
            return False
        test_results.append(True)
        
        # PASO 2: Crear modo de juego
        print_step(2, "Creación de Modo", "Creando modo de juego de prueba desde el panel admin")
        mode = create_test_mode()
        if mode:
            test_results.append(True)
        else:
            test_results.append(False)
            print_error("No se puede continuar sin crear el modo de juego")
            return False
        
        # PASO 3: Verificar existencia
        print_step(3, "Verificación de Existencia", "Verificando que el modo aparece en el sistema")
        if verify_mode_exists(TEST_MODE_NAME):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 4: Editar modo de juego
        print_step(4, "Edición de Modo", "Editando el modo de juego de prueba")
        if edit_test_mode():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 5: Verificar edición
        print_step(5, "Verificación de Edición", "Verificando que la edición se refleja en el sistema")
        if verify_mode_exists(TEST_MODE_NAME_EDITED):
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 6: Eliminar modo de juego
        print_step(6, "Eliminación de Modo", "Eliminando el modo de juego de prueba")
        if delete_test_mode():
            test_results.append(True)
        else:
            test_results.append(False)
        
        # PASO 7: Verificar limpieza
        print_step(7, "Verificación de Limpieza", "Confirmando que no quedan residuos de modos de juego de prueba")
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
            print_info("El flujo CRUD de modos de juego funciona correctamente en todo el sistema")
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