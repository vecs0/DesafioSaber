import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import random
import time
from datetime import datetime
import pygame
from PIL import Image, ImageTk
import requests
import threading
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.auto_backup import auto_backup

# Imports para funcionalidades del juego
try:
    from achievements import AchievementManager
except ImportError:
    print("⚠️ AchievementManager no disponible")
    class AchievementManager:
        def __init__(self, app):
            pass

try:
    from cloud_sync import WebSocketListener
except ImportError:
    print("⚠️ WebSocketListener no disponible")
    class WebSocketListener:
        def __init__(self, app):
            pass
        def start(self):
            pass

# Importar sistema de registro y sincronización
try:
    from user_registration import UserRegistration, UserLogin
    from cloud_sync import CloudSync, OfflineManager
    REGISTRATION_AVAILABLE = True
except ImportError:
    print("⚠️ Sistema de registro no disponible")
    REGISTRATION_AVAILABLE = False
try:
    from api_client import APIClient
except ImportError:
    try:
        from .api_client import APIClient
    except ImportError:
        # Crear una clase dummy si no se puede importar
        class APIClient:
            def __init__(self):
                pass
            def get_categories(self):
                return ["Historia", "Ciencia", "Geografía", "Arte", "Deportes", "Entretenimiento"]
            def get_sounds(self):
                return []
            def get_questions(self):
                return []
            def save_score(self, score_data):
                return True
            def report_error(self, error_data):
                return True
import socketio
# Importaciones de matplotlib con manejo de errores
try:
    import matplotlib
    matplotlib.use('Agg')  # Usar backend no interactivo
    import matplotlib.pyplot as plt
    try:
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        MATPLOTLIB_AVAILABLE = True
    except ImportError:
        # Si el backend tkagg no está disponible, usar solo matplotlib básico
        FigureCanvasTkAgg = None
        MATPLOTLIB_AVAILABLE = False
        print("Backend tkagg no disponible. Los gráficos no se mostrarán.")
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    FigureCanvasTkAgg = None
    print("Matplotlib no está disponible. Los gráficos no se mostrarán.")

# Importación de numpy con manejo de errores
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy no está disponible. Algunas funcionalidades pueden no funcionar correctamente.")

# Inicializar pygame y mixer correctamente
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

class SoundManager:
    def __init__(self):
        """Inicializa el administrador de sonidos"""
        self.enabled = True
        self.sounds = {}
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sound_files = {
            'acierto': os.path.join(base_dir, 'assets', 'sounds', 'acierto.mp3'),
            'errado': os.path.join(base_dir, 'assets', 'sounds', 'errado.mp3'),
            'despliegue': os.path.join(base_dir, 'assets', 'sounds', 'despliegue_opciones.mp3'),
            'intro_music': os.path.join(base_dir, 'assets', 'sounds', 'intro.mp3')
        }
        try:
            for sound_name, sound_file in self.sound_files.items():
                if not os.path.exists(sound_file):
                    print(f"[Advertencia] No se encontró el archivo de sonido: {sound_file}")
                    continue
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_file)
                except Exception as e:
                    print(f"Error cargando sonido {sound_name}: {e}")
        except Exception as e:
            print(f"Error inicializando pygame.mixer: {e}")
            self.enabled = False
    
    def play_sound(self, sound_name, volume=1.0, loop=False):
        """Reproduce un sonido con volumen opcional y opción de bucle"""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            if loop:
                sound.play(-1)  # -1 significa reproducir en bucle infinito
            else:
                sound.play()
        except Exception as e:
            print(f"Error reproduciendo sonido {sound_name}: {e}")
    
    def stop_sound(self, sound_name):
        """Detiene un sonido específico"""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        try:
            self.sounds[sound_name].stop()
        except Exception as e:
            print(f"Error deteniendo sonido {sound_name}: {e}")
    
    def stop_all_sounds(self):
        """Detiene todos los sonidos"""
        if not self.enabled:
            return
        
        try:
            pygame.mixer.stop()
        except Exception as e:
            print(f"Error deteniendo todos los sonidos: {e}")
    
    def set_enabled(self, enabled):
        """Activa o desactiva el administrador de sonidos"""
        self.enabled = enabled

class GameMode:
    CLASSIC = "Clásico"
    TIMEATTACK = "Contrarreloj"
    DUEL = "Duelo"

    _dynamic_configs = None

    @staticmethod
    def load_dynamic_configs():
        """Carga la configuración de modos desde la API si está disponible, si no, usa local."""
        try:
            import requests
            response = requests.get('http://localhost:5000/api/config', timeout=2)
            if response.status_code == 200:
                config = response.json()
                if 'game_modes' in config:
                    # Mapear claves del backend a las internas
                    mapped_modes = {}
                    for m in config['game_modes']:
                        name = m.get('name')
                        mapped = {
                            'num_questions': m.get('numQuestions', m.get('num_questions', 15)),
                            'time_per_question': m.get('timePerQuestion', m.get('time_per_question', 30)),
                            'is_global_timer': m.get('isGlobalTimer', m.get('is_global_timer', False)),
                            'points_correct': m.get('pointsCorrect', m.get('points_correct', 100)),
                            'points_incorrect': m.get('pointsIncorrect', m.get('points_incorrect', -25)),
                            'bonus_streak': m.get('bonusStreak', m.get('bonus_streak', 50)),
                            'bonus_streak_threshold': m.get('bonusStreakThreshold', m.get('bonus_streak_threshold', 3)),
                            'bonus_perfect': m.get('bonusPerfect', m.get('bonus_perfect', 0)),
                            'bonus_speed': m.get('bonusSpeed', m.get('bonus_speed', 0)),
                            'total_time': m.get('totalTime', m.get('total_time', 60)),
                            'penalty_wrong': m.get('penaltyWrong', m.get('penalty_wrong', 50)),
                        }
                        mapped_modes[name] = mapped
                    GameMode._dynamic_configs = mapped_modes
                    print('[API] Modos de juego mapeados dinámicamente:', GameMode._dynamic_configs)
        except Exception as e:
            print('[API] No se pudo cargar modos de juego dinámicos:', e)
            GameMode._dynamic_configs = None

    @staticmethod
    def get_config(mode):
        """Obtiene la configuración según el modo de juego, priorizando la API si está disponible."""
        if GameMode._dynamic_configs is not None:
            # Buscar por nombre exacto o alias
            m = GameMode._dynamic_configs.get(mode)
            if not m:
                # Buscar por alias
                aliases = {
                    GameMode.CLASSIC: ['Clásico', 'Classic'],
                    GameMode.TIMEATTACK: ['Contrarreloj', 'TimeAttack'],
                    GameMode.DUEL: ['Duelo', 'Duel']
                }
                for key, names in aliases.items():
                    if mode in names and key in GameMode._dynamic_configs:
                        m = GameMode._dynamic_configs[key]
                        break
            if m:
                # Normalizar claves para compatibilidad
                return {
                    'num_questions': m.get('num_questions', 15),
                    'time_per_question': m.get('time_per_question', 30),
                    'is_global_timer': m.get('is_global_timer', False),
                    'points_correct': m.get('points_correct', 100),
                    'points_incorrect': m.get('points_incorrect', -25),
                    'bonus_streak': m.get('bonus_streak', 50),
                    'bonus_streak_threshold': m.get('bonus_streak_threshold', 3),
                    'bonus_perfect': m.get('bonus_perfect', 0),
                    'bonus_speed': m.get('bonus_speed', 0),
                    'total_time': m.get('total_time', 60)
                }
        # Fallback local
        configs = {
            GameMode.CLASSIC: {
                'num_questions': 15,
                'time_per_question': 30,
                'is_global_timer': False,
                'points_correct': 100,
                'points_incorrect': -25,
                'bonus_streak': 50,
                'bonus_streak_threshold': 3,
                'bonus_perfect': 200,
                'bonus_speed': 0
            },
            GameMode.TIMEATTACK: {
                'total_time': 60,
                'is_global_timer': True,
                'points_correct': 100,
                'points_incorrect': -25,
                'bonus_streak': 50,
                'bonus_streak_threshold': 3,
                'bonus_perfect': 0,
                'bonus_speed': 10
            },
            GameMode.DUEL: {
                'num_questions': 10,
                'time_per_question': 15,
                'is_global_timer': False,
                'points_correct': 100,
                'points_incorrect': -50,
                'bonus_streak': 50,
                'bonus_streak_threshold': 3,
                'bonus_perfect': 0,
                'bonus_speed': 0
            }
        }
        return configs.get(mode, configs[GameMode.CLASSIC])

    @staticmethod
    def get_mode_description(mode):
        config = GameMode.get_config(mode)
        print(f"[DEPURACIÓN] get_mode_description para {mode}: config = {config}")
        if mode == GameMode.CLASSIC:
            desc = f"{config.get('time_per_question', 30)} segundos por pregunta\n{config.get('num_questions', 15)} preguntas\n+{config.get('bonus_perfect', 200)} puntos por puntuación perfecta"
        elif mode == GameMode.TIMEATTACK:
            desc = f"{config.get('total_time', 60)} segundos totales\nPreguntas ilimitadas\n+{config.get('bonus_per_second', 10)} puntos por segundo restante"
        elif mode == GameMode.DUEL:
            desc = f"{config.get('time_per_question', 15)} segundos por pregunta\n{config.get('num_questions', 10)} preguntas (5 por jugador)\nPenalización -{config.get('penalty_wrong', 50)} puntos"
        else:
            desc = "Modo de juego"
        print(f"[DEPURACIÓN] Descripción generada para {mode}: {desc}")
        return desc

class Question:
    def __init__(self, category, question, answers, correct_answer, mode=None, difficulty='normal'):
        self.category = category
        self.question = question
        self.answers = answers.copy()  # Hacer una copia para no modificar la original
        # Si correct_answer es un índice numérico, convertirlo a la respuesta correcta
        if isinstance(correct_answer, int):
            self.correct_answer = self.answers[correct_answer]
        else:
            self.correct_answer = correct_answer
        self.mode = mode
        self.difficulty = difficulty
        self.used = False
        # Mezclar las opciones inicialmente
        self.mezclar_opciones()

    def mezclar_opciones(self):
        """Mezcla las opciones de respuesta manteniendo la respuesta correcta"""
        # Guardar la respuesta correcta
        correct = self.correct_answer
        # Mezclar las opciones
        random.shuffle(self.answers)
        # Asegurarse de que la respuesta correcta esté en la lista
        if correct not in self.answers:
            # Si la respuesta correcta no está en la lista, reemplazar una aleatoria
            self.answers[random.randint(0, len(self.answers)-1)] = correct
        # Actualizar la respuesta correcta
        self.correct_answer = correct
    
    def __eq__(self, other):
        if not isinstance(other, Question):
            return False
        return (self.question == other.question and 
                self.category == other.category and 
                self.mode == other.mode)
    
    def __hash__(self):
        return hash((self.question, self.category, self.mode))

class ContrarrelojMode:
    def __init__(self, parent, categoria, username):
        self.parent = parent
        self.categoria = categoria
        self.username = username
        self.tiempo_total = 60
        self.tiempo_restante = self.tiempo_total
        self.puntuacion = 0
        self.correctas = 0
        self.incorrectas = 0
        
        # Configurar estilo de la barra de progreso
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("blue.Horizontal.TProgressbar", 
                       troughcolor='#2c3e50',
                       background='#3498db',
                       thickness=10)
        style.configure("yellow.Horizontal.TProgressbar", 
                       troughcolor='#2c3e50',
                       background='#f1c40f',
                       thickness=10)
        style.configure("red.Horizontal.TProgressbar", 
                       troughcolor='#2c3e50',
                       background='#e74c3c',
                       thickness=10)
    
    def iniciar_juego(self):
        """Inicia el juego en modo contrareloj"""
        # Configuración inicial
        stats = {
            'username': self.username,
            'modo': GameMode.TIMEATTACK,
            'categoria': self.categoria,
            'correctas': 0,
            'incorrectas': 0,
            'tiempo_global': self.tiempo_total,
            'is_global_timer': True,
            'pregunta_actual': 1
        }
        
        # Obtener preguntas iniciales desde la API
        preguntas_disponibles = self.parent.obtener_preguntas_api(self.categoria, 'normal')
        if not preguntas_disponibles:
            messagebox.showerror("Error", "No hay suficientes preguntas disponibles para esta categoría")
            return
        
        # Seleccionar preguntas aleatorias iniciales
        preguntas = random.sample(preguntas_disponibles, min(5, len(preguntas_disponibles)))
        
        # Mostrar primera pregunta
        self.parent.mostrar_pregunta(preguntas, 0, stats)

class DesafioSaberApp:
    def __init__(self, root):
        self.root = root
        # Obtener título dinámicamente desde la API
        self.game_title = "DesafíoSaber"
        self.load_game_title()
        self.root.title(f"{self.game_title} - Juego de Conocimiento")
        
        # Configurar la ventana
        self.center_window()
        
        # Inicializar variables
        self.current_user = None
        self.current_duel = None
        self.usuarios_registrados = {}
        self.preguntas_todas = []
        self.sound_manager = SoundManager()
        self.achievement_manager = AchievementManager(self)
        
        # Definir los estilos de categorías
        self.category_styles = {
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
            }
        }
        
        # Cargar usuario actual si existe
        self.load_current_user()
        
        # Inicializar sincronización en la nube
        if REGISTRATION_AVAILABLE:
            try:
                from cloud_sync import CloudSync
                self.cloud_sync = CloudSync()
            except ImportError:
                self.cloud_sync = None
        else:
            self.cloud_sync = None
        
        # Inicializar cliente API
        try:
            self.api_client = APIClient()
        except:
            self.api_client = None
        
        # Cargar datos
        self.cargar_usuarios_registrados()
        self.cargar_todas_las_preguntas()
        
        # Configurar frame principal
        self.main_frame = tk.Frame(self.root, bg="#1a2a2e")
        self.main_frame.pack(expand=True, fill="both")
        
        # Inicializar WebSocket
        try:
            self.websocket_listener = WebSocketListener(self)
            self.websocket_listener.start()
        except Exception as e:
            print(f"Error iniciando WebSocket: {e}")
            self.websocket_listener = None
        
        # Mostrar pantalla de introducción
        self.show_intro_screen()
        
        GameMode.load_dynamic_configs()  # Precargar modos desde la API si es posible
        self.precarga_completa = False
        self.categorias_precargadas = None
        self.precargar_datos_background()
    
    def load_game_title(self):
        """Carga el título del juego desde archivo local para mayor velocidad"""
        try:
            # Cargar desde archivo local en lugar de API para mayor velocidad
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                if config and 'title' in config:
                    self.game_title = config['title']
                    # Actualizar el título de la ventana
                    self.root.title(f"{self.game_title} - Juego de Conocimiento")
                    print(f"Título del juego cargado: {self.game_title}")
                    return
        except Exception as e:
            print(f"Error cargando título del juego desde archivo local: {e}")
        
        # Fallback a API si no existe el archivo local
        try:
            if self.api_client:
                config = self.api_client.get_config()
                if config and 'title' in config:
                    self.game_title = config['title']
                    # Actualizar el título de la ventana
                    self.root.title(f"{self.game_title} - Juego de Conocimiento")
                    print(f"Título del juego cargado: {self.game_title}")
                    return
        except Exception as e:
            print(f"Error cargando título del juego desde API: {e}")
        
        # Usar título por defecto
        self.game_title = "DesafíoSaber"

    def load_current_user(self):
        """Carga el usuario actual desde el archivo de persistencia (optimizado)"""
        try:
            current_user_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'current_user.json')
            if os.path.exists(current_user_file):
                with open(current_user_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                    self.current_user = user_data.get('username')
                    print(f"Usuario cargado: {self.current_user}")
        except Exception as e:
            print(f"Error cargando usuario actual: {e}")
            self.current_user = None

    def save_current_user(self, username=None):
        """Guarda el usuario actual en el archivo de persistencia (optimizado)"""
        try:
            current_user_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'current_user.json')
            user_data = {
                'username': username or self.current_user,
                'timestamp': datetime.now().isoformat()
            }
            os.makedirs(os.path.dirname(current_user_file), exist_ok=True)
            with open(current_user_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando usuario actual: {e}")

    def clear_current_user(self):
        """Limpia el usuario actual del archivo de persistencia (optimizado)"""
        try:
            current_user_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'current_user.json')
            if os.path.exists(current_user_file):
                os.remove(current_user_file)
        except Exception as e:
            print(f"Error limpiando usuario actual: {e}")

    def save_current_duel(self, username1, username2, mode, category):
        """Guarda los datos del duelo actual"""
        try:
            duel_data = {
                'username1': username1,
                'username2': username2,
                'mode': mode,
                'category': category,
                'timestamp': datetime.now().isoformat()
            }
            os.makedirs('data', exist_ok=True)
            with open('data/current_duel.json', 'w', encoding='utf-8') as f:
                json.dump(duel_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando duelo actual: {e}")

    def clear_current_duel(self):
        """Limpia los datos del duelo actual"""
        try:
            if os.path.exists('data/current_duel.json'):
                os.remove('data/current_duel.json')
        except Exception as e:
            print(f"Error limpiando duelo actual: {e}")

    def sync_duel_results(self, stats):
        """Sincroniza los resultados del duelo con el backend para ambos jugadores"""
        try:
            # Sincronizar estadísticas del jugador 1
            if stats.get('username1'):
                self.actualizar_estadisticas_usuario(
                    stats['username1'], 
                    stats.get('puntos1', 0), 
                    stats.get('modo', 'Duelo'), 
                    {
                        'correctas': stats.get('correctas1', 0),
                        'incorrectas': stats.get('incorrectas1', 0),
                        'categoria': stats.get('categoria', '')
                    }
                )
            
            # Sincronizar estadísticas del jugador 2
            if stats.get('username2'):
                self.actualizar_estadisticas_usuario(
                    stats['username2'], 
                    stats.get('puntos2', 0), 
                    stats.get('modo', 'Duelo'), 
                    {
                        'correctas': stats.get('correctas2', 0),
                        'incorrectas': stats.get('incorrectas2', 0),
                        'categoria': stats.get('categoria', '')
                    }
                )
            
            print("Resultados del duelo sincronizados con el backend")
        except Exception as e:
            print(f"Error sincronizando resultados del duelo: {e}")

    # Definir los estilos de categorías con diseños mejorados
    category_styles = {
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
        }
    }
    
    def load_category_colors(self):
        """Carga los colores de categorías desde la API"""
        try:
            import requests
            response = requests.get('http://localhost:5000/api/category_colors')
            if response.status_code == 200:
                self.category_styles = response.json()
                print("✅ Colores de categorías cargados desde API")
        except Exception as e:
            print(f"Error cargando colores de categorías: {e}")
            # Fallback a colores por defecto
            self.category_styles = {}
    
    def load_button_styles(self):
        """Carga los estilos de botones desde la API"""
        try:
            import requests
            response = requests.get('http://localhost:5000/api/button-styles')
            if response.status_code == 200:
                self.button_styles = response.json()
                print("✅ Estilos de botones actualizados")
        except Exception as e:
            print(f"Error cargando estilos de botones: {e}")
            # Fallback a estilos por defecto
            self.button_styles = {}
    
    def apply_button_style(self, button, style_type="default"):
        """Aplica estilos de botón según la configuración cargada"""
        if not hasattr(self, 'button_styles') or not self.button_styles:
            return
        
        styles = self.button_styles
        
        # Configurar colores y propiedades
        button.configure(
            bg=styles.get('button_color', '#3498db'),
            fg=styles.get('button_text_color', 'white'),
            relief=styles.get('button_relief', 'flat'),
            borderwidth=styles.get('button_border_width', 0),
            font=(styles.get('button_font', 'Arial'), 
                  styles.get('button_font_size', 14), 
                  styles.get('button_font_weight', 'bold'))
        )
    
    def cargar_usuarios_registrados(self):
        """Carga la lista de usuarios registrados desde el ranking (optimizado)"""
        try:
            ranking_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ranking.json')
            with open(ranking_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Si el archivo es una lista, convertirlo a dict
                if isinstance(data, list):
                    data = {"rankings": data}
                    with open(ranking_file, 'w', encoding='utf-8') as fw:
                        json.dump(data, fw, ensure_ascii=False, indent=4)
                for ranking in data.get('rankings', []):
                    username = ranking.get('username')
                    if username and username != "Anónimo":
                        if username not in self.usuarios_registrados:
                            self.usuarios_registrados[username] = {
                                'mejor_puntuacion': ranking['score'],
                                'modo': ranking['mode']
                            }
                        elif ranking['score'] > self.usuarios_registrados[username]['mejor_puntuacion']:
                            self.usuarios_registrados[username]['mejor_puntuacion'] = ranking['score']
                            self.usuarios_registrados[username]['modo'] = ranking['mode']
        except FileNotFoundError:
            self.usuarios_registrados = {}
        except Exception as e:
            print(f"Error al cargar usuarios: {e}")
            self.usuarios_registrados = {}
    
    def show_registration(self):
        """Muestra el diálogo de registro"""
        if REGISTRATION_AVAILABLE:
            registration = UserRegistration(self.root, self.on_user_registered)
            registration.show_registration_dialog()
        else:
            messagebox.showinfo("Información", "El sistema de registro no está disponible.")
    
    def show_login(self):
        """Muestra el diálogo de inicio de sesión"""
        if REGISTRATION_AVAILABLE:
            login = UserLogin(self.root, self.on_user_logged_in)
            login.show_login_dialog()
        else:
            messagebox.showinfo("Información", "El sistema de inicio de sesión no está disponible.")
    
    def on_user_registered(self, username):
        """Callback cuando un usuario se registra (optimizado)"""
        self.current_user = username
        # Guardar usuario actual en persistencia
        self.save_current_user(username)
        messagebox.showinfo("Éxito", f"¡Bienvenido a DesafíoSaber, {username}!\n\nTu cuenta se ha creado correctamente.")
        
        # Recargar usuarios registrados (optimizado)
        self.cargar_usuarios_registrados()
        
        # Descargar datos del usuario desde el servidor (en background)
        if self.cloud_sync:
            threading.Thread(target=lambda: self.cloud_sync.download_user_data(username), daemon=True).start()
        
        # Actualizar la interfaz para mostrar el usuario actual
        self.setup_main_menu()
    
    def on_user_logged_in(self, username):
        """Callback cuando un usuario inicia sesión (optimizado)"""
        self.current_user = username
        # Guardar usuario actual en persistencia
        self.save_current_user(username)
        messagebox.showinfo("Éxito", f"¡Bienvenido de vuelta, {username}!\n\nHas iniciado sesión correctamente.")
        
        # Descargar datos del usuario desde el servidor (en background)
        if self.cloud_sync:
            threading.Thread(target=lambda: self.cloud_sync.download_user_data(username), daemon=True).start()
        
        # Actualizar la interfaz para mostrar el usuario actual
        self.setup_main_menu()
    
    def logout_user(self):
        """Cierra la sesión del usuario actual"""
        if self.current_user:
            username = self.current_user
            self.current_user = None
            # Limpiar usuario actual de persistencia
            self.clear_current_user()
            messagebox.showinfo("Sesión Cerrada", f"Has cerrado sesión como {username}.\n\nPuedes iniciar sesión nuevamente cuando quieras.")
            
            # Actualizar la interfaz
            self.setup_main_menu()
    
    def clear_main_frame(self):
        """Limpia el frame principal"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def obtener_preguntas_api(self, categoria=None, dificultad=None):
        """Obtiene las preguntas desde la memoria y las filtra por categoría y dificultad (filtrado estricto y robusto)"""
        import unicodedata
        def normalizar(texto):
            if not texto:
                return ''
            texto = texto.lower().strip()
            texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
            return texto.replace('í','i').replace('á','a').replace('é','e').replace('ó','o').replace('ú','u')
        try:
            if hasattr(self, 'preguntas_todas') and self.preguntas_todas:
                preguntas = self.preguntas_todas
            else:
                self.cargar_todas_las_preguntas()
                preguntas = self.preguntas_todas
            print(f'[DEPURACIÓN] obtener_preguntas_api - Categoría solicitada: {categoria}')
            print(f'[DEPURACIÓN] Total preguntas antes de filtrar: {len(preguntas)}')
            if categoria:
                preguntas_filtradas = []
                categoria_normalizada = normalizar(categoria)
                # Mapa de equivalencias válidas
                equivalencias = {
                    'ciencia': {'ciencia','ciencias'},
                    'historia': {'historia'},
                    'geografia': {'geografia','geografía'},
                    'arte': {'arte'},
                    'deportes': {'deportes'},
                    'entretenimiento': {'entretenimiento'}
                }
                categorias_validas = equivalencias.get(categoria_normalizada, {categoria_normalizada})
                categorias_validas = set(normalizar(c) for c in categorias_validas)
                categorias_encontradas = set()
                categorias_erroneas = set()
                for q in preguntas:
                    qcat = getattr(q, 'category', None)
                    qcat_norm = normalizar(qcat)
                    if qcat_norm in categorias_validas:
                        preguntas_filtradas.append(q)
                        categorias_encontradas.add(qcat_norm)
                    else:
                        categorias_erroneas.add(qcat_norm)
                preguntas = preguntas_filtradas
                print(f'[DEPURACIÓN] Preguntas después de filtrar por categoría "{categoria}": {len(preguntas)}')
                if categorias_erroneas:
                    print(f'[ADVERTENCIA] Se encontraron preguntas con categorías no reconocidas para "{categoria}": {categorias_erroneas}')
            if dificultad:
                preguntas = [q for q in preguntas if hasattr(q, 'difficulty') and q.difficulty and normalizar(q.difficulty) == normalizar(dificultad)]
                print(f'[DEPURACIÓN] Preguntas después de filtrar por dificultad "{dificultad}": {len(preguntas)}')
            return preguntas
        except Exception as e:
            print(f"Error filtrando preguntas en memoria: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def setup_main_menu(self):
        self.clear_main_frame()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        main_container = tk.Frame(self.main_frame)
        main_container.pack(expand=True, fill="both")
        canvas = tk.Canvas(main_container, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        try:
            bg_image = Image.open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'menu_background.png'))
            bg_image = bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        except Exception as e:
            print(f"Error al cargar imagen de fondo: {e}")
            canvas.configure(bg="#1a2a2e")
        # Header profesional
        header_frame = tk.Frame(main_container, bg="#2c3e50", height=70)
        header_frame.place(relx=0, rely=0, relwidth=1)
        header_frame.pack_propagate(False)

        # Frame para los iconos alineados a la derecha
        icons_frame = tk.Frame(header_frame, bg="#2c3e50")
        icons_frame.pack(side="right", padx=30, pady=10)

        # Función para tooltips
        def add_tooltip(widget, text):
            tooltip = tk.Toplevel(widget, bg="#222", padx=5, pady=2)
            tooltip.withdraw()
            tooltip.overrideredirect(True)
            label = tk.Label(tooltip, text=text, bg="#222", fg="white", font=("Arial", 9))
            label.pack()
            def enter(event):
                x = widget.winfo_rootx() + widget.winfo_width()//2
                y = widget.winfo_rooty() + widget.winfo_height() + 5
                tooltip.geometry(f"+{x}+{y}")
                tooltip.deiconify()
            def leave(event):
                tooltip.withdraw()
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

        # Icono Salir
        exit_btn = tk.Button(
            icons_frame,
            text="🚪",
            font=("Arial", 18, "bold"),
            bg="#34495e",
            fg="white",
            bd=0,
            cursor="hand2",
            command=self.root.quit,
            width=2, height=1
        )
        exit_btn.pack(side="right", padx=(8, 0))
        add_tooltip(exit_btn, "Salir del juego")

        # Icono Reportar error
        report_btn = tk.Button(
            icons_frame,
            text="🐞",
            font=("Arial", 18, "bold"),
            bg="#e74c3c",
            fg="white",
            bd=0,
            cursor="hand2",
            command=self.show_error_report_dialog,
            width=2, height=1
        )
        report_btn.pack(side="right", padx=(8, 0))
        add_tooltip(report_btn, "Reportar error")

        # Iconos de registro/login
        if REGISTRATION_AVAILABLE:
            # Icono registro
            register_btn = tk.Button(
                icons_frame,
                text="📝",
                font=("Arial", 18, "bold"),
                bg="#3498db",
                fg="white",
                bd=0,
                cursor="hand2",
                command=self.show_registration,
                width=2, height=1
            )
            register_btn.pack(side="right", padx=(8, 0))
            add_tooltip(register_btn, "Registrarse")

            # Icono login
            login_btn = tk.Button(
                icons_frame,
                text="👤",
                font=("Arial", 18, "bold"),
                bg="#e67e22",
                fg="white",
                bd=0,
                cursor="hand2",
                command=self.show_login,
                width=2, height=1
            )
            login_btn.pack(side="right", padx=(8, 0))
            add_tooltip(login_btn, "Iniciar sesión")

            # Si hay usuario logueado, mostrar icono usuario y cerrar sesión
            if self.current_user:
                # Mostrar nombre del usuario actual
                user_info_frame = tk.Frame(icons_frame, bg="#2c3e50")
                user_info_frame.pack(side="right", padx=(8, 0))
                
                user_label = tk.Label(
                    user_info_frame,
                    text=f"👤 {self.current_user}",
                    font=("Arial", 12, "bold"),
                    bg="#2c3e50",
                    fg="#2ecc71"
                )
                user_label.pack(side="left", padx=(0, 5))
                add_tooltip(user_label, f"Usuario actual: {self.current_user}")
                
                # Icono cerrar sesión
                logout_btn = tk.Button(
                    icons_frame,
                    text="🚪",
                    font=("Arial", 18, "bold"),
                    bg="#95a5a6",
                    fg="white",
                    bd=0,
                    cursor="hand2",
                    command=self.logout_user,
                    width=2, height=1
                )
                logout_btn.pack(side="right", padx=(8, 0))
                add_tooltip(logout_btn, "Cerrar sesión")

        # Título centrado
        nombre_juego = "¡DesafíoSaber!"
        # Sombra sutil para el texto
        for dx, dy in [(-2,2),(2,2),(-2,-2),(2,-2)]:
            tk.Label(
                header_frame,
                text=nombre_juego,
                font=("Arial Black", 28, "bold"),
                bg="#2c3e50",
                fg="#222222",
            ).place(relx=0.5, rely=0.5, anchor="center", x=dx, y=dy)
        tk.Label(
            header_frame,
            text=nombre_juego,
            font=("Arial Black", 28, "bold"),
            bg="#2c3e50",
            fg="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Botones del menú principal centrados
        buttons = [
            {"text": "🎮 JUGAR", "command": self.menu_jugar, "color": "#2ecc71", "y": 400},
            {"text": "🏆 LOGROS", "command": self.mostrar_logros, "color": "#f39c12", "y": 480},
            {"text": "📊 ESTADÍSTICAS", "command": self.mostrar_estadisticas, "color": "#9b59b6", "y": 560},
            {"text": "🏅 RANKING", "command": self.mostrar_ranking, "color": "#e74c3c", "y": 640}
        ]
        for btn_config in buttons:
            btn_container = tk.Frame(main_container)
            btn_container_window = canvas.create_window(
                screen_width//2,
                btn_config["y"],
                window=btn_container,
                anchor="center"
            )
            shadow_frame = tk.Frame(
                btn_container,
                bg="#1a2a2e",
                width=320,
                height=55
            )
            shadow_frame.place(x=3, y=3)
            btn = tk.Button(
                btn_container,
                text=btn_config["text"],
                command=btn_config["command"],
                font=("Arial", 18, "bold"),
                bg=btn_config["color"],
                fg="white",
                bd=0,
                cursor="hand2",
                relief="flat",
                width=20,
                height=1
            )
            btn.pack(padx=2, pady=2)
            
            # Aplicar estilos dinámicos
            self.apply_button_style(btn)
            
            # Mantener colores específicos del menú pero usar estilos dinámicos para hover
            def on_enter(e, button=btn, color=btn_config["color"]):
                hover_color = self.adjust_color(color, 0.8)
                button.configure(bg=hover_color, relief="raised")
            def on_leave(e, button=btn, color=btn_config["color"]):
                button.configure(bg=color, relief="flat")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Versión y créditos
        canvas.create_text(
            screen_width//2,
            screen_height - 20,
            text="v1.0.0 · Desarrollado con ❤️ por el equipo DesafíoSaber",
            font=("Arial", 10),
            fill="white"
        )
    
    def menu_jugar(self):
        # Forzar recarga de modos desde la API antes de mostrar el menú
        GameMode.load_dynamic_configs()
        # Mostrar loading si los datos no están listos
        if not self.precarga_completa or not hasattr(self, 'preguntas_todas') or not self.preguntas_todas or not hasattr(self, 'usuarios_registrados'):
            print('--- DEPURACIÓN ---')
            print('precarga_completa:', self.precarga_completa)
            print('preguntas_todas existe:', hasattr(self, 'preguntas_todas'))
            if hasattr(self, 'preguntas_todas'):
                print('preguntas_todas longitud:', len(self.preguntas_todas))
                print('Ejemplo pregunta:', self.preguntas_todas[0].__dict__ if self.preguntas_todas else 'VACÍO')
            print('usuarios_registrados existe:', hasattr(self, 'usuarios_registrados'))
            if hasattr(self, 'usuarios_registrados'):
                print('usuarios_registrados longitud:', len(self.usuarios_registrados))
                print('Ejemplo usuario:', list(self.usuarios_registrados.keys())[:3])
            print('-------------------')
            self.clear_main_frame()
            loading_label = tk.Label(self.main_frame, text="Cargando datos...", font=("Arial", 24), fg="#3498db", bg="#1a2a2e")
            loading_label.pack(expand=True)
            self.root.after(100, self.menu_jugar)  # Reintentar en 100ms (más rápido)
            return
        self.clear_main_frame()
        # Frame central
        center_frame = tk.Frame(self.main_frame, bg="#1a2a2e")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        # Título
        tk.Label(
            center_frame,
            text="Selecciona el Modo de Juego",
            font=("Arial", 36, "bold"),
            fg="#3498db",
            bg="#1a2a2e"
        ).pack(pady=(0, 50))
        # Frame para los modos de juego
        modes_frame = tk.Frame(center_frame, bg="#1a2a2e")
        modes_frame.pack(pady=20)
        # Configuración de los modos de juego
        modos = [
            ("Clásico", "🎮", GameMode.get_mode_description("Clásico"), "#2ecc71"),
            ("Contrarreloj", "⏱️", GameMode.get_mode_description("Contrarreloj"), "#3498db"),
            ("Duelo", "⚔️", GameMode.get_mode_description("Duelo"), "#e74c3c")
        ]
        # Log de depuración para mostrar los valores usados en el menú
        print("[DEPURACIÓN] Descripciones de modos en menú:")
        for name, _, desc, _ in modos:
            print(f"  {name}: {desc}")
        
        def show_user_dialog(modo, categoria):
            """Muestra un diálogo para ingresar el nombre de usuario"""
            # Validar modo duelo - solo para usuarios registrados
            if modo == GameMode.DUEL:
                if not self.usuarios_registrados:
                    messagebox.showwarning("⚠️ Modo Duelo", "El modo Duelo solo está disponible para usuarios registrados.\nPor favor, regístrate o inicia sesión para jugar.")
                    return
                self.show_duel_dialog(modo, categoria)
                return
            
            dialog = tk.Toplevel(self.root)
            dialog.title("Ingresa tu nombre")
            dialog.geometry("400x250")
            dialog.configure(bg="#1a2a2e")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Centrar la ventana
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            # Frame principal
            main_frame = tk.Frame(dialog, bg="#1a2a2e")
            main_frame.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Título
            tk.Label(
                main_frame,
                text="Ingresa tu nombre para comenzar",
                font=("Helvetica", 14, "bold"),
                bg="#1a2a2e",
                fg="white"
            ).pack(pady=(0, 20))
            
            # Frame para el combobox y entrada de texto
            input_frame = tk.Frame(main_frame, bg="#1a2a2e")
            input_frame.pack(fill="x", pady=(0, 20))
            
            # Variable para almacenar el nombre de usuario
            username_var = tk.StringVar()
            
            # Pre-seleccionar usuario actual si está logueado
            if self.current_user:
                username_var.set(self.current_user)
            
            # Crear Combobox con usuarios registrados
            usuarios = ["Selecciona un usuario existente"] + list(self.usuarios_registrados.keys())
            combo = ttk.Combobox(
                input_frame,
                values=usuarios,
                state="readonly",
                width=30
            )
            combo.pack(pady=(0, 10))
            
            # Pre-seleccionar usuario actual en el combobox si está logueado
            if self.current_user and self.current_user in usuarios:
                combo.set(self.current_user)
            else:
                combo.set("Selecciona un usuario existente")
            
            # Entrada de texto
            entry = tk.Entry(
                input_frame,
                font=("Helvetica", 12),
                bg="#2c3e50",
                fg="white",
                insertbackground="white",
                textvariable=username_var,
                width=30
            )
            entry.pack()
            
            def on_combo_select(event):
                selected = combo.get()
                if selected and selected != "Selecciona un usuario existente":
                    username_var.set(selected)
                    entry.focus_set()  # Dar foco al entry para permitir edición
            
            combo.bind('<<ComboboxSelected>>', on_combo_select)
            
            # Frame para botones
            button_frame = tk.Frame(main_frame, bg="#1a2a2e")
            button_frame.pack(fill="x", pady=(20, 0))
            
            def validate_and_start():
                username = username_var.get().strip()
                if not username:
                    messagebox.showwarning("Advertencia", "Por favor ingresa un nombre de usuario")
                    return
                dialog.destroy()
                self.iniciar_juego(username, modo, categoria)
            
            # Botón Comenzar
            start_button = tk.Button(
                button_frame,
                text="Comenzar",
                font=("Helvetica", 10),
                bg="#2ecc71",
                fg="white",
                relief="flat",
                command=validate_and_start,
                width=10,
                height=1
            )
            start_button.pack(side="left", expand=True, padx=3)
            
            # Botón Cancelar
            cancel_button = tk.Button(
                button_frame,
                text="Cancelar",
                font=("Helvetica", 10),
                bg="#e74c3c",
                fg="white",
                relief="flat",
                command=dialog.destroy,
                width=10,
                height=1
            )
            cancel_button.pack(side="left", expand=True, padx=3)
            
            # Dar foco inicial al entry
            entry.focus_set()
            
            # Configurar el diálogo para cerrarse con Escape
            dialog.bind('<Escape>', lambda e: dialog.destroy())
            # Configurar el entry para activar el botón Comenzar con Enter
            entry.bind('<Return>', lambda e: validate_and_start())
        
        for name, icon, desc, color in modos:
            # Frame para cada modo
            mode_frame = tk.Frame(modes_frame, bg="#2c3e50", padx=20, pady=20)
            mode_frame.pack(side="left", padx=10)
            
            # Icono y nombre
            tk.Label(
                mode_frame,
                text=icon,
                font=("Segoe UI Emoji", 48),
                fg=color,
                bg="#2c3e50"
            ).pack()
            
            tk.Label(
                mode_frame,
                text=name,
                font=("Arial", 18, "bold"),
                fg="white",
                bg="#2c3e50"
            ).pack()
            
            # Descripción
            tk.Label(
                mode_frame,
                text=desc,
                font=("Arial", 12),
                fg="#95a5a6",
                bg="#2c3e50",
                justify="center"
            ).pack(pady=10)
            
            # Frame para categorías
            categories_frame = tk.Frame(mode_frame, bg="#2c3e50")
            categories_frame.pack(fill="x", pady=(0, 10))
            
            # Label para categorías
            tk.Label(
                categories_frame,
                text="Categoría:",
                font=("Arial", 12, "bold"),
                fg="#3498db",
                bg="#2c3e50"
            ).pack(side="left", padx=(0, 5))
            
            # Lista de categorías disponibles desde la API
            categorias_disponibles = self.get_available_categories()
            
            # Combobox para categorías
            category_combo = ttk.Combobox(
                categories_frame,
                values=categorias_disponibles,
                state="readonly",
                width=15
            )
            category_combo.set(categorias_disponibles[0])  # Seleccionar primera categoría por defecto
            category_combo.pack()
            
            # Botón jugar
            btn = tk.Button(
                mode_frame,
                text="JUGAR",
                command=lambda m=name, c=category_combo: show_user_dialog(m, c.get()),
                font=("Arial", 14),
                bg=color,
                fg="white",
                bd=0,
                cursor="hand2",
                padx=20,
                pady=5
            )
            btn.pack(pady=10)
            
            # Efectos hover
            def on_enter(e, button=btn, hover_color=self.adjust_color(color, 0.8)):
                button.configure(bg=hover_color)
            
            def on_leave(e, button=btn, normal_color=color):
                button.configure(bg=normal_color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Botón volver
        volver_frame = tk.Frame(center_frame, bg="#1a2a2e")
        volver_frame.pack(pady=30)
        
        volver_btn = tk.Button(
            volver_frame,
            text="Volver al Menú Principal",
            command=self.setup_main_menu,
            font=("Arial", 14),
            bg="#95a5a6",
            fg="white",
            bd=0,
            cursor="hand2",
            padx=20,
            pady=10
        )
        volver_btn.pack()
        
        # Efectos hover para el botón volver
        def on_enter_volver(e):
            volver_btn.configure(bg=self.adjust_color("#95a5a6", 0.8))
        
        def on_leave_volver(e):
            volver_btn.configure(bg="#95a5a6")
        
        volver_btn.bind("<Enter>", on_enter_volver)
        volver_btn.bind("<Leave>", on_leave_volver)

    def iniciar_juego(self, username, modo, categoria):
        self.clear_main_frame()
        config = GameMode.get_config(modo)
        print(f"[DEPURACIÓN] Configuración usada para {modo}: {config}")
        def normalizar(texto):
            import unicodedata
            if not texto:
                return ''
            texto = texto.lower().strip()
            texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
            return texto.replace('í','i').replace('á','a').replace('é','e').replace('ó','o').replace('ú','u')
        cat_norm = normalizar(categoria)
        preguntas = []  # Inicializar para evitar UnboundLocalError
        if modo == GameMode.TIMEATTACK:
            tiempo_total = config.get('total_time', 60)
            stats = {
                'username': username,
                'modo': modo,
                'categoria': categoria,
                'correctas': 0,
                'incorrectas': 0,
                'tiempo_global': tiempo_total,
                'tiempo_restante': tiempo_total,
                'is_global_timer': True,
                'pregunta_actual': 1,
                'total_preguntas': 9999,  # Prácticamente ilimitadas
                'preguntas_usadas': set(),
                'preguntas_disponibles': []  # Pool de preguntas para el modo contrarreloj
            }
            preguntas_disponibles = self.obtener_preguntas_api(categoria)
            preguntas_disponibles = [q for q in preguntas_disponibles if normalizar(getattr(q, 'category', '')) == cat_norm]
            if not preguntas_disponibles:
                messagebox.showerror("Error", "No hay preguntas válidas para esta categoría. Corrige el banco de preguntas.")
                return
            stats['preguntas_disponibles'] = preguntas_disponibles
            preguntas = random.sample(preguntas_disponibles, min(5, len(preguntas_disponibles)))
            random.shuffle(preguntas)
            print(f"[DEPURACIÓN] Preguntas disponibles para {modo}: {len(preguntas_disponibles)}")
            print(f"[DEPURACIÓN] Preguntas iniciales seleccionadas: {len(preguntas)}")
            self.mostrar_pregunta(preguntas, 0, stats)
        else:
            preguntas = self.obtener_preguntas_api(categoria)
            preguntas = [q for q in preguntas if normalizar(getattr(q, 'category', '')) == cat_norm]
            num_preguntas = config.get('num_questions', 15)
            if not preguntas or len(preguntas) < num_preguntas:
                messagebox.showerror("Error", f"No hay suficientes preguntas válidas para esta categoría (se requieren {num_preguntas}). Corrige el banco de preguntas.")
                return
            preguntas = random.sample(preguntas, num_preguntas)
            random.shuffle(preguntas)
            preguntas_usadas = set()
            stats = {
                'username': username,
                'modo': modo,
                'categoria': categoria,
                'correctas': 0,
                'incorrectas': 0,
                'tiempo_pregunta': config.get('time_per_question', 30),
                'tiempo_restante': config.get('time_per_question', 30),
                'is_global_timer': False,
                'pregunta_actual': 1,
                'total_preguntas': num_preguntas,
                'preguntas_usadas': preguntas_usadas
            }
        if preguntas:
            print(f"[DEPURACIÓN] Número de preguntas seleccionadas: {len(preguntas)} (esperado: {config.get('num_questions', 15)})")
        print(f"[DEPURACIÓN] Tiempo por pregunta: {config.get('time_per_question', 30)}s")
        self.mostrar_pregunta(preguntas, 0, stats)

    def mostrar_pregunta(self, preguntas, indice, stats):
        """Muestra una pregunta"""
        # Para modo Contrarreloj, verificar si se acabó el tiempo
        if stats['modo'] == GameMode.TIMEATTACK and stats.get('tiempo_restante', 0) <= 0:
            try:
                print('[DEPURACIÓN] Tiempo agotado en Contrarreloj, mostrando resultados')
                self.mostrar_resultados(stats)
            except Exception as e:
                print(f'[ERROR] mostrar_resultados (Contrarreloj): {e}')
            return
        
        # Para otros modos, verificar si se acabaron las preguntas
        if stats['modo'] != GameMode.TIMEATTACK and (indice >= len(preguntas) or stats['pregunta_actual'] > stats['total_preguntas']):
            try:
                print('[DEPURACIÓN] Llamando a mostrar_resultados (Clásico)')
                self.mostrar_resultados(stats)
            except Exception as e:
                print(f'[ERROR] mostrar_resultados (Clásico): {e}')
            return
        
        # Para modo Contrarreloj, si se acabaron las preguntas actuales, tomar más del pool
        if stats['modo'] == GameMode.TIMEATTACK and indice >= len(preguntas):
            preguntas_disponibles = stats.get('preguntas_disponibles', [])
            preguntas_usadas = stats.get('preguntas_usadas', set())
            
            # Filtrar preguntas no usadas
            preguntas_no_usadas = [q for q in preguntas_disponibles if q not in preguntas_usadas]
            
            if not preguntas_no_usadas:
                # Si no hay más preguntas disponibles, mostrar resultados
                try:
                    print('[DEPURACIÓN] No hay más preguntas disponibles en Contrarreloj')
                    self.mostrar_resultados(stats)
                except Exception as e:
                    print(f'[ERROR] mostrar_resultados (Contrarreloj): {e}')
                return
            
            # Tomar más preguntas del pool
            nuevas_preguntas = random.sample(preguntas_no_usadas, min(5, len(preguntas_no_usadas)))
            random.shuffle(nuevas_preguntas)
            
            # Actualizar la lista de preguntas y reiniciar el índice
            preguntas.extend(nuevas_preguntas)
            indice = len(preguntas) - len(nuevas_preguntas)
            print(f'[DEPURACIÓN] Agregadas {len(nuevas_preguntas)} nuevas preguntas al pool de Contrarreloj')
        
        # Evitar repetir preguntas
        pregunta = preguntas[indice]
        if pregunta in stats['preguntas_usadas']:
            self.mostrar_pregunta(preguntas, indice + 1, stats)
            return
        stats['preguntas_usadas'].add(pregunta)
        
        # Limpiar ventana
        self.clear_main_frame()
        
        # Obtener pregunta actual
        pregunta = preguntas[indice]
        
        # Variables para el temporizador
        if stats['modo'] == GameMode.TIMEATTACK:
            tiempo_restante = [stats['tiempo_global']]
            tiempo_total = stats['tiempo_global']
        else:
            tiempo_restante = [stats['tiempo_pregunta']]
            tiempo_total = stats['tiempo_pregunta']
        timer_active = [True]
        warning_played = [False]
        
        # Obtener estilo de la categoría
        categoria = pregunta.category
        estilo = self.category_styles.get(categoria, {
            "bg_color": "#1a2a2e",
            "icon": "❓",
            "text_color": "white",
            "hover_color": "#2c3e50",
            "border_color": "#1a2a2e",
            "shadow_color": "#1a2a2e"
        })
        
        # Frame principal con color de categoría y borde
        main_container = tk.Frame(self.main_frame, bg=estilo["bg_color"])
        main_container.pack(expand=True, fill="both", padx=40, pady=30)
        
        # Agregar borde decorativo
        border_frame = tk.Frame(main_container, bg=estilo["border_color"], bd=2)
        border_frame.pack(expand=True, fill="both", padx=2, pady=2)
        
        # Frame interior con el contenido
        content_frame = tk.Frame(border_frame, bg=estilo["bg_color"])
        content_frame.pack(expand=True, fill="both")
        
        # Header con información
        header_frame = tk.Frame(content_frame, bg=estilo["bg_color"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Info del juego
        info_frame = tk.Frame(header_frame, bg=estilo["bg_color"], height=50)
        info_frame.pack(fill="x", padx=20, pady=10)
        info_frame.pack_propagate(False)
        
        # Frame para el botón volver y la categoría (izquierda)
        left_frame = tk.Frame(info_frame, bg=estilo["bg_color"])
        left_frame.pack(side="left", fill="y")
        
        # Botón volver al menú con estilo mejorado
        def confirmar_salir():
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres volver al menú principal?\nPerderás el progreso actual."):
                timer_active[0] = False
                self.setup_main_menu()
        
        back_btn = tk.Button(
            left_frame,
            text="🏠",
            command=confirmar_salir,
            font=("Arial", 20),
            bg=estilo["bg_color"],
            fg=estilo["text_color"],
            bd=0,
            cursor="hand2",
            relief="flat",
            padx=10
        )
        back_btn.pack(side="left", padx=(0, 10))
        
        # Efectos hover para el botón volver
        def on_enter(e):
            back_btn.configure(bg=estilo["hover_color"])
        
        def on_leave(e):
            back_btn.configure(bg=estilo["bg_color"])
        
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        
        # Título de la categoría con ícono y estilo mejorado
        category_label = tk.Label(
            left_frame,
            text=f"{estilo['icon']} {categoria}",
            font=("Arial", 24, "bold"),
            fg=estilo["text_color"],
            bg=estilo["bg_color"]
        )
        category_label.pack(side="left")
        
        # Información central (puntuación o número de pregunta)
        info_center = tk.Frame(info_frame, bg=estilo["bg_color"])
        info_center.pack(side="left", expand=True)
        
        if stats['modo'] == GameMode.TIMEATTACK:
            # En modo contrareloj mostrar puntuación y preguntas respondidas
            total_respondidas = stats['correctas'] + stats['incorrectas']
            info_text = f"Puntuación: {stats['correctas'] * 100} | Respondidas: {total_respondidas}"
        else:
            # En modo clásico mostrar número de pregunta actual
            info_text = f"Pregunta {stats['pregunta_actual']}/{stats['total_preguntas']}"
        
        tk.Label(
            info_center,
            text=info_text,
            font=("Arial", 18, "bold"),
            fg=estilo["text_color"],
            bg=estilo["bg_color"]
        ).pack()
        
        # Frame para temporizador y barra de progreso
        timer_container = tk.Frame(info_frame, bg=estilo["bg_color"])
        timer_container.pack(side="right", fill="y")
        
        # Temporizador
        timer_label = tk.Label(
            timer_container,
            text=f"⏱️ {int(tiempo_restante[0])}s",
            font=("Arial", 20, "bold"),
            fg=estilo["text_color"],
            bg=estilo["bg_color"]
        )
        timer_label.pack()
        
        # Barra de progreso del tiempo
        progress_frame = tk.Frame(timer_container, bg="#2c3e50", width=200, height=10)
        progress_frame.pack(fill="x", pady=5)
        progress_frame.pack_propagate(False)
        
        progress_bar = tk.Frame(progress_frame, bg="#3498db", width=200, height=10)
        progress_bar.place(relx=0, rely=0, relwidth=1)
        
        def update_timer():
            if not timer_active[0]:
                return
                
            if tiempo_restante[0] > 0:
                tiempo_restante[0] -= 1
                try:
                    timer_label.config(text=f"⏱️ {int(tiempo_restante[0])}s")
                    progress_width = tiempo_restante[0]/tiempo_total
                    progress_bar.place(relwidth=max(0, min(1, progress_width)))
                    
                    # Actualizar tiempo global en modo contrareloj
                    if stats['modo'] == GameMode.TIMEATTACK:
                        stats['tiempo_global'] = tiempo_restante[0]
                    
                    if tiempo_restante[0] > 0:
                        self.main_frame.after(1000, update_timer)
                    else:
                        # Tiempo agotado
                        timer_active[0] = False
                        # Mostrar la respuesta correcta en verde
                        for btn in answer_buttons:
                            btn.configure(state="disabled")
                            if btn.cget("text") == pregunta.correct_answer:
                                btn.configure(bg="#32CD32")  # Verde más vivo
                        
                        if stats['modo'] == GameMode.TIMEATTACK:
                            # En contrareloj, mostrar resultados cuando se acaba el tiempo
                            self.main_frame.after(1500, lambda: self.mostrar_resultados(stats))
                        else:
                            # En modo clásico, registrar como incorrecta y continuar
                            stats['incorrectas'] += 1
                            stats['pregunta_actual'] += 1
                            self.main_frame.after(300, lambda: self.mostrar_pregunta(preguntas, indice + 1, stats))
                except Exception as e:
                    print(f"Error en el temporizador: {e}")
                    timer_active[0] = False
        
        # Frame para la pregunta
        question_frame = tk.Frame(content_frame, bg=estilo["bg_color"])
        question_frame.pack(fill="x", pady=20)
        
        # Mostrar pregunta
        tk.Label(
            question_frame,
            text=pregunta.question,
            font=("Arial", 16),
            wraplength=600,
            justify="center",
            fg=estilo["text_color"],
            bg=estilo["bg_color"]
        ).pack(pady=10)
        
        # Frame para las opciones
        options_frame = tk.Frame(content_frame, bg=estilo["bg_color"])
        options_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Mezclar opciones
        opciones = pregunta.answers.copy()
        random.shuffle(opciones)
        
        # Lista para almacenar los botones
        answer_buttons = []
        
        # Crear botones de opciones
        for i, opcion in enumerate(opciones):
            # Frame contenedor para cada opción
            btn_container = tk.Frame(options_frame, bg=estilo["bg_color"])
            btn_container.pack(fill="x", pady=5)
            
            # Botón de opción con estilo mejorado
            btn = tk.Button(
                btn_container,
                text=opcion,
                font=("Arial", 14),
                wraplength=600,
                fg="#1a2a2e",
                bg="white",    # Fondo blanco
                bd=0,
                cursor="hand2",
                relief="flat",
                padx=20,
                pady=10,
            )
            answer_buttons.append(btn)
            
            # Restaurar animación de aparición con sonido
            def show_button(button, delay):
                def _show():
                    button.pack(fill="x")
                    if delay == 0:  # Solo reproducir sonido para el primer botón
                        self.sound_manager.play_sound('despliegue', 0.5)
                self.main_frame.after(delay, _show)
            
            # Mostrar botones secuencialmente
            show_button(btn, i * 200)  # 200ms de retraso entre cada botón
            
            # Efectos hover mejorados
            def on_enter(e, button=btn):
                if button['state'] != 'disabled':
                    button.configure(
                        bg="#f0f0f0",  # Gris muy claro al hover
                        relief="raised"  # Efecto de elevación
                    )
                    
            def on_leave(e, button=btn):
                if button['state'] != 'disabled':
                    button.configure(
                        bg="white",     # Volver a blanco
                        relief="flat"   # Quitar elevación
                    )
                    
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            
            btn.configure(command=lambda r=opcion: check_answer(r))
        
        def check_answer(respuesta):
            if not timer_active[0]:
                return
            timer_active[0] = False
            selected_btn = None
            correct_btn = None
            for btn in answer_buttons:
                if btn.cget("text") == respuesta:
                    selected_btn = btn
                if btn.cget("text") == pregunta.correct_answer:
                    correct_btn = btn

            # Feedback visual y sonoro inmediato
            bonificacion = False
            bonificacion_speed = False
            if respuesta == pregunta.correct_answer:
                if correct_btn:
                    correct_btn.configure(bg="#32CD32")
                stats['correctas'] += 1
                bonus = GameMode.get_config(stats['modo']).get('points_correct', 100)
                # Bonificación por racha
                stats['racha'] = stats.get('racha', 0) + 1
                if stats['racha'] >= GameMode.get_config(stats['modo']).get('bonus_streak_threshold', 3):
                    bonus += GameMode.get_config(stats['modo']).get('bonus_streak', 50)
                    bonificacion = True
                # Bonificación por velocidad (solo en modo contrarreloj)
                if stats['modo'] == GameMode.TIMEATTACK and GameMode.get_config(stats['modo']).get('bonus_speed', 0) > 0:
                    tiempo_restante = stats.get('tiempo_restante', 0)
                    if tiempo_restante > 0:
                        speed_bonus = GameMode.get_config(stats['modo']).get('bonus_speed', 0) * tiempo_restante
                        bonus += speed_bonus
                        bonificacion_speed = True
                stats['puntuacion'] = stats.get('puntuacion', 0) + bonus
                self.sound_manager.play_sound('acierto', 0.8)
            else:
                if selected_btn:
                    selected_btn.configure(bg="#FF4C4C")
                if correct_btn:
                    correct_btn.configure(bg="#32CD32")
                stats['incorrectas'] += 1
                stats['racha'] = 0
                # Aplicar descuento por respuesta incorrecta SIEMPRE, incluso si la puntuación es 0
                descuento = GameMode.get_config(stats['modo']).get('points_incorrect', -25)
                stats['puntuacion'] = max(0, stats.get('puntuacion', 0) + descuento)
                print(f'[DEPURACIÓN] Descuento aplicado por error: {descuento}, nueva puntuación: {stats["puntuacion"]}')
                self.sound_manager.play_sound('errado', 0.8)

            # Deshabilitar todos los botones
            for btn in answer_buttons:
                btn.configure(state="disabled")

            stats['pregunta_actual'] += 1

            # Mostrar bonificaciones (solo visual, no lógica pesada)
            if bonificacion:
                self.mostrar_bonificacion(f"¡Bonificación por racha! +{GameMode.get_config(stats['modo']).get('bonus_streak', 50)} puntos ✨")
            if bonificacion_speed:
                self.mostrar_bonificacion(f"¡Bonificación por velocidad! +{GameMode.get_config(stats['modo']).get('bonus_speed', 0) * stats.get('tiempo_restante', 0)} puntos ⚡")

            # Transición fluida: solo feedback visual, luego cambio de pregunta
            def next_question():
                try:
                    self.mostrar_pregunta(preguntas, indice + 1, stats)
                except Exception as e:
                    print(f"Error al mostrar la siguiente pregunta: {e}")
            self.main_frame.after(500, next_question)
        
        # Iniciar temporizador
        update_timer()

    def mostrar_resultados(self, stats):
        try:
            print('[DEPURACIÓN] Entrando a mostrar_resultados')
            print(f'[DEPURACIÓN] stats recibido: {stats}')
            
            # Validar que stats no sea None
            if not stats:
                print('[ERROR] stats es None o vacío')
                stats = {}
            
            self.clear_main_frame()
            
            # Intentar guardar en historial solo si stats es válido
            try:
                self.guardar_en_historial(stats)
            except Exception as e:
                print(f'[ERROR] No se pudo guardar en historial: {e}')
            
            # Frame principal para resultados
            results_frame = tk.Frame(self.main_frame, bg="#1a2a2e")
            results_frame.pack(expand=True, fill="both", padx=40, pady=30)
            
            tk.Label(
                results_frame,
                text="🏆 Resultados Finales",
                font=("Arial", 36, "bold"),
                fg="#3498db",
                bg="#1a2a2e"
            ).pack(pady=(0, 40))
            
            stats_frame = tk.Frame(results_frame, bg="#2c3e50")
            stats_frame.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Extraer y validar datos de stats con valores por defecto seguros
            username = str(stats.get('username', 'Anónimo')).strip() or 'Anónimo'
            modo = str(stats.get('modo', 'Clásico')).strip() or 'Clásico'
            categoria = str(stats.get('categoria', 'General')).strip() or 'General'
            
            # Convertir valores numéricos de forma segura
            try:
                correctas = int(stats.get('correctas', 0)) if stats.get('correctas') is not None else 0
            except (ValueError, TypeError):
                correctas = 0
                
            try:
                incorrectas = int(stats.get('incorrectas', 0)) if stats.get('incorrectas') is not None else 0
            except (ValueError, TypeError):
                incorrectas = 0
                
            try:
                puntuacion = int(stats.get('puntuacion', 0)) if stats.get('puntuacion') is not None else 0
            except (ValueError, TypeError):
                puntuacion = 0
            
            print(f'[DEPURACIÓN] Datos procesados - Usuario: {username}, Modo: {modo}, Categoría: {categoria}')
            print(f'[DEPURACIÓN] Datos procesados - Correctas: {correctas}, Incorrectas: {incorrectas}, Puntuación: {puntuacion}')
            tk.Label(
                stats_frame,
                text=f"👤 Jugador: {username}",
                font=("Arial", 24, "bold"),
                fg="white",
                bg="#2c3e50"
            ).pack(pady=(20, 10))
            
            tk.Label(
                stats_frame,
                text=f"🎮 Modo: {modo}",
                font=("Arial", 20),
                fg="white",
                bg="#2c3e50"
            ).pack(pady=10)
            
            tk.Label(
                stats_frame,
                text=f"📚 Categoría: {categoria}",
                font=("Arial", 20),
                fg="white",
                bg="#2c3e50"
            ).pack(pady=10)
            
            # Obtener configuración del modo de forma segura
            try:
                config = GameMode.get_config(modo if modo and modo != '-' else GameMode.CLASSIC)
                print(f'[DEPURACIÓN] Configuración obtenida para modo "{modo}": {config}')
            except Exception as e:
                print(f'[ERROR] Error obteniendo configuración: {e}')
                config = GameMode.get_config(GameMode.CLASSIC)
            
            # Calcular bonificación perfecta de forma segura
            bonus_perfect = 0
            try:
                bonus_perfect = int(config.get('bonus_perfect', 0)) if config.get('bonus_perfect') is not None else 0
            except (ValueError, TypeError):
                bonus_perfect = 0
            
            # Aplicar bonificación perfecta solo en modo clásico
            if modo == GameMode.CLASSIC:
                try:
                    total_preguntas = int(config.get('num_questions', 15)) if config.get('num_questions') is not None else 15
                    if correctas == total_preguntas and bonus_perfect > 0:
                        puntuacion += bonus_perfect
                        stats['bonus_perfect'] = bonus_perfect
                        print(f'[DEPURACIÓN] Bonificación perfecta aplicada: +{bonus_perfect} puntos')
                        self.mostrar_bonificacion(f"¡Puntuación perfecta! +{bonus_perfect} puntos ⭐")
                except Exception as e:
                    print(f'[ERROR] Error calculando bonificación perfecta: {e}')
            if modo == GameMode.TIMEATTACK:
                tk.Label(
                    stats_frame,
                    text=f"✨ Puntuación Final: {puntuacion}",
                    font=("Arial", 28, "bold"),
                    fg="#f1c40f",
                    bg="#2c3e50"
                ).pack(pady=20)
                tk.Label(
                    stats_frame,
                    text=f"✅ Respuestas Correctas: {correctas}",
                    font=("Arial", 20),
                    fg="#2ecc71",
                    bg="#2c3e50"
                ).pack(pady=5)
                tk.Label(
                    stats_frame,
                    text=f"❌ Respuestas Incorrectas: {incorrectas}",
                    font=("Arial", 20),
                    fg="#e74c3c",
                    bg="#2c3e50"
                ).pack(pady=5)
                total_respuestas = correctas + incorrectas
                if total_respuestas > 0:
                    precision = (correctas / total_respuestas) * 100
                else:
                    precision = 0
                tk.Label(
                    stats_frame,
                    text=f"🎯 Precisión: {precision:.1f}%",
                    font=("Arial", 20),
                    fg="#3498db",
                    bg="#2c3e50"
                ).pack(pady=5)
            else:
                total_preguntas = config.get('num_questions', 15)
                tk.Label(
                    stats_frame,
                    text=f"✨ Puntuación Final: {puntuacion}",
                    font=("Arial", 28, "bold"),
                    fg="#f1c40f",
                    bg="#2c3e50"
                ).pack(pady=20)
                tk.Label(
                    stats_frame,
                    text=f"✅ Respuestas Correctas: {correctas} de {total_preguntas}",
                    font=("Arial", 20),
                    fg="#2ecc71",
                    bg="#2c3e50"
                ).pack(pady=5)
                tk.Label(
                    stats_frame,
                    text=f"❌ Respuestas Incorrectas: {incorrectas}",
                    font=("Arial", 20),
                    fg="#e74c3c",
                    bg="#2c3e50"
                ).pack(pady=5)
                if total_preguntas > 0:
                    precision = (correctas / total_preguntas) * 100
                else:
                    precision = 0
                tk.Label(
                    stats_frame,
                    text=f"🎯 Precisión: {precision:.1f}%",
                    font=("Arial", 20),
                    fg="#3498db",
                    bg="#2c3e50"
                ).pack(pady=5)
            if stats.get('bonus_perfect'):
                tk.Label(
                    stats_frame,
                    text=f"⭐ Bonificación perfecta: +{stats.get('bonus_perfect', 0)} puntos",
                    font=("Arial", 16, "bold"),
                    fg="#f1c40f",
                    bg="#2c3e50"
                ).pack(pady=5)
            # Verificar logros solo si hay usuario logueado y es el mismo
            try:
                if self.current_user and username == self.current_user:
                    self.achievement_manager.check_achievements(stats)
            except Exception as e:
                print(f'[ERROR] Error verificando logros: {e}')
            
            # Guardar puntuación de forma segura
            try:
                self.guardar_puntuacion(puntuacion, modo, username, stats)
                print(f'[DEPURACIÓN] Puntuación guardada: {puntuacion} puntos para {username}')
            except Exception as e:
                print(f'[ERROR] Error guardando puntuación: {e}')
            
            # Botones de acción
            buttons_frame = tk.Frame(results_frame, bg="#1a2a2e")
            buttons_frame.pack(pady=30)
            
            tk.Button(
                buttons_frame,
                text="🔄 Jugar Otra Vez",
                font=("Arial", 14, "bold"),
                bg="#3498db",
                fg="white",
                relief="flat",
                command=lambda: self.iniciar_juego(username, modo, categoria)
            ).pack(side="left", padx=10)
            
            tk.Button(
                buttons_frame,
                text="🎮 Jugar Otro Modo",
                font=("Arial", 14, "bold"),
                bg="#e67e22",
                fg="white",
                relief="flat",
                command=self.menu_jugar
            ).pack(side="left", padx=10)
            
            tk.Button(
                buttons_frame,
                text="🏠 Volver al Menú",
                font=("Arial", 14, "bold"),
                bg="#95a5a6",
                fg="white",
                relief="flat",
                command=self.setup_main_menu
            ).pack(side="left", padx=10)
            
            print('[DEPURACIÓN] mostrar_resultados completado exitosamente')
            
        except Exception as e:
            print(f'[ERROR] mostrar_resultados: {e}')
            print(f'[ERROR] stats recibido: {stats}')
            import traceback
            traceback.print_exc()
            
            # Mostrar error en la interfaz de forma amigable
            self.clear_main_frame()
            error_frame = tk.Frame(self.main_frame, bg="#1a2a2e")
            error_frame.pack(expand=True, fill="both", padx=40, pady=30)
            
            tk.Label(
                error_frame,
                text="❌ Error al mostrar resultados",
                font=("Arial", 24, "bold"),
                fg="#e74c3c",
                bg="#1a2a2e"
            ).pack(pady=(0, 20))
            
            tk.Label(
                error_frame,
                text="Ha ocurrido un error al procesar los resultados.",
                font=("Arial", 16),
                fg="white",
                bg="#1a2a2e"
            ).pack(pady=(0, 10))
            
            tk.Label(
                error_frame,
                text="Detalles técnicos:",
                font=("Arial", 14, "bold"),
                fg="#f39c12",
                bg="#1a2a2e"
            ).pack(pady=(20, 5))
            
            tk.Label(
                error_frame,
                text=str(e),
                font=("Arial", 12),
                fg="#95a5a6",
                bg="#1a2a2e",
                wraplength=600
            ).pack(pady=(0, 30))
            
            # Botón para volver al menú
            tk.Button(
                error_frame,
                text="🏠 Volver al Menú Principal",
                font=("Arial", 14, "bold"),
                bg="#3498db",
                fg="white",
                relief="flat",
                command=self.setup_main_menu
            ).pack()

    def guardar_puntuacion(self, puntuacion, modo, username="Anónimo", stats=None):
        """Guarda la puntuación en el archivo de ranking y en la API"""
        try:
            # Guardar localmente
            try:
                with open('data/ranking.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Si el archivo es una lista antigua, convertir a dict
                if isinstance(data, list):
                    ranking_data = data
                    data = {"rankings": ranking_data}
                else:
                    ranking_data = data.get("rankings", [])
            except FileNotFoundError:
                data = {"rankings": []}
                ranking_data = data["rankings"]
            
            # Crear nueva entrada con datos completos
            nueva_puntuacion = {
                "id": len(ranking_data) + 1,
                "username": username,
                "score": puntuacion,
                "mode": modo,
                "categoria": stats.get('categoria', 'General') if stats else 'General',
                "correctas": stats.get('correctas', 0) if stats else 0,
                "incorrectas": stats.get('incorrectas', 0) if stats else 0,
                "tiempo": stats.get('tiempo_total', 0) if stats else 0,
                "fecha": datetime.now().isoformat()
            }
            
            data["rankings"].append(nueva_puntuacion)
            
            # Ordenar por puntuación descendente
            data["rankings"].sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Guardar archivo local
            with open('data/ranking.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Guardar en API y actualizar estadísticas del usuario
            def save_to_api():
                try:
                    # Guardar puntuación en ranking
                    self.api_client.save_score(nueva_puntuacion)
                    
                    # Actualizar estadísticas del usuario
                    if username != "Anónimo":
                        self.actualizar_estadisticas_usuario(username, puntuacion, modo, stats)
                        
                except Exception as e:
                    print(f"Error guardando en API: {e}")
            
            threading.Thread(target=save_to_api, daemon=True).start()
            
        except Exception as e:
            print(f"Error guardando puntuación: {e}")
            messagebox.showerror("Error", "No se pudo guardar la puntuación")

    def mostrar_ranking(self):
        """Muestra el ranking de jugadores (reforzado con logs y manejo de errores visual)"""
        import threading
        self.clear_main_frame()
        loading_label = tk.Label(self.main_frame, text="Cargando ranking...", font=("Arial", 24), fg="#3498db", bg="#1a2a2e")
        loading_label.pack(expand=True)

        def cargar_y_mostrar():
            import os
            import json
            from datetime import datetime
            try:
                with open(os.path.join("data", "ranking.json"), "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and 'rankings' in data:
                    ranking_data = data['rankings']
                elif isinstance(data, list):
                    ranking_data = data
                else:
                    ranking_data = []
                if not isinstance(ranking_data, list):
                    ranking_data = []
                ranking_data = [r for r in ranking_data if isinstance(r, dict)]
                # --- NUEVO: incluir todos los usuarios registrados aunque no tengan partidas ---
                try:
                    with open(os.path.join("data", "usuarios.json"), "r", encoding="utf-8") as f_users:
                        users_data = json.load(f_users)
                    if isinstance(users_data, dict):
                        all_users = list(users_data.values())
                    elif isinstance(users_data, list):
                        all_users = users_data
                    else:
                        all_users = []
                except Exception as e:
                    print(f"Error cargando usuarios para ranking completo: {e}")
                    all_users = []
                usernames_in_ranking = set(r.get("username") for r in ranking_data if r.get("username"))
                for user in all_users:
                    uname = user.get("username")
                    if uname and uname not in usernames_in_ranking and uname.lower() != "admin":
                        ranking_data.append({
                            "username": uname,
                            "score": 0,
                            "mode": "-",
                            "categoria": "-",
                            "correctas": 0,
                            "incorrectas": 0,
                            "tiempo": 0,
                            "fecha": "-"
                        })
                print(f"[DEBUG] Ranking cargado: {len(ranking_data)} registros (incluyendo usuarios sin partidas)")
                if not ranking_data:
                    print("[DEBUG] Ranking vacío tras filtrado")
            except Exception as e:
                print(f"Error cargando ranking: {e}")
                ranking_data = []
                error_msg = str(e)
                self.main_frame.after(0, lambda: self._mostrar_ranking_ui([], error_msg))
                return
            self.main_frame.after(0, lambda: self._mostrar_ranking_ui(ranking_data, None))
        threading.Thread(target=cargar_y_mostrar, daemon=True).start()

    def _mostrar_ranking_ui(self, ranking_data, error_msg=None):
        import tkinter as tk
        from tkinter import ttk
        from datetime import datetime
        self.clear_main_frame()
        main_container = tk.Frame(self.main_frame, bg="#1a2a2e")
        main_container.pack(expand=True, fill="both", padx=20, pady=20)
        header_frame = tk.Frame(main_container, bg="#2c3e50", height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            title_frame,
            text="🏆",
            font=("Segoe UI Emoji", 36),
            fg="#f1c40f",
            bg="#2c3e50"
        ).pack(side="left", padx=(0, 10))
        tk.Label(
            title_frame,
            text="Ranking Global",
            font=("Helvetica", 32, "bold"),
            fg="#f1c40f",
            bg="#2c3e50"
        ).pack(side="left")
        volver_btn = tk.Button(
            header_frame,
            text="🏠",
            font=("Segoe UI Emoji", 32, "bold"),
            bg="#2c3e50",
            fg="white",
            bd=0,
            cursor="hand2",
            padx=18,
            pady=8,
            relief="flat",
            command=self.setup_main_menu,
            activebackground="#34495e",
            activeforeground="white",
            highlightthickness=0
        )
        volver_btn.place(relx=0.01, rely=0.5, anchor="w", width=64, height=64)
        volver_btn.configure(borderwidth=0, highlightbackground="#2c3e50", highlightcolor="#2c3e50")
        volver_btn.update()
        volver_btn.after(100, lambda: volver_btn.config(width=2, height=2))
        volver_btn.bind("<Enter>", lambda e: volver_btn.config(bg="#34495e"))
        volver_btn.bind("<Leave>", lambda e: volver_btn.config(bg="#2c3e50"))
        volver_btn.configure(overrelief="flat")

        # --- FILTROS ---
        filtros_frame = tk.Frame(main_container, bg="#2c3e50")
        filtros_frame.pack(fill="x", pady=(0, 10))
        modo_var = tk.StringVar(value="Todos")
        categoria_var = tk.StringVar(value="Todas")
        modos = ["Todos", "Clásico", "Contrarreloj", "Duelo"]
        categorias = ["Todas"] + sorted(list({r.get("categoria", "-") for r in ranking_data if r.get("categoria")}))
        def actualizar_tabla():
            modo = modo_var.get()
            categoria = categoria_var.get()
            filtrados = ranking_data
            if modo != "Todos":
                filtrados = [r for r in filtrados if r.get("mode", "").lower() == modo.lower()]
            if categoria != "Todas":
                filtrados = [r for r in filtrados if r.get("categoria", "").lower() == categoria.lower()]
            mostrar_tabla(filtrados)
        for m in modos:
            btn = tk.Radiobutton(
                filtros_frame, text=f"  {m}", variable=modo_var, value=m,
                font=("Arial", 12, "bold"), indicatoron=0,
                bg="#3498db" if m=="Todos" else "#2c3e50",
                fg="white", selectcolor="#3498db",
                width=12, padx=8, pady=6,
                relief="flat", borderwidth=0,
                command=actualizar_tabla
            )
            btn.pack(side="left", padx=6, pady=8)
        tk.Label(filtros_frame, text="", bg="#2c3e50", width=2).pack(side="left")
        tk.Label(filtros_frame, text="Categoría:", font=("Arial", 12, "bold"), fg="#f1c40f", bg="#2c3e50").pack(side="left")
        cat_combo = ttk.Combobox(filtros_frame, values=categorias, state="readonly", textvariable=categoria_var, width=16)
        cat_combo.pack(side="left", padx=8)
        cat_combo.bind('<<ComboboxSelected>>', lambda e: actualizar_tabla())
        # --- FIN FILTROS ---

        table_container = tk.Frame(main_container, bg="#2c3e50")
        table_container.pack(expand=True, fill="both", padx=20, pady=20)
        canvas = tk.Canvas(table_container, bg="#2c3e50", highlightthickness=0)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2c3e50")
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(frame_id, width=canvas.winfo_width())
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width() if canvas.winfo_width() > 0 else 800
        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas_width)
        headers = [
            ("#", 5, "center"),
            ("Jugador", 16, "w"),
            ("Puntaje", 10, "center"),
            ("Correctas", 10, "center"),
            ("Incorrectas", 12, "center"),
            ("Modo", 12, "center"),
            ("Categoría", 14, "center"),
            ("Tiempo", 8, "center"),
            ("Fecha", 18, "center")
        ]
        def mostrar_tabla(data):
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            for i, (header, width, anchor) in enumerate(headers):
                lbl = tk.Label(
                    scrollable_frame,
                    text=header,
                    font=("Arial", 12, "bold"),
                    fg="#f1c40f",
                    bg="#1a2a2e",
                    width=width,
                    anchor=anchor
                )
                lbl.grid(row=0, column=i, padx=2, pady=5, sticky="nsew")
                scrollable_frame.grid_columnconfigure(i, weight=1)
            if error_msg:
                tk.Label(
                    scrollable_frame,
                    text=f"Error al cargar el ranking: {error_msg}",
                    font=("Arial", 14),
                    fg="#e74c3c",
                    bg="#1a2a2e"
                ).grid(row=1, column=0, columnspan=len(headers), pady=50, sticky="ew")
                return
            if not data:
                tk.Label(
                    scrollable_frame,
                    text="No hay jugadores registrados aún. ¡Regístrate y sé el primero en aparecer en el ranking!",
                    font=("Arial", 14),
                    fg="#95a5a6",
                    bg="#1a2a2e"
                ).grid(row=1, column=0, columnspan=len(headers), pady=50, sticky="ew")
                return
            for i, score in enumerate(data[:50]):
                bg_color = "#2c3e50" if i % 2 == 0 else "#34495e"
                username = score.get("username", "Anónimo")
                puntaje = score.get("score", 0)
                correctas = score.get("correctas", 0)
                incorrectas = score.get("incorrectas", 0)
                modo = score.get("mode", "-")
                categoria = score.get("categoria", "-")
                tiempo = score.get("tiempo", 0)
                fecha = score.get("fecha", "-")
                try:
                    if isinstance(fecha, str) and fecha not in ("-", "Desconocida"):
                        fecha_obj = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
                        fecha = fecha_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    pass
                row_data = [
                    (f"{i+1}", "center", headers[0][1]),
                    (username, "w", headers[1][1]),
                    (str(puntaje), "center", headers[2][1]),
                    (str(correctas), "center", headers[3][1]),
                    (str(incorrectas), "center", headers[4][1]),
                    (modo, "center", headers[5][1]),
                    (categoria, "center", headers[6][1]),
                    (str(tiempo), "center", headers[7][1]),
                    (fecha, "center", headers[8][1])
                ]
                for j, (value, anchor, width) in enumerate(row_data):
                    lbl = tk.Label(
                        scrollable_frame,
                        text=value,
                        font=("Arial", 10),
                        fg="white",
                        bg=bg_color,
                        width=width,
                        anchor=anchor
                    )
                    lbl.grid(row=i+1, column=j, padx=2, pady=3, sticky="nsew")
                    scrollable_frame.grid_columnconfigure(j, weight=1)
            scrollable_frame.update_idletasks()
            frame_height = scrollable_frame.winfo_height()
            canvas_height = canvas.winfo_height()
            if frame_height > canvas_height:
                v_scrollbar.pack(side="right", fill="y")
            else:
                v_scrollbar.pack_forget()
            frame_width = scrollable_frame.winfo_width()
            canvas_width = canvas.winfo_width()
            if frame_width > canvas_width:
                h_scrollbar.pack(side="bottom", fill="x")
            else:
                h_scrollbar.pack_forget()
        mostrar_tabla(ranking_data)

    def adjust_color(self, color, factor):
        """Ajusta el brillo de un color hex"""
        # Mapa de colores nombrados a hex
        color_map = {
            "white": "#FFFFFF",
            "black": "#000000",
            "red": "#FF0000",
            "green": "#00FF00",
            "blue": "#0000FF"
        }
        
        # Si el color es un nombre, convertirlo a hex
        if color.lower() in color_map:
            color = color_map[color.lower()]
        
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def obtener_preguntas_disponibles(self, categoria, dificultad):
        """Obtiene las preguntas disponibles desde la API según la categoría y dificultad"""
        return self.obtener_preguntas_api(categoria, dificultad)
    
    def contar_preguntas_por_dificultad(self, categoria):
        """Cuenta las preguntas disponibles por dificultad para una categoría desde la API"""
        try:
            # Obtener todas las preguntas de la categoría desde la API
            preguntas = self.obtener_preguntas_api(categoria)
            
            conteo = {
                'Fácil': 0,
                'Normal': 0,
                'Difícil': 0
            }
            
            for pregunta in preguntas:
                dificultad = pregunta.difficulty.capitalize()
                if dificultad in conteo:
                    conteo[dificultad] += 1
            
            return conteo
        except Exception as e:
            print(f"Error contando preguntas por dificultad: {e}")
            return {'Fácil': 0, 'Normal': 0, 'Difícil': 0}

    def show_duel_dialog(self, modo, categoria):
        """Muestra un diálogo moderno para ingresar los nombres de los dos jugadores"""
        dialog = tk.Toplevel(self.root)
        dialog.title("⚔️ Modo Duelo - DesafíoSaber")
        dialog.geometry("600x700")
        dialog.configure(bg="#1a2a2e")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centrar la ventana
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal con scroll
        main_container = tk.Frame(dialog, bg="#1a2a2e")
        main_container.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_container, bg="#1a2a2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a2a2e")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header moderno
        header_frame = tk.Frame(scrollable_frame, bg="#2c3e50", height=150)
        header_frame.pack(fill="x", pady=(0, 30))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(
            title_frame,
            text="⚔️",
            font=("Arial", 48),
            bg="#2c3e50",
            fg="#e74c3c"
        ).pack()
        
        tk.Label(
            title_frame,
            text="MODO DUELO",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack()
        
        tk.Label(
            title_frame,
            text=f"Categoría: {categoria} | Modo: {modo}",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#95a5a6"
        ).pack()
        
        # Información del duelo
        info_frame = tk.Frame(scrollable_frame, bg="#1a2a2e")
        info_frame.pack(fill="x", pady=(0, 30))
        
        info_text = "🎯 Dos jugadores se enfrentarán en una batalla de conocimiento.\nCada uno responderá preguntas alternadamente y ganará quien obtenga más puntos."
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 11),
            wraplength=500,
            justify="center",
            bg="#1a2a2e",
            fg="#95a5a6"
        )
        info_label.pack()
        
        # Variables para los nombres
        username1_var = tk.StringVar()
        username2_var = tk.StringVar()
        
        # Función para crear frame de jugador moderno
        def create_player_frame(player_num, username_var):
            frame = tk.Frame(scrollable_frame, bg="#2c3e50", relief="flat", bd=2)
            frame.pack(fill="x", pady=15, padx=10)
            
            # Header del jugador
            player_header = tk.Frame(frame, bg="#34495e", height=50)
            player_header.pack(fill="x")
            player_header.pack_propagate(False)
            
            tk.Label(
                player_header,
                text=f"👤 JUGADOR {player_num}",
                font=("Arial", 14, "bold"),
                bg="#34495e",
                fg="white"
            ).pack(side="left", padx=15, pady=15)
            
            # Contenido del jugador
            content_frame = tk.Frame(frame, bg="#2c3e50")
            content_frame.pack(fill="x", padx=20, pady=20)
            
            # Obtener usuarios registrados
            usuarios_registrados = list(self.usuarios_registrados.keys())
            usuarios_registrados.insert(0, "Selecciona un usuario existente")
            usuarios_registrados.append("Nuevo usuario")
            
            # Combobox moderno
            tk.Label(
                content_frame,
                text="Usuario existente:",
                font=("Arial", 11, "bold"),
                bg="#2c3e50",
                fg="white",
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            
            combo = ttk.Combobox(
                content_frame, 
                values=usuarios_registrados, 
                state="readonly", 
                font=("Arial", 11),
                width=40
            )
            combo.pack(fill="x", pady=(0, 15))
            combo.set("Selecciona un usuario existente")
            
            # Entrada de texto moderna
            tk.Label(
                content_frame,
                text="O ingresa un nuevo nombre:",
                font=("Arial", 11, "bold"),
                bg="#2c3e50",
                fg="white",
                anchor="w"
            ).pack(fill="x", pady=(0, 5))
            
            entry = tk.Entry(
                content_frame,
                font=("Arial", 12),
                bg="#34495e",
                fg="white",
                insertbackground="white",
                relief="flat",
                bd=0,
                textvariable=username_var
            )
            entry.pack(fill="x", ipady=10, ipadx=10)
            
            def on_combo_select(event):
                selected = combo.get()
                if selected and selected not in ["Selecciona un usuario existente", "Nuevo usuario"]:
                    username_var.set(selected)
                elif selected == "Nuevo usuario":
                    username_var.set("")
                    entry.focus()
            
            combo.bind('<<ComboboxSelected>>', on_combo_select)
            
            return frame
        
        # Crear frames para ambos jugadores
        player1_frame = create_player_frame(1, username1_var)
        player2_frame = create_player_frame(2, username2_var)
        
        # Frame para botones modernos
        button_frame = tk.Frame(scrollable_frame, bg="#1a2a2e", height=100)
        button_frame.pack(fill="x", pady=(30, 0))
        button_frame.pack_propagate(False)
        
        def validate_and_start():
            username1 = username1_var.get().strip()
            username2 = username2_var.get().strip()
            
            if not username1 or not username2:
                messagebox.showwarning("⚠️ Advertencia", "Por favor ingresa nombres para ambos jugadores")
                return
            
            if username1 == username2:
                messagebox.showwarning("⚠️ Advertencia", "Los nombres de los jugadores deben ser diferentes")
                return
            
            # Validar que ambos usuarios estén registrados
            if username1 not in self.usuarios_registrados:
                messagebox.showerror("❌ Error", f"El usuario '{username1}' no está registrado.\nEl modo Duelo solo está disponible para usuarios registrados.")
                return
            
            if username2 not in self.usuarios_registrados:
                messagebox.showerror("❌ Error", f"El usuario '{username2}' no está registrado.\nEl modo Duelo solo está disponible para usuarios registrados.")
                return
            
            # Guardar datos del duelo
            self.save_current_duel(username1, username2, modo, categoria)
            
            dialog.destroy()
            self.iniciar_juego_duelo(username1, username2, modo, categoria)
        
        # Botón Comenzar moderno
        start_button = tk.Button(
            button_frame,
            text="⚔️ ¡COMENZAR DUELO!",
            font=("Arial", 14, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="flat",
            bd=0,
            command=validate_and_start,
            cursor="hand2",
            height=2
        )
        start_button.pack(side="left", expand=True, fill="x", padx=(0, 10), pady=20)
        
        # Botón Cancelar moderno
        cancel_button = tk.Button(
            button_frame,
            text="❌ CANCELAR",
            font=("Arial", 14, "bold"),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            bd=0,
            command=dialog.destroy,
            cursor="hand2",
            height=2
        )
        cancel_button.pack(side="left", expand=True, fill="x", padx=(10, 0), pady=20)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Bind del scroll con mouse
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Enfoque en el primer campo
        username1_var.trace("w", lambda *args: canvas.yview_moveto(0))

    def iniciar_juego_duelo(self, username1, username2, modo, categoria):
        """Inicia el juego en modo duelo con dos jugadores"""
        mode_config = GameMode.get_config(modo)
        print(f"[DEPURACIÓN] Configuración usada para Duelo: {mode_config}")
        def normalizar(texto):
            import unicodedata
            if not texto:
                return ''
            texto = texto.lower().strip()
            texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
            return texto.replace('í','i').replace('á','a').replace('é','e').replace('ó','o').replace('ú','u')
        cat_norm = normalizar(categoria)
        preguntas_disponibles = self.obtener_preguntas_api(categoria)
        preguntas_disponibles = [q for q in preguntas_disponibles if normalizar(getattr(q, 'category', '')) == cat_norm]
        num_preguntas = mode_config.get('num_questions', 10)
        if not preguntas_disponibles or len(preguntas_disponibles) < num_preguntas:
            messagebox.showwarning("Advertencia", f"No hay suficientes preguntas válidas en esta categoría para el duelo (se requieren {num_preguntas}). Corrige el banco de preguntas.")
            self.setup_main_menu()
            return
        preguntas = random.sample(preguntas_disponibles, num_preguntas)
        print(f"[DEPURACIÓN] Preguntas seleccionadas para el duelo: {num_preguntas}")
        print(f"[DEPURACIÓN] Tiempo por pregunta (Duelo): {mode_config.get('time_per_question', 15)}s")
        preguntas_usadas = set()
        stats = {
            'modo': modo,
            'username1': username1,
            'username2': username2,
            'categoria': categoria,
            'correctas1': 0,
            'correctas2': 0,
            'incorrectas1': 0,
            'incorrectas2': 0,
            'turno_actual': 1,
            'pregunta_actual': 1,
            'total_preguntas': num_preguntas,
            'preguntas_usadas': preguntas_usadas
        }
        self.mostrar_pregunta_duelo(preguntas, 0, stats)

    def mostrar_pregunta_duelo(self, preguntas, indice, stats):
        """Muestra una pregunta en el modo duelo"""
        # Verificar si hemos llegado al final
        if indice >= len(preguntas) or stats['pregunta_actual'] > stats['total_preguntas']:
            self.mostrar_resultados_duelo(stats)
            return
            
        pregunta = preguntas[indice]
        self.clear_main_frame()
        
        # Variables para el temporizador
        mode_config = GameMode.get_config(stats['modo'])
        tiempo_pregunta = mode_config.get('time_per_question', 15)
        tiempo_restante = [tiempo_pregunta]
        timer_active = [True]
        
        # Obtener estilo de la categoría
        categoria = pregunta.category
        estilo = self.category_styles.get(categoria, {
            "bg_color": "#1a2a2e",
            "icon": "❓",
            "text_color": "white",
            "hover_color": "#2c3e50",
            "border_color": "#1a2a2e",
            "shadow_color": "#1a2a2e"
        })
        
        # Frame principal
        main_container = tk.Frame(self.main_frame, bg=estilo["bg_color"])
        main_container.pack(expand=True, fill="both", padx=40, pady=30)
        
        # Header con información
        header_frame = tk.Frame(main_container, bg=estilo["bg_color"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Info del juego
        info_frame = tk.Frame(header_frame, bg=estilo["bg_color"])
        info_frame.pack(fill="x", padx=20, pady=10)
        
        # Frame para el botón volver y la categoría (izquierda)
        left_frame = tk.Frame(info_frame, bg=estilo["bg_color"])
        left_frame.pack(side="left", fill="y")
        
        # Botón volver al menú
        def confirmar_salir():
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres volver al menú principal?\nPerderás el progreso actual."):
                timer_active[0] = False
                self.setup_main_menu()
        
        back_btn = tk.Button(
            left_frame,
            text="🏠",
            command=confirmar_salir,
            font=("Arial", 20),
            bg=estilo["bg_color"],
            fg=estilo["text_color"],
            bd=0,
            cursor="hand2"
        )
        back_btn.pack(side="left", padx=(0, 10))
        
        # Efectos hover para el botón volver
        def on_enter(e):
            back_btn.configure(bg=self.adjust_color(estilo["bg_color"], 1.2))
        
        def on_leave(e):
            back_btn.configure(bg=estilo["bg_color"])
        
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        
        # Título de la categoría con ícono
        category_label = tk.Label(
            left_frame,
            text=f"{estilo['icon']} {categoria}",
            font=("Arial", 24, "bold"),
            fg=estilo["text_color"],
            bg=estilo["bg_color"]
        )
        category_label.pack(side="left")
        
        # Frame para el temporizador y turno (derecha)
        right_frame = tk.Frame(info_frame, bg=estilo["bg_color"])
        right_frame.pack(side="right", fill="y")
        
        # Mostrar turno actual
        turno_label = tk.Label(
            right_frame,
            text=f"Turno de {stats['username1'] if stats['turno_actual'] == 1 else stats['username2']}",
            font=("Arial", 16, "bold"),
            fg=estilo["text_color"],
            bg=estilo["bg_color"]
        )
        turno_label.pack(side="right", padx=10)
        
        # Frame para el temporizador
        timer_frame = tk.Frame(right_frame, bg=estilo["bg_color"])
        timer_frame.pack(side="right")
        
        # Etiqueta del temporizador
        timer_label = tk.Label(
            timer_frame,
            text=f"⏱️ {tiempo_restante[0]}s",
            font=("Arial", 14),
            fg=estilo["text_color"],
            bg=estilo["bg_color"]
        )
        timer_label.pack()
        
        # Barra de progreso del tiempo
        progress_bar = tk.Frame(timer_frame, bg="#2ecc71", height=4)
        progress_bar.pack(fill="x")
        progress_bar.place(relwidth=1)
        
        # Frame para la pregunta
        question_frame = tk.Frame(main_container, bg=estilo["bg_color"])
        question_frame.pack(fill="x", pady=20)
        
        # Mostrar pregunta
        tk.Label(
            question_frame,
            text=pregunta.question,
            font=("Arial", 16),
            wraplength=600,
            justify="center",
            fg=estilo["text_color"],
            bg=estilo["bg_color"]
        ).pack(pady=10)
        
        # Frame para las opciones
        options_frame = tk.Frame(main_container, bg=estilo["bg_color"])
        options_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Mezclar opciones
        opciones = pregunta.answers.copy()
        random.shuffle(opciones)
        
        # Lista para almacenar los botones
        botones_opciones = []
        
        # Crear botones de opciones
        for i, opcion in enumerate(opciones):
            # Frame contenedor para cada opción
            btn_container = tk.Frame(options_frame, bg=estilo["bg_color"])
            btn_container.pack(fill="x", pady=5)
            
            # Botón de opción con estilo mejorado
            btn = tk.Button(
                btn_container,
                text=opcion,
                font=("Arial", 14),
                wraplength=600,
                fg="#1a2a2e",
                bg="white",    # Fondo blanco
                bd=0,
                cursor="hand2",
                relief="flat",
                padx=20,
                pady=10,
            )
            botones_opciones.append(btn)
            
            # Restaurar animación de aparición con sonido
            def show_button(button, delay):
                def _show():
                    button.pack(fill="x")
                    if delay == 0:  # Solo reproducir sonido para el primer botón
                        self.sound_manager.play_sound('despliegue', 0.5)
                self.main_frame.after(delay, _show)
            
            # Mostrar botones secuencialmente
            show_button(btn, i * 200)  # 200ms de retraso entre cada botón
            
            # Efectos hover mejorados
            def on_enter(e, button=btn):
                if button['state'] != 'disabled':
                    button.configure(
                        bg="#f0f0f0",  # Gris muy claro al hover
                        relief="raised"  # Efecto de elevación
                    )
                    
            def on_leave(e, button=btn):
                if button['state'] != 'disabled':
                    button.configure(
                        bg="white",     # Volver a blanco
                        relief="flat"   # Quitar elevación
                    )
                    
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            btn.configure(command=lambda r=opcion: check_answer(r))
            
            # Efectos hover mejorados
            def on_enter(e, button=btn):
                if button['state'] != 'disabled':
                    button.configure(
                        bg="#f0f0f0",  # Gris muy claro al hover
                        relief="raised"  # Efecto de elevación
                    )
                    
            def on_leave(e, button=btn):
                if button['state'] != 'disabled':
                    button.configure(
                        bg="white",     # Volver a blanco
                        relief="flat"   # Quitar elevación
                    )
                    
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            
            btn.configure(command=lambda r=opcion: check_answer(r))
        
        def check_answer(respuesta):
            if not timer_active[0]:  # Si el temporizador ya no está activo, no hacer nada
                return
            timer_active[0] = False  # Detener el temporizador
            selected_btn = None
            correct_btn = None
            for btn in botones_opciones:
                if btn.cget("text") == respuesta:
                    selected_btn = btn
                if btn.cget("text") == pregunta.correct_answer:
                    correct_btn = btn
            
            # Obtener configuración del modo
            config = GameMode.get_config(stats['modo'])
            points_correct = config.get('points_correct', 100)
            points_incorrect = config.get('points_incorrect', -50)
            bonus_streak = config.get('bonus_streak', 50)
            bonus_streak_threshold = config.get('bonus_streak_threshold', 3)
            
            # Feedback visual
            bonificacion = False
            jugador = '1' if stats['turno_actual'] == 1 else '2'
            if respuesta == pregunta.correct_answer:
                if correct_btn:
                    correct_btn.configure(bg="#32CD32")
                stats[f'correctas{jugador}'] += 1
                bonus = points_correct
                
                # Bonificación por racha
                stats['racha'] = stats.get('racha', 0) + 1
                if stats['racha'] >= bonus_streak_threshold:
                    bonus += bonus_streak
                    bonificacion = True
                
                stats['puntuacion'] = stats.get('puntuacion', 0) + bonus
                self.sound_manager.play_sound('acierto', 0.8)
            else:
                if selected_btn:
                    selected_btn.configure(bg="#FF4C4C")
                if correct_btn:
                    correct_btn.configure(bg="#32CD32")
                stats[f'incorrectas{jugador}'] += 1
                stats['racha'] = 0
                # Aplicar descuento por respuesta incorrecta SIEMPRE, incluso si la puntuación es 0
                stats['puntuacion'] = max(0, stats.get('puntuacion', 0) + points_incorrect)
                self.sound_manager.play_sound('errado', 0.8)
            
            # Deshabilitar todos los botones
            for btn in botones_opciones:
                btn.configure(state="disabled")
            
            # Cambiar turno
            stats['turno_actual'] = 2 if stats['turno_actual'] == 1 else 1
            
            # Solo incrementar pregunta si ambos jugadores ya respondieron
            if stats['turno_actual'] == 1:  # Si volvemos al jugador 1, significa que el jugador 2 ya respondió
                stats['pregunta_actual'] += 1
            
            if bonificacion:
                self.mostrar_bonificacion(f"¡Bonificación por racha! +{bonus_streak} puntos ✨")
            
            # Avanzar a la siguiente pregunta solo si ambos jugadores respondieron
            if stats['turno_actual'] == 1:  # Volvemos al jugador 1, siguiente pregunta
                self.main_frame.after(1500, lambda: self.mostrar_pregunta_duelo(preguntas, indice + 1, stats))
            else:  # Cambio de turno, misma pregunta
                self.main_frame.after(1000, lambda: self.mostrar_pregunta_duelo(preguntas, indice, stats))
            
        # Función para actualizar el temporizador
        def update_timer():
            if not timer_active[0]:
                return
                
            if tiempo_restante[0] > 0:
                try:
                    timer_label.configure(text=f"⏱️ {tiempo_restante[0]}s")
                    progress_bar.place(relwidth=tiempo_restante[0]/tiempo_pregunta)
                    tiempo_restante[0] -= 1
                    
                    if tiempo_restante[0] > 0:
                        self.main_frame.after(1000, update_timer)
                    else:
                        # Tiempo agotado
                        timer_active[0] = False
                        # Mostrar la respuesta correcta en verde
                        for btn in botones_opciones:
                            btn.configure(state="disabled")
                            if btn.cget("text") == pregunta.correct_answer:
                                btn.configure(bg="#32CD32")  # Verde más vivo
                        # Registrar como incorrecta pero sin restar puntos
                        if stats['turno_actual'] == 1:
                            stats['incorrectas1'] += 1
                        else:
                            stats['incorrectas2'] += 1
                        # Cambiar turno
                        stats['turno_actual'] = 2 if stats['turno_actual'] == 1 else 1
                        
                        # Solo incrementar pregunta si ambos jugadores ya respondieron
                        if stats['turno_actual'] == 1:  # Si volvemos al jugador 1, significa que el jugador 2 ya respondió
                            stats['pregunta_actual'] += 1
                            self.main_frame.after(1500, lambda: self.mostrar_pregunta_duelo(preguntas, indice + 1, stats))
                        else:  # Cambio de turno, misma pregunta
                            self.main_frame.after(1000, lambda: self.mostrar_pregunta_duelo(preguntas, indice, stats))
                except Exception as e:
                    print(f"Error en el temporizador: {e}")
                    timer_active[0] = False
        
        # Iniciar temporizador
        update_timer()

    def mostrar_resultados_duelo(self, stats):
        try:
            print('[DEPURACIÓN] Entrando a mostrar_resultados_duelo')
            print(f'[DEPURACIÓN] stats: {stats}')
            self.clear_main_frame()
            # Obtener configuración del modo
            config = GameMode.get_config(stats.get('modo', GameMode.DUEL))
            points_correct = config.get('points_correct', 100)
            # Inicializar y controlar tipos de todos los campos
            username1 = stats.get('username1', '-') or '-'
            username2 = stats.get('username2', '-') or '-'
            modo = stats.get('modo', GameMode.DUEL) or GameMode.DUEL
            categoria = stats.get('categoria', 'General') or 'General'
            correctas1 = stats.get('correctas1', 0) or 0
            correctas2 = stats.get('correctas2', 0) or 0
            incorrectas1 = stats.get('incorrectas1', 0) or 0
            incorrectas2 = stats.get('incorrectas2', 0) or 0
            try:
                correctas1 = int(correctas1)
            except Exception:
                correctas1 = 0
            try:
                correctas2 = int(correctas2)
            except Exception:
                correctas2 = 0
            try:
                incorrectas1 = int(incorrectas1)
            except Exception:
                incorrectas1 = 0
            try:
                incorrectas2 = int(incorrectas2)
            except Exception:
                incorrectas2 = 0
            puntos_j1 = stats.get('puntos1', correctas1 * points_correct)
            puntos_j2 = stats.get('puntos2', correctas2 * points_correct)
            try:
                puntos_j1 = int(puntos_j1)
            except Exception:
                puntos_j1 = correctas1 * points_correct
            try:
                puntos_j2 = int(puntos_j2)
            except Exception:
                puntos_j2 = correctas2 * points_correct
            # Actualizar stats con puntos
            stats['puntos1'] = puntos_j1
            stats['puntos2'] = puntos_j2
            # Sincronizar resultados con el backend
            self.sync_duel_results(stats)
            self.clear_current_duel()
            # Guardar en historial para ambos jugadores
            stats_j1 = {
                'username': username1,
                'modo': modo,
                'categoria': categoria,
                'puntuacion': puntos_j1,
                'correctas': correctas1,
                'incorrectas': incorrectas1,
            }
            stats_j2 = {
                'username': username2,
                'modo': modo,
                'categoria': categoria,
                'puntuacion': puntos_j2,
                'correctas': correctas2,
                'incorrectas': incorrectas2,
            }
            self.guardar_en_historial(stats_j1)
            self.guardar_en_historial(stats_j2)
            ganador = None
            if puntos_j1 > puntos_j2:
                ganador = username1
            elif puntos_j2 > puntos_j1:
                ganador = username2
            # Frame principal
            main_container = tk.Frame(self.main_frame, bg="#1a2a2e")
            main_container.pack(expand=True, fill="both", padx=40, pady=30)
            tk.Label(
                main_container,
                text="🏆 Resultados del Duelo",
                font=("Helvetica", 36, "bold"),
                fg="#3498db",
                bg="#1a2a2e"
            ).pack(pady=(0, 30))
            results_frame = tk.Frame(main_container, bg="#2c3e50", padx=40, pady=30)
            results_frame.pack(fill="x")
            players_frame = tk.Frame(results_frame, bg="#2c3e50")
            players_frame.pack(fill="x", pady=20)
            def create_player_panel(username, correctas, incorrectas, puntos, is_winner):
                panel = tk.Frame(players_frame, bg="#2c3e50", padx=20)
                panel.pack(side="left", expand=True, fill="both")
                if is_winner:
                    tk.Label(panel, text="👑", font=("Arial", 36), bg="#2c3e50", fg="#f1c40f").pack()
                tk.Label(panel, text=username, font=("Arial", 24, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=10)
                stats_frame = tk.Frame(panel, bg="#2c3e50")
                stats_frame.pack(fill="x", pady=10)
                tk.Label(stats_frame, text=f"✅ Correctas: {correctas}", font=("Arial", 16), bg="#2c3e50", fg="#2ecc71").pack(pady=5)
                tk.Label(stats_frame, text=f"❌ Incorrectas: {incorrectas}", font=("Arial", 16), bg="#2c3e50", fg="#e74c3c").pack(pady=5)
                tk.Label(panel, text=f"🎯 {puntos} puntos", font=("Arial", 20, "bold"), bg="#2c3e50", fg="#3498db").pack(pady=10)
            create_player_panel(username1, correctas1, incorrectas1, puntos_j1, ganador == username1)
            create_player_panel(username2, correctas2, incorrectas2, puntos_j2, ganador == username2)
            # Si hay empate, mostrar botón de desempate
            if puntos_j1 == puntos_j2:
                tk.Label(main_container, text="¡Empate!", font=("Arial", 22, "bold"), fg="#f1c40f", bg="#1a2a2e").pack(pady=10)
                tk.Button(
                    main_container,
                    text="Desempatar",
                    font=("Arial", 16, "bold"),
                    bg="#e67e22",
                    fg="white",
                    relief="flat",
                    command=lambda: self.iniciar_desempate_duelo(stats)
                ).pack(pady=20)
            else:
                # Verificar logros solo para usuarios logueados
                if self.current_user:
                    current_user_stats = None
                    if self.current_user == username1:
                        current_user_stats = {
                            'username': username1,
                            'modo': modo,
                            'categoria': categoria,
                            'correctas': correctas1,
                            'incorrectas': incorrectas1,
                            'puntuacion': puntos_j1,
                            'duel_victories': 1 if puntos_j1 > puntos_j2 else 0
                        }
                    elif self.current_user == username2:
                        current_user_stats = {
                            'username': username2,
                            'modo': modo,
                            'categoria': categoria,
                            'correctas': correctas2,
                            'incorrectas': incorrectas2,
                            'puntuacion': puntos_j2,
                            'duel_victories': 1 if puntos_j2 > puntos_j1 else 0
                        }
                    if current_user_stats:
                        self.achievement_manager.check_achievements(current_user_stats)
                self.guardar_puntuacion(puntos_j1, modo, username1, stats_j1)
                self.guardar_puntuacion(puntos_j2, modo, username2, stats_j2)
                messagebox.showinfo("✅ Sincronización", f"Los resultados de {username1} y {username2} han sido sincronizados con el servidor.")
            # Botones de acción
            buttons_frame = tk.Frame(main_container, bg="#1a2a2e")
            buttons_frame.pack(pady=30)
            tk.Button(
                buttons_frame,
                text="🔄 Jugar Otra Vez",
                font=("Arial", 14, "bold"),
                bg="#3498db",
                fg="white",
                relief="flat",
                command=lambda: self.iniciar_juego_duelo(username1, username2, modo, categoria)
            ).pack(side="left", padx=10)
            tk.Button(
                buttons_frame,
                text="🎮 Jugar Otro Modo",
                font=("Arial", 14, "bold"),
                bg="#e67e22",
                fg="white",
                relief="flat",
                command=self.menu_jugar
            ).pack(side="left", padx=10)
            tk.Button(
                buttons_frame,
                text="🏠 Volver al Menú",
                font=("Arial", 14, "bold"),
                bg="#95a5a6",
                fg="white",
                relief="flat",
                command=self.setup_main_menu
            ).pack(side="left", padx=10)
        except Exception as e:
            print(f'[ERROR] mostrar_resultados_duelo: {e}')
            print(f'[ERROR] stats recibido: {stats}')
            import traceback
            traceback.print_exc()
            self.clear_main_frame()
            tk.Label(self.main_frame, text=f"Error al mostrar resultados del duelo: {e}", font=("Arial", 18), fg="#e74c3c", bg="#1a2a2e").pack(expand=True, pady=80)

    def precargar_datos_background(self):
        """Precarga datos en segundo plano para mejorar el rendimiento"""
        def cargar_en_background():
            try:
                # Cargar preguntas en segundo plano (solo una vez)
                if not hasattr(self, 'preguntas_todas') or not self.preguntas_todas:
                    self.cargar_todas_las_preguntas()
                # Cargar usuarios registrados (solo una vez)
                if not hasattr(self, 'usuarios_registrados') or not self.usuarios_registrados:
                    self.cargar_usuarios_registrados()
                # Cargar categorías desde la API
                try:
                    import requests
                    response = requests.get('http://localhost:5000/api/categories', timeout=2)
                    if response.status_code == 200:
                        api_categories = response.json()
                        if isinstance(api_categories, list):
                            self.categorias_precargadas = api_categories
                except Exception as e:
                    print(f'[DEPURACIÓN] No se pudo precargar categorías desde la API: {e}')
                # Recargar modos dinámicos por si cambiaron
                GameMode.load_dynamic_configs()
                self.precarga_completa = True
                print('[DEPURACIÓN] Precarga de datos completa')
            except Exception as e:
                print(f'[DEPURACIÓN] Error en precarga: {e}')
        
        # Ejecutar en segundo plano para no bloquear la UI
        threading.Thread(target=cargar_en_background, daemon=True).start()

    def cargar_usuarios_registrados(self):
        """Carga la lista de usuarios registrados desde el ranking (optimizado)"""
        # Evitar cargar múltiples veces
        if hasattr(self, 'usuarios_registrados') and self.usuarios_registrados:
            return
            
        try:
            # Usar ruta absoluta para mayor velocidad
            ranking_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ranking.json')
            with open(ranking_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Si el archivo es una lista, convertirlo a dict
                if isinstance(data, list):
                    data = {"rankings": data}
                    with open(ranking_file, 'w', encoding='utf-8') as fw:
                        json.dump(data, fw, ensure_ascii=False, indent=4)
                for ranking in data.get('rankings', []):
                    username = ranking.get('username')
                    if username and username != "Anónimo":
                        if username not in self.usuarios_registrados:
                            self.usuarios_registrados[username] = {
                                'mejor_puntuacion': ranking['score'],
                                'modo': ranking['mode']
                            }
                        elif ranking['score'] > self.usuarios_registrados[username]['mejor_puntuacion']:
                            self.usuarios_registrados[username]['mejor_puntuacion'] = ranking['score']
                            self.usuarios_registrados[username]['modo'] = ranking['mode']
        except FileNotFoundError:
            self.usuarios_registrados = {}
        except Exception as e:
            print(f"Error al cargar usuarios: {e}")
            self.usuarios_registrados = {}
    
    def actualizar_puntuacion_usuario(self, username, score, mode):
        """Actualiza la puntuación de un usuario en el ranking"""
        try:
            with open('data/ranking.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Buscar puntuación anterior del usuario en el mismo modo
            for ranking in data.get('rankings', []):
                if ranking.get('username') == username and ranking.get('mode') == mode:
                    if score > ranking['score']:
                        ranking['score'] = score
                        ranking['date'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        break
            else:
                # Si no existe una puntuación anterior, agregar una nueva
                nueva_puntuacion = {
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "mode": mode,
                    "score": score,
                    "username": username
                }
                data["rankings"].append(nueva_puntuacion)
            
            # Ordenar por puntuación más alta
            data["rankings"].sort(key=lambda x: x["score"], reverse=True)
            
            # Mantener solo las mejores 100 puntuaciones
            data["rankings"] = data["rankings"][:100]
            
            with open('data/ranking.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            # Actualizar la lista de usuarios registrados
            if username not in self.usuarios_registrados:
                self.usuarios_registrados[username] = {
                    'mejor_puntuacion': score,
                    'modo': mode
                }
            elif score > self.usuarios_registrados[username]['mejor_puntuacion']:
                self.usuarios_registrados[username]['mejor_puntuacion'] = score
                self.usuarios_registrados[username]['modo'] = mode
                
        except Exception as e:
            print(f"Error al actualizar puntuación: {e}")
            messagebox.showerror("Error", "No se pudo actualizar la puntuación")
    
    def actualizar_estadisticas_usuario(self, username, score, mode, stats):
        """Actualiza las estadísticas del usuario y sincroniza con el servidor"""
        try:
            with open('data/usuarios.json', 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            # Manejar tanto listas como diccionarios
            if isinstance(loaded_data, list):
                users = loaded_data
                is_dict_format = False
            elif isinstance(loaded_data, dict):
                users = list(loaded_data.values())
                is_dict_format = True
            else:
                return
            
            for user in users:
                if user.get('username', '').lower() == username.lower():
                    if 'stats' not in user:
                        user['stats'] = {}
                    
                    # Actualizar estadísticas básicas
                    user['stats']['total_games'] = user['stats'].get('total_games', 0) + 1
                    user['stats']['total_score'] = user['stats'].get('total_score', 0) + score
                    
                    if score > user['stats'].get('best_score', 0):
                        user['stats']['best_score'] = score
                    
                    # Actualizar estadísticas por modo
                    if mode == "Clásico":
                        user['stats']['classic_games'] = user['stats'].get('classic_games', 0) + 1
                    elif mode == "Contrarreloj":
                        user['stats']['timeattack_games'] = user['stats'].get('timeattack_games', 0) + 1
                    elif mode == "Duelo":
                        user['stats']['duel_games'] = user['stats'].get('duel_games', 0) + 1
                    
                    # Actualizar estadísticas de respuestas
                    if stats:
                        user['stats']['total_correct'] = user['stats'].get('total_correct', 0) + stats.get('correctas', 0)
                        user['stats']['total_incorrect'] = user['stats'].get('total_incorrect', 0) + stats.get('incorrectas', 0)
                        
                        # Actualizar racha máxima
                        if stats.get('correctas', 0) > user['stats'].get('max_streak', 0):
                            user['stats']['max_streak'] = stats.get('correctas', 0)
                    
                    # Actualizar categoría favorita
                    if stats and stats.get('categoria'):
                        if 'categories_played' not in user['stats']:
                            user['stats']['categories_played'] = []
                        if stats.get('categoria') not in user['stats']['categories_played']:
                            user['stats']['categories_played'].append(stats.get('categoria'))
                    
                    # Actualizar último juego
                    user['stats']['last_played'] = datetime.now().isoformat()
                    
                    break
            
            # Guardar en el formato correcto
            if is_dict_format:
                users_dict = {}
                for u in users:
                    users_dict[u['username']] = u
                with open('data/usuarios.json', 'w', encoding='utf-8') as f:
                    auto_backup('data/usuarios.json')
                    json.dump(users_dict, f, ensure_ascii=False, indent=2)
            else:
                with open('data/usuarios.json', 'w', encoding='utf-8') as f:
                    auto_backup('data/usuarios.json')
                    json.dump(users, f, ensure_ascii=False, indent=2)
                
            # Sincronizar con servidor
            self.sincronizar_estadisticas_usuario(username, user['stats'])
                
        except Exception as e:
            print(f"Error actualizando estadísticas de usuario: {e}")
    
    def sincronizar_estadisticas_usuario(self, username, stats):
        """Sincroniza las estadísticas del usuario con el servidor"""
        try:
            import requests
            
            # Buscar el usuario en el servidor
            response = requests.get("http://localhost:5000/api/players")
            if response.status_code == 200:
                players = response.json()
                for player in players:
                    if player.get('username', '').lower() == username.lower():
                        # Actualizar estadísticas
                        update_data = {
                            'stats': stats
                        }
                        requests.put(f"http://localhost:5000/api/players/{player['id']}", json=update_data, timeout=5)
                        print(f"Estadísticas de {username} sincronizadas con el servidor")
                        break
        except Exception as e:
            print(f"Error sincronizando estadísticas: {e}")

    def center_window(self):
        """Centra y configura la ventana en pantalla completa"""
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Configurar la ventana para que ocupe toda la pantalla
        self.root.state('zoomed')
        
        # Asegurar que la ventana tenga las dimensiones correctas
        self.root.update_idletasks()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Si las dimensiones no son 1920x1080, ajustar el tamaño
        if window_width != 1920 or window_height != 1080:
            # Calcular la escala para mantener la proporción 16:9
            scale = min(screen_width/1920, screen_height/1080)
            new_width = int(1920 * scale)
            new_height = int(1080 * scale)
            
            # Centrar la ventana
            x = (screen_width - new_width) // 2
            y = (screen_height - new_height) // 2
            
            # Aplicar las nuevas dimensiones
            self.root.geometry(f"{new_width}x{new_height}+{x}+{y}")
        
        # Agregar tecla de escape para salir de pantalla completa
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())
    
    def toggle_fullscreen(self):
        """Alterna entre pantalla completa y ventana normal"""
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
            self.root.state('zoomed')
        else:
            self.root.attributes('-fullscreen', True)

    def load_sounds(self):
        """Carga los sonidos del juego"""
        try:
            pygame.mixer.init()
            self.sound_manager = SoundManager()
        except Exception as e:
            print(f"Error al inicializar el sistema de sonido: {e}")
            self.sound_manager = None

    def _calculate_fade_color(self, hex_color, alpha):
        """Calcula el color interpolado para el efecto fade."""
        # Convertir el color hex a RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Interpolar con negro
        r = int(r * alpha)
        g = int(g * alpha)
        b = int(b * alpha)
        
        return f'#{r:02x}{g:02x}{b:02x}'

    def _create_dissolve_pattern(self, width, height, density=0.1):
        """Crea un patrón de disolución aleatorio."""
        pattern = []
        total_pixels = width * height
        dissolve_pixels = int(total_pixels * density)
        for _ in range(dissolve_pixels):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            pattern.append((x, y))
        return pattern

    def show_intro_screen(self):
        """Muestra la pantalla de intro con animación y música"""
        # Limpiar la ventana
        self.clear_main_frame()
        
        try:
            # Variables para controlar la animación y widgets
            animation_state = {
                'music_started': False,
                'transition_started': False,
                'widgets': {}  # Almacenar referencias a widgets
            }
            
            # Frame para el menú principal (inicialmente invisible, al fondo)
            menu_frame = tk.Frame(self.main_frame, bg='#1E2329')
            menu_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            animation_state['widgets']['menu'] = menu_frame
            
            # Canvas para el efecto de disolución (en medio)
            dissolve_canvas = tk.Canvas(
                self.main_frame,
                bg='#1E2329',
                highlightthickness=0,
                width=self.root.winfo_screenwidth(),
                height=self.root.winfo_screenheight()
            )
            dissolve_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
            animation_state['widgets']['canvas'] = dissolve_canvas
            
            # Frame para la intro con fondo oscuro que coincide con la imagen (arriba)
            intro_frame = tk.Frame(self.main_frame, bg='#1E2329')
            intro_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            animation_state['widgets']['intro'] = intro_frame
            
            # Cargar y mostrar el logo
            logo_image = Image.open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'logo.png'))
            
            # Calcular proporciones para ajuste al 85% de la pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            target_width = int(screen_width * 0.85)
            target_height = int(screen_height * 0.85)
            
            # Mantener proporción de aspecto
            img_ratio = logo_image.size[0] / logo_image.size[1]
            if target_width / target_height > img_ratio:
                new_height = target_height
                new_width = int(new_height * img_ratio)
            else:
                new_width = target_width
                new_height = int(new_width / img_ratio)
            
            # Redimensionar imagen manteniendo el canal alpha
            logo_image = logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crear un nuevo frame transparente para el logo
            logo_frame = tk.Frame(intro_frame, bg='#1E2329')
            logo_frame.place(relx=0.5, rely=0.5, anchor="center")
            animation_state['widgets']['logo_frame'] = logo_frame
            
            # Convertir y mostrar la imagen
            logo_photo = ImageTk.PhotoImage(logo_image)
            
            # Label para el logo con el mismo color de fondo
            logo_label = tk.Label(
                logo_frame,
                image=logo_photo,
                bg='#1E2329'
            )
            logo_label.image = logo_photo
            logo_label.pack()
            animation_state['widgets']['logo_label'] = logo_label
            
            # Función para aparecer suavemente
            def fade_in(alpha=0.0):
                if alpha < 1.0:
                    alpha += 0.02
                    self.root.attributes('-alpha', alpha)
                    self.root.after(10, lambda: fade_in(alpha))
                else:
                    if not animation_state['music_started']:
                        animation_state['music_started'] = True
                        # Reproducir música de intro
                        self.sound_manager.play_sound('intro_music', volume=0.5)
                        # Iniciar verificación de música
                        self.root.after(100, check_music)
            
            # Función para verificar cuando termina la música
            def check_music():
                if not animation_state['transition_started']:
                    if not pygame.mixer.get_busy():
                        animation_state['transition_started'] = True
                        prepare_transition()
                    else:
                        self.root.after(100, check_music)
            
            # Función para preparar la transición
            def prepare_transition():
                # Preparar el menú principal
                self.setup_main_menu()
                
                # Asegurarse de que el canvas existe y está configurado
                if 'canvas' in animation_state['widgets']:
                    canvas = animation_state['widgets']['canvas']
                    if canvas.winfo_exists():
                        canvas.tkraise()
                        # Crear patrón de disolución
                        dissolve_pattern = self._create_dissolve_pattern(screen_width, screen_height, density=0.15)
                        dissolve_transition(dissolve_pattern, 0)
            
            # Función para la transición con disolución
            def dissolve_transition(pattern, index, alpha_intro=1.0):
                try:
                    if index < len(pattern):
                        # Verificar que los widgets existen
                        canvas = animation_state['widgets'].get('canvas')
                        intro = animation_state['widgets'].get('intro')
                        logo_frame = animation_state['widgets'].get('logo_frame')
                        logo_label = animation_state['widgets'].get('logo_label')
                        
                        if all(w and w.winfo_exists() for w in [canvas, intro, logo_frame, logo_label]):
                            # Crear puntos de disolución
                            batch_size = len(pattern) // 50  # Procesar en lotes para suavidad
                            for i in range(batch_size):
                                if index + i < len(pattern):
                                    x, y = pattern[index + i]
                                    canvas.create_rectangle(
                                        x, y, x+3, y+3,  # Tamaño ligeramente mayor para mejor efecto
                                        fill='#1E2329',
                                        outline='#1E2329'
                                    )
                            
                            # Ajustar opacidad del frame de intro
                            alpha_intro -= 0.02
                            
                            # Actualizar colores
                            bg_color_intro = self._calculate_fade_color('#1E2329', alpha_intro)
                            intro.configure(bg=bg_color_intro)
                            logo_frame.configure(bg=bg_color_intro)
                            logo_label.configure(bg=bg_color_intro)
                            
                            self.root.after(10, lambda: dissolve_transition(
                                pattern, index + batch_size, alpha_intro
                            ))
                        else:
                            # Si algún widget no existe, limpiar y terminar
                            cleanup_widgets()
                    else:
                        cleanup_widgets()
                except tk.TclError:
                    cleanup_widgets()
            
            def cleanup_widgets():
                """Limpia los widgets de manera segura"""
                # Detener la música
                self.sound_manager.stop_sound('intro_music')
                
                # Limpiar widgets en orden inverso
                for widget_name in ['logo_label', 'logo_frame', 'intro', 'canvas']:
                    if widget_name in animation_state['widgets']:
                        widget = animation_state['widgets'][widget_name]
                        try:
                            if widget and widget.winfo_exists():
                                widget.destroy()
                        except tk.TclError:
                            pass  # Ignorar errores si el widget ya fue destruido
                        animation_state['widgets'][widget_name] = None
            
            # Iniciar con transparencia total
            self.root.attributes('-alpha', 0.0)
            # Iniciar la animación
            fade_in()
            
        except Exception as e:
            print(f"Error en la pantalla de intro: {e}")
            self.setup_main_menu()

    def show_error_report_dialog(self):
        """Muestra un diálogo para reportar errores"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Reportar Error")
        dialog.geometry("500x400")
        dialog.configure(bg="#1a2a2e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar la ventana
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg="#1a2a2e")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        tk.Label(
            main_frame,
            text="🐛 Reportar Error",
            font=("Helvetica", 16, "bold"),
            bg="#1a2a2e",
            fg="#e74c3c"
        ).pack(pady=(0, 20))
        
        # Descripción
        tk.Label(
            main_frame,
            text="Ayúdanos a mejorar el juego reportando cualquier error que encuentres:",
            font=("Helvetica", 10),
            bg="#1a2a2e",
            fg="white",
            wraplength=450
        ).pack(pady=(0, 20))
        
        # Campo de nombre
        tk.Label(
            main_frame,
            text="Tu nombre (opcional):",
            font=("Helvetica", 10, "bold"),
            bg="#1a2a2e",
            fg="white"
        ).pack(anchor="w")
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(
            main_frame,
            textvariable=name_var,
            font=("Helvetica", 10),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            width=50
        )
        name_entry.pack(fill="x", pady=(5, 15))
        
        # Campo de descripción del error
        tk.Label(
            main_frame,
            text="Descripción del error:",
            font=("Helvetica", 10, "bold"),
            bg="#1a2a2e",
            fg="white"
        ).pack(anchor="w")
        
        error_text = tk.Text(
            main_frame,
            height=8,
            font=("Helvetica", 10),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            wrap="word"
        )
        error_text.pack(fill="both", expand=True, pady=(5, 15))
        
        # Frame para botones
        button_frame = tk.Frame(main_frame, bg="#1a2a2e")
        button_frame.pack(fill="x")
        
        def send_report():
            """Envía el reporte de error"""
            name = name_var.get().strip()
            error_desc = error_text.get("1.0", tk.END).strip()
            
            if not error_desc:
                messagebox.showwarning("Advertencia", "Por favor describe el error que encontraste.")
                return
            
            # Preparar datos del error
            error_data = {
                "name": name if name else "Anónimo",
                "description": error_desc,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            # Enviar reporte
            def send_async():
                success = self.api_client.report_error(error_data)
                if success:
                    dialog.after(0, lambda: messagebox.showinfo("Éxito", "Error reportado correctamente. Gracias por tu ayuda."))
                    dialog.after(0, dialog.destroy)
                else:
                    dialog.after(0, lambda: messagebox.showerror("Error", "No se pudo enviar el reporte. Inténtalo más tarde."))
            
            # Ejecutar en hilo separado
            threading.Thread(target=send_async, daemon=True).start()
        
        def cancel():
            """Cancela el reporte"""
            dialog.destroy()
        
        # Botones
        tk.Button(
            button_frame,
            text="Enviar Reporte",
            command=send_report,
            font=("Helvetica", 10, "bold"),
            bg="#27ae60",
            fg="white",
            bd=0,
            cursor="hand2",
            relief="flat",
            width=15
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=cancel,
            font=("Helvetica", 10),
            bg="#95a5a6",
            fg="white",
            bd=0,
            cursor="hand2",
            relief="flat",
            width=15
        ).pack(side="left")

    def cargar_todas_las_preguntas(self):
        """Carga todas las preguntas desde archivos locales para mayor velocidad y solo acepta categorías válidas"""
        import unicodedata
        def normalizar(texto):
            if not texto:
                return ''
            texto = texto.lower().strip()
            texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
            return texto.replace('í','i').replace('á','a').replace('é','e').replace('ó','o').replace('ú','u')
        categorias_validas = {
            'historia', 'ciencia', 'geografia', 'arte', 'deportes', 'entretenimiento'
        }
        try:
            # Cargar desde archivo local en lugar de API para mayor velocidad
            questions_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'questions.json')
            if os.path.exists(questions_file):
                with open(questions_file, 'r', encoding='utf-8') as f:
                    questions_data = json.load(f)
            else:
                questions_data = self.api_client.get_questions() if self.api_client else []
            preguntas = []
            preguntas_descartadas = 0
            for q in questions_data:
                categoria_q = q.get('categoria')
                if categoria_q == 'Ciencias':
                    categoria_q = 'Ciencia'
                cat_norm = normalizar(categoria_q)
                if cat_norm not in categorias_validas:
                    preguntas_descartadas += 1
                    print(f'[ADVERTENCIA] Pregunta descartada por categoría inválida: "{categoria_q}" -> "{cat_norm}" | Pregunta: {q.get("pregunta")[:60]}...')
                    continue
                question = Question(
                    category=categoria_q,
                    question=q.get('pregunta'),
                    answers=q.get('opciones', []),
                    correct_answer=q.get('respuesta'),
                    mode=q.get('modo', GameMode.CLASSIC),
                    difficulty=q.get('dificultad', 'normal')
                )
                preguntas.append(question)
            self.preguntas_todas = preguntas
            print('[DEPURACIÓN] Preguntas cargadas:', len(self.preguntas_todas))
            if preguntas_descartadas > 0:
                print(f'[ADVERTENCIA] Total de preguntas descartadas por categoría inválida: {preguntas_descartadas}')
            if self.preguntas_todas:
                print('[DEPURACIÓN] Categorías:', list(set(q.category for q in self.preguntas_todas)))
                print('[DEPURACIÓN] Dificultades:', list(set(q.difficulty for q in self.preguntas_todas)))
                print('[DEPURACIÓN] Ejemplo pregunta:', self.preguntas_todas[0].__dict__)
            else:
                print('[DEPURACIÓN] No se cargaron preguntas. Revisa el formato de questions.json')
        except Exception as e:
            print(f"Error cargando todas las preguntas: {e}")
            self.preguntas_todas = []

    def recargar_preguntas(self):
        """Permite recargar las preguntas manualmente si se agregan nuevas desde el panel admin"""
        self.cargar_todas_las_preguntas()

    def mostrar_bonificacion(self, msg):
        """Muestra un mensaje de bonificación temporal"""
        if hasattr(self, 'bono_label') and self.bono_label:
            self.bono_label.destroy()
        self.bono_label = tk.Label(self.main_frame, text=msg, font=("Arial", 18, "bold"), fg="#f1c40f", bg="#2c3e50")
        self.bono_label.pack(pady=10)
        self.main_frame.after(1500, lambda: self.bono_label.destroy())

    def show_achievement_popup(self, achievement):
        """Muestra un popup animado cuando se desbloquea un logro"""
        popup = tk.Toplevel(self.root)
        popup.title("¡Logro Desbloqueado!")
        popup.geometry("400x200")
        popup.configure(bg="#1a2a2e")
        popup.attributes('-topmost', True)
        
        # Centrar la ventana
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        
        # Contenido del popup
        main_frame = tk.Frame(popup, bg="#1a2a2e")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Icono y título
        tk.Label(
            main_frame,
            text=achievement.icon,
            font=("Arial", 48),
            bg="#1a2a2e",
            fg="#f1c40f"
        ).pack(pady=(0, 10))
        
        tk.Label(
            main_frame,
            text="¡Logro Desbloqueado!",
            font=("Arial", 18, "bold"),
            bg="#1a2a2e",
            fg="#f1c40f"
        ).pack(pady=(0, 5))
        
        tk.Label(
            main_frame,
            text=achievement.name,
            font=("Arial", 16, "bold"),
            bg="#1a2a2e",
            fg="white"
        ).pack(pady=(0, 5))
        
        tk.Label(
            main_frame,
            text=achievement.description,
            font=("Arial", 12),
            bg="#1a2a2e",
            fg="#bdc3c7",
            wraplength=350
        ).pack(pady=(0, 10))
        
        if achievement.reward_points > 0:
            tk.Label(
                main_frame,
                text=f"+{achievement.reward_points} puntos",
                font=("Arial", 14, "bold"),
                bg="#1a2a2e",
                fg="#2ecc71"
            ).pack()
        
        # Cerrar automáticamente después de 3 segundos
        popup.after(3000, popup.destroy)
        
        # Reproducir sonido de logro
        self.sound_manager.play_sound('acierto', 0.6)

    def mostrar_logros(self):
        """Muestra la sección de logros con scroll fluido y botón volver (ícono de casa grande a la izquierda)"""
        self.clear_main_frame()
        main_container = tk.Frame(self.main_frame, bg="#1a2a2e")
        main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header solo con botón volver (ícono de casa grande)
        header_frame = tk.Frame(main_container, bg="#2c3e50", height=80)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        volver_btn = tk.Button(
            header_frame,
            text="🏠",
            font=("Arial", 32, "bold"),
            bg="#2c3e50",
            fg="white",
            bd=0,
            cursor="hand2",
            command=self.setup_main_menu
        )
        volver_btn.pack(side="left", padx=20, pady=10)
        tk.Label(
            header_frame,
            text="Logros",
            font=("Arial", 28, "bold"),
            bg="#2c3e50",
            fg="#f1c40f"
        ).pack(side="left", padx=20, pady=20)
        
        # Si no hay usuario logueado, mostrar mensaje personalizado y salir
        if not hasattr(self, 'current_user') or not self.current_user:
            msg = "Inicia sesión para ver y desbloquear tus logros personales."
            tk.Label(main_container, text=msg, font=("Arial", 18), bg="#1a2a2e", fg="#95a5a6").pack(expand=True, pady=80)
            return
        
        # Cargar logros disponibles y del usuario
        try:
            with open('data/achievements.json', 'r', encoding='utf-8') as f:
                achievements_data = json.load(f)
            with open('data/user_achievements.json', 'r', encoding='utf-8') as f:
                user_achievements = json.load(f)
            unlocked_achievements = user_achievements.get('unlocked', [])
            
            # Crear contenedor con scroll
            canvas = tk.Canvas(main_container, bg="#1a2a2e", highlightthickness=0)
            scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#1a2a2e")
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Título del usuario y progreso
            user_title = tk.Label(
                scrollable_frame,
                text=f"Logros de {self.current_user}",
                font=("Arial", 20, "bold"),
                bg="#1a2a2e",
                fg="#3498db"
            )
            user_title.pack(pady=(0, 10))
            
            total_achievements = len(achievements_data)
            unlocked_count = len(unlocked_achievements)
            progress_percent = (unlocked_count / total_achievements) * 100 if total_achievements > 0 else 0
            progress_label = tk.Label(
                scrollable_frame,
                text=f"Progreso: {unlocked_count}/{total_achievements} logros  |  Completado: {progress_percent:.1f}%",
                font=("Arial", 14),
                bg="#1a2a2e",
                fg="#f1c40f"
            )
            progress_label.pack(pady=(0, 20))
            
            # Sección de logros desbloqueados
            if unlocked_achievements:
                unlocked_frame = tk.Frame(scrollable_frame, bg="#1a2a2e")
                unlocked_frame.pack(fill="x", pady=(0, 20))
                tk.Label(
                    unlocked_frame,
                    text="🏆 Logros Desbloqueados",
                    font=("Arial", 18, "bold"),
                    bg="#1a2a2e",
                    fg="#2ecc71"
                ).pack(pady=(0, 15))
                
                # Grid de logros desbloqueados (3 columnas por fila)
                unlocked_grid = tk.Frame(unlocked_frame, bg="#1a2a2e")
                unlocked_grid.pack(fill="x")
                columns = 3
                for i, achievement_id in enumerate(unlocked_achievements):
                    achievement = next((a for a in achievements_data if a['id'] == achievement_id), None)
                    if achievement:
                        row = i // columns
                        col = i % columns
                        frame = tk.Frame(unlocked_grid, bg="#1a2a2e")
                        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                        self.create_achievement_card(frame, achievement, True)
                for col in range(columns):
                    unlocked_grid.grid_columnconfigure(col, weight=1)
            
            # Sección de logros pendientes
            pending_achievements = [a for a in achievements_data if a['id'] not in unlocked_achievements]
            if pending_achievements:
                pending_frame = tk.Frame(scrollable_frame, bg="#1a2a2e")
                pending_frame.pack(fill="x", pady=(0, 20))
                tk.Label(
                    pending_frame,
                    text="🎯 Logros Pendientes",
                    font=("Arial", 18, "bold"),
                    bg="#1a2a2e",
                    fg="#e67e22"
                ).pack(pady=(0, 15))
                
                # Grid de logros pendientes (3 columnas por fila)
                pending_grid = tk.Frame(pending_frame, bg="#1a2a2e")
                pending_grid.pack(fill="x")
                columns = 3
                for i, achievement in enumerate(pending_achievements):
                    row = i // columns
                    col = i % columns
                    frame = tk.Frame(pending_grid, bg="#1a2a2e")
                    frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                    self.create_achievement_card(frame, achievement, False)
                for col in range(columns):
                    pending_grid.grid_columnconfigure(col, weight=1)
            
            # Configurar scroll
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Configurar scroll con mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        except Exception as e:
            print(f"Error cargando logros: {e}")
            error_msg = "Error al cargar los logros. Intenta de nuevo."
            tk.Label(main_container, text=error_msg, font=("Arial", 16), bg="#1a2a2e", fg="#e74c3c").pack(expand=True, pady=80)

    def mostrar_estadisticas(self):
        """Muestra las estadísticas detalladas del jugador con header profesional solo con botón volver"""
        self.clear_main_frame()
        main_container = tk.Frame(self.main_frame, bg="#1a2a2e")
        main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header solo con botón volver (ícono de casa grande)
        header_frame = tk.Frame(main_container, bg="#2c3e50", height=80)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        volver_btn = tk.Button(
            header_frame,
            text="🏠",
            font=("Arial", 32, "bold"),
            bg="#2c3e50",
            fg="white",
            bd=0,
            cursor="hand2",
            command=self.setup_main_menu
        )
        volver_btn.pack(side="left", padx=20, pady=10)
        tk.Label(
            header_frame,
            text="Estadísticas",
            font=("Arial", 28, "bold"),
            bg="#2c3e50",
            fg="#f1c40f"
        ).pack(side="left", padx=20, pady=20)
        
        # Si no hay usuario logueado, mostrar mensaje personalizado y salir
        if not hasattr(self, 'current_user') or not self.current_user:
            msg = "Inicia sesión para ver tus estadísticas personales."
            tk.Label(main_container, text=msg, font=("Arial", 18), bg="#1a2a2e", fg="#95a5a6").pack(expand=True, pady=80)
            return
        
        # Cargar estadísticas del usuario
        try:
            with open('data/user_stats.json', 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
            
            user_stats = stats_data.get('users', {}).get(self.current_user, {})
            
            if not user_stats:
                # Si no hay estadísticas, crear estructura básica
                user_stats = {
                    "username": self.current_user,
                    "total_games": 0,
                    "classic_games": 0,
                    "timeattack_games": 0,
                    "duel_games": 0,
                    "total_correct": 0,
                    "total_incorrect": 0,
                    "max_streak": 0,
                    "highest_score": 0,
                    "duel_victories": 0,
                    "categories_played": [],
                    "last_played": None
                }
            
            # Crear contenedor con scroll
            canvas = tk.Canvas(main_container, bg="#1a2a2e", highlightthickness=0)
            scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#1a2a2e")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Título del usuario
            user_title = tk.Label(
                scrollable_frame,
                text=f"Estadísticas de {self.current_user}",
                font=("Arial", 20, "bold"),
                bg="#1a2a2e",
                fg="#3498db"
            )
            user_title.pack(pady=(0, 20))
            
            # Resumen general
            summary_frame = tk.Frame(scrollable_frame, bg="#2c3e50", padx=20, pady=15)
            summary_frame.pack(fill="x", pady=(0, 20))
            
            tk.Label(
                summary_frame,
                text="📊 Resumen General",
                font=("Arial", 18, "bold"),
                bg="#2c3e50",
                fg="#f1c40f"
            ).pack(pady=(0, 15))
            
            # Grid de estadísticas principales
            main_stats_frame = tk.Frame(summary_frame, bg="#2c3e50")
            main_stats_frame.pack(fill="x")
            
            # Primera fila
            row1 = tk.Frame(main_stats_frame, bg="#2c3e50")
            row1.pack(fill="x", pady=5)
            
            self.create_stat_card(row1, "🎮 Total Partidas", str(user_stats.get('total_games', 0)), "#3498db")
            self.create_stat_card(row1, "🏆 Puntuación Máxima", str(user_stats.get('highest_score', 0)), "#f1c40f")
            self.create_stat_card(row1, "🔥 Racha Máxima", str(user_stats.get('max_streak', 0)), "#e67e22")
            
            # Segunda fila
            row2 = tk.Frame(main_stats_frame, bg="#2c3e50")
            row2.pack(fill="x", pady=5)
            
            total_answers = user_stats.get('total_correct', 0) + user_stats.get('total_incorrect', 0)
            accuracy = (user_stats.get('total_correct', 0) / total_answers * 100) if total_answers > 0 else 0
            
            self.create_stat_card(row2, "✅ Correctas", str(user_stats.get('total_correct', 0)), "#2ecc71")
            self.create_stat_card(row2, "❌ Incorrectas", str(user_stats.get('total_incorrect', 0)), "#e74c3c")
            self.create_stat_card(row2, "🎯 Precisión", f"{accuracy:.1f}%", "#9b59b6")
            
            # Estadísticas por modo de juego
            modes_frame = tk.Frame(scrollable_frame, bg="#34495e", padx=20, pady=15)
            modes_frame.pack(fill="x", pady=(0, 20))
            
            tk.Label(
                modes_frame,
                text="🎲 Modos de Juego",
                font=("Arial", 18, "bold"),
                bg="#34495e",
                fg="#f1c40f"
            ).pack(pady=(0, 15))
            
            modes_grid = tk.Frame(modes_frame, bg="#34495e")
            modes_grid.pack(fill="x")
            
            self.create_mode_card(modes_grid, "🏛️ Clásico", user_stats.get('classic_games', 0), "#3498db")
            self.create_mode_card(modes_grid, "⏰ Contrarreloj", user_stats.get('timeattack_games', 0), "#e67e22")
            self.create_mode_card(modes_grid, "⚔️ Duelo", user_stats.get('duel_games', 0), "#e74c3c")
            
            # Victorias en duelos
            if user_stats.get('duel_games', 0) > 0:
                duel_stats_frame = tk.Frame(scrollable_frame, bg="#2c3e50", padx=20, pady=15)
                duel_stats_frame.pack(fill="x", pady=(0, 20))
                
                duel_victories = user_stats.get('duel_victories', 0)
                duel_games = user_stats.get('duel_games', 0)
                win_rate = (duel_victories / duel_games * 100) if duel_games > 0 else 0
                
                tk.Label(
                    duel_stats_frame,
                    text="⚔️ Estadísticas de Duelo",
                    font=("Arial", 18, "bold"),
                    bg="#2c3e50",
                    fg="#f1c40f"
                ).pack(pady=(0, 15))
                
                duel_grid = tk.Frame(duel_stats_frame, bg="#2c3e50")
                duel_grid.pack(fill="x")
                
                self.create_stat_card(duel_grid, "🏆 Victorias", str(duel_victories), "#2ecc71")
                self.create_stat_card(duel_grid, "📊 Porcentaje", f"{win_rate:.1f}%", "#f1c40f")
            
            # Categorías jugadas
            categories_played = user_stats.get('categories_played', [])
            if categories_played:
                categories_frame = tk.Frame(scrollable_frame, bg="#34495e", padx=20, pady=15)
                categories_frame.pack(fill="x", pady=(0, 20))
                
                tk.Label(
                    categories_frame,
                    text="📚 Categorías Jugadas",
                    font=("Arial", 18, "bold"),
                    bg="#34495e",
                    fg="#f1c40f"
                ).pack(pady=(0, 15))
                
                categories_text = ", ".join(categories_played)
                tk.Label(
                    categories_frame,
                    text=categories_text,
                    font=("Arial", 14),
                    bg="#34495e",
                    fg="#ecf0f1",
                    wraplength=600
                ).pack()
            
            # Última partida
            last_played = user_stats.get('last_played')
            if last_played:
                last_game_frame = tk.Frame(scrollable_frame, bg="#2c3e50", padx=20, pady=15)
                last_game_frame.pack(fill="x", pady=(0, 20))
                
                tk.Label(
                    last_game_frame,
                    text="🕒 Última Partida",
                    font=("Arial", 18, "bold"),
                    bg="#2c3e50",
                    fg="#f1c40f"
                ).pack(pady=(0, 10))
                
                # Formatear fecha
                try:
                    from datetime import datetime
                    last_date = datetime.fromisoformat(last_played.replace('Z', '+00:00'))
                    formatted_date = last_date.strftime("%d/%m/%Y a las %H:%M")
                    tk.Label(
                        last_game_frame,
                        text=formatted_date,
                        font=("Arial", 14),
                        bg="#2c3e50",
                        fg="#ecf0f1"
                    ).pack()
                except:
                    tk.Label(
                        last_game_frame,
                        text=last_played,
                        font=("Arial", 14),
                        bg="#2c3e50",
                        fg="#ecf0f1"
                    ).pack()
            
            # Configurar scroll
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Configurar scroll con mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        except Exception as e:
            print(f"Error cargando estadísticas: {e}")
            error_msg = "Error al cargar las estadísticas. Intenta de nuevo."
            tk.Label(main_container, text=error_msg, font=("Arial", 16), bg="#1a2a2e", fg="#e74c3c").pack(expand=True, pady=80)

    def iniciar_desempate_duelo(self, stats):
        """Inicia el desempate del duelo"""
        self.clear_main_frame()
        main_container = tk.Frame(self.main_frame, bg="#1a2a2e")
        main_container.pack(expand=True, fill="both", padx=40, pady=30)
        tk.Label(
            main_container,
            text="🤝 Desempate",
            font=("Helvetica", 36, "bold"),
            fg="#3498db",
            bg="#1a2a2e"
        ).pack(pady=(0, 30))
        results_frame = tk.Frame(main_container, bg="#2c3e50", padx=40, pady=30)
        results_frame.pack(fill="x")
        players_frame = tk.Frame(results_frame, bg="#2c3e50")
        players_frame.pack(fill="x", pady=20)
        def create_player_panel(username, correctas, incorrectas, puntos, is_winner):
            panel = tk.Frame(players_frame, bg="#2c3e50", padx=20)
            panel.pack(side="left", expand=True, fill="both")
            if is_winner:
                tk.Label(panel, text="👑", font=("Arial", 36), bg="#2c3e50", fg="#f1c40f").pack()
            tk.Label(panel, text=username, font=("Arial", 24, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=10)
            stats_frame = tk.Frame(panel, bg="#2c3e50")
            stats_frame.pack(fill="x", pady=10)
            tk.Label(stats_frame, text=f"✅ Correctas: {correctas}", font=("Arial", 16), bg="#2c3e50", fg="#2ecc71").pack(pady=5)
            tk.Label(stats_frame, text=f"❌ Incorrectas: {incorrectas}", font=("Arial", 16), bg="#2c3e50", fg="#e74c3c").pack(pady=5)
            tk.Label(panel, text=f"🎯 {puntos} puntos", font=("Arial", 20, "bold"), bg="#2c3e50", fg="#3498db").pack(pady=10)
        create_player_panel(stats['username1'], stats['correctas1'], stats['incorrectas1'], stats['puntos1'], True)
        create_player_panel(stats['username2'], stats['correctas2'], stats['incorrectas2'], stats['puntos2'], False)
        # Botón Volver al Menú
        volver_btn = tk.Button(
            main_container,
            text="🏠 Volver al Menú",
            font=("Arial", 14, "bold"),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            command=self.setup_main_menu
        )
        volver_btn.pack(pady=20)

    def create_stat_card(self, parent, title, value, color):
        """Crea una tarjeta de estadística individual"""
        card = tk.Frame(parent, bg="#34495e", relief="raised", bd=2, padx=15, pady=10)
        card.pack(side="left", expand=True, fill="both", padx=5)
        
        tk.Label(
            card,
            text=title,
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="#bdc3c7"
        ).pack()
        
        tk.Label(
            card,
            text=value,
            font=("Arial", 18, "bold"),
            bg="#34495e",
            fg=color
        ).pack()

    def create_mode_card(self, parent, mode_name, games_count, color):
        """Crea una tarjeta de modo de juego"""
        card = tk.Frame(parent, bg="#34495e", relief="raised", bd=2, padx=20, pady=15)
        card.pack(side="left", expand=True, fill="both", padx=5)
        
        tk.Label(
            card,
            text=mode_name,
            font=("Arial", 14, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        ).pack()
        
        tk.Label(
            card,
            text=str(games_count),
            font=("Arial", 24, "bold"),
            bg="#34495e",
            fg=color
        ).pack()
        
        tk.Label(
            card,
            text="partidas",
            font=("Arial", 10),
            bg="#34495e",
            fg="#95a5a6"
        ).pack()

    def create_achievement_card(self, parent, achievement, unlocked):
        """Crea una tarjeta de logro optimizada para grid 2x2"""
        card_frame = tk.Frame(parent, bg="#34495e", relief="raised", bd=2, width=280, height=180)
        card_frame.pack(side="left", fill="both", expand=True, pady=2, padx=2)
        card_frame.pack_propagate(False)  # Mantener tamaño fijo

        # Frame principal con padding
        main_frame = tk.Frame(card_frame, bg="#34495e")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header con icono y estado
        header_frame = tk.Frame(main_frame, bg="#34495e")
        header_frame.pack(fill="x", pady=(0, 8))

        # Icono del logro
        icon_label = tk.Label(
            header_frame,
            text=achievement.get('icon', '🏆'),
            font=("Arial", 24),
            bg="#34495e",
            fg=("#f1c40f" if unlocked else "#95a5a6")
        )
        icon_label.pack(side="left")

        # Estado del logro
        status_text = "✅" if unlocked else "🔒"
        status_label = tk.Label(
            header_frame,
            text=status_text,
            font=("Arial", 16),
            bg="#34495e",
            fg=("#2ecc71" if unlocked else "#e74c3c")
        )
        status_label.pack(side="right")

        # Título del logro
        title_label = tk.Label(
            main_frame,
            text=achievement.get('name', 'Logro'),
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg=("white" if unlocked else "#95a5a6"),
            wraplength=250
        )
        title_label.pack(pady=(0, 5))

        # Descripción del logro
        desc_label = tk.Label(
            main_frame,
            text=achievement.get('description', 'Descripción no disponible'),
            font=("Arial", 10),
            bg="#34495e",
            fg="#bdc3c7" if unlocked else "#7f8c8d",
            wraplength=250,
            justify="center"
        )
        desc_label.pack(pady=(0, 8))

        # Puntos de recompensa
        reward_points = achievement.get('reward_points', 0)
        if reward_points > 0:
            reward_label = tk.Label(
                main_frame,
                text=f"+{reward_points} puntos",
                font=("Arial", 11, "bold"),
                bg="#34495e",
                fg=("#2ecc71" if unlocked else "#95a5a6")
            )
            reward_label.pack()

        # Configurar colores según estado
        if not unlocked:
            card_frame.configure(bg="#2c3e50")
            main_frame.configure(bg="#2c3e50")
            header_frame.configure(bg="#2c3e50")

    def get_available_categories(self):
        """Obtiene la lista de categorías precargadas si existen, si no, consulta la API o usa los estilos"""
        if self.categorias_precargadas:
            return self.categorias_precargadas
        try:
            import requests
            response = requests.get('http://localhost:5000/api/categories', timeout=2)
            if response.status_code == 200:
                api_categories = response.json()
                if isinstance(api_categories, list):
                    return api_categories
        except Exception as e:
            print(f'[DEPURACIÓN] No se pudo obtener categorías desde la API: {e}')
        return list(self.category_styles.keys())

    def guardar_en_historial(self, stats):
        """Guarda los datos de la partida en el historial (data/game_history.json)"""
        try:
            import os, json
            historial_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'game_history.json')
            if os.path.exists(historial_file):
                with open(historial_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    data = []
            else:
                data = []
            # Agregar la nueva partida
            data.append(stats)
            with open(historial_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print('[DEPURACIÓN] Partida guardada en historial')
        except Exception as e:
            print(f'[ERROR] guardar_en_historial: {e}')

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    app = DesafioSaberApp(root)
    root.mainloop()