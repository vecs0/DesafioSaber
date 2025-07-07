import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
import uuid
from datetime import datetime
import requests
import threading

class UserRegistration:
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.users_file = 'data/usuarios.json'
        self.api_url = "http://localhost:5000/api"
        
    def show_registration_dialog(self):
        """Muestra el diálogo de registro de usuario moderno"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Registro de Usuario - DesafíoSaber")
        self.dialog.geometry("450x650")
        self.dialog.minsize(450, 650)
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.configure(bg="#1a2a2e")

        # Frame principal para todo el contenido
        main_frame = tk.Frame(self.dialog, bg="#1a2a2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header con título
        header_frame = tk.Frame(main_frame, bg="#2c3e50", height=120)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Título centrado
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(
            title_frame,
            text="📝",
            font=("Arial", 32),
            bg="#2c3e50",
            fg="#3498db"
        ).pack()
        
        tk.Label(
            title_frame,
            text="Registro de Usuario",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack()

        # Frame de campos - EXACTAMENTE IGUAL AL LOGIN
        fields_frame = tk.Frame(main_frame, bg="#1a2a2e")
        fields_frame.pack(fill="both", expand=True)

        # Información - EXACTAMENTE IGUAL AL LOGIN
        info_label = tk.Label(
            fields_frame,
            text="Crea tu cuenta para guardar tu progreso y sincronizar tus datos en la nube.",
            font=("Arial", 11),
            wraplength=400,
            justify="center",
            bg="#1a2a2e",
            fg="#95a5a6"
        )
        info_label.pack(pady=(0, 30))

        # Nombre completo
        tk.Label(
            fields_frame,
            text="Nombre completo:",
            font=("Arial", 12, "bold"),
            bg="#1a2a2e",
            fg="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.fullname_var = tk.StringVar()
        self.fullname_entry = tk.Entry(
            fields_frame,
            textvariable=self.fullname_var,
            font=("Arial", 12),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.fullname_entry.pack(fill="x", pady=(0, 15), ipady=8, ipadx=10)

        # Nombre de usuario
        tk.Label(
            fields_frame,
            text="Nombre de usuario:",
            font=("Arial", 12, "bold"),
            bg="#1a2a2e",
            fg="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            fields_frame,
            textvariable=self.username_var,
            font=("Arial", 12),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.username_entry.pack(fill="x", pady=(0, 15), ipady=8, ipadx=10)

        # Contraseña
        tk.Label(
            fields_frame,
            text="Contraseña:",
            font=("Arial", 12, "bold"),
            bg="#1a2a2e",
            fg="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            fields_frame,
            textvariable=self.password_var,
            show="•",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.password_entry.pack(fill="x", pady=(0, 15), ipady=8, ipadx=10)

        # Confirmar contraseña
        tk.Label(
            fields_frame,
            text="Confirmar contraseña:",
            font=("Arial", 12, "bold"),
            bg="#1a2a2e",
            fg="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = tk.Entry(
            fields_frame,
            textvariable=self.confirm_password_var,
            show="•",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 15), ipady=8, ipadx=10)

        # Email (opcional)
        tk.Label(
            fields_frame,
            text="Email (opcional):",
            font=("Arial", 12, "bold"),
            bg="#1a2a2e",
            fg="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(
            fields_frame,
            textvariable=self.email_var,
            font=("Arial", 12),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.email_entry.pack(fill="x", pady=(0, 30), ipady=8, ipadx=10)

        # Información adicional
        info_text = "ℹ️ Tu cuenta se sincronizará automáticamente y podrás ver tus estadísticas en cualquier dispositivo."
        info_label2 = tk.Label(
            fields_frame,
            text=info_text,
            justify="center",
            wraplength=400,
            bg="#1a2a2e",
            fg="#95a5a6",
            font=("Arial", 10)
        )
        info_label2.pack(pady=(20, 0))

        # --- BLOQUE DE BOTONES SIEMPRE VISIBLE AL FINAL ---
        # Elimina cualquier otro pack/grid/place de botones previos si existiera
        for widget in main_frame.pack_slaves():
            if isinstance(widget, tk.Frame) and widget != fields_frame:
                widget.destroy()
        buttons_frame = tk.Frame(main_frame, bg="#1a2a2e", height=80)
        buttons_frame.pack(side="bottom", fill="x", pady=(20, 0))
        buttons_frame.pack_propagate(False)

        reg_btn = tk.Button(
            buttons_frame,
            text="📝 REGISTRAR",
            font=("Arial", 14, "bold"),
            bg="#2ecc71",
            fg="white",
            bd=0,
            relief="flat",
            command=self.register_user,
            cursor="hand2",
            height=2
        )
        reg_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

        cancel_btn = tk.Button(
            buttons_frame,
            text="❌ CANCELAR",
            font=("Arial", 14, "bold"),
            bg="#e74c3c",
            fg="white",
            bd=0,
            relief="flat",
            command=self.dialog.destroy,
            cursor="hand2",
            height=2
        )
        cancel_btn.pack(side="left", expand=True, fill="x", padx=(10, 0))
        # --- FIN BLOQUE DE BOTONES ---

        # Enfoque en el primer campo
        self.fullname_entry.focus()

        # CENTRAR la ventana después de empacar todo
        self.dialog.update_idletasks()
        w = self.dialog.winfo_width()
        h = self.dialog.winfo_height()
        ws = self.dialog.winfo_screenwidth()
        hs = self.dialog.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        self.dialog.lift()
        self.dialog.focus_force()
        
    def register_user(self):
        """Registra un nuevo usuario"""
        # Validaciones
        if not self.validate_fields():
            return
            
        # Crear usuario
        user_data = {
            "id": self.generate_user_id(),
            "fullName": self.fullname_var.get().strip(),
            "username": self.username_var.get().strip().lower(),
            "password": self.hash_password(self.password_var.get()),
            "email": self.email_var.get().strip() if self.email_var.get().strip() else None,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "stats": {
                "total_games": 0,
                "total_score": 0,
                "best_score": 0,
                "favorite_mode": None,
                "favorite_category": None
            }
        }
        
        # Guardar localmente
        if self.save_user_locally(user_data):
            # Sincronizar con servidor (en segundo plano)
            threading.Thread(target=self.sync_to_server, args=(user_data,), daemon=True).start()
            
            messagebox.showinfo("Éxito", f"¡Usuario {user_data['username']} registrado correctamente!\n\nTu cuenta se sincronizará automáticamente.")
            
            if self.callback:
                self.callback(user_data['username'])
                
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "No se pudo registrar el usuario. Inténtalo de nuevo.")
    
    def validate_fields(self):
        """Valida los campos del formulario"""
        # Campos requeridos
        if not self.fullname_var.get().strip():
            messagebox.showerror("Error", "El nombre completo es obligatorio.")
            self.fullname_entry.focus()
            return False
            
        if not self.username_var.get().strip():
            messagebox.showerror("Error", "El nombre de usuario es obligatorio.")
            self.username_entry.focus()
            return False
            
        if not self.password_var.get():
            messagebox.showerror("Error", "La contraseña es obligatoria.")
            self.password_entry.focus()
            return False
            
        # Validar contraseñas
        if self.password_var.get() != self.confirm_password_var.get():
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            self.password_entry.focus()
            return False
            
        if len(self.password_var.get()) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres.")
            self.password_entry.focus()
            return False
            
        # Validar nombre de usuario
        username = self.username_var.get().strip().lower()
        if len(username) < 3:
            messagebox.showerror("Error", "El nombre de usuario debe tener al menos 3 caracteres.")
            self.username_entry.focus()
            return False
            
        if not username.replace('_', '').replace('-', '').isalnum():
            messagebox.showerror("Error", "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.")
            self.username_entry.focus()
            return False
            
        # Verificar si el usuario ya existe
        if self.user_exists(username):
            messagebox.showerror("Error", "El nombre de usuario ya está en uso.")
            self.username_entry.focus()
            return False
            
        return True
    
    def user_exists(self, username):
        """Verifica si un usuario ya existe"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Manejar tanto listas como diccionarios
                    if isinstance(loaded_data, list):
                        return any(user.get('username', '').lower() == username.lower() for user in loaded_data)
                    elif isinstance(loaded_data, dict):
                        return username.lower() in [user.get('username', '').lower() for user in loaded_data.values()]
        except Exception:
            pass
        return False
    
    def generate_user_id(self):
        """Genera un ID único para el usuario"""
        return str(uuid.uuid4())
    
    def hash_password(self, password):
        """Encripta la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def save_user_locally(self, user_data):
        """Guarda el usuario en el archivo local"""
        try:
            users = {}
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, list):
                        for user in loaded_data:
                            users[user['username']] = user
                    elif isinstance(loaded_data, dict):
                        users = loaded_data
            users[user_data['username']] = user_data
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando usuario: {e}")
            return False
    
    def sync_to_server(self, user_data):
        """Sincroniza el usuario con el servidor"""
        try:
            # Preparar datos para el servidor
            server_data = {
                'username': user_data['username'],
                'fullName': user_data['fullName'],
                'password': user_data['password'],
                'email': user_data['email'],
                'created_at': user_data['created_at'],
                'last_login': user_data['last_login'],
                'stats': user_data['stats'],
                'score': 0,
                'mode': '',
                'categoria': '',
                'correctas': 0,
                'incorrectas': 0,
                'tiempo': 0
            }
            
            # Enviar al servidor
            response = requests.post(f"{self.api_url}/players", json=server_data, timeout=5)
            if response.status_code == 201:
                print(f"Usuario {user_data['username']} sincronizado con el servidor")
                return True
            else:
                print(f"Error sincronizando usuario: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error de conexión al sincronizar: {e}")
            return False

class UserLogin:
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.users_file = 'data/usuarios.json'
        
    def show_login_dialog(self):
        """Muestra el diálogo de inicio de sesión moderno"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Iniciar Sesión - DesafíoSaber")
        self.dialog.geometry("450x500")
        self.dialog.minsize(450, 500)
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.configure(bg="#1a2a2e")

        # Frame principal para todo el contenido
        main_frame = tk.Frame(self.dialog, bg="#1a2a2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header con título
        header_frame = tk.Frame(main_frame, bg="#2c3e50", height=120)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Título centrado
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(
            title_frame,
            text="👤",
            font=("Arial", 32),
            bg="#2c3e50",
            fg="#3498db"
        ).pack()
        
        tk.Label(
            title_frame,
            text="Iniciar Sesión",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack()

        # Frame de campos
        fields_frame = tk.Frame(main_frame, bg="#1a2a2e")
        fields_frame.pack(fill="both", expand=True)

        # Información
        info_label = tk.Label(
            fields_frame,
            text="Ingresa tus credenciales para acceder a tu cuenta y sincronizar tus datos.",
            font=("Arial", 11),
            wraplength=400,
            justify="center",
            bg="#1a2a2e",
            fg="#95a5a6"
        )
        info_label.pack(pady=(0, 30))

        # Usuario
        tk.Label(
            fields_frame,
            text="Usuario:",
            font=("Arial", 12, "bold"),
            bg="#1a2a2e",
            fg="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            fields_frame,
            textvariable=self.username_var,
            font=("Arial", 12),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.username_entry.pack(fill="x", pady=(0, 20), ipady=8, ipadx=10)

        # Contraseña
        tk.Label(
            fields_frame,
            text="Contraseña:",
            font=("Arial", 12, "bold"),
            bg="#1a2a2e",
            fg="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            fields_frame,
            textvariable=self.password_var,
            show="•",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0
        )
        self.password_entry.pack(fill="x", pady=(0, 30), ipady=8, ipadx=10)

        # Frame de botones - SIEMPRE AL FINAL
        buttons_frame = tk.Frame(main_frame, bg="#1a2a2e", height=80)
        buttons_frame.pack(side="bottom", fill="x", pady=(20, 0))
        buttons_frame.pack_propagate(False)

        # Botón iniciar sesión
        login_btn = tk.Button(
            buttons_frame,
            text="🔓 INICIAR SESIÓN",
            font=("Arial", 14, "bold"),
            bg="#2ecc71",
            fg="white",
            bd=0,
            relief="flat",
            command=self.login_user,
            cursor="hand2",
            height=2
        )
        login_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

        # Botón cancelar
        cancel_btn = tk.Button(
            buttons_frame,
            text="❌ CANCELAR",
            font=("Arial", 14, "bold"),
            bg="#e74c3c",
            fg="white",
            bd=0,
            relief="flat",
            command=self.dialog.destroy,
            cursor="hand2",
            height=2
        )
        cancel_btn.pack(side="left", expand=True, fill="x", padx=(10, 0))

        # Enfoque en el primer campo
        self.username_entry.focus()

        # CENTRAR la ventana después de empacar todo
        self.dialog.update_idletasks()
        w = self.dialog.winfo_width()
        h = self.dialog.winfo_height()
        ws = self.dialog.winfo_screenwidth()
        hs = self.dialog.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        self.dialog.lift()
        self.dialog.focus_force()
        
    def login_user(self):
        """Autentica al usuario"""
        username = self.username_var.get().strip().lower()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor completa todos los campos.")
            return
            
        # Verificar credenciales
        user = self.authenticate_user(username, password)
        if user:
            # Actualizar último login
            self.update_last_login(user['username'])
            
            messagebox.showinfo("Éxito", f"¡Bienvenido de vuelta, {user['fullName']}!")
            
            if self.callback:
                self.callback(user['username'])
                
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            self.password_entry.focus()
    
    def authenticate_user(self, username, password):
        """Autentica las credenciales del usuario"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                # Manejar tanto listas como diccionarios
                if isinstance(loaded_data, list):
                    users = loaded_data
                elif isinstance(loaded_data, dict):
                    users = list(loaded_data.values())
                else:
                    return None
                
                for user in users:
                    if (user.get('username', '').lower() == username and 
                        user.get('password') == hashed_password):
                        return user
        except Exception as e:
            print(f"Error autenticando usuario: {e}")
        return None
    
    def update_last_login(self, username):
        """Actualiza la fecha del último login"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
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
                        user['last_login'] = datetime.now().isoformat()
                        # Sincronizar con servidor
                        self.sync_login_to_server(user)
                        break
                
                # Guardar en el formato correcto
                if is_dict_format:
                    users_dict = {}
                    for u in users:
                        users_dict[u['username']] = u
                    with open(self.users_file, 'w', encoding='utf-8') as f:
                        json.dump(users_dict, f, ensure_ascii=False, indent=2)
                else:
                    with open(self.users_file, 'w', encoding='utf-8') as f:
                        json.dump(users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error actualizando último login: {e}")
    
    def sync_login_to_server(self, user_data):
        """Sincroniza el login con el servidor"""
        try:
            api_url = "http://localhost:5000/api"
            # Buscar el usuario en el servidor y actualizar último login
            response = requests.get(f"{api_url}/players")
            if response.status_code == 200:
                players = response.json()
                for player in players:
                    if player.get('username', '').lower() == user_data['username'].lower():
                        # Actualizar último login
                        update_data = {
                            'last_login': user_data['last_login']
                        }
                        requests.put(f"{api_url}/players/{player['id']}", json=update_data, timeout=5)
                        print(f"Login de {user_data['username']} sincronizado con el servidor")
                        break
        except Exception as e:
            print(f"Error sincronizando login: {e}") 