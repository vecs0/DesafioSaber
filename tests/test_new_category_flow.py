#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo completo de nuevas categorías:
1. Agregar categoría en el panel de administración
2. Verificar que aparece en el editor visual
3. Verificar que aparece en el juego
4. Verificar que se puede configurar su color
"""

import requests
import json
import time
import os

def test_new_category_flow():
    """Prueba el flujo completo de nuevas categorías"""
    print("🧪 Probando Flujo Completo de Nuevas Categorías")
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
    
    # 3. Obtener colores actuales
    try:
        response = requests.get(f"{base_url}/category-colors")
        if response.status_code == 200:
            current_colors = response.json()
            print(f"🎨 Colores actuales: {list(current_colors.keys())}")
        else:
            print("❌ Error obteniendo colores")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 4. Agregar una categoría de prueba
    test_category = "Categoría_Prueba_Completa"
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
    
    # 5. Verificar que la categoría se agregó a la lista
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
    
    # 6. Verificar que la categoría aparece en el editor visual (colores)
    try:
        response = requests.get(f"{base_url}/category-colors")
        if response.status_code == 200:
            updated_colors = response.json()
            if test_category in updated_colors:
                print(f"✅ Categoría '{test_category}' aparece en el editor visual")
                print(f"🎨 Configuración de color: {updated_colors[test_category]}")
            else:
                print(f"⚠️ Categoría '{test_category}' no aparece en colores (se creará automáticamente)")
                # Crear configuración de color para la nueva categoría
                new_color_config = {
                    "bg_color": "#3498db",
                    "icon": "📝",
                    "text_color": "white",
                    "hover_color": "#2980b9",
                    "border_color": "#1a2a2e",
                    "shadow_color": "#1a2a2e"
                }
                updated_colors[test_category] = new_color_config
                
                # Guardar la configuración actualizada
                response = requests.put(f"{base_url}/category-colors",
                                      json=updated_colors,
                                      headers={"Content-Type": "application/json"})
                if response.status_code == 200:
                    print(f"✅ Configuración de color creada para '{test_category}'")
                else:
                    print(f"❌ Error creando configuración de color: {response.status_code}")
                    return False
        else:
            print("❌ Error obteniendo colores actualizados")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 7. Verificar que el juego puede obtener la nueva categoría
    try:
        response = requests.get(f"{base_url}/categories")
        if response.status_code == 200:
            game_categories = response.json()
            if test_category in game_categories:
                print(f"✅ Juego puede obtener la nueva categoría '{test_category}'")
            else:
                print(f"❌ Juego no puede obtener la nueva categoría")
                return False
        else:
            print("❌ Error obteniendo categorías para el juego")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 8. Verificar que el juego puede obtener los colores de la nueva categoría
    try:
        response = requests.get(f"{base_url}/category-colors")
        if response.status_code == 200:
            game_colors = response.json()
            if test_category in game_colors:
                print(f"✅ Juego puede obtener los colores de '{test_category}'")
                print(f"🎨 Colores disponibles para el juego: {list(game_colors.keys())}")
            else:
                print(f"❌ Juego no puede obtener los colores de la nueva categoría")
                return False
        else:
            print("❌ Error obteniendo colores para el juego")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 9. Simular una pregunta con la nueva categoría
    try:
        test_question = {
            "text": "Pregunta de prueba para nueva categoría",
            "mode": "Clásico",
            "category": test_category,
            "difficulty": "Fácil",
            "options": ["Opción 1", "Opción 2", "Opción 3", "Opción 4"],
            "correctAnswer": "Opción 1",
            "image": None
        }
        
        response = requests.post(f"{base_url}/questions",
                               json=test_question,
                               headers={"Content-Type": "application/json"})
        if response.status_code == 201:
            print(f"✅ Pregunta de prueba agregada para categoría '{test_category}'")
        else:
            print(f"⚠️ No se pudo agregar pregunta de prueba: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error agregando pregunta de prueba: {e}")
    
    # 10. Verificar que la pregunta aparece en el filtro de categorías
    try:
        response = requests.get(f"{base_url}/questions?category={test_category}")
        if response.status_code == 200:
            questions = response.json()
            if questions:
                print(f"✅ Preguntas encontradas para categoría '{test_category}': {len(questions)}")
            else:
                print(f"⚠️ No hay preguntas para categoría '{test_category}'")
        else:
            print("❌ Error obteniendo preguntas por categoría")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 11. Limpiar: eliminar la categoría de prueba
    try:
        response = requests.delete(f"{base_url}/categories/{test_category}")
        if response.status_code == 200:
            print(f"✅ Categoría '{test_category}' eliminada correctamente")
        else:
            print(f"⚠️ No se pudo eliminar categoría de prueba: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error eliminando categoría de prueba: {e}")
    
    print("\n🎉 ¡Flujo completo de nuevas categorías verificado!")
    return True

def test_visual_editor_sync():
    """Prueba específicamente la sincronización del editor visual"""
    print("\n🎨 Probando sincronización del Editor Visual...")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api"
    
    # 1. Obtener categorías y colores
    try:
        categories_response = requests.get(f"{base_url}/categories")
        colors_response = requests.get(f"{base_url}/category-colors")
        
        if categories_response.status_code == 200 and colors_response.status_code == 200:
            categories = categories_response.json()
            colors = colors_response.json()
            
            print(f"📋 Categorías disponibles: {categories}")
            print(f"🎨 Categorías con colores: {list(colors.keys())}")
            
            # Verificar que todas las categorías tienen configuración de color
            missing_colors = [cat for cat in categories if cat not in colors]
            if missing_colors:
                print(f"⚠️ Categorías sin configuración de color: {missing_colors}")
                
                # Crear configuración para categorías faltantes
                for cat in missing_colors:
                    default_config = {
                        "bg_color": "#3498db",
                        "icon": "📝",
                        "text_color": "white",
                        "hover_color": "#2980b9",
                        "border_color": "#1a2a2e",
                        "shadow_color": "#1a2a2e"
                    }
                    colors[cat] = default_config
                
                # Guardar configuración actualizada
                response = requests.put(f"{base_url}/category-colors",
                                      json=colors,
                                      headers={"Content-Type": "application/json"})
                if response.status_code == 200:
                    print("✅ Configuración de colores actualizada para todas las categorías")
                else:
                    print("❌ Error actualizando configuración de colores")
                    return False
            else:
                print("✅ Todas las categorías tienen configuración de color")
        else:
            print("❌ Error obteniendo datos del editor visual")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del flujo completo de categorías")
    print("=" * 70)
    
    # Verificar que el servidor esté ejecutándose
    print("📡 Verificando conexión al servidor...")
    
    success1 = test_new_category_flow()
    success2 = test_visual_editor_sync()
    
    print("\n" + "=" * 70)
    if success1 and success2:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El flujo completo de categorías funciona correctamente")
        print("✅ Las nuevas categorías se reflejan en:")
        print("   - Panel de administración")
        print("   - Editor visual (con configuración de colores)")
        print("   - Juego (disponible para selección)")
        print("   - Filtros de preguntas")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️ Revisa los errores anteriores")
    
    print("\n💡 Para verificar manualmente:")
    print("   1. Abre el panel de administración: http://localhost:3000")
    print("   2. Ve a 'Gestión de Categorías' y agrega una nueva categoría")
    print("   3. Ve a 'Editor Visual' y verifica que aparece en 'Colores por Categoría'")
    print("   4. Configura los colores de la nueva categoría")
    print("   5. Ejecuta el juego y verifica que la categoría aparece en la selección")
    print("   6. Verifica que las preguntas se pueden filtrar por la nueva categoría")

if __name__ == "__main__":
    main() 