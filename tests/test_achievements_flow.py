#!/usr/bin/env python3
"""
Test de Sistema de Logros y Estadísticas
Valida el flujo completo de logros, estadísticas de usuario, ranking
y sincronización de datos de juego.
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000/api"
ACHIEVEMENTS_FILE = "data/achievements.json"
USER_STATS_FILE = "data/user_stats.json"
GAME_HISTORY_FILE = "data/game_history.json"
RANKING_FILE = "data/ranking.json"

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

def test_achievements_flow():
    """Test completo del flujo de logros y estadísticas"""
    
    print("🏆 INICIANDO TEST DE SISTEMA DE LOGROS Y ESTADÍSTICAS")
    print(f"📡 Conectando a: {BASE_URL}")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/achievements", timeout=5)
        if response.status_code != 200:
            print_error("Servidor no responde correctamente")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"No se puede conectar al servidor: {e}")
        return False
    
    print_success("Servidor conectado correctamente")
    
    # PASO 1: Verificar endpoints de logros y estadísticas
    print_step(1, "VERIFICAR ENDPOINTS DE LOGROS Y ESTADÍSTICAS")
    
    endpoints_to_test = [
        ("/achievements", "Logros"),
        ("/user_stats", "Estadísticas de usuario"),
        ("/game_history", "Historial de juego"),
        ("/stats", "Estadísticas generales")
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print_success(f"{description}: OK")
                print_info(f"  - Respuesta: {type(data).__name__}")
                if isinstance(data, list):
                    print_info(f"  - Elementos: {len(data)}")
                elif isinstance(data, dict):
                    print_info(f"  - Claves: {list(data.keys())}")
            else:
                print_error(f"{description}: Error {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Excepción en {description}: {e}")
            return False
    
    # PASO 2: Crear usuario de prueba para estadísticas
    print_step(2, "CREAR USUARIO DE PRUEBA PARA ESTADÍSTICAS")
    
    test_user = {
        "username": "test_stats_user",
        "fullName": "Usuario Estadísticas",
        "password": "password123",
        "email": "stats@example.com"
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
    
    # PASO 3: Simular partidas y agregar puntuaciones
    print_step(3, "SIMULAR PARTIDAS Y AGREGAR PUNTUACIONES")
    
    test_scores = [
        {
            "username": test_user["username"],
            "score": 1500,
            "mode": "Clásico",
            "categoria": "Historia",
            "correctas": 15,
            "incorrectas": 5,
            "tiempo": 300
        },
        {
            "username": test_user["username"],
            "score": 2000,
            "mode": "Contrarreloj",
            "categoria": "Ciencia",
            "correctas": 20,
            "incorrectas": 0,
            "tiempo": 180
        },
        {
            "username": test_user["username"],
            "score": 1200,
            "mode": "Clásico",
            "categoria": "Geografía",
            "correctas": 12,
            "incorrectas": 8,
            "tiempo": 400
        }
    ]
    
    for i, score_data in enumerate(test_scores, 1):
        try:
            response = requests.post(f"{BASE_URL}/ranking", json=score_data)
            if response.status_code == 200:
                result = response.json()
                print_success(f"Puntuación {i} agregada: {score_data['score']} puntos")
                print_info(f"  - Modo: {score_data['mode']}")
                print_info(f"  - Categoría: {score_data['categoria']}")
            else:
                print_error(f"Error agregando puntuación {i}: {response.text}")
                return False
        except Exception as e:
            print_error(f"Excepción agregando puntuación {i}: {e}")
            return False
    
    # PASO 4: Verificar ranking actualizado
    print_step(4, "VERIFICAR RANKING ACTUALIZADO")
    
    try:
        response = requests.get(f"{BASE_URL}/ranking")
        if response.status_code == 200:
            ranking = response.json()
            user_scores = [r for r in ranking if r.get('username') == test_user['username']]
            
            if len(user_scores) >= len(test_scores):
                print_success(f"Ranking actualizado: {len(user_scores)} puntuaciones del usuario")
                for score in user_scores:
                    print_info(f"  - {score['score']} pts ({score['mode']} - {score['categoria']})")
            else:
                print_error(f"Faltan puntuaciones en ranking. Esperadas: {len(test_scores)}, Encontradas: {len(user_scores)}")
                return False
        else:
            print_error(f"Error obteniendo ranking: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción obteniendo ranking: {e}")
        return False
    
    # PASO 5: Verificar estadísticas de usuario
    print_step(5, "VERIFICAR ESTADÍSTICAS DE USUARIO")
    
    try:
        response = requests.get(f"{BASE_URL}/user_stats")
        if response.status_code == 200:
            stats = response.json()
            user_stats = [s for s in stats if s.get('username') == test_user['username']]
            
            if user_stats:
                user_stat = user_stats[0]
                print_success(f"Estadísticas encontradas para {test_user['username']}")
                print_info(f"  - Total de juegos: {user_stat.get('total_games', 'N/A')}")
                print_info(f"  - Puntuación total: {user_stat.get('total_score', 'N/A')}")
                print_info(f"  - Mejor puntuación: {user_stat.get('best_score', 'N/A')}")
                print_info(f"  - Modo favorito: {user_stat.get('favorite_mode', 'N/A')}")
                print_info(f"  - Categoría favorita: {user_stat.get('favorite_category', 'N/A')}")
            else:
                print_error(f"No se encontraron estadísticas para {test_user['username']}")
                return False
        else:
            print_error(f"Error obteniendo estadísticas: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción obteniendo estadísticas: {e}")
        return False
    
    # PASO 6: Verificar historial de juego
    print_step(6, "VERIFICAR HISTORIAL DE JUEGO")
    
    try:
        response = requests.get(f"{BASE_URL}/game_history")
        if response.status_code == 200:
            history = response.json()
            user_history = [h for h in history if h.get('username') == test_user['username']]
            
            if user_history:
                print_success(f"Historial encontrado: {len(user_history)} partidas")
                for game in user_history[:3]:  # Mostrar solo las primeras 3
                    print_info(f"  - {game.get('fecha', 'N/A')}: {game.get('score', 0)} pts")
            else:
                print_info("No se encontró historial específico del usuario")
        else:
            print_error(f"Error obteniendo historial: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción obteniendo historial: {e}")
        return False
    
    # PASO 7: Verificar archivos JSON de logros y estadísticas
    print_step(7, "VERIFICAR ARCHIVOS JSON DE LOGROS Y ESTADÍSTICAS")
    
    files_to_check = [
        (ACHIEVEMENTS_FILE, "Logros"),
        (USER_STATS_FILE, "Estadísticas de usuario"),
        (GAME_HISTORY_FILE, "Historial de juego"),
        (RANKING_FILE, "Ranking")
    ]
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print_success(f"Archivo cargado: {file_path}")
                print_info(f"  - Tipo: {type(data).__name__}")
                if isinstance(data, list):
                    print_info(f"  - Elementos: {len(data)}")
                elif isinstance(data, dict):
                    print_info(f"  - Claves: {list(data.keys())}")
            except Exception as e:
                print_error(f"Error leyendo {file_path}: {e}")
                return False
        else:
            print_info(f"Archivo no encontrado (puede ser normal): {file_path}")
    
    # PASO 8: Simular logros desbloqueados
    print_step(8, "SIMULAR LOGROS DESBLOQUEADOS")
    
    # Crear un logro de prueba en el archivo
    test_achievement = {
        "id": "test_achievement_1",
        "name": "Primer Juego",
        "description": "Completar tu primera partida",
        "icon": "🎮",
        "unlocked_by": test_user['username'],
        "unlocked_at": datetime.now().isoformat(),
        "points": 100
    }
    
    try:
        # Cargar logros existentes
        if os.path.exists(ACHIEVEMENTS_FILE):
            with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                achievements = json.load(f)
        else:
            achievements = []
        
        # Agregar logro de prueba
        if isinstance(achievements, list):
            achievements.append(test_achievement)
        else:
            achievements = [test_achievement]
        
        # Guardar logros
        with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(achievements, f, indent=2, ensure_ascii=False)
        
        print_success(f"Logro de prueba creado: {test_achievement['name']}")
        print_info(f"  - Desbloqueado por: {test_achievement['unlocked_by']}")
        print_info(f"  - Puntos: {test_achievement['points']}")
        
    except Exception as e:
        print_error(f"Error creando logro de prueba: {e}")
        return False
    
    # PASO 9: Verificar sincronización de logros
    print_step(9, "VERIFICAR SINCRONIZACIÓN DE LOGROS")
    
    try:
        response = requests.get(f"{BASE_URL}/achievements")
        if response.status_code == 200:
            achievements = response.json()
            test_achievements = [a for a in achievements if a.get('id') == test_achievement['id']]
            
            if test_achievements:
                print_success("Logro sincronizado correctamente")
                achievement = test_achievements[0]
                print_info(f"  - Nombre: {achievement.get('name')}")
                print_info(f"  - Desbloqueado por: {achievement.get('unlocked_by')}")
            else:
                print_error("Logro no encontrado en la API")
                return False
        else:
            print_error(f"Error obteniendo logros: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando logros: {e}")
        return False
    
    # PASO 10: Limpiar datos de prueba
    print_step(10, "LIMPIAR DATOS DE PRUEBA")
    
    # Eliminar usuario de prueba
    try:
        response = requests.delete(f"{BASE_URL}/players/{user_id}")
        if response.status_code == 200:
            print_success(f"Usuario eliminado: {test_user['username']}")
        else:
            print_error(f"Error eliminando usuario: {response.text}")
    except Exception as e:
        print_error(f"Excepción eliminando usuario: {e}")
    
    # Limpiar logro de prueba
    try:
        if os.path.exists(ACHIEVEMENTS_FILE):
            with open(ACHIEVEMENTS_FILE, 'r', encoding='utf-8') as f:
                achievements = json.load(f)
            
            # Remover logro de prueba
            if isinstance(achievements, list):
                achievements = [a for a in achievements if a.get('id') != test_achievement['id']]
            
            with open(ACHIEVEMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(achievements, f, indent=2, ensure_ascii=False)
            
            print_success("Logro de prueba eliminado")
    except Exception as e:
        print_error(f"Error eliminando logro de prueba: {e}")
    
    print_success("🏆 TEST DE SISTEMA DE LOGROS Y ESTADÍSTICAS COMPLETADO EXITOSAMENTE")
    return True

if __name__ == "__main__":
    success = test_achievements_flow()
    sys.exit(0 if success else 1) 