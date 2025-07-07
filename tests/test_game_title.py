#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad del título del juego
"""

import requests
import json
import time
import os

def test_game_title():
    """Prueba la funcionalidad del título del juego"""
    print("🎮 Probando funcionalidad del título del juego...")
    print("=" * 50)
    
    # URLs de la API
    base_url = "http://localhost:5000/api"
    
    # 1. Verificar que el servidor esté funcionando
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
        else:
            print("❌ Servidor no responde correctamente")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False
    
    # 2. Obtener configuración actual
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            current_config = response.json()
            current_title = current_config.get('title', 'No definido')
            print(f"📋 Título actual: '{current_title}'")
        else:
            print("❌ Error obteniendo configuración")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 3. Cambiar el título del juego
    test_title = "DesafíoSaber - Prueba"
    try:
        new_config = {**current_config, 'title': test_title}
        response = requests.put(f"{base_url}/config", 
                              json=new_config,
                              headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"✅ Título cambiado a: '{test_title}'")
        else:
            print(f"❌ Error cambiando título: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 4. Verificar que el cambio se guardó
    time.sleep(1)  # Pequeña pausa para asegurar sincronización
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            updated_config = response.json()
            updated_title = updated_config.get('title', 'No definido')
            if updated_title == test_title:
                print(f"✅ Título actualizado correctamente: '{updated_title}'")
            else:
                print(f"❌ Título no se actualizó correctamente")
                print(f"   Esperado: '{test_title}'")
                print(f"   Obtenido: '{updated_title}'")
                return False
        else:
            print("❌ Error obteniendo configuración actualizada")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 5. Restaurar título original
    try:
        original_config = {**current_config, 'title': 'DesafíoSaber'}
        response = requests.put(f"{base_url}/config", 
                              json=original_config,
                              headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print("✅ Título restaurado a: 'DesafíoSaber'")
        else:
            print(f"❌ Error restaurando título: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 6. Verificar que el archivo config.json se actualizó
    try:
        config_file = "data/config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                file_title = file_config.get('title', 'No definido')
                if file_title == 'DesafíoSaber':
                    print("✅ Archivo config.json actualizado correctamente")
                else:
                    print(f"❌ Archivo config.json no se actualizó correctamente")
                    print(f"   Título en archivo: '{file_title}'")
                    return False
        else:
            print("⚠️ Archivo config.json no encontrado")
    except Exception as e:
        print(f"❌ Error verificando archivo: {e}")
        return False
    
    print("\n🎉 ¡Todas las pruebas del título del juego pasaron!")
    return True

def test_title_in_game():
    """Prueba que el juego pueda obtener el título desde la API"""
    print("\n🎮 Probando obtención del título desde el juego...")
    print("=" * 50)
    
    try:
        # Simular la llamada que hace el juego
        response = requests.get("http://localhost:5000/api/config")
        if response.status_code == 200:
            config = response.json()
            title = config.get('title', 'No definido')
            print(f"✅ Juego puede obtener título: '{title}'")
            
            # Verificar que el título coincide con el archivo
            config_file = "data/config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    file_title = file_config.get('title', 'No definido')
                if title == file_title:
                    print("✅ Título del juego coincide con el archivo")
                else:
                    print("❌ Título del juego NO coincide con el archivo")
                    print(f"   API: '{title}'")
                    print(f"   Archivo: '{file_title}'")
                    return False
            else:
                print("⚠️ Archivo config.json no encontrado")
        else:
            print(f"❌ Error obteniendo configuración: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del título del juego")
    print("=" * 60)
    
    # Verificar que el servidor esté ejecutándose
    print("📡 Verificando conexión al servidor...")
    
    success1 = test_game_title()
    success2 = test_title_in_game()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La funcionalidad del título del juego funciona correctamente")
        print("✅ El panel de administración y el juego están sincronizados")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️ Revisa los errores anteriores")
    
    print("\n💡 Para verificar manualmente:")
    print("   1. Abre el panel de administración: http://localhost:3000")
    print("   2. Ve a 'Configuración del Sistema'")
    print("   3. Cambia el 'Título del Juego'")
    print("   4. Haz clic en 'Guardar Título'")
    print("   5. Ejecuta el juego y verifica que el título cambió en la ventana")

if __name__ == "__main__":
    main() 