#!/usr/bin/env python3
"""
Script de prueba para verificar la sincronización de categorías
entre el panel de administración y el juego
"""

import requests
import json
import time
import os

def test_categories_sync():
    """Prueba la sincronización de categorías"""
    print("🧪 Probando sincronización de categorías...")
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
    
    # 2. Obtener categorías actuales
    try:
        response = requests.get(f"{base_url}/categories")
        if response.status_code == 200:
            current_categories = response.json()
            print(f"📋 Categorías actuales: {current_categories}")
        else:
            print("❌ Error obteniendo categorías")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 3. Agregar una categoría de prueba
    test_category = "Categoría_Prueba_Sync"
    try:
        response = requests.post(f"{base_url}/categories", 
                               json={"name": test_category},
                               headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"✅ Categoría '{test_category}' agregada correctamente")
        else:
            print(f"❌ Error agregando categoría: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 4. Verificar que la categoría se agregó
    time.sleep(1)  # Pequeña pausa para asegurar sincronización
    try:
        response = requests.get(f"{base_url}/categories")
        if response.status_code == 200:
            updated_categories = response.json()
            if test_category in updated_categories:
                print(f"✅ Categoría '{test_category}' aparece en la lista actualizada")
                print(f"📋 Categorías actualizadas: {updated_categories}")
            else:
                print(f"❌ Categoría '{test_category}' no aparece en la lista")
                return False
        else:
            print("❌ Error obteniendo categorías actualizadas")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 5. Eliminar la categoría de prueba
    try:
        response = requests.delete(f"{base_url}/categories/{test_category}")
        if response.status_code == 200:
            print(f"✅ Categoría '{test_category}' eliminada correctamente")
        else:
            print(f"❌ Error eliminando categoría: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 6. Verificar que la categoría se eliminó
    time.sleep(1)
    try:
        response = requests.get(f"{base_url}/categories")
        if response.status_code == 200:
            final_categories = response.json()
            if test_category not in final_categories:
                print(f"✅ Categoría '{test_category}' eliminada de la lista")
                print(f"📋 Categorías finales: {final_categories}")
            else:
                print(f"❌ Categoría '{test_category}' aún aparece en la lista")
                return False
        else:
            print("❌ Error obteniendo categorías finales")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n🎉 ¡Todas las pruebas de sincronización pasaron!")
    return True

def test_game_categories():
    """Prueba que el juego pueda obtener las categorías"""
    print("\n🎮 Probando obtención de categorías desde el juego...")
    print("=" * 50)
    
    try:
        # Simular la llamada que hace el juego
        response = requests.get("http://localhost:5000/api/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Juego puede obtener categorías: {categories}")
            
            # Verificar que las categorías coinciden con el archivo
            categories_file = "data/categories.json"
            if os.path.exists(categories_file):
                with open(categories_file, 'r', encoding='utf-8') as f:
                    file_categories = json.load(f)
                if categories == file_categories:
                    print("✅ Categorías del juego coinciden con el archivo")
                else:
                    print("❌ Categorías del juego NO coinciden con el archivo")
                    print(f"   Archivo: {file_categories}")
                    print(f"   API: {categories}")
                    return False
            else:
                print("⚠️ Archivo categories.json no encontrado")
        else:
            print(f"❌ Error obteniendo categorías: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de sincronización de categorías")
    print("=" * 60)
    
    # Verificar que el servidor esté ejecutándose
    print("📡 Verificando conexión al servidor...")
    
    success1 = test_categories_sync()
    success2 = test_game_categories()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La sincronización de categorías funciona correctamente")
        print("✅ El panel de administración y el juego están sincronizados")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️ Revisa los errores anteriores")
    
    print("\n💡 Para verificar manualmente:")
    print("   1. Abre el panel de administración: http://localhost:3000")
    print("   2. Ve a 'Gestión de Categorías'")
    print("   3. Agrega una nueva categoría")
    print("   4. Ve a 'Editor Visual' y verifica que aparece en 'Fondo por Categoría'")
    print("   5. Ejecuta el juego y verifica que la categoría aparece")

if __name__ == "__main__":
    main() 