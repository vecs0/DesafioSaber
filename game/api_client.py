import requests
import json
import os
import time
from datetime import datetime
from flask import Flask, jsonify, request
import sys
from paths import ROOT_DIR, DATA_DIR
from auto_backup import auto_backup

class APIClient:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10  # 10 segundos de timeout
        
    def is_server_available(self):
        """Verifica si el servidor está disponible"""
        try:
            response = self.session.get(f"{self.base_url}/stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_questions(self):
        """Obtiene las preguntas desde el servidor"""
        try:
            response = self.session.get(f"{self.base_url}/questions")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error obteniendo preguntas: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error de conexión al obtener preguntas: {e}")
            return []
    
    def get_config(self):
        """Obtiene la configuración del juego desde el servidor"""
        try:
            response = self.session.get(f"{self.base_url}/config")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error obteniendo configuración: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error de conexión al obtener configuración: {e}")
            return {}
    
    def get_game_modes(self):
        """Obtiene los modos de juego desde el servidor"""
        try:
            response = self.session.get(f"{self.base_url}/game-modes")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error obteniendo modos de juego: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error de conexión al obtener modos de juego: {e}")
            return []
    
    def add_score(self, username, score, mode, categoria="", correctas=0, incorrectas=0, tiempo=0):
        """Añade una puntuación al ranking"""
        try:
            data = {
                'username': username,
                'score': score,
                'mode': mode,
                'categoria': categoria,
                'correctas': correctas,
                'incorrectas': incorrectas,
                'tiempo': tiempo
            }
            
            response = self.session.post(f"{self.base_url}/ranking", json=data)
            if response.status_code == 201:
                print(f"Puntuación de {username} guardada exitosamente")
                return True
            else:
                print(f"Error guardando puntuación: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error de conexión al guardar puntuación: {e}")
            return False
    
    def sync_data(self, action, data=None):
        """Sincroniza datos con el servidor"""
        try:
            payload = {'action': action}
            if data:
                payload['data'] = data
                
            response = self.session.post(f"{self.base_url}/sync", json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error en sincronización: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error de conexión en sincronización: {e}")
            return None
    
    def update_local_files(self):
        """Actualiza los archivos locales con datos del servidor"""
        try:
            # Obtener preguntas actualizadas
            questions = self.get_questions()
            if questions:
                with open('data/questions.json', 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                print("Archivo questions.json actualizado")
            
            # Obtener configuración actualizada
            config = self.get_config()
            if config:
                with open('data/config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print("Archivo config.json actualizado")
                
            return True
        except Exception as e:
            print(f"Error actualizando archivos locales: {e}")
            return False
    
    def check_for_updates(self, last_check_file="last_update_check.txt"):
        """Verifica si hay actualizaciones disponibles"""
        try:
            # Verificar si el servidor está disponible
            if not self.is_server_available():
                return False
            
            # Leer la última verificación
            last_check = 0
            if os.path.exists(last_check_file):
                with open(last_check_file, 'r') as f:
                    last_check = float(f.read().strip())
            
            # Verificar cada 5 minutos
            current_time = time.time()
            if current_time - last_check > 300:  # 5 minutos
                # Actualizar archivos locales
                success = self.update_local_files()
                if success:
                    # Guardar timestamp de la verificación
                    with open(last_check_file, 'w') as f:
                        f.write(str(current_time))
                    return True
            
            return False
        except Exception as e:
            print(f"Error verificando actualizaciones: {e}")
            return False

    def get_categories(self):
        """Obtiene las categorías desde el servidor"""
        try:
            response = self.session.get(f"{self.base_url}/categories")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error obteniendo categorías: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error de conexión al obtener categorías: {e}")
            return []

    def get_sounds(self):
        """Obtiene la lista de sonidos desde el servidor"""
        try:
            response = self.session.get(f"{self.base_url}/sounds")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error obteniendo sonidos: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error de conexión al obtener sonidos: {e}")
            return []

# Instancia global del cliente API
api_client = APIClient()

def initialize_api_connection():
    """Inicializa la conexión con la API"""
    if api_client.is_server_available():
        print("✅ Servidor de administración conectado")
        print("🔄 Verificando actualizaciones...")
        api_client.check_for_updates()
        return True
    else:
        print("⚠️  Servidor de administración no disponible")
        print("📁 Usando archivos locales")
        return False

def save_score_to_api(username, score, mode, categoria="", correctas=0, incorrectas=0, tiempo=0):
    """Guarda una puntuación tanto localmente como en la API"""
    # Guardar localmente (código existente del juego)
    # ... (aquí iría el código existente de guardar_puntuacion)
    
    # Intentar guardar en la API
    if api_client.is_server_available():
        api_client.add_score(username, score, mode, categoria, correctas, incorrectas, tiempo)
    else:
        print("⚠️  No se pudo conectar con el servidor para guardar la puntuación")

def load_questions_from_api():
    """Carga las preguntas desde la API si está disponible"""
    if api_client.is_server_available():
        questions = api_client.get_questions()
        if questions:
            return questions
    
    # Si no hay conexión, cargar desde archivo local
    try:
        with open('data/questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando preguntas locales: {e}")
        return []

def load_config_from_api():
    """Carga la configuración desde la API si está disponible"""
    if api_client.is_server_available():
        config = api_client.get_config()
        if config:
            return config
    
    # Si no hay conexión, cargar desde archivo local
    try:
        with open('data/config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando configuración local: {e}")
        return {}

app = Flask(__name__)


@app.route('/api/user_stats', methods=['GET'])
def get_user_stats():
    """Devuelve las estadísticas detalladas de todos los usuarios"""
    stats_file = os.path.join(DATA_DIR, 'user_stats.json')
    if not os.path.exists(stats_file):
        return jsonify({'users': {}, 'last_updated': None})
    with open(stats_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(stats_file, 'w', encoding='utf-8') as f:
        auto_backup(stats_file)
    return jsonify(data)

@app.route('/api/user_achievements', methods=['GET'])
def get_user_achievements():
    """Devuelve los logros desbloqueados por usuario"""
    achievements_file = os.path.join(DATA_DIR, 'user_achievements.json')
    if not os.path.exists(achievements_file):
        return jsonify({'unlocked': [], 'last_updated': None})
    with open(achievements_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(achievements_file, 'w', encoding='utf-8') as f:
        auto_backup(achievements_file)
    return jsonify(data)

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Devuelve la lista de logros disponibles"""
    achievements_file = os.path.join(DATA_DIR, 'achievements.json')
    if not os.path.exists(achievements_file):
        return jsonify([])
    with open(achievements_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/game_history', methods=['GET'])
def get_game_history():
    """Devuelve el historial de partidas"""
    history_file = os.path.join(DATA_DIR, 'game_history.json')
    if not os.path.exists(history_file):
        return jsonify({'history': [], 'last_updated': None})
    with open(history_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5001, debug=True) 