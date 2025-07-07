#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión entre el juego y el panel de administración
"""

import requests
import json
import time

def test_api_connection():
    """Prueba la conexión con la API del panel de administración"""
    print("🧪 Probando conexión con el panel de administración...")
    
    try:
        # Probar endpoint de jugadores
        response = requests.get("http://localhost:5000/api/players", timeout=5)
        if response.status_code == 200:
            players = response.json()
            print(f"✅ Jugadores cargados: {len(players)}")
            for player in players:
                print(f"   - {player.get('username', 'N/A')} ({player.get('fullName', 'N/A')})")
        else:
            print(f"❌ Error cargando jugadores: {response.status_code}")
            return False
        
        # Probar endpoint de ranking
        response = requests.get("http://localhost:5000/api/ranking", timeout=5)
        if response.status_code == 200:
            ranking = response.json()
            rankings_list = ranking.get('rankings', []) if isinstance(ranking, dict) else ranking
            print(f"✅ Ranking cargado: {len(rankings_list)} entradas")
        else:
            print(f"❌ Error cargando ranking: {response.status_code}")
            return False
        
        # Probar endpoint de configuración
        response = requests.get("http://localhost:5000/api/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Configuración cargada")
        else:
            print(f"❌ Error cargando configuración: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. Asegúrate de que el panel esté ejecutándose.")
        return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_user_registration():
    """Prueba el registro de un usuario de prueba"""
    print("\n🧪 Probando registro de usuario...")
    
    test_user = {
        'username': 'test_user',
        'fullName': 'Usuario de Prueba',
        'password': 'test123',
        'email': 'test@example.com',
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'last_login': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'stats': {
            'total_games': 0,
            'total_score': 0,
            'best_score': 0,
            'favorite_mode': '',
            'favorite_category': ''
        },
        'score': 0,
        'mode': '',
        'categoria': '',
        'correctas': 0,
        'incorrectas': 0,
        'tiempo': 0
    }
    
    try:
        response = requests.post("http://localhost:5000/api/players", json=test_user, timeout=5)
        if response.status_code == 201:
            print("✅ Usuario de prueba registrado correctamente")
            return True
        else:
            print(f"❌ Error registrando usuario: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return False

def test_user_update():
    """Prueba la actualización de un usuario"""
    print("\n🧪 Probando actualización de usuario...")
    
    try:
        # Obtener usuarios
        response = requests.get("http://localhost:5000/api/players", timeout=5)
        if response.status_code == 200:
            players = response.json()
            if players:
                # Actualizar el primer usuario
                player = players[0]
                update_data = {
                    'fullName': f"{player.get('fullName', '')} (Actualizado)",
                    'stats': {
                        'total_games': 5,
                        'total_score': 1000,
                        'best_score': 500
                    }
                }
                
                response = requests.put(f"http://localhost:5000/api/players/{player['id']}", 
                                      json=update_data, timeout=5)
                if response.status_code == 200:
                    print("✅ Usuario actualizado correctamente")
                    return True
                else:
                    print(f"❌ Error actualizando usuario: {response.status_code}")
                    return False
            else:
                print("⚠️ No hay usuarios para actualizar")
                return True
        else:
            print(f"❌ Error obteniendo usuarios: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en actualización: {e}")
        return False

def main():
    print("🎮 Prueba de Conexión - DesafíoSaber")
    print("=" * 50)
    
    # Probar conexión básica
    if not test_api_connection():
        print("\n❌ Falló la prueba de conexión básica")
        return
    
    # Probar registro de usuario
    if not test_user_registration():
        print("\n❌ Falló la prueba de registro")
        return
    
    # Probar actualización de usuario
    if not test_user_update():
        print("\n❌ Falló la prueba de actualización")
        return
    
    print("\n🎉 ¡Todas las pruebas pasaron!")
    print("✅ El panel de administración está funcionando correctamente")
    print("✅ La sincronización entre juego y panel está operativa")

if __name__ == "__main__":
    main() 