#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de colores de categorías
"""

import requests
import json
import time
import os

def test_category_colors():
    """Prueba la funcionalidad de colores de categorías"""
    print("🎨 Probando funcionalidad de colores de categorías...")
    print("=" * 60)
    
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
    
    # 2. Obtener colores actuales de categorías
    try:
        response = requests.get(f"{base_url}/category-colors")
        if response.status_code == 200:
            current_colors = response.json()
            print(f"📋 Colores actuales cargados: {len(current_colors)} categorías")
            for category, colors in current_colors.items():
                print(f"   {category}: {colors.get('bg_color', 'N/A')}")
        else:
            print("❌ Error obteniendo colores de categorías")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 3. Cambiar el color de una categoría específica
    test_category = "Historia"
    test_color = "#ff6b6b"  # Color rojo claro
    
    try:
        response = requests.put(f"{base_url}/category-colors/{test_category}", 
                              json={"bg_color": test_color},
                              headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"✅ Color de {test_category} cambiado a: {test_color}")
        else:
            print(f"❌ Error cambiando color: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 4. Verificar que el cambio se guardó
    time.sleep(1)  # Pequeña pausa para asegurar sincronización
    try:
        response = requests.get(f"{base_url}/category-colors")
        if response.status_code == 200:
            updated_colors = response.json()
            if test_category in updated_colors and updated_colors[test_category].get('bg_color') == test_color:
                print(f"✅ Color actualizado correctamente: {test_color}")
            else:
                print(f"❌ Color no se actualizó correctamente")
                print(f"   Esperado: {test_color}")
                print(f"   Obtenido: {updated_colors.get(test_category, {}).get('bg_color', 'N/A')}")
                return False
        else:
            print("❌ Error obteniendo colores actualizados")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 5. Restaurar color original
    original_color = "#2c3e50"
    try:
        response = requests.put(f"{base_url}/category-colors/{test_category}", 
                              json={"bg_color": original_color},
                              headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"✅ Color de {test_category} restaurado a: {original_color}")
        else:
            print(f"❌ Error restaurando color: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 6. Verificar que el archivo category_colors.json se actualizó
    try:
        colors_file = "data/category_colors.json"
        if os.path.exists(colors_file):
            with open(colors_file, 'r', encoding='utf-8') as f:
                file_colors = json.load(f)
                if test_category in file_colors and file_colors[test_category].get('bg_color') == original_color:
                    print("✅ Archivo category_colors.json actualizado correctamente")
                else:
                    print(f"❌ Archivo category_colors.json no se actualizó correctamente")
                    print(f"   Color en archivo: {file_colors.get(test_category, {}).get('bg_color', 'N/A')}")
                    return False
        else:
            print("⚠️ Archivo category_colors.json no encontrado")
    except Exception as e:
        print(f"❌ Error verificando archivo: {e}")
        return False
    
    print("\n🎉 ¡Todas las pruebas de colores de categorías pasaron!")
    return True

def test_colors_in_game():
    """Prueba que el juego pueda obtener los colores desde la API"""
    print("\n🎮 Probando obtención de colores desde el juego...")
    print("=" * 60)
    
    try:
        # Simular la llamada que hace el juego
        response = requests.get("http://localhost:5000/api/category-colors")
        if response.status_code == 200:
            colors = response.json()
            print(f"✅ Juego puede obtener colores: {len(colors)} categorías")
            
            # Verificar que los colores coinciden con el archivo
            colors_file = "data/category_colors.json"
            if os.path.exists(colors_file):
                with open(colors_file, 'r', encoding='utf-8') as f:
                    file_colors = json.load(f)
                if colors == file_colors:
                    print("✅ Colores del juego coinciden con el archivo")
                else:
                    print("❌ Colores del juego NO coinciden con el archivo")
                    return False
            else:
                print("⚠️ Archivo category_colors.json no encontrado")
        else:
            print(f"❌ Error obteniendo colores: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_visual_editor_integration():
    """Prueba la integración con el Editor Visual"""
    print("\n🎨 Probando integración con Editor Visual...")
    print("=" * 60)
    
    try:
        # Verificar que el endpoint funciona para el Editor Visual
        response = requests.get("http://localhost:5000/api/category-colors")
        if response.status_code == 200:
            colors = response.json()
            
            # Simular cambio desde el Editor Visual
            test_category = "Ciencia"
            test_color = "#00ff88"  # Color verde brillante
            
            response = requests.put(f"http://localhost:5000/api/category-colors/{test_category}", 
                                  json={"bg_color": test_color},
                                  headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                print(f"✅ Editor Visual puede cambiar color de {test_category}")
                
                # Verificar que el cambio se aplicó
                response = requests.get("http://localhost:5000/api/category-colors")
                if response.status_code == 200:
                    updated_colors = response.json()
                    if updated_colors.get(test_category, {}).get('bg_color') == test_color:
                        print("✅ Cambio desde Editor Visual aplicado correctamente")
                        
                        # Restaurar color original
                        original_color = "#27ae60"
                        requests.put(f"http://localhost:5000/api/category-colors/{test_category}", 
                                   json={"bg_color": original_color},
                                   headers={"Content-Type": "application/json"})
                        print("✅ Color restaurado")
                    else:
                        print("❌ Cambio desde Editor Visual no se aplicó")
                        return False
                else:
                    print("❌ Error verificando cambio desde Editor Visual")
                    return False
            else:
                print(f"❌ Editor Visual no puede cambiar colores: {response.status_code}")
                return False
        else:
            print(f"❌ Error obteniendo colores para Editor Visual: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de colores de categorías")
    print("=" * 80)
    
    # Verificar que el servidor esté ejecutándose
    print("📡 Verificando conexión al servidor...")
    
    success1 = test_category_colors()
    success2 = test_colors_in_game()
    success3 = test_visual_editor_integration()
    
    print("\n" + "=" * 80)
    if success1 and success2 and success3:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La funcionalidad de colores de categorías funciona correctamente")
        print("✅ El Editor Visual y el juego están sincronizados")
        print("✅ Los cambios se reflejan en tiempo real")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️ Revisa los errores anteriores")
    
    print("\n💡 Para verificar manualmente:")
    print("   1. Abre el panel de administración: http://localhost:3000")
    print("   2. Ve a 'Editor Visual'")
    print("   3. Selecciona una categoría en 'Fondo por Categoría'")
    print("   4. Cambia el color y verifica la vista previa")
    print("   5. Ejecuta el juego y verifica que el color cambió")
    print("   6. Los cambios se aplican en tiempo real sin reiniciar")

if __name__ == "__main__":
    main() 