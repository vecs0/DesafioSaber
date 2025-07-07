#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de estilos de botones
"""

import requests
import json
import time
import sys
import os

# Configuración
API_BASE_URL = "http://localhost:5000/api"
BUTTON_STYLES_FILE = "data/button_styles.json"

def test_button_styles_api():
    """Prueba los endpoints de estilos de botones"""
    print("🧪 Probando API de estilos de botones...")
    
    # Test 1: Obtener estilos de botones
    print("\n1. Obteniendo estilos de botones...")
    try:
        response = requests.get(f"{API_BASE_URL}/button-styles", timeout=5)
        if response.status_code == 200:
            styles = response.json()
            print(f"✅ Estilos obtenidos: {json.dumps(styles, indent=2)}")
        else:
            print(f"❌ Error obteniendo estilos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Test 2: Actualizar estilos de botones
    print("\n2. Actualizando estilos de botones...")
    new_styles = {
        "button_shape": "rounded-full",
        "button_color": "#ff6b6b",
        "button_text_color": "white",
        "button_hover_color": "#ee5a52",
        "button_border_width": 2,
        "button_relief": "raised",
        "button_font": "Arial",
        "button_font_size": 16,
        "button_font_weight": "bold"
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/button-styles",
            json=new_styles,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Estilos actualizados: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error actualizando estilos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Test 3: Verificar que los cambios se guardaron
    print("\n3. Verificando cambios guardados...")
    time.sleep(1)  # Pequeña pausa para asegurar que se guardó
    try:
        response = requests.get(f"{API_BASE_URL}/button-styles", timeout=5)
        if response.status_code == 200:
            updated_styles = response.json()
            if updated_styles.get('button_shape') == 'rounded-full' and updated_styles.get('button_color') == '#ff6b6b':
                print("✅ Cambios verificados correctamente")
            else:
                print("❌ Los cambios no se aplicaron correctamente")
                return False
        else:
            print(f"❌ Error verificando cambios: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Test 4: Restaurar estilos originales
    print("\n4. Restaurando estilos originales...")
    original_styles = {
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
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/button-styles",
            json=original_styles,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Estilos originales restaurados")
        else:
            print(f"❌ Error restaurando estilos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    return True

def test_websocket_notifications():
    """Prueba las notificaciones WebSocket"""
    print("\n🔌 Probando notificaciones WebSocket...")
    
    try:
        import socketio
        sio = socketio.Client()
        
        notification_received = False
        
        @sio.event
        def connect():
            print("✅ Conectado al WebSocket")
        
        @sio.on('data_update')
        def on_data_update(data):
            nonlocal notification_received
            if data.get('type') == 'button_styles':
                print("✅ Notificación WebSocket recibida para estilos de botones")
                notification_received = True
        
        # Conectar al WebSocket
        sio.connect('http://localhost:5000')
        
        # Cambiar estilos para trigger notificación
        test_styles = {
            "button_shape": "rounded-none",
            "button_color": "#9b59b6",
            "button_text_color": "white",
            "button_hover_color": "#8e44ad",
            "button_border_width": 1,
            "button_relief": "sunken",
            "button_font": "Arial",
            "button_font_size": 12,
            "button_font_weight": "normal"
        }
        
        response = requests.put(
            f"{API_BASE_URL}/button-styles",
            json=test_styles,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        # Esperar notificación
        time.sleep(2)
        
        if notification_received:
            print("✅ Notificación WebSocket funcionando correctamente")
        else:
            print("⚠️ No se recibió notificación WebSocket")
        
        # Restaurar estilos
        original_styles = {
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
        
        requests.put(
            f"{API_BASE_URL}/button-styles",
            json=original_styles,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        sio.disconnect()
        return notification_received
        
    except ImportError:
        print("⚠️ socketio-client no disponible, saltando prueba WebSocket")
        return True
    except Exception as e:
        print(f"❌ Error en prueba WebSocket: {e}")
        return False

def test_file_integrity():
    """Prueba la integridad del archivo de estilos"""
    print("\n📁 Probando integridad del archivo...")
    
    if not os.path.exists(BUTTON_STYLES_FILE):
        print(f"❌ Archivo {BUTTON_STYLES_FILE} no existe")
        return False
    
    try:
        with open(BUTTON_STYLES_FILE, 'r', encoding='utf-8') as f:
            styles = json.load(f)
        
        required_fields = [
            'button_shape', 'button_color', 'button_text_color', 
            'button_hover_color', 'button_border_width', 'button_relief',
            'button_font', 'button_font_size', 'button_font_weight'
        ]
        
        missing_fields = [field for field in required_fields if field not in styles]
        
        if missing_fields:
            print(f"❌ Campos faltantes: {missing_fields}")
            return False
        else:
            print("✅ Archivo de estilos válido")
            return True
            
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🎮 Pruebas de Estilos de Botones - DesafíoSaber")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{API_BASE_URL}/categories", timeout=5)
        if response.status_code != 200:
            print("❌ El servidor no está respondiendo correctamente")
            print("   Asegúrate de que el servidor esté corriendo en http://localhost:5000")
            return False
    except Exception as e:
        print("❌ No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:5000")
        return False
    
    # Ejecutar pruebas
    tests = [
        ("API de estilos de botones", test_button_styles_api),
        ("Notificaciones WebSocket", test_websocket_notifications),
        ("Integridad del archivo", test_file_integrity)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en prueba {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print(f"\n{'='*50}")
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! Los estilos de botones funcionan correctamente.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 