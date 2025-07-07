#!/usr/bin/env python3
"""
Test de Sistema de Backup y Restauración
Valida la creación, verificación y restauración de backups
de todos los archivos críticos del sistema.
"""

import requests
import json
import time
import os
import sys
import shutil
import zipfile
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000/api"
BACKUP_DIR = "backups"
DATA_DIR = "data"

def print_step(step, description):
    print(f"\n{'='*60}")
    print(f"PASO {step}: {description}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def create_backup():
    """Crear un backup completo del sistema"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    # Crear directorio de backup
    os.makedirs(backup_path, exist_ok=True)
    
    # Archivos críticos a respaldar
    critical_files = [
        "data/questions.json",
        "data/categories.json", 
        "data/usuarios.json",
        "data/admins.json",
        "data/ranking.json",
        "data/config.json",
        "data/game_history.json",
        "data/user_stats.json",
        "data/achievements.json",
        "data/current_duel.json",
        "data/desafiosaber_data.json"
    ]
    
    backed_up_files = []
    for file_path in critical_files:
        if os.path.exists(file_path):
            try:
                # Crear estructura de directorios en backup
                backup_file_path = os.path.join(backup_path, file_path)
                os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                
                # Copiar archivo
                shutil.copy2(file_path, backup_file_path)
                backed_up_files.append(file_path)
                print_success(f"Backup creado: {file_path}")
            except Exception as e:
                print_error(f"Error creando backup de {file_path}: {e}")
                return None
        else:
            print_warning(f"Archivo no encontrado: {file_path}")
    
    # Crear archivo de metadatos del backup
    metadata = {
        "backup_name": backup_name,
        "timestamp": datetime.now().isoformat(),
        "files_backed_up": backed_up_files,
        "total_files": len(backed_up_files),
        "backup_size": sum(os.path.getsize(os.path.join(backup_path, f)) for f in backed_up_files if os.path.exists(os.path.join(backup_path, f)))
    }
    
    metadata_path = os.path.join(backup_path, "backup_metadata.json")
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print_success(f"Metadatos del backup creados: {metadata_path}")
    except Exception as e:
        print_error(f"Error creando metadatos: {e}")
        return None
    
    return backup_path, metadata

def verify_backup(backup_path, metadata):
    """Verificar la integridad del backup"""
    print_info("Verificando integridad del backup...")
    
    # Verificar que todos los archivos existen
    for file_path in metadata["files_backed_up"]:
        backup_file_path = os.path.join(backup_path, file_path)
        if not os.path.exists(backup_file_path):
            print_error(f"Archivo faltante en backup: {file_path}")
            return False
        
        # Verificar que el archivo es JSON válido
        try:
            with open(backup_file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            print_success(f"Archivo verificado: {file_path}")
        except json.JSONDecodeError as e:
            print_error(f"Archivo JSON corrupto: {file_path} - {e}")
            return False
        except Exception as e:
            print_error(f"Error verificando archivo: {file_path} - {e}")
            return False
    
    # Verificar tamaño total
    actual_size = sum(os.path.getsize(os.path.join(backup_path, f)) for f in metadata["files_backed_up"])
    if actual_size != metadata["backup_size"]:
        print_warning(f"Tamaño del backup no coincide. Esperado: {metadata['backup_size']}, Actual: {actual_size}")
    
    print_success("Backup verificado correctamente")
    return True

def restore_backup(backup_path, metadata):
    """Restaurar el backup"""
    print_info("Iniciando restauración del backup...")
    
    # Crear backup del estado actual antes de restaurar
    current_backup_path, current_metadata = create_backup()
    if current_backup_path:
        print_success(f"Backup del estado actual creado: {current_backup_path}")
    
    restored_files = []
    for file_path in metadata["files_backed_up"]:
        backup_file_path = os.path.join(backup_path, file_path)
        if os.path.exists(backup_file_path):
            try:
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Restaurar archivo
                shutil.copy2(backup_file_path, file_path)
                restored_files.append(file_path)
                print_success(f"Archivo restaurado: {file_path}")
            except Exception as e:
                print_error(f"Error restaurando {file_path}: {e}")
                return False
        else:
            print_error(f"Archivo no encontrado en backup: {file_path}")
            return False
    
    print_success(f"Restauración completada: {len(restored_files)} archivos restaurados")
    return True

def test_backup_restore_flow():
    """Test completo del flujo de backup y restauración"""
    
    print("💾 INICIANDO TEST DE SISTEMA DE BACKUP Y RESTAURACIÓN")
    print(f"📡 Conectando a: {BASE_URL}")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=5)
        if response.status_code != 200:
            print_error("Servidor no responde correctamente")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"No se puede conectar al servidor: {e}")
        return False
    
    print_success("Servidor conectado correctamente")
    
    # PASO 1: Crear directorio de backups
    print_step(1, "CREAR DIRECTORIO DE BACKUPS")
    
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR)
            print_success(f"Directorio de backups creado: {BACKUP_DIR}")
        except Exception as e:
            print_error(f"Error creando directorio de backups: {e}")
            return False
    else:
        print_success(f"Directorio de backups ya existe: {BACKUP_DIR}")
    
    # PASO 2: Crear datos de prueba
    print_step(2, "CREAR DATOS DE PRUEBA")
    
    # Crear categoría de prueba
    test_category = "Test_Backup_Category"
    try:
        response = requests.post(f"{BASE_URL}/categories", json={"name": test_category})
        if response.status_code == 200:
            print_success(f"Categoría de prueba creada: {test_category}")
        else:
            print_error(f"Error creando categoría de prueba: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción creando categoría: {e}")
        return False
    
    # Crear pregunta de prueba
    test_question = {
        "pregunta": "Pregunta de prueba para backup",
        "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
        "respuesta_correcta": 0,
        "categoria": test_category,
        "dificultad": "media"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/questions", json=test_question)
        if response.status_code == 200:
            question_result = response.json()
            question_id = question_result.get('question', {}).get('id')
            print_success(f"Pregunta de prueba creada: ID {question_id}")
        else:
            print_error(f"Error creando pregunta de prueba: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción creando pregunta: {e}")
        return False
    
    # PASO 3: Crear backup inicial
    print_step(3, "CREAR BACKUP INICIAL")
    
    backup_path, metadata = create_backup()
    if not backup_path:
        print_error("Error creando backup inicial")
        return False
    
    print_success(f"Backup inicial creado: {backup_path}")
    print_info(f"  - Archivos respaldados: {metadata['total_files']}")
    print_info(f"  - Tamaño total: {metadata['backup_size']} bytes")
    
    # PASO 4: Verificar backup inicial
    print_step(4, "VERIFICAR BACKUP INICIAL")
    
    if not verify_backup(backup_path, metadata):
        print_error("Verificación del backup inicial falló")
        return False
    
    # PASO 5: Modificar datos para probar restauración
    print_step(5, "MODIFICAR DATOS PARA PROBAR RESTAURACIÓN")
    
    # Modificar la pregunta de prueba
    updated_question = {
        "pregunta": "Pregunta modificada para test de backup",
        "opciones": ["Nueva A", "Nueva B", "Nueva C", "Nueva D"],
        "respuesta_correcta": 1,
        "categoria": test_category,
        "dificultad": "alta"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/questions/{question_id}", json=updated_question)
        if response.status_code == 200:
            print_success("Pregunta modificada para test")
        else:
            print_error(f"Error modificando pregunta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción modificando pregunta: {e}")
        return False
    
    # Verificar que la modificación se aplicó
    try:
        response = requests.get(f"{BASE_URL}/questions/{question_id}")
        if response.status_code == 200:
            question_data = response.json()
            if question_data.get('pregunta') == updated_question['pregunta']:
                print_success("Modificación verificada correctamente")
            else:
                print_error("La modificación no se aplicó correctamente")
                return False
        else:
            print_error(f"Error obteniendo pregunta modificada: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando modificación: {e}")
        return False
    
    # PASO 6: Restaurar backup
    print_step(6, "RESTAURAR BACKUP")
    
    if not restore_backup(backup_path, metadata):
        print_error("Error restaurando backup")
        return False
    
    # PASO 7: Verificar restauración
    print_step(7, "VERIFICAR RESTAURACIÓN")
    
    # Verificar que la pregunta volvió a su estado original
    try:
        response = requests.get(f"{BASE_URL}/questions/{question_id}")
        if response.status_code == 200:
            question_data = response.json()
            if question_data.get('pregunta') == test_question['pregunta']:
                print_success("Restauración verificada: pregunta restaurada correctamente")
            else:
                print_error("La restauración no funcionó correctamente")
                print_info(f"  - Esperado: {test_question['pregunta']}")
                print_info(f"  - Actual: {question_data.get('pregunta')}")
                return False
        else:
            print_error(f"Error obteniendo pregunta restaurada: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción verificando restauración: {e}")
        return False
    
    # PASO 8: Crear backup comprimido
    print_step(8, "CREAR BACKUP COMPRIMIDO")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_backup_name = f"backup_compressed_{timestamp}.zip"
    zip_backup_path = os.path.join(BACKUP_DIR, zip_backup_name)
    
    try:
        with zipfile.ZipFile(zip_backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
        
        zip_size = os.path.getsize(zip_backup_path)
        print_success(f"Backup comprimido creado: {zip_backup_path}")
        print_info(f"  - Tamaño original: {metadata['backup_size']} bytes")
        print_info(f"  - Tamaño comprimido: {zip_size} bytes")
        print_info(f"  - Compresión: {((1 - zip_size/metadata['backup_size']) * 100):.1f}%")
        
    except Exception as e:
        print_error(f"Error creando backup comprimido: {e}")
        return False
    
    # PASO 9: Probar restauración desde backup comprimido
    print_step(9, "PROBAR RESTAURACIÓN DESDE BACKUP COMPRIMIDO")
    
    # Crear directorio temporal para extraer
    temp_extract_dir = os.path.join(BACKUP_DIR, f"temp_extract_{timestamp}")
    os.makedirs(temp_extract_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_backup_path, 'r') as zipf:
            zipf.extractall(temp_extract_dir)
        
        print_success("Backup comprimido extraído correctamente")
        
        # Verificar que se puede restaurar desde el backup extraído
        extracted_backup_dir = os.path.join(temp_extract_dir, os.listdir(temp_extract_dir)[0])
        metadata_path = os.path.join(extracted_backup_dir, "backup_metadata.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                extracted_metadata = json.load(f)
            
            if verify_backup(extracted_backup_dir, extracted_metadata):
                print_success("Backup extraído verificado correctamente")
            else:
                print_error("Verificación del backup extraído falló")
                return False
        else:
            print_error("Metadatos no encontrados en backup extraído")
            return False
            
    except Exception as e:
        print_error(f"Error extrayendo backup comprimido: {e}")
        return False
    finally:
        # Limpiar directorio temporal
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
            print_success("Directorio temporal eliminado")
    
    # PASO 10: Limpiar datos de prueba
    print_step(10, "LIMPIAR DATOS DE PRUEBA")
    
    # Eliminar pregunta de prueba
    try:
        response = requests.delete(f"{BASE_URL}/questions/{question_id}")
        if response.status_code == 200:
            print_success("Pregunta de prueba eliminada")
        else:
            print_error(f"Error eliminando pregunta: {response.text}")
    except Exception as e:
        print_error(f"Excepción eliminando pregunta: {e}")
    
    # Eliminar categoría de prueba
    try:
        response = requests.delete(f"{BASE_URL}/categories/{test_category}")
        if response.status_code == 200:
            print_success("Categoría de prueba eliminada")
        else:
            print_error(f"Error eliminando categoría: {response.text}")
    except Exception as e:
        print_error(f"Excepción eliminando categoría: {e}")
    
    # Limpiar backups de prueba (mantener solo los últimos 3)
    try:
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")]
        backup_files.sort(reverse=True)
        
        # Mantener solo los últimos 3 backups
        for old_backup in backup_files[3:]:
            old_backup_path = os.path.join(BACKUP_DIR, old_backup)
            if os.path.isdir(old_backup_path):
                shutil.rmtree(old_backup_path)
            elif old_backup.endswith('.zip'):
                os.remove(old_backup_path)
            print_success(f"Backup antiguo eliminado: {old_backup}")
            
    except Exception as e:
        print_error(f"Error limpiando backups antiguos: {e}")
    
    print_success("💾 TEST DE SISTEMA DE BACKUP Y RESTAURACIÓN COMPLETADO EXITOSAMENTE")
    return True

if __name__ == "__main__":
    success = test_backup_restore_flow()
    sys.exit(0 if success else 1) 