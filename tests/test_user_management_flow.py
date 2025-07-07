#!/usr/bin/env python3
"""
Test de Gestión de Usuarios y Administradores
Valida el flujo completo de creación, edición, eliminación y sincronización
de usuarios y administradores en el sistema.
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000/api"
USERS_FILE = "data/usuarios.json"
ADMINS_FILE = "data/admins.json"

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

def test_user_management_flow():
    """Test completo del flujo de gestión de usuarios"""
    
    print("🧪 INICIANDO TEST DE GESTIÓN DE USUARIOS Y ADMINS")
    print(f"📡 Conectando a: {BASE_URL}")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/players", timeout=5)
        if response.status_code != 200:
            print_error("Servidor no responde correctamente")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"No se puede conectar al servidor: {e}")
        return False
    
    print_success("Servidor conectado correctamente")
    
    # PASO 1: Crear usuarios de prueba
    print_step(1, "CREAR USUARIOS DE PRUEBA")
    
    test_users = [
        {
            "username": "test_user_1",
            "fullName": "Usuario Prueba 1",
            "password": "password123",
            "email": "test1@example.com"
        },
        {
            "username": "test_user_2", 
            "fullName": "Usuario Prueba 2",
            "password": "password456",
            "email": "test2@example.com"
        }
    ]
    
    created_users = []
    for user_data in test_users:
        try:
            response = requests.post(f"{BASE_URL}/players", json=user_data)
            if response.status_code == 201:
                user = response.json()['player']
                created_users.append(user)
                print_success(f"Usuario creado: {user['username']} (ID: {user['id']})")
            else:
                print_error(f"Error creando usuario {user_data['username']}: {response.text}")
                return False
        except Exception as e:
            print_error(f"Excepción creando usuario {user_data['username']}: {e}")
            return False
    
    # PASO 2: Verificar que los usuarios se crearon
    print_step(2, "VERIFICAR USUARIOS CREADOS")
    
    try:
        response = requests.get(f"{BASE_URL}/players")
        if response.status_code == 200:
            players = response.json()
            created_usernames = [u['username'] for u in created_users]
            found_users = [p for p in players if p['username'] in created_usernames]
            
            if len(found_users) == len(created_users):
                print_success(f"Se encontraron {len(found_users)} usuarios creados")
                for user in found_users:
                    print_info(f"  - {user['username']} (ID: {user['id']})")
            else:
                print_error(f"Faltan usuarios. Esperados: {len(created_users)}, Encontrados: {len(found_users)}")
                return False
        else:
            print_error(f"Error obteniendo usuarios: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción obteniendo usuarios: {e}")
        return False
    
    # PASO 3: Editar usuarios
    print_step(3, "EDITAR USUARIOS")
    
    if created_users:
        user_to_edit = created_users[0]
        update_data = {
            "fullName": "Usuario Prueba 1 - Editado",
            "email": "test1_edited@example.com",
            "newPassword": "newpassword123"
        }
        
        try:
            response = requests.put(f"{BASE_URL}/players/{user_to_edit['id']}", json=update_data)
            if response.status_code == 200:
                updated_user = response.json()['player']
                print_success(f"Usuario editado: {updated_user['username']}")
                print_info(f"  - Nombre actualizado: {updated_user['fullName']}")
                print_info(f"  - Email actualizado: {updated_user['email']}")
            else:
                print_error(f"Error editando usuario: {response.text}")
                return False
        except Exception as e:
            print_error(f"Excepción editando usuario: {e}")
            return False
    
    # PASO 4: Crear administradores
    print_step(4, "CREAR ADMINISTRADORES")
    
    test_admins = [
        {
            "username": "test_admin_1",
            "fullName": "Admin Prueba 1",
            "password": "admin123",
            "email": "admin1@example.com",
            "is_admin": True
        }
    ]
    
    created_admins = []
    for admin_data in test_admins:
        try:
            response = requests.post(f"{BASE_URL}/admin-users", json=admin_data)
            if response.status_code == 201:
                admin = response.json()['user']
                created_admins.append(admin)
                print_success(f"Admin creado: {admin['username']} (ID: {admin['id']})")
            else:
                print_error(f"Error creando admin {admin_data['username']}: {response.text}")
                return False
        except Exception as e:
            print_error(f"Excepción creando admin {admin_data['username']}: {e}")
            return False
    
    # PASO 5: Verificar administradores
    print_step(5, "VERIFICAR ADMINISTRADORES")
    
    try:
        response = requests.get(f"{BASE_URL}/admin-users")
        if response.status_code == 200:
            admins_data = response.json()
            admins = admins_data.get('users', [])
            created_admin_usernames = [a['username'] for a in created_admins]
            found_admins = [a for a in admins if a['username'] in created_admin_usernames]
            
            if len(found_admins) == len(created_admins):
                print_success(f"Se encontraron {len(found_admins)} administradores")
                for admin in found_admins:
                    print_info(f"  - {admin['username']} (ID: {admin['id']}) - Admin: {admin.get('is_admin', False)}")
            else:
                print_error(f"Faltan administradores. Esperados: {len(created_admins)}, Encontrados: {len(found_admins)}")
                return False
        else:
            print_error(f"Error obteniendo administradores: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción obteniendo administradores: {e}")
        return False
    
    # PASO 6: Verificar separación de usuarios y admins
    print_step(6, "VERIFICAR SEPARACIÓN DE USUARIOS Y ADMINS")
    
    try:
        # Obtener solo jugadores
        players_response = requests.get(f"{BASE_URL}/players")
        players = players_response.json() if players_response.status_code == 200 else []
        
        # Obtener solo admins
        admins_response = requests.get(f"{BASE_URL}/admin-users")
        admins_data = admins_response.json() if admins_response.status_code == 200 else {'users': []}
        admins = admins_data.get('users', [])
        
        # Verificar que no hay overlap
        player_usernames = {p['username'] for p in players}
        admin_usernames = {a['username'] for a in admins}
        overlap = player_usernames & admin_usernames
        
        if not overlap:
            print_success("Separación correcta: no hay usuarios duplicados entre players y admins")
            print_info(f"  - Jugadores: {len(players)}")
            print_info(f"  - Administradores: {len(admins)}")
        else:
            print_error(f"Usuarios duplicados encontrados: {overlap}")
            return False
            
    except Exception as e:
        print_error(f"Excepción verificando separación: {e}")
        return False
    
    # PASO 7: Verificar archivos JSON
    print_step(7, "VERIFICAR ARCHIVOS JSON")
    
    # Verificar archivo de usuarios
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            print_success(f"Archivo de usuarios cargado: {USERS_FILE}")
            print_info(f"  - Formato: {type(users_data).__name__}")
            if isinstance(users_data, dict):
                print_info(f"  - Usuarios en archivo: {len(users_data)}")
            elif isinstance(users_data, list):
                print_info(f"  - Usuarios en archivo: {len(users_data)}")
        except Exception as e:
            print_error(f"Error leyendo archivo de usuarios: {e}")
            return False
    else:
        print_error(f"Archivo de usuarios no encontrado: {USERS_FILE}")
        return False
    
    # Verificar archivo de admins
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
                admins_data = json.load(f)
            print_success(f"Archivo de admins cargado: {ADMINS_FILE}")
            print_info(f"  - Formato: {type(admins_data).__name__}")
            if isinstance(admins_data, dict):
                print_info(f"  - Admins en archivo: {len(admins_data)}")
            elif isinstance(admins_data, list):
                print_info(f"  - Admins en archivo: {len(admins_data)}")
        except Exception as e:
            print_error(f"Error leyendo archivo de admins: {e}")
            return False
    else:
        print_error(f"Archivo de admins no encontrado: {ADMINS_FILE}")
        return False
    
    # PASO 8: Limpiar datos de prueba
    print_step(8, "LIMPIAR DATOS DE PRUEBA")
    
    # Eliminar usuarios de prueba
    for user in created_users:
        try:
            response = requests.delete(f"{BASE_URL}/players/{user['id']}")
            if response.status_code == 200:
                print_success(f"Usuario eliminado: {user['username']}")
            else:
                print_error(f"Error eliminando usuario {user['username']}: {response.text}")
        except Exception as e:
            print_error(f"Excepción eliminando usuario {user['username']}: {e}")
    
    # Eliminar admins de prueba
    for admin in created_admins:
        try:
            response = requests.delete(f"{BASE_URL}/admin-users/{admin['id']}")
            if response.status_code == 200:
                print_success(f"Admin eliminado: {admin['username']}")
            else:
                print_error(f"Error eliminando admin {admin['username']}: {response.text}")
        except Exception as e:
            print_error(f"Excepción eliminando admin {admin['username']}: {e}")
    
    print_success("🧪 TEST DE GESTIÓN DE USUARIOS COMPLETADO EXITOSAMENTE")
    return True

if __name__ == "__main__":
    success = test_user_management_flow()
    sys.exit(0 if success else 1) 