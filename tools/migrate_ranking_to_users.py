import json
import os
from datetime import datetime

RANKING_FILE = os.path.join('data', 'ranking.json')
USERS_FILE = os.path.join('data', 'usuarios.json')

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def migrate():
    # Cargar usuarios existentes
    users = load_json(USERS_FILE)
    if isinstance(users, dict):
        users = list(users.values())
    usernames = {u['username'] for u in users if 'username' in u}

    # Cargar ranking
    ranking_data = load_json(RANKING_FILE)
    if isinstance(ranking_data, dict) and 'rankings' in ranking_data:
        ranking = ranking_data['rankings']
    else:
        ranking = ranking_data if isinstance(ranking_data, list) else []

    # Migrar cada jugador que no esté en usuarios.json
    for player in ranking:
        if player['username'] not in usernames:
            new_user = {
                'id': player.get('id'),
                'username': player.get('username'),
                'fullName': player.get('username'),
                'password': '',
                'email': None,
                'created_at': player.get('fecha', datetime.now().isoformat()),
                'last_login': player.get('fecha', datetime.now().isoformat()),
                'stats': {
                    'total_games': 0,
                    'total_score': 0,
                    'best_score': 0,
                    'favorite_mode': None,
                    'favorite_category': None
                },
                'score': player.get('score', 0),
                'mode': player.get('mode', ''),
                'categoria': player.get('categoria', ''),
                'correctas': player.get('correctas', 0),
                'incorrectas': player.get('incorrectas', 0),
                'tiempo': player.get('tiempo', 0),
                'fecha': player.get('fecha', datetime.now().isoformat())
            }
            users.append(new_user)
            print(f"Migrado: {player['username']}")
        else:
            print(f"Ya existe: {player['username']}")
    save_json(USERS_FILE, users)
    print("Migración completada.")

if __name__ == '__main__':
    migrate() 