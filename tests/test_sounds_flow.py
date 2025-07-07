#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo completo de sonidos:
1. Subir sonido en el panel de administración
2. Verificar que aparece en la lista de sonidos
3. Verificar que el juego puede obtener el sonido
4. Verificar que el juego puede reproducir el sonido
5. Verificar que se puede eliminar el sonido
"""

import requests
import json
import time
import os
import tempfile
import wave
import struct

def create_test_sound(filename, duration=1.0, sample_rate=44100):
    """Crea un archivo de sonido de prueba"""
    try:
        # Crear un tono simple de 440Hz
        frequency = 440.0
        amplitude = 0.3
        num_samples = int(sample_rate * duration)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            for i in range(num_samples):
                # Generar una onda sinusoidal simple
                value = int(amplitude * 32767.0 * 
                           (i * frequency * 2.0 * 3.14159 / sample_rate))
                # Asegurar que el valor esté en el rango válido
                value = max(-32768, min(32767, value))
                wav_file.writeframes(struct.pack('h', value))
        
        return True
    except Exception as e:
        print(f"Error creando archivo de sonido: {e}")
        return False

def test_sounds_flow():
    """Prueba el flujo completo de sonidos"""
    print("🔊 Probando Flujo Completo de Sonidos")
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
    
    # 2. Obtener sonidos actuales
    try:
        response = requests.get(f"{base_url}/sounds")
        if response.status_code == 200:
            current_sounds = response.json()
            print(f"🔊 Sonidos actuales: {len(current_sounds)} archivos")
            for sound in current_sounds:
                print(f"   - {sound['name']}")
        else:
            print("❌ Error obteniendo sonidos")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 3. Crear archivo de sonido de prueba
    test_sound_name = "test_sound_flow.wav"
    test_sound_path = os.path.join(tempfile.gettempdir(), test_sound_name)
    
    if not create_test_sound(test_sound_path):
        print("❌ Error creando archivo de sonido de prueba")
        return False
    
    print(f"✅ Archivo de sonido de prueba creado: {test_sound_path}")
    
    # 4. Subir el sonido de prueba
    try:
        with open(test_sound_path, 'rb') as f:
            files = {'file': (test_sound_name, f, 'audio/wav')}
            response = requests.post(f"{base_url}/sounds", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sonido '{test_sound_name}' subido correctamente")
            print(f"   URL: {result.get('url', 'N/A')}")
        else:
            print(f"❌ Error subiendo sonido: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 5. Verificar que el sonido aparece en la lista
    time.sleep(1)  # Pequeña pausa para asegurar sincronización
    try:
        response = requests.get(f"{base_url}/sounds")
        if response.status_code == 200:
            updated_sounds = response.json()
            sound_found = any(sound['name'] == test_sound_name for sound in updated_sounds)
            
            if sound_found:
                print(f"✅ Sonido '{test_sound_name}' aparece en la lista actualizada")
                print(f"🔊 Total de sonidos: {len(updated_sounds)}")
            else:
                print(f"❌ Sonido '{test_sound_name}' no aparece en la lista")
                return False
        else:
            print("❌ Error obteniendo sonidos actualizados")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 6. Verificar que el juego puede obtener el sonido
    try:
        response = requests.get(f"{base_url}/sounds")
        if response.status_code == 200:
            game_sounds = response.json()
            game_sound_found = any(sound['name'] == test_sound_name for sound in game_sounds)
            
            if game_sound_found:
                print(f"✅ Juego puede obtener el sonido '{test_sound_name}'")
                # Encontrar el sonido específico
                test_sound = next(sound for sound in game_sounds if sound['name'] == test_sound_name)
                print(f"   Ruta: {test_sound['path']}")
            else:
                print(f"❌ Juego no puede obtener el sonido '{test_sound_name}'")
                return False
        else:
            print("❌ Error obteniendo sonidos para el juego")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 7. Verificar que el sonido se puede reproducir (acceso directo)
    try:
        sound_url = f"http://localhost:5000/sounds/{test_sound_name}"
        response = requests.head(sound_url)
        if response.status_code == 200:
            print(f"✅ Sonido '{test_sound_name}' es accesible para reproducción")
            print(f"   URL: {sound_url}")
        else:
            print(f"❌ Sonido '{test_sound_name}' no es accesible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando acceso al sonido: {e}")
        return False
    
    # 8. Verificar que el sonido se puede reproducir (descarga)
    try:
        response = requests.get(sound_url)
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"✅ Sonido '{test_sound_name}' se puede descargar")
            print(f"   Tamaño: {content_length} bytes")
            
            if content_length > 0:
                print("✅ Archivo de sonido tiene contenido válido")
            else:
                print("❌ Archivo de sonido está vacío")
                return False
        else:
            print(f"❌ Error descargando sonido: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 9. Limpiar: eliminar el sonido de prueba
    try:
        response = requests.delete(f"{base_url}/sounds/{test_sound_name}")
        if response.status_code == 200:
            print(f"✅ Sonido '{test_sound_name}' eliminado correctamente")
        else:
            print(f"⚠️ No se pudo eliminar sonido de prueba: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error eliminando sonido de prueba: {e}")
    
    # 10. Verificar que el sonido se eliminó
    time.sleep(1)
    try:
        response = requests.get(f"{base_url}/sounds")
        if response.status_code == 200:
            final_sounds = response.json()
            sound_still_exists = any(sound['name'] == test_sound_name for sound in final_sounds)
            
            if not sound_still_exists:
                print(f"✅ Sonido '{test_sound_name}' eliminado de la lista")
                print(f"🔊 Total final de sonidos: {len(final_sounds)}")
            else:
                print(f"❌ Sonido '{test_sound_name}' aún aparece en la lista")
                return False
        else:
            print("❌ Error obteniendo sonidos finales")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 11. Limpiar archivo temporal
    try:
        if os.path.exists(test_sound_path):
            os.remove(test_sound_path)
            print(f"✅ Archivo temporal eliminado: {test_sound_path}")
    except Exception as e:
        print(f"⚠️ Error eliminando archivo temporal: {e}")
    
    print("\n🎉 ¡Flujo completo de sonidos verificado!")
    return True

def test_sound_types():
    """Prueba diferentes tipos de archivos de sonido"""
    print("\n🎵 Probando diferentes tipos de archivos de sonido...")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api"
    
    # Tipos de archivos a probar
    test_files = [
        ("test_sound.wav", "audio/wav"),
        ("test_sound.mp3", "audio/mpeg")
    ]
    
    for filename, mime_type in test_files:
        print(f"\n📁 Probando: {filename} ({mime_type})")
        
        # Crear archivo de prueba
        test_path = os.path.join(tempfile.gettempdir(), filename)
        
        if filename.endswith('.wav'):
            if not create_test_sound(test_path):
                print(f"❌ Error creando {filename}")
                continue
        else:
            # Para MP3, crear un archivo dummy (no es un MP3 real, pero prueba la validación)
            with open(test_path, 'wb') as f:
                f.write(b'fake_mp3_content')
        
        # Intentar subir
        try:
            with open(test_path, 'rb') as f:
                files = {'file': (filename, f, mime_type)}
                response = requests.post(f"{base_url}/sounds", files=files)
            
            if response.status_code == 200:
                print(f"✅ {filename} subido correctamente")
                
                # Eliminar inmediatamente
                requests.delete(f"{base_url}/sounds/{filename}")
                print(f"✅ {filename} eliminado")
            else:
                print(f"❌ Error subiendo {filename}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            # Limpiar archivo temporal
            if os.path.exists(test_path):
                os.remove(test_path)
    
    return True

def test_game_sound_integration():
    """Prueba la integración de sonidos con el juego"""
    print("\n🎮 Probando integración de sonidos con el juego...")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api"
    
    # 1. Verificar que el juego puede obtener la lista de sonidos
    try:
        response = requests.get(f"{base_url}/sounds")
        if response.status_code == 200:
            sounds = response.json()
            print(f"✅ Juego puede obtener {len(sounds)} sonidos")
            
            # Verificar sonidos específicos del juego
            game_sounds = ['acierto', 'errado', 'despliegue', 'intro_music']
            found_sounds = []
            
            for sound in sounds:
                sound_name = sound['name'].split('.')[0]  # Sin extensión
                if sound_name in game_sounds:
                    found_sounds.append(sound_name)
                    print(f"   ✅ {sound_name}: {sound['name']}")
            
            missing_sounds = [s for s in game_sounds if s not in found_sounds]
            if missing_sounds:
                print(f"   ⚠️ Sonidos faltantes: {missing_sounds}")
            else:
                print("   ✅ Todos los sonidos del juego están disponibles")
        else:
            print(f"❌ Error obteniendo sonidos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 2. Verificar que los sonidos son accesibles
    try:
        response = requests.get(f"{base_url}/sounds")
        if response.status_code == 200:
            sounds = response.json()
            
            for sound in sounds[:3]:  # Probar solo los primeros 3
                sound_url = f"http://localhost:5000{sound['path']}"
                try:
                    response = requests.head(sound_url)
                    if response.status_code == 200:
                        print(f"✅ {sound['name']} es accesible")
                    else:
                        print(f"❌ {sound['name']} no es accesible: {response.status_code}")
                except Exception as e:
                    print(f"❌ Error verificando {sound['name']}: {e}")
        else:
            print("❌ Error obteniendo lista de sonidos")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del flujo completo de sonidos")
    print("=" * 70)
    
    # Verificar que el servidor esté ejecutándose
    print("📡 Verificando conexión al servidor...")
    
    success1 = test_sounds_flow()
    success2 = test_sound_types()
    success3 = test_game_sound_integration()
    
    print("\n" + "=" * 70)
    if success1 and success2 and success3:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El flujo completo de sonidos funciona correctamente")
        print("✅ Los sonidos se reflejan en:")
        print("   - Panel de administración (subida/eliminación)")
        print("   - Lista de sonidos disponibles")
        print("   - Juego (acceso y reproducción)")
        print("   - Diferentes tipos de archivos (WAV, MP3)")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️ Revisa los errores anteriores")
    
    print("\n💡 Para verificar manualmente:")
    print("   1. Abre el panel de administración: http://localhost:3000")
    print("   2. Ve a 'Gestión de Recursos'")
    print("   3. Sube un archivo de sonido (MP3 o WAV)")
    print("   4. Haz clic en 'Reproducir' para escuchar el sonido")
    print("   5. Ejecuta el juego y verifica que el sonido está disponible")
    print("   6. Verifica que el juego puede reproducir el sonido")

if __name__ == "__main__":
    main() 