import json
import os
import requests
import threading
import time
from datetime import datetime
import hashlib
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.auto_backup import auto_backup

class CloudSync:
    def __init__(self, api_url="http://localhost:5000/api"):
        self.api_url = api_url
        self.sync_interval = 30  # Sincronizar cada 30 segundos
        self.last_sync = {}
        self.sync_running = False
        
    def start_auto_sync(self):
        """Inicia la sincronización automática en segundo plano"""
        if not self.sync_running:
            self.sync_running = True
            threading.Thread(target=self._auto_sync_loop, daemon=True).start()
            print("🔄 Sincronización automática iniciada")
    
    def stop_auto_sync(self):
        """Detiene la sincronización automática"""
        self.sync_running = False
        print("⏹️ Sincronización automática detenida")
    
    def _auto_sync_loop(self):
        """Bucle de sincronización automática"""
        while self.sync_running:
            try:
                self.sync_all_data()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"Error en sincronización automática: {e}")
                time.sleep(60)  # Esperar más tiempo si hay error
    
    def sync_all_data(self):
        """Sincroniza todos los datos del usuario"""
        try:
            # Sincronizar usuarios
            self.sync_users()
            
            # Sincronizar estadísticas
            self.sync_user_stats()
            
            # Sincronizar ranking
            self.sync_ranking()
            
            # Sincronizar logros
            self.sync_achievements()
            
            print("✅ Sincronización completada")
            
        except Exception as e:
            print(f"❌ Error en sincronización: {e}")
    
    def sync_users(self):
        """Sincroniza usuarios locales con el servidor"""
        try:
            local_users = self.load_local_users()
            
            for user in local_users:
                # Verificar si el usuario ya existe en el servidor
                server_user = self.get_server_user(user['username'])
                
                if not server_user:
                    # Usuario nuevo, enviar al servidor
                    self.create_server_user(user)
                else:
                    # Usuario existe, actualizar si es necesario
                    if self.needs_update(user, server_user):
                        self.update_server_user(user)
                        
        except Exception as e:
            print(f"Error sincronizando usuarios: {e}")
    
    def sync_user_stats(self):
        """Sincroniza estadísticas de usuario"""
        try:
            if os.path.exists('data/user_stats.json'):
                with open('data/user_stats.json', 'r', encoding='utf-8') as f:
                    local_stats = json.load(f)
                
                # Enviar estadísticas al servidor
                response = requests.post(f"{self.api_url}/user_stats", json=local_stats, timeout=10)
                if response.status_code == 200:
                    print("📊 Estadísticas sincronizadas")
                    
        except Exception as e:
            print(f"Error sincronizando estadísticas: {e}")
    
    def sync_ranking(self):
        """Sincroniza el ranking local con el servidor"""
        try:
            if os.path.exists('data/ranking.json'):
                with open('data/ranking.json', 'r', encoding='utf-8') as f:
                    local_ranking = json.load(f)
                
                # Obtener ranking del servidor
                response = requests.get(f"{self.api_url}/ranking", timeout=10)
                if response.status_code == 200:
                    server_ranking = response.json()
                    
                    # Combinar rankings
                    merged_ranking = self.merge_rankings(local_ranking, server_ranking)
                    
                    # Guardar ranking combinado
                    with open('data/ranking.json', 'w', encoding='utf-8') as f:
                        json.dump(merged_ranking, f, ensure_ascii=False, indent=2)
                    
                    print("🏆 Ranking sincronizado")
                    
        except Exception as e:
            print(f"Error sincronizando ranking: {e}")
    
    def sync_achievements(self):
        """Sincroniza logros del usuario"""
        try:
            if os.path.exists('data/achievements.json'):
                with open('data/achievements.json', 'r', encoding='utf-8') as f:
                    local_achievements = json.load(f)
                
                # Enviar logros al servidor
                response = requests.post(f"{self.api_url}/achievements", json=local_achievements, timeout=10)
                if response.status_code == 200:
                    print("🏅 Logros sincronizados")
                    
        except Exception as e:
            print(f"Error sincronizando logros: {e}")
    
    def load_local_users(self):
        """Carga usuarios locales"""
        try:
            if os.path.exists('data/usuarios.json'):
                with open('data/usuarios.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def get_server_user(self, username):
        """Obtiene un usuario del servidor"""
        try:
            response = requests.get(f"{self.api_url}/players?username={username}", timeout=10)
            if response.status_code == 200:
                users = response.json()
                return next((user for user in users if user.get('username') == username), None)
        except Exception:
            pass
        return None
    
    def create_server_user(self, user_data):
        """Crea un usuario en el servidor"""
        try:
            response = requests.post(f"{self.api_url}/players", json=user_data, timeout=10)
            if response.status_code == 201:
                print(f"👤 Usuario {user_data['username']} creado en el servidor")
                return True
        except Exception as e:
            print(f"Error creando usuario en servidor: {e}")
        return False
    
    def update_server_user(self, user_data):
        """Actualiza un usuario en el servidor"""
        try:
            response = requests.put(f"{self.api_url}/players/{user_data['id']}", json=user_data, timeout=10)
            if response.status_code == 200:
                print(f"🔄 Usuario {user_data['username']} actualizado en el servidor")
                return True
        except Exception as e:
            print(f"Error actualizando usuario en servidor: {e}")
        return False
    
    def needs_update(self, local_user, server_user):
        """Verifica si un usuario necesita actualización"""
        # Comparar fechas de último login
        local_last_login = local_user.get('last_login', '')
        server_last_login = server_user.get('last_login', '')
        
        if local_last_login > server_last_login:
            return True
            
        # Comparar estadísticas
        local_stats = local_user.get('stats', {})
        server_stats = server_user.get('stats', {})
        
        if local_stats.get('total_games', 0) > server_stats.get('total_games', 0):
            return True
            
        return False
    
    def merge_rankings(self, local_ranking, server_ranking):
        """Combina rankings locales y del servidor"""
        try:
            # Manejar diferentes formatos de datos
            if isinstance(local_ranking, list):
                local_scores = local_ranking
            else:
                local_scores = local_ranking.get('rankings', [])
            
            if isinstance(server_ranking, list):
                server_scores = server_ranking
            else:
                server_scores = server_ranking.get('rankings', [])
            
            # Crear diccionario de puntuaciones por usuario
            all_scores = {}
            
            # Agregar puntuaciones locales
            for score in local_scores:
                if isinstance(score, dict):
                    key = f"{score.get('username')}_{score.get('mode')}_{score.get('categoria')}"
                    if key not in all_scores or score.get('score', 0) > all_scores[key].get('score', 0):
                        all_scores[key] = score
            
            # Agregar puntuaciones del servidor
            for score in server_scores:
                if isinstance(score, dict):
                    key = f"{score.get('username')}_{score.get('mode')}_{score.get('categoria')}"
                    if key not in all_scores or score.get('score', 0) > all_scores[key].get('score', 0):
                        all_scores[key] = score
            
            # Convertir de vuelta a lista y ordenar
            merged_scores = list(all_scores.values())
            merged_scores.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return {'rankings': merged_scores}
            
        except Exception as e:
            print(f"Error combinando rankings: {e}")
            return local_ranking
    
    def download_user_data(self, username):
        """Descarga datos de un usuario desde el servidor"""
        try:
            # Descargar estadísticas
            response = requests.get(f"{self.api_url}/user_stats/{username}", timeout=10)
            if response.status_code == 200:
                user_stats = response.json()
                
                # Guardar estadísticas localmente
                self.save_user_stats_locally(username, user_stats)
                print(f"📥 Datos de {username} descargados del servidor")
                return True
                
        except Exception as e:
            print(f"Error descargando datos de usuario: {e}")
        return False
    
    def save_user_stats_locally(self, username, stats):
        """Guarda estadísticas de usuario localmente"""
        try:
            if os.path.exists('data/user_stats.json'):
                with open('data/user_stats.json', 'r', encoding='utf-8') as f:
                    all_stats = json.load(f)
            else:
                all_stats = {'users': {}}
            
            all_stats['users'][username] = stats
            
            with open('data/user_stats.json', 'w', encoding='utf-8') as f:
                auto_backup('data/user_stats.json')
                json.dump(all_stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error guardando estadísticas localmente: {e}")
    
    def get_sync_status(self):
        """Obtiene el estado de sincronización"""
        return {
            'running': self.sync_running,
            'last_sync': self.last_sync,
            'interval': self.sync_interval
        }
    
    def force_sync(self):
        """Fuerza una sincronización inmediata"""
        print("🔄 Iniciando sincronización forzada...")
        self.sync_all_data()
        print("✅ Sincronización forzada completada")

class OfflineManager:
    def __init__(self):
        self.offline_queue = []
        self.queue_file = 'data/offline_queue.json'
        self.load_queue()
    
    def add_to_queue(self, action, data):
        """Agrega una acción a la cola offline"""
        queue_item = {
            'id': self.generate_queue_id(),
            'action': action,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'retries': 0
        }
        
        self.offline_queue.append(queue_item)
        self.save_queue()
        print(f"📝 Acción agregada a cola offline: {action}")
    
    def process_queue(self):
        """Procesa la cola offline cuando hay conexión"""
        if not self.offline_queue:
            return
            
        print(f"🔄 Procesando {len(self.offline_queue)} acciones en cola...")
        
        processed = []
        failed = []
        
        for item in self.offline_queue:
            try:
                if self.execute_action(item):
                    processed.append(item)
                else:
                    item['retries'] += 1
                    if item['retries'] < 3:
                        failed.append(item)
            except Exception as e:
                print(f"Error procesando acción {item['action']}: {e}")
                item['retries'] += 1
                if item['retries'] < 3:
                    failed.append(item)
        
        # Actualizar cola
        self.offline_queue = failed
        self.save_queue()
        
        print(f"✅ {len(processed)} acciones procesadas, {len(failed)} fallidas")
    
    def execute_action(self, item):
        """Ejecuta una acción de la cola"""
        try:
            if item['action'] == 'save_score':
                return self.execute_save_score(item['data'])
            elif item['action'] == 'update_stats':
                return self.execute_update_stats(item['data'])
            elif item['action'] == 'save_achievement':
                return self.execute_save_achievement(item['data'])
            else:
                print(f"Acción desconocida: {item['action']}")
                return False
        except Exception as e:
            print(f"Error ejecutando acción: {e}")
            return False
    
    def execute_save_score(self, data):
        """Ejecuta guardar puntuación"""
        try:
            response = requests.post("http://localhost:5000/api/ranking", json=data, timeout=10)
            return response.status_code == 201
        except Exception:
            return False
    
    def execute_update_stats(self, data):
        """Ejecuta actualizar estadísticas"""
        try:
            response = requests.post("http://localhost:5000/api/user_stats", json=data, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def execute_save_achievement(self, data):
        """Ejecuta guardar logro"""
        try:
            response = requests.post("http://localhost:5000/api/achievements", json=data, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_queue_id(self):
        """Genera un ID único para la cola"""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    
    def load_queue(self):
        """Carga la cola desde archivo"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    self.offline_queue = json.load(f)
        except Exception:
            self.offline_queue = []
    
    def save_queue(self):
        """Guarda la cola en archivo"""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.offline_queue, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando cola offline: {e}")
    
    def get_queue_status(self):
        """Obtiene el estado de la cola"""
        return {
            'pending': len(self.offline_queue),
            'items': self.offline_queue
        } 