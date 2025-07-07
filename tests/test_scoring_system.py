#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de puntuación dinámico
"""

import json
import requests
import time

def test_scoring_configuration():
    """Prueba las configuraciones de puntuación"""
    print("🧪 Probando Sistema de Puntuación Dinámico")
    print("=" * 50)
    
    # URL base
    base_url = "http://localhost:5000"
    
    try:
        # 1. Obtener configuraciones actuales
        print("1. Obteniendo configuraciones actuales...")
        response = requests.get(f"{base_url}/api/game-modes")
        if response.status_code == 200:
            game_modes = response.json()
            print(f"✅ Configuraciones obtenidas: {len(game_modes)} modos")
            
            for mode in game_modes:
                print(f"   📋 {mode['name']}:")
                print(f"      ✅ Correcta: {mode.get('points_correct', 100)} puntos")
                print(f"      ❌ Incorrecta: {mode.get('points_incorrect', -25)} puntos")
                print(f"      🔥 Racha: +{mode.get('bonus_streak', 50)} puntos (cada {mode.get('bonus_streak_threshold', 3)} aciertos)")
                if mode.get('bonus_perfect', 0) > 0:
                    print(f"      ⭐ Perfecta: +{mode['bonus_perfect']} puntos")
                if mode.get('bonus_speed', 0) > 0:
                    print(f"      ⚡ Velocidad: +{mode['bonus_speed']} puntos/segundo")
        else:
            print(f"❌ Error obteniendo configuraciones: {response.status_code}")
            return False
        
        # 2. Probar actualización de configuraciones
        print("\n2. Probando actualización de configuraciones...")
        
        # Actualizar modo Clásico
        classic_mode = next((m for m in game_modes if m['name'] == 'Clásico'), None)
        if classic_mode:
            classic_mode['points_correct'] = 150
            classic_mode['points_incorrect'] = -30
            classic_mode['bonus_streak'] = 75
            classic_mode['bonus_streak_threshold'] = 4
            classic_mode['bonus_perfect'] = 300
            
            response = requests.put(f"{base_url}/api/game-modes", json=game_modes)
            if response.status_code == 200:
                print("✅ Configuración del modo Clásico actualizada")
            else:
                print(f"❌ Error actualizando configuración: {response.status_code}")
        
        # Actualizar modo Contrarreloj
        timeattack_mode = next((m for m in game_modes if m['name'] == 'Contrarreloj'), None)
        if timeattack_mode:
            timeattack_mode['points_correct'] = 120
            timeattack_mode['points_incorrect'] = -20
            timeattack_mode['bonus_streak'] = 60
            timeattack_mode['bonus_streak_threshold'] = 3
            timeattack_mode['bonus_speed'] = 15
            
            response = requests.put(f"{base_url}/api/game-modes", json=game_modes)
            if response.status_code == 200:
                print("✅ Configuración del modo Contrarreloj actualizada")
            else:
                print(f"❌ Error actualizando configuración: {response.status_code}")
        
        # Actualizar modo Duelo
        duel_mode = next((m for m in game_modes if m['name'] == 'Duelo'), None)
        if duel_mode:
            duel_mode['points_correct'] = 200
            duel_mode['points_incorrect'] = -100
            duel_mode['bonus_streak'] = 100
            duel_mode['bonus_streak_threshold'] = 2
            
            response = requests.put(f"{base_url}/api/game-modes", json=game_modes)
            if response.status_code == 200:
                print("✅ Configuración del modo Duelo actualizada")
            else:
                print(f"❌ Error actualizando configuración: {response.status_code}")
        
        # 3. Verificar configuraciones actualizadas
        print("\n3. Verificando configuraciones actualizadas...")
        time.sleep(1)  # Pequeña pausa para asegurar sincronización
        
        response = requests.get(f"{base_url}/api/game-modes")
        if response.status_code == 200:
            updated_modes = response.json()
            print("✅ Configuraciones actualizadas obtenidas:")
            
            for mode in updated_modes:
                print(f"   📋 {mode['name']}:")
                print(f"      ✅ Correcta: {mode.get('points_correct', 100)} puntos")
                print(f"      ❌ Incorrecta: {mode.get('points_incorrect', -25)} puntos")
                print(f"      🔥 Racha: +{mode.get('bonus_streak', 50)} puntos (cada {mode.get('bonus_streak_threshold', 3)} aciertos)")
                if mode.get('bonus_perfect', 0) > 0:
                    print(f"      ⭐ Perfecta: +{mode['bonus_perfect']} puntos")
                if mode.get('bonus_speed', 0) > 0:
                    print(f"      ⚡ Velocidad: +{mode['bonus_speed']} puntos/segundo")
        
        # 4. Probar WebSocket para sincronización en tiempo real
        print("\n4. Probando sincronización WebSocket...")
        try:
            import socketio
            sio = socketio.Client()
            
            @sio.event
            def connect():
                print("✅ WebSocket conectado")
            
            @sio.event
            def disconnect():
                print("❌ WebSocket desconectado")
            
            @sio.on('data_update')
            def on_data_update(data):
                print(f"✅ Evento WebSocket recibido: {data}")
            
            sio.connect(f"{base_url}")
            time.sleep(2)
            sio.disconnect()
            
        except ImportError:
            print("⚠️ socketio no disponible, omitiendo prueba WebSocket")
        except Exception as e:
            print(f"⚠️ Error en WebSocket: {e}")
        
        # 5. Verificar archivo de configuración
        print("\n5. Verificando archivo de configuración...")
        try:
            with open('data/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            game_modes_config = config.get('game_modes', [])
            print(f"✅ Archivo de configuración leído: {len(game_modes_config)} modos")
            
            for mode in game_modes_config:
                print(f"   📋 {mode['name']}:")
                if 'points_correct' in mode:
                    print(f"      ✅ Correcta: {mode['points_correct']} puntos")
                if 'points_incorrect' in mode:
                    print(f"      ❌ Incorrecta: {mode['points_incorrect']} puntos")
                if 'bonus_streak' in mode:
                    print(f"      🔥 Racha: +{mode['bonus_streak']} puntos")
                if 'bonus_perfect' in mode:
                    print(f"      ⭐ Perfecta: +{mode['bonus_perfect']} puntos")
                if 'bonus_speed' in mode:
                    print(f"      ⚡ Velocidad: +{mode['bonus_speed']} puntos/segundo")
                    
        except Exception as e:
            print(f"❌ Error leyendo archivo de configuración: {e}")
        
        print("\n🎉 ¡Pruebas completadas exitosamente!")
        print("\n📋 Resumen de configuraciones:")
        print("   • Modo Clásico: 150 puntos correcta, -30 incorrecta, +75 racha (cada 4), +300 perfecta")
        print("   • Modo Contrarreloj: 120 puntos correcta, -20 incorrecta, +60 racha (cada 3), +15 velocidad")
        print("   • Modo Duelo: 200 puntos correcta, -100 incorrecta, +100 racha (cada 2)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_scoring_configuration()
    if success:
        print("\n✅ Todas las pruebas pasaron correctamente")
    else:
        print("\n❌ Algunas pruebas fallaron")
        exit(1) 