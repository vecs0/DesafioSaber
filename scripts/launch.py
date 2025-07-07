#!/usr/bin/env python3
"""
Lanzador automático del sistema DesafíoSaber
Ejecuta la verificación y luego inicia el sistema
"""

import os
import sys
import subprocess

def main():
    print("🎮 Iniciando DesafíoSaber...")
    
    # Ejecutar verificación
    try:
        subprocess.run([sys.executable, 'fix_system.py'], check=True)
        print("✅ Verificación completada")
    except subprocess.CalledProcessError:
        print("❌ Error en la verificación")
        return
    
    # Preguntar qué iniciar
    print("\n¿Qué quieres iniciar?")
    print("1. Panel de administración")
    print("2. Juego")
    print("3. Ambos")
    
    choice = input("Selecciona una opción (1-3): ").strip()
    
    if choice == "1":
        print("🌐 Iniciando panel de administración...")
        subprocess.run([sys.executable, 'start_system.py'])
    elif choice == "2":
        print("🎮 Iniciando juego...")
        subprocess.run([sys.executable, 'game/main.py'])
    elif choice == "3":
        print("🚀 Iniciando sistema completo...")
        subprocess.run([sys.executable, 'start_system.py'])
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
