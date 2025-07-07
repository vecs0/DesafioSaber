#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de logros
"""

import json
import os
import sys

# Agregar el directorio del juego al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

def test_achievements_system():
    """Prueba el sistema completo de logros"""
    
    print("🏆 Iniciando pruebas del sistema de logros...")
    print("=" * 60)
    
    # Test 1: Verificar que se cargan todos los logros
    print("\n1️⃣ Verificando carga de logros...")
    
    try:
        with open('data/achievements.json', 'r', encoding='utf-8') as f:
            achievements_data = json.load(f)
            print(f"✅ Se cargaron {len(achievements_data)} logros desde el archivo")
            
            # Mostrar algunos logros
            print("\n📋 Logros disponibles:")
            for i, achievement in enumerate(achievements_data[:5], 1):
                print(f"   {i}. {achievement['name']} - {achievement['description']}")
            print(f"   ... y {len(achievements_data) - 5} más")
            
    except Exception as e:
        print(f"❌ Error cargando logros: {e}")
        return False
    
    # Test 2: Verificar tipos de condiciones soportadas
    print("\n2️⃣ Verificando tipos de condiciones...")
    
    condition_types = set()
    for achievement in achievements_data:
        condition_types.add(achievement['condition_type'])
    
    print(f"✅ Tipos de condiciones encontradas: {len(condition_types)}")
    print(f"   {', '.join(sorted(condition_types))}")
    
    # Test 3: Verificar que el archivo está protegido
    print("\n3️⃣ Verificando protección del archivo...")
    
    try:
        # Importar desde el archivo correcto
        import sys
        sys.path.append('game')
        from main import AchievementManager
        
        # Crear una instancia temporal para probar
        class MockApp:
            def show_achievement_popup(self, achievement):
                pass
        
        manager = AchievementManager(MockApp())
        
        # Verificar que no sobrescribe el archivo existente
        original_size = os.path.getsize('data/achievements.json')
        manager.create_default_achievements()
        new_size = os.path.getsize('data/achievements.json')
        
        if original_size == new_size:
            print("✅ Archivo protegido correctamente (no se sobrescribió)")
        else:
            print("❌ El archivo fue modificado")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de protección: {e}")
        return False
    
    # Test 4: Verificar estructura de logros
    print("\n4️⃣ Verificando estructura de logros...")
    
    required_fields = ['id', 'name', 'description', 'icon', 'condition_type', 'condition_value', 'reward_points']
    
    for achievement in achievements_data:
        missing_fields = [field for field in required_fields if field not in achievement]
        if missing_fields:
            print(f"❌ Logro '{achievement.get('name', 'Sin nombre')}' falta campos: {missing_fields}")
            return False
    
    print("✅ Todos los logros tienen la estructura correcta")
    
    # Test 5: Verificar nombres corregidos
    print("\n5️⃣ Verificando nombres corregidos...")
    
    speed_achievements = [a for a in achievements_data if 'velocidad' in a['name'].lower()]
    for achievement in speed_achievements:
        if 'demonio' in achievement['name'].lower():
            print(f"❌ Logro aún tiene 'Demonio': {achievement['name']}")
            return False
    
    print("✅ Nombres corregidos correctamente")
    
    print("\n🎉 ¡Todas las pruebas del sistema de logros pasaron!")
    print(f"📊 Total de logros disponibles: {len(achievements_data)}")
    print(f"🎯 Tipos de condiciones soportadas: {len(condition_types)}")
    
    return True

def show_achievements_summary():
    """Muestra un resumen de todos los logros disponibles"""
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN COMPLETO DE LOGROS")
    print("=" * 60)
    
    try:
        with open('data/achievements.json', 'r', encoding='utf-8') as f:
            achievements = json.load(f)
        
        # Agrupar por dificultad
        basic = []
        intermediate = []
        advanced = []
        
        for achievement in achievements:
            points = achievement['reward_points']
            if points <= 100:
                basic.append(achievement)
            elif points <= 300:
                intermediate.append(achievement)
            else:
                advanced.append(achievement)
        
        print(f"\n🥉 LOGROS BÁSICOS ({len(basic)}):")
        for achievement in basic:
            print(f"   {achievement['icon']} {achievement['name']} - {achievement['reward_points']} pts")
        
        print(f"\n🥈 LOGROS INTERMEDIOS ({len(intermediate)}):")
        for achievement in intermediate:
            print(f"   {achievement['icon']} {achievement['name']} - {achievement['reward_points']} pts")
        
        print(f"\n🥇 LOGROS AVANZADOS ({len(advanced)}):")
        for achievement in advanced:
            print(f"   {achievement['icon']} {achievement['name']} - {achievement['reward_points']} pts")
        
        total_points = sum(a['reward_points'] for a in achievements)
        print(f"\n💰 Total de puntos disponibles: {total_points}")
        
    except Exception as e:
        print(f"❌ Error mostrando resumen: {e}")

if __name__ == "__main__":
    success = test_achievements_system()
    if success:
        show_achievements_summary()
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.") 