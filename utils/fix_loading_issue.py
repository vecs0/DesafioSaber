import json
import os
from datetime import datetime

# Ruta base
base_dir = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, 'data')

# 1. Agregar usuario de prueba a ranking.json y usuarios.json
ranking_file = os.path.join(data_dir, 'ranking.json')
usuarios_file = os.path.join(data_dir, 'usuarios.json')

# Usuario de prueba
test_user = {
    "username": "TestUser",
    "score": 1000,
    "mode": "Clásico",
    "categoria": "Historia",
    "correctas": 10,
    "incorrectas": 2,
    "tiempo": 300,
    "fecha": datetime.now().isoformat()
}

# Agregar a ranking.json
try:
    if os.path.exists(ranking_file):
        with open(ranking_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            rankings = data.get('rankings', [])
        else:
            rankings = data
        if not any(u.get('username') == 'TestUser' for u in rankings):
            rankings.append(test_user)
            if isinstance(data, dict):
                data['rankings'] = rankings
            else:
                data = rankings
            with open(ranking_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print('✅ Usuario de prueba agregado a ranking.json')
        else:
            print('ℹ️ Usuario de prueba ya existe en ranking.json')
except Exception as e:
    print(f'❌ Error actualizando ranking.json: {e}')

# Agregar a usuarios.json
try:
    if os.path.exists(usuarios_file):
        with open(usuarios_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            if 'TestUser' not in data:
                data['TestUser'] = {
                    "username": "TestUser",
                    "stats": {
                        "total_games": 1,
                        "total_score": 1000,
                        "best_score": 1000,
                        "classic_games": 1,
                        "total_correct": 10,
                        "total_incorrect": 2,
                        "max_streak": 5,
                        "categories_played": ["Historia"],
                        "last_played": datetime.now().isoformat()
                    }
                }
                with open(usuarios_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print('✅ Usuario de prueba agregado a usuarios.json')
            else:
                print('ℹ️ Usuario de prueba ya existe en usuarios.json')
        elif isinstance(data, list):
            if not any(u.get('username') == 'TestUser' for u in data):
                data.append({
                    "username": "TestUser",
                    "stats": {
                        "total_games": 1,
                        "total_score": 1000,
                        "best_score": 1000,
                        "classic_games": 1,
                        "total_correct": 10,
                        "total_incorrect": 2,
                        "max_streak": 5,
                        "categories_played": ["Historia"],
                        "last_played": datetime.now().isoformat()
                    }
                })
                with open(usuarios_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print('✅ Usuario de prueba agregado a usuarios.json')
            else:
                print('ℹ️ Usuario de prueba ya existe en usuarios.json')
except Exception as e:
    print(f'❌ Error actualizando usuarios.json: {e}')

# 2. Agregar pregunta de prueba a questions.json
questions_file = os.path.join(data_dir, 'questions.json')
test_question = {
    "categoria": "Historia",
    "pregunta": "¿En qué año comenzó la Segunda Guerra Mundial?",
    "opciones": [
        "1939",
        "1945",
        "1914",
        "1929"
    ],
    "respuesta": "1939",
    "dificultad": "Fácil",
    "modo": "Clásico",
    "fecha_creacion": datetime.now().isoformat(),
    "id": 9999
}
try:
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not any(q.get('pregunta') == test_question['pregunta'] for q in data):
            data.append(test_question)
            with open(questions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print('✅ Pregunta de prueba agregada a questions.json')
        else:
            print('ℹ️ Pregunta de prueba ya existe en questions.json')
except Exception as e:
    print(f'❌ Error actualizando questions.json: {e}') 