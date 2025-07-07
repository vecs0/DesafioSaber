#!/usr/bin/env python3
"""
Script de prueba para verificar que el editor visual puede cargar todos los datos
"""

import requests
import json
import sys

# Configuración
API_BASE_URL = "http://localhost:5000/api"

def test_visual_editor_data():
    """Prueba que todos los datos necesarios para el editor visual estén disponibles"""
    print("🎨 Probando datos del Editor Visual...")
    
    # Test 1: Categorías
    print("\n1. Probando endpoint de categorías...")
    try:
        response = requests.get(f"{API_BASE_URL}/categories", timeout=5)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categorías obtenidas: {categories}")
            if not categories:
                print("⚠️ No hay categorías disponibles")
                return False
        else:
            print(f"❌ Error obteniendo categorías: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Test 2: Colores de categorías
    print("\n2. Probando endpoint de colores de categorías...")
    try:
        response = requests.get(f"{API_BASE_URL}/category-colors", timeout=5)
        if response.status_code == 200:
            colors = response.json()
            print(f"✅ Colores obtenidos para {len(colors)} categorías")
            if not colors:
                print("⚠️ No hay colores de categorías disponibles")
                return False
        else:
            print(f"❌ Error obteniendo colores: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Test 3: Estilos de botones
    print("\n3. Probando endpoint de estilos de botones...")
    try:
        response = requests.get(f"{API_BASE_URL}/button-styles", timeout=5)
        if response.status_code == 200:
            styles = response.json()
            print(f"✅ Estilos de botones obtenidos: {json.dumps(styles, indent=2)}")
            required_fields = [
                'button_shape', 'button_color', 'button_text_color', 
                'button_hover_color', 'button_border_width', 'button_relief',
                'button_font', 'button_font_size', 'button_font_weight'
            ]
            missing_fields = [field for field in required_fields if field not in styles]
            if missing_fields:
                print(f"❌ Campos faltantes en estilos: {missing_fields}")
                return False
        else:
            print(f"❌ Error obteniendo estilos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Test 4: Verificar CORS headers
    print("\n4. Verificando headers CORS...")
    try:
        response = requests.get(f"{API_BASE_URL}/categories", timeout=5)
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Headers', 
            'Access-Control-Allow-Methods'
        ]
        missing_cors = [header for header in cors_headers if header not in response.headers]
        if missing_cors:
            print(f"❌ Headers CORS faltantes: {missing_cors}")
            return False
        else:
            print("✅ Headers CORS configurados correctamente")
    except Exception as e:
        print(f"❌ Error verificando CORS: {e}")
        return False
    
    return True

def test_frontend_compatibility():
    """Prueba la compatibilidad con el frontend"""
    print("\n🌐 Probando compatibilidad con frontend...")
    
    # Simular peticiones desde el frontend
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000'
    }
    
    # Test 1: Petición GET desde frontend
    try:
        response = requests.get(f"{API_BASE_URL}/categories", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Petición GET desde frontend exitosa")
        else:
            print(f"❌ Error en petición GET: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en petición GET: {e}")
        return False
    
    # Test 2: Petición PUT desde frontend (simular actualización)
    try:
        test_data = {
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
        response = requests.put(f"{API_BASE_URL}/button-styles", 
                              json=test_data, 
                              headers=headers, 
                              timeout=5)
        if response.status_code == 200:
            print("✅ Petición PUT desde frontend exitosa")
        else:
            print(f"❌ Error en petición PUT: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en petición PUT: {e}")
        return False
    
    return True

def main():
    """Función principal de pruebas"""
    print("🎨 Pruebas del Editor Visual - DesafíoSaber")
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
        ("Datos del Editor Visual", test_visual_editor_data),
        ("Compatibilidad con Frontend", test_frontend_compatibility)
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
        print("🎉 ¡Todas las pruebas pasaron! El editor visual debería funcionar correctamente.")
        print("\n💡 Si sigues viendo errores en el navegador:")
        print("   1. Limpia la caché del navegador (Ctrl+F5)")
        print("   2. Verifica que no haya errores en la consola del navegador")
        print("   3. Asegúrate de que el panel de administración esté corriendo")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 