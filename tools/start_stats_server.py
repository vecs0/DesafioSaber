#!/usr/bin/env python3
"""
Servidor de Estadísticas para DesafíoSaber
Expone endpoints REST para estadísticas, logros e historial de partidas
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Agregar el directorio del juego al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

app = Flask(__name__)
CORS(app)  # Habilitar CORS para el frontend

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@app.route('/api/user_stats', methods=['GET'])
def get_user_stats():
    """Devuelve las estadísticas detalladas de todos los usuarios"""
    stats_file = os.path.join(DATA_DIR, 'user_stats.json')
    if not os.path.exists(stats_file):
        return jsonify({'users': {}, 'last_updated': None})
    
    try:
        with open(stats_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Error leyendo estadísticas: {e}")
        return jsonify({'users': {}, 'last_updated': None, 'error': str(e)})

@app.route('/api/user_achievements', methods=['GET'])
def get_user_achievements():
    """Devuelve los logros desbloqueados por usuario"""
    achievements_file = os.path.join(DATA_DIR, 'user_achievements.json')
    if not os.path.exists(achievements_file):
        return jsonify({'unlocked': [], 'last_updated': None})
    
    try:
        with open(achievements_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Error leyendo logros: {e}")
        return jsonify({'unlocked': [], 'last_updated': None, 'error': str(e)})

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    """Devuelve la lista de logros disponibles"""
    achievements_file = os.path.join(DATA_DIR, 'achievements.json')
    if not os.path.exists(achievements_file):
        return jsonify([])
    
    try:
        with open(achievements_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Error leyendo logros disponibles: {e}")
        return jsonify([])

@app.route('/api/game_history', methods=['GET'])
def get_game_history():
    """Devuelve el historial de partidas"""
    history_file = os.path.join(DATA_DIR, 'game_history.json')
    if not os.path.exists(history_file):
        return jsonify({'history': [], 'last_updated': None})
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"Error leyendo historial: {e}")
        return jsonify({'history': [], 'last_updated': None, 'error': str(e)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servidor"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'DesafíoSaber Stats API'
    })

if __name__ == '__main__':
    print("🚀 Iniciando Servidor de Estadísticas DesafíoSaber...")
    print("📍 Puerto: 5001")
    print("🌐 Endpoints disponibles:")
    print("   - GET /api/user_stats")
    print("   - GET /api/user_achievements") 
    print("   - GET /api/achievements")
    print("   - GET /api/game_history")
    print("   - GET /api/health")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}") 