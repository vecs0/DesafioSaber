from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import json
import os
import threading
import time
from datetime import datetime
import sqlite3
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, emit
import subprocess

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuración
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav'}
UPLOADS_ADMIN_FOLDER = os.path.join('uploads', 'admins')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_IMAGE_SIZE = 1 * 1024 * 1024  # 1MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear carpeta de uploads si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
os.makedirs(UPLOADS_ADMIN_FOLDER, exist_ok=True)

# Rutas de archivos de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.abspath(os.path.join(BASE_DIR, '../data'))
QUESTIONS_FILE = os.path.join(DATA_FOLDER, 'questions.json')
RANKING_FILE = os.path.join(DATA_FOLDER, 'ranking.json')
CONFIG_FILE = os.path.join(DATA_FOLDER, 'config.json')
GAME_DATA_FILE = os.path.join(DATA_FOLDER, 'desafiosaber_data.json')
CATEGORIES_FILE = os.path.join(DATA_FOLDER, 'categories.json')
SOUNDS_FOLDERS = [os.path.abspath(os.path.join(BASE_DIR, '../assets/sounds')), os.path.abspath(os.path.join(BASE_DIR, '../sounds'))]
SOUNDS_EXTENSIONS = ('.mp3', '.wav')
USERS_FILE = os.path.join(DATA_FOLDER, 'usuarios.json')
RESET_FILE = os.path.join(os.path.dirname(__file__), '../reset_admin.txt')
USER_STATS_FILE = os.path.join(DATA_FOLDER, 'user_stats.json')
ADMINS_FILE = os.path.join(DATA_FOLDER, 'admins.json')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def load_json_file(file_path):
    """Carga un archivo JSON de forma segura y repara si es necesario (usuarios)."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Reparar usuarios.json si es lista
                if file_path.endswith('usuarios.json') and isinstance(data, list):
                    print(f"[FIX] usuarios.json estaba en formato lista, convirtiendo a dict...")
                    data_dict = {u['username']: u for u in data if 'username' in u}
                    with open(file_path, 'w', encoding='utf-8') as fw:
                        json.dump(data_dict, fw, ensure_ascii=False, indent=2)
                    return data_dict
                return data
        else:
            print(f"[DEBUG] Archivo {file_path} no existe")
        return []
    except Exception as e:
        print(f"Error cargando {file_path}: {e}")
        return []

def save_json_file(file_path, data):
    """Guarda datos en un archivo JSON de forma segura"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando {file_path}: {e}")
        return False

def load_users_file():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                # Migrar a lista si es necesario
                data = list(data.values())
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_users_file(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando usuarios.json: {e}")
        return False

# Rutas de la API

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Obtiene todas las preguntas, con soporte de filtros y paginación"""
    questions = load_json_file(QUESTIONS_FILE)
    # Filtros
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    mode = request.args.get('mode')
    if category:
        questions = [q for q in questions if q.get('categoria', '').lower() == category.lower()]
    if difficulty:
        questions = [q for q in questions if q.get('dificultad', '').lower() == difficulty.lower()]
    if mode:
        questions = [q for q in questions if q.get('modo', '').lower() == mode.lower()]
    # Paginación
    try:
        limit = int(request.args.get('limit', 0))
        offset = int(request.args.get('offset', 0))
    except ValueError:
        limit = 0
        offset = 0
    if offset:
        questions = questions[offset:]
    if limit:
        questions = questions[:limit]
    return jsonify(questions)

@app.route('/api/questions', methods=['POST'])
def add_question():
    """Añade una nueva pregunta"""
    try:
        data = request.json
        questions = load_json_file(QUESTIONS_FILE)
        
        # Generar ID único
        new_id = max([q.get('id', 0) for q in questions], default=0) + 1
        
        new_question = {
            'id': new_id,
            'modo': data.get('mode', 'Clásico'),
            'categoria': data.get('category', ''),
            'dificultad': data.get('difficulty', 'Fácil'),
            'pregunta': data.get('text', ''),
            'opciones': data.get('options', []),
            'respuesta': data.get('correctAnswer', ''),
            'imagen': data.get('image', None),
            'fecha_creacion': datetime.now().isoformat()
        }
        
        questions.append(new_question)
        
        if save_json_file(QUESTIONS_FILE, questions):
            notify_update('questions')
            return jsonify({'success': True, 'question': new_question}), 201
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    """Actualiza una pregunta existente"""
    try:
        data = request.json
        questions = load_json_file(QUESTIONS_FILE)
        
        for i, question in enumerate(questions):
            if question.get('id') == question_id:
                questions[i].update({
                    'modo': data.get('mode', question.get('modo')),
                    'categoria': data.get('category', question.get('categoria')),
                    'dificultad': data.get('difficulty', question.get('dificultad')),
                    'pregunta': data.get('text', question.get('pregunta')),
                    'opciones': data.get('options', question.get('opciones')),
                    'respuesta': data.get('correctAnswer', question.get('respuesta')),
                    'imagen': data.get('image', question.get('imagen')),
                    'fecha_modificacion': datetime.now().isoformat()
                })
                
                if save_json_file(QUESTIONS_FILE, questions):
                    notify_update('questions')
                    return jsonify({'success': True, 'question': questions[i]})
                else:
                    return jsonify({'success': False, 'error': 'Error al guardar'}), 500
        
        return jsonify({'success': False, 'error': 'Pregunta no encontrada'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """Elimina una pregunta"""
    try:
        questions = load_json_file(QUESTIONS_FILE)
        questions = [q for q in questions if q.get('id') != question_id]
        
        if save_json_file(QUESTIONS_FILE, questions):
            notify_update('questions')
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    ranking = load_json_file(RANKING_FILE)
    # Si es un dict con 'rankings', obtener la lista
    if isinstance(ranking, dict) and 'rankings' in ranking:
        ranking_list = ranking['rankings']
    elif isinstance(ranking, list):
        ranking_list = ranking
    else:
        ranking_list = []
    
    # Filtrar usuarios admin del ranking
    ranking_list = [r for r in ranking_list if r.get('username', '').lower() != 'admin']
    
    # --- NUEVO: incluir todos los usuarios registrados aunque no tengan partidas ---
    try:
        users = load_json_file(USERS_FILE)
        if isinstance(users, dict):
            all_users = list(users.values())
        elif isinstance(users, list):
            all_users = users
        else:
            all_users = []
    except Exception as e:
        print(f"Error cargando usuarios para ranking completo: {e}")
        all_users = []
    
    usernames_in_ranking = set(r.get("username") for r in ranking_list if r.get("username"))
    for user in all_users:
        uname = user.get("username")
        if uname and uname not in usernames_in_ranking and uname.lower() != "admin":
            ranking_list.append({
                "username": uname,
                "score": 0,
                "mode": "-",
                "categoria": "-",
                "correctas": 0,
                "incorrectas": 0,
                "tiempo": 0,
                "fecha": "-"
            })
    
    # Devolver en el formato correcto
    return jsonify({'rankings': ranking_list})

@app.route('/api/ranking', methods=['POST'])
def add_score():
    """Añade una nueva puntuación al ranking"""
    try:
        data = request.json
        ranking = load_json_file(RANKING_FILE)
        
        new_score = {
            'id': len(ranking) + 1,
            'username': data.get('username', 'Anónimo'),
            'score': data.get('score', 0),
            'mode': data.get('mode', 'Clásico'),
            'categoria': data.get('categoria', ''),
            'correctas': data.get('correctas', 0),
            'incorrectas': data.get('incorrectas', 0),
            'tiempo': data.get('tiempo', 0),
            'fecha': datetime.now().isoformat()
        }
        
        ranking.append(new_score)
        
        # Ordenar por puntuación descendente
        ranking.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        if save_json_file(RANKING_FILE, ranking):
            notify_update('ranking')
            return jsonify({'success': True, 'ranking': ranking}), 201
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/config', methods=['GET'])
def get_config():
    """Obtiene la configuración del juego"""
    config = load_json_file(CONFIG_FILE)
    return jsonify(config)

@app.route('/api/config', methods=['PUT'])
def update_config():
    """Actualiza la configuración del juego"""
    try:
        data = request.json
        config = load_json_file(CONFIG_FILE)
        
        config.update(data)
        
        if save_json_file(CONFIG_FILE, config):
            notify_update('config')
            return jsonify({'success': True, 'config': config})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/game-modes', methods=['GET'])
def get_game_modes():
    """Obtiene los modos de juego configurados"""
    config = load_json_file(CONFIG_FILE)
    game_modes = config.get('game_modes', [
        {'name': 'Clásico', 'numQuestions': 15, 'timePerQuestion': 30},
        {'name': 'Contrarreloj', 'totalTime': 60, 'isGlobalTimer': True},
        {'name': 'Duelo', 'numQuestions': 10, 'timePerQuestion': 15}
    ])
    return jsonify(game_modes)

@app.route('/api/game-modes', methods=['PUT'])
def update_game_modes():
    """Actualiza los modos de juego"""
    try:
        data = request.json
        config = load_json_file(CONFIG_FILE)
        
        config['game_modes'] = data
        
        if save_json_file(CONFIG_FILE, config):
            notify_update('game_modes')
            return jsonify({'success': True, 'game_modes': data})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Sube un archivo (imagen o sonido)"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            return jsonify({
                'success': True, 
                'filename': filename,
                'url': f'/uploads/{filename}'
            })
        
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Sirve archivos subidos"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas del juego"""
    try:
        questions = load_json_file(QUESTIONS_FILE)
        ranking_raw = load_json_file(RANKING_FILE)
        users = load_json_file(USERS_FILE)
        
        # Soportar ranking como lista o como dict con clave 'rankings'
        if isinstance(ranking_raw, dict) and 'rankings' in ranking_raw:
            ranking = ranking_raw['rankings']
        elif isinstance(ranking_raw, list):
            ranking = ranking_raw
        else:
            ranking = []
            
        # Contar usuarios registrados (excluyendo admin)
        if isinstance(users, dict):
            registered_users = [u for u in users.values() if u.get('username') and str(u.get('username')).lower() != 'admin']
        elif isinstance(users, list):
            registered_users = [u for u in users if u.get('username') and str(u.get('username')).lower() != 'admin']
        else:
            registered_users = []
        
        # Debug: imprimir información para verificar
        print(f"[DEBUG] Tipo de usuarios: {type(users)}")
        print(f"[DEBUG] Usuarios cargados: {len(users) if users else 0}")
        print(f"[DEBUG] Usuarios registrados (sin admin): {len(registered_users)}")
        if isinstance(users, dict):
            print(f"[DEBUG] Nombres de usuarios: {list(users.keys())}")
            print(f"[DEBUG] Contenido completo: {users}")
        elif isinstance(users, list):
            print(f"[DEBUG] Nombres de usuarios: {[u.get('username') for u in users]}")
        else:
            print(f"[DEBUG] Usuarios es None o tipo inesperado: {users}")
            
        if not isinstance(questions, list):
            questions = []
            
        # Estadísticas básicas
        stats = {
            'total_questions': len(questions),
            'total_players': len(registered_users),  # Jugadores registrados
            'total_games': len(ranking),
            'questions_by_category': {},
            'questions_by_difficulty': {},
            'top_players': sorted(ranking, key=lambda x: x.get('score', 0), reverse=True)[:10] if ranking else []
        }
        # Contar preguntas por categoría y dificultad
        for question in questions:
            if isinstance(question, dict):
                category = question.get('categoria', 'Sin categoría')
                difficulty = question.get('dificultad', 'Sin dificultad')
                stats['questions_by_category'][category] = stats['questions_by_category'].get(category, 0) + 1
                stats['questions_by_difficulty'][difficulty] = stats['questions_by_difficulty'].get(difficulty, 0) + 1
        return jsonify(stats)
    except Exception as e:
        print(f"Error en get_stats: {e}")
        # Devolver estadísticas vacías en caso de error
        return jsonify({
            'total_questions': 0,
            'total_players': 0,
            'total_games': 0,
            'questions_by_category': {},
            'questions_by_difficulty': {},
            'top_players': []
        })

@app.route('/api/sync', methods=['POST'])
def sync_data():
    """Sincroniza datos entre el juego y el panel de administración"""
    try:
        data = request.json
        sync_type = data.get('type', '')
        
        if sync_type == 'questions':
            # Recargar preguntas desde el archivo
            questions = load_json_file(QUESTIONS_FILE)
            return jsonify({'success': True, 'questions': questions})
        elif sync_type == 'ranking':
            # Recargar ranking desde el archivo
            ranking = load_json_file(RANKING_FILE)
            return jsonify({'success': True, 'ranking': ranking})
        else:
            return jsonify({'success': False, 'error': 'Tipo de sincronización no válido'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/errors', methods=['POST'])
def report_error():
    """Reporta un error desde el juego"""
    try:
        data = request.json
        
        # Crear archivo de errores si no existe
        errors_file = os.path.join(DATA_FOLDER, 'errors.json')
        errors = load_json_file(errors_file)
        
        # Agregar nuevo error
        new_error = {
            'id': len(errors) + 1,
            'name': data.get('name', 'Anónimo'),
            'description': data.get('description', ''),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'version': data.get('version', '1.0.0'),
            'status': 'pendiente'
        }
        
        errors.append(new_error)
        
        # Guardar errores
        if save_json_file(errors_file, errors):
            return jsonify({'success': True, 'error': new_error}), 201
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/errors', methods=['GET'])
def get_errors():
    """Obtiene la lista de errores reportados"""
    errors_file = os.path.join(DATA_FOLDER, 'errors.json')
    errors = load_json_file(errors_file)
    return jsonify(errors)

@app.route('/api/errors/<int:error_id>', methods=['PUT'])
def update_error(error_id):
    """Actualiza el estado de un error reportado"""
    try:
        data = request.json
        errors_file = os.path.join(DATA_FOLDER, 'errors.json')
        errors = load_json_file(errors_file)
        
        for i, error in enumerate(errors):
            if error.get('id') == error_id:
                errors[i].update({
                    'status': data.get('status', error.get('status')),
                    'updated_at': datetime.now().isoformat()
                })
                
                if save_json_file(errors_file, errors):
                    return jsonify({'success': True, 'error': errors[i]})
                else:
                    return jsonify({'success': False, 'error': 'Error al guardar'}), 500
        
        return jsonify({'success': False, 'error': 'Error no encontrado'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = load_json_file(CATEGORIES_FILE)
    response = jsonify(categories)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.json
    categories = load_json_file(CATEGORIES_FILE)
    if data.get('name') and data['name'] not in categories:
        categories.append(data['name'])
        save_json_file(CATEGORIES_FILE, categories)
        notify_update('categories')
        return jsonify({'success': True, 'categories': categories})
    return jsonify({'success': False, 'error': 'Nombre inválido o ya existe'}), 400

@app.route('/api/categories/<string:name>', methods=['PUT'])
def update_category(name):
    data = request.json
    categories = load_json_file(CATEGORIES_FILE)
    if name in categories and data.get('newName'):
        idx = categories.index(name)
        categories[idx] = data['newName']
        save_json_file(CATEGORIES_FILE, categories)
        notify_update('categories')
        return jsonify({'success': True, 'categories': categories})
    return jsonify({'success': False, 'error': 'Categoría no encontrada o nombre inválido'}), 400

@app.route('/api/categories/<string:name>', methods=['DELETE'])
def delete_category(name):
    categories = load_json_file(CATEGORIES_FILE)
    if name in categories:
        # Eliminar la categoría
        categories.remove(name)
        save_json_file(CATEGORIES_FILE, categories)
        
        # Manejar preguntas asociadas a la categoría eliminada
        questions = load_json_file(QUESTIONS_FILE)
        if isinstance(questions, list):
            # Opción 1: Eliminar todas las preguntas de la categoría
            questions = [q for q in questions if q.get('categoria') != name]
            
            # Opción 2: Reasignar preguntas a una categoría por defecto
            # Si prefieres reasignar en lugar de eliminar, descomenta estas líneas:
            # default_category = categories[0] if categories else 'General'
            # for q in questions:
            #     if q.get('categoria') == name:
            #         q['categoria'] = default_category
            
            save_json_file(QUESTIONS_FILE, questions)
            notify_update('questions')
        
        notify_update('categories')
        return jsonify({'success': True, 'categories': categories})
    return jsonify({'success': False, 'error': 'Categoría no encontrada'}), 404

@app.route('/api/sounds', methods=['GET'])
def list_sounds():
    sound_files = {}
    for folder in SOUNDS_FOLDERS:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.lower().endswith(SOUNDS_EXTENSIONS):
                    file_path = os.path.join(folder, f)
                    # Solo incluir archivos con tamaño mayor a cero y no duplicados
                    if os.path.getsize(file_path) > 0 and f not in sound_files:
                        sound_files[f] = {'name': f, 'path': f'/sounds/{f}'}
    return jsonify(list(sound_files.values()))

@app.route('/api/sounds', methods=['POST'])
def upload_sound():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder = SOUNDS_FOLDERS[0]
        file.save(os.path.join(folder, filename))
        return jsonify({'success': True, 'filename': filename, 'url': f'/sounds/{filename}'})
    return jsonify({'success': False, 'error': 'File type not allowed'}), 400

@app.route('/api/sounds/<string:filename>', methods=['DELETE'])
def delete_sound(filename):
    deleted = False
    for folder in SOUNDS_FOLDERS:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted = True
    if deleted:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404

@app.route('/sounds/<string:filename>')
def serve_sound(filename):
    for folder in SOUNDS_FOLDERS:
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            return send_from_directory(folder, filename)
    return 'Archivo no encontrado', 404

@app.route('/api/players', methods=['GET'])
def get_players():
    users = load_json_file(USERS_FILE)
    if isinstance(users, dict):
        users = list(users.values())
    elif isinstance(users, list):
        pass
    else:
        users = []
    # Solo jugadores (no admins)
    players = [u for u in users if not u.get('is_admin', False)]
    return jsonify(players)

@app.route('/api/players', methods=['POST'])
def add_player():
    data = request.json
    users = load_json_file(USERS_FILE)
    if isinstance(users, dict):
        users_dict = users
    elif isinstance(users, list):
        users_dict = {u['username']: u for u in users if 'username' in u}
    else:
        users_dict = {}
    # Verificar si el usuario ya existe
    if data.get('username') in users_dict:
        return jsonify({'success': False, 'error': 'Usuario ya existe'}), 409
    new_id = max([int(u.get('id', 0)) for u in users_dict.values() if str(u.get('id', '')).isdigit()], default=0) + 1
    new_user = {
        'id': str(new_id),
        'username': data.get('username', ''),
        'fullName': data.get('fullName', ''),
        'password': data.get('password', ''),
        'email': data.get('email', ''),
        'created_at': data.get('created_at', datetime.now().isoformat()),
        'last_login': data.get('last_login', datetime.now().isoformat()),
        'stats': data.get('stats', {
            'total_games': 0,
            'total_score': 0,
            'best_score': 0,
            'favorite_mode': '',
            'favorite_category': ''
        }),
        'score': data.get('score', 0),
        'mode': data.get('mode', ''),
        'categoria': data.get('categoria', ''),
        'correctas': data.get('correctas', 0),
        'incorrectas': data.get('incorrectas', 0),
        'tiempo': data.get('tiempo', 0),
        'fecha': datetime.now().isoformat()
    }
    users_dict[new_user['username']] = new_user
    save_json_file(USERS_FILE, users_dict)
    notify_update('players')
    return jsonify({'success': True, 'player': new_user}), 201

@app.route('/api/players/<string:user_id>', methods=['PUT'])
def update_player(user_id):
    data = request.json
    users = load_json_file(USERS_FILE)
    # Manejar diferentes formatos de archivo
    if isinstance(users, dict):
        users_list = list(users.values())
        is_dict_format = True
    elif isinstance(users, list):
        users_list = users
        is_dict_format = False
    else:
        users_list = []
        is_dict_format = False
    for i, user in enumerate(users_list):
        if str(user.get('id')) == str(user_id):
            if 'newPassword' in data and data['newPassword']:
                import hashlib
                user['password'] = hashlib.sha256(data['newPassword'].encode()).hexdigest()
            for key, value in data.items():
                if key != 'newPassword':
                    if key == 'stats' and isinstance(value, dict):
                        if 'stats' not in user:
                            user['stats'] = {}
                        user['stats'].update(value)
                    else:
                        user[key] = value
            if is_dict_format:
                users_dict = {}
                for u in users_list:
                    users_dict[u['username']] = u
                save_json_file(USERS_FILE, users_dict)
            else:
                save_json_file(USERS_FILE, users_list)
            notify_update('players')
            return jsonify({'success': True, 'player': users_list[i]})
    return jsonify({'success': False, 'error': 'Jugador no encontrado'}), 404

@app.route('/api/players/<string:user_id>', methods=['DELETE'])
def delete_player(user_id):
    users = load_json_file(USERS_FILE)
    if isinstance(users, dict):
        users_list = list(users.values())
        is_dict_format = True
    elif isinstance(users, list):
        users_list = users
        is_dict_format = False
    else:
        users_list = []
        is_dict_format = False
    new_users = [u for u in users_list if str(u.get('id')) != str(user_id)]
    if is_dict_format:
        users_dict = {}
        for u in new_users:
            users_dict[u['username']] = u
        save_json_file(USERS_FILE, users_dict)
    else:
        save_json_file(USERS_FILE, new_users)
    notify_update('players')
    return jsonify({'success': True})

@app.route('/api/admins', methods=['GET'])
def get_admins():
    admins = load_json_file(ADMINS_FILE)
    if isinstance(admins, dict):
        admins = list(admins.values())
    # Solo admins
    admins = [a for a in admins if a.get('is_admin', True)]
    return jsonify(admins)

@app.route('/api/admin-users', methods=['GET'])
def get_admin_users():
    admins = load_json_file(ADMINS_FILE)
    # Filtrar solo administradores reales
    if isinstance(admins, dict):
        admins = list(admins.values())
    elif not isinstance(admins, list):
        admins = []
    # Solo admins (is_admin True o por convención)
    admins = [a for a in admins if a.get('is_admin', True)]
    return jsonify({'success': True, 'users': admins})

@app.route('/api/admin-users', methods=['POST'])
def add_admin_user():
    data = request.json
    admins = load_json_file(ADMINS_FILE)
    if isinstance(admins, dict):
        admins_dict = admins
    elif isinstance(admins, list):
        admins_dict = {a['username']: a for a in admins if 'username' in a}
    else:
        admins_dict = {}
    if data.get('username') in admins_dict:
        return jsonify({'success': False, 'error': 'El nombre de usuario ya existe'}), 409
    new_id = max([int(a.get('id', 0)) for a in admins_dict.values() if str(a.get('id', '')).isdigit()], default=0) + 1
    new_admin = {
        'id': str(new_id),
        'username': data.get('username', ''),
        'fullName': data.get('fullName', ''),
        'password': data.get('password', ''),
        'email': data.get('email', ''),
        'created_at': data.get('created_at', datetime.now().isoformat()),
        'last_login': data.get('last_login', datetime.now().isoformat()),
        'is_admin': True
    }
    admins_dict[new_admin['username']] = new_admin
    save_json_file(ADMINS_FILE, admins_dict)
    return jsonify({'success': True, 'user': new_admin}), 201

@app.route('/api/admin-users/<int:user_id>', methods=['PUT'])
def update_admin_user(user_id):
    data = request.json
    admins = load_json_file(ADMINS_FILE)
    for i, admin in enumerate(admins):
        if admin.get('id') == user_id:
            admins[i].update({
                'fullName': data.get('fullName', admin.get('fullName', '')),
                'username': data.get('username', admin.get('username', '')),
                'password': data.get('password', admin.get('password', '')),
                'email': data.get('email', admin.get('email', ''))
            })
            if save_json_file(ADMINS_FILE, admins):
                notify_update('admin_users')
                return jsonify({'success': True, 'user': admins[i]})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
    return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

@app.route('/api/admin-users/<int:user_id>', methods=['DELETE'])
def delete_admin_user(user_id):
    admins = load_json_file(ADMINS_FILE)
    # Convertir a lista si es dict
    if isinstance(admins, dict):
        admins_list = list(admins.values())
    else:
        admins_list = admins
    # No permitir eliminar el admin principal (id=1)
    if str(user_id) == '1':
        return jsonify({'success': False, 'error': 'No se puede eliminar el administrador principal'}), 403
    new_admins = [a for a in admins_list if str(a.get('id')) != str(user_id)]
    # Guardar como dict por username
    admins_dict = {a['username']: a for a in new_admins if 'username' in a}
    save_json_file(ADMINS_FILE, admins_dict)
    notify_update('admin_users')
    return jsonify({'success': True})

@app.route('/api/admin-recovery', methods=['POST'])
def admin_recovery():
    # Solo permitir si existe el archivo de recuperación
    if not os.path.exists(RESET_FILE):
        return jsonify({'success': False, 'error': 'Recuperación no habilitada'}), 403
    data = request.json
    new_password = data.get('password', '').strip()
    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'error': 'Contraseña inválida'}), 400
    admins = load_json_file(ADMINS_FILE)
    if not admins:
        return jsonify({'success': False, 'error': 'No hay administradores registrados'}), 404
    # Restablecer la contraseña del primer admin
    admins[0]['password'] = new_password
    if save_json_file(ADMINS_FILE, admins):
        os.remove(RESET_FILE)
        return jsonify({'success': True, 'message': 'Contraseña restablecida correctamente'})
    else:
        return jsonify({'success': False, 'error': 'Error al guardar'}), 500

@app.route('/api/admin-users/<int:user_id>/image', methods=['POST'])
def upload_admin_image(user_id):
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No se envió imagen'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400
    if not allowed_image(file.filename):
        return jsonify({'success': False, 'error': 'Formato no permitido (solo JPG/PNG)'}), 400
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_IMAGE_SIZE:
        return jsonify({'success': False, 'error': 'La imagen supera el tamaño máximo de 1MB'}), 400
    filename = secure_filename(f"admin_{user_id}.{file.filename.rsplit('.', 1)[1].lower()}")
    filepath = os.path.join(UPLOADS_ADMIN_FOLDER, filename)
    file.save(filepath)
    # Actualizar usuario
    admins = load_json_file(ADMINS_FILE)
    for a in admins:
        if a.get('id') == user_id:
            a['image'] = f"/uploads/admins/{filename}"
            break
    save_json_file(ADMINS_FILE, admins)
    return jsonify({'success': True, 'image': f"/uploads/admins/{filename}"})

@app.route('/uploads/admins/<filename>')
def serve_admin_image(filename):
    return send_from_directory(UPLOADS_ADMIN_FOLDER, filename)

@app.route('/api/user_stats', methods=['GET'])
def get_user_stats():
    try:
        if os.path.exists(USER_STATS_FILE):
            with open(USER_STATS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Si el archivo es un dict con 'users', devolver solo eso
            if isinstance(data, dict) and 'users' in data:
                return jsonify({'users': data['users']})
            elif isinstance(data, dict):
                return jsonify({'users': data})
        return jsonify({'users': {}})
    except Exception as e:
        print(f"Error en /api/user_stats: {e}")
        return jsonify({'users': {}})

@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    # Devuelve una lista vacía o de ejemplo
    return jsonify([])

@app.route('/api/game_history', methods=['GET'])
def get_game_history():
    # Devuelve un historial vacío o de ejemplo
    return jsonify({'history': []})

@app.route('/api/category-colors', methods=['GET'])
def get_category_colors():
    """Obtiene los colores de las categorías"""
    try:
        colors_file = os.path.join(DATA_FOLDER, 'category_colors.json')
        if os.path.exists(colors_file):
            colors = load_json_file(colors_file)
        else:
            # Crear archivo con colores por defecto
            colors = {
                "Historia": {
                    "bg_color": "#2c3e50",
                    "icon": "📚",
                    "text_color": "white",
                    "hover_color": "#34495e",
                    "border_color": "#1a2a2e",
                    "shadow_color": "#1a2a2e"
                },
                "Ciencia": {
                    "bg_color": "#27ae60",
                    "icon": "🔬",
                    "text_color": "white",
                    "hover_color": "#2ecc71",
                    "border_color": "#1a2a2e",
                    "shadow_color": "#1a2a2e"
                },
                "Geografía": {
                    "bg_color": "#16a085",
                    "icon": "🌎",
                    "text_color": "white",
                    "hover_color": "#1abc9c",
                    "border_color": "#1a2a2e",
                    "shadow_color": "#1a2a2e"
                },
                "Arte": {
                    "bg_color": "#8e44ad",
                    "icon": "🎨",
                    "text_color": "white",
                    "hover_color": "#9b59b6",
                    "border_color": "#1a2a2e",
                    "shadow_color": "#1a2a2e"
                },
                "Deportes": {
                    "bg_color": "#d35400",
                    "icon": "⚽",
                    "text_color": "white",
                    "hover_color": "#e67e22",
                    "border_color": "#1a2a2e",
                    "shadow_color": "#1a2a2e"
                },
                "Entretenimiento": {
                    "bg_color": "#c0392b",
                    "icon": "🎮",
                    "text_color": "white",
                    "hover_color": "#e74c3c",
                    "border_color": "#1a2a2e",
                    "shadow_color": "#1a2a2e"
                },
                "General": {
                    "bg_color": "#1a2a2e",
                    "icon": "❓",
                    "text_color": "white",
                    "hover_color": "#2c3e50",
                    "border_color": "#1a2a2e",
                    "shadow_color": "#1a2a2e"
                }
            }
            save_json_file(colors_file, colors)
        response = jsonify(colors)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response
    except Exception as e:
        print(f"Error obteniendo colores de categorías: {e}")
        return jsonify({})

@app.route('/api/category-colors', methods=['PUT'])
def update_category_colors():
    """Actualiza los colores de las categorías"""
    try:
        data = request.json
        colors_file = os.path.join(DATA_FOLDER, 'category_colors.json')
        
        if save_json_file(colors_file, data):
            notify_update('category_colors')
            return jsonify({'success': True, 'colors': data})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/category-colors/<string:category>', methods=['PUT'])
def update_category_color(category):
    """Actualiza el color de una categoría específica"""
    try:
        data = request.json
        colors_file = os.path.join(DATA_FOLDER, 'category_colors.json')
        colors = load_json_file(colors_file)
        
        if category in colors:
            colors[category].update(data)
            if save_json_file(colors_file, colors):
                notify_update('category_colors')
                return jsonify({'success': True, 'category': category, 'colors': colors[category]})
            else:
                return jsonify({'success': False, 'error': 'Error al guardar'}), 500
        else:
            return jsonify({'success': False, 'error': 'Categoría no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/button-styles', methods=['GET'])
def get_button_styles():
    """Obtiene los estilos de botones"""
    try:
        styles_file = os.path.join(DATA_FOLDER, 'button_styles.json')
        if os.path.exists(styles_file):
            styles = load_json_file(styles_file)
        else:
            # Crear archivo con estilos por defecto
            styles = {
                "button_shape": "rounded-lg",
                "button_color": "#3498db",
                "button_text_color": "white",
                "button_hover_color": "#2980b9",
                "button_border_width": 0,
                "button_relief": "flat",
                "button_font": "Arial",
                "button_font_size": 14,
                "button_font_weight": "bold"
            }
            save_json_file(styles_file, styles)
        response = jsonify(styles)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response
    except Exception as e:
        print(f"Error obteniendo estilos de botones: {e}")
        return jsonify({})

@app.route('/api/button-styles', methods=['PUT'])
def update_button_styles():
    """Actualiza los estilos de botones"""
    try:
        data = request.json
        styles_file = os.path.join(DATA_FOLDER, 'button_styles.json')
        
        if save_json_file(styles_file, data):
            notify_update('button_styles')
            return jsonify({'success': True, 'styles': data})
        else:
            return jsonify({'success': False, 'error': 'Error al guardar'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def notify_update(tipo):
    socketio.emit('data_update', {'type': tipo})

def is_admin_authenticated():
    # Aquí puedes mejorar la autenticación según tu sistema
    token = request.headers.get('X-Admin-Token')
    # Por simplicidad, usa un token fijo (cámbialo en producción)
    return token == 'admin-secret-token'

@app.route('/api/clean-orphan-questions', methods=['POST'])
def clean_orphan_questions_api():
    if not is_admin_authenticated():
        abort(403, description='No autorizado')
    try:
        # Ejecutar el script de limpieza
        result = subprocess.run(['python', '../utils/clean_orphan_questions.py'], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        output = result.stdout + '\n' + result.stderr
        if result.returncode == 0:
            notify_update('questions')
            return jsonify({'success': True, 'output': output})
        else:
            return jsonify({'success': False, 'error': output}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Servidor de administracion iniciado en http://localhost:5000")
    print("API disponible en http://localhost:5000/api/")
    print("Web de administracion en http://localhost:3000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True) 