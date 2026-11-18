#!/usr/bin/env python3
"""
Limpia preguntas huérfanas: elimina preguntas cuya categoría no esté en la lista oficial.
Hace backup automático antes de modificar el archivo.
"""
import json
import shutil
import os
from datetime import datetime

# Rutas relativas al directorio raíz del proyecto
CATEGORIES_FILE = '../data/categories.json'
QUESTIONS_FILE = '../data/questions.json'
BACKUP_DIR = '../backups'


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def make_backup(src):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dst = os.path.join(BACKUP_DIR, f'questions_backup_{timestamp}.json')
    shutil.copy2(src, dst)
    return dst

def clean_orphan_questions():
    print('--- LIMPIEZA DE PREGUNTAS HUÉRFANAS ---')
    categories = set(load_json(CATEGORIES_FILE))
    questions = load_json(QUESTIONS_FILE)
    print(f'Categorías oficiales: {sorted(categories)}')
    print(f'Preguntas totales antes: {len(questions)}')

    # Backup
    backup_path = make_backup(QUESTIONS_FILE)
    print(f'Backup creado: {backup_path}')

    # Filtrar preguntas válidas
    valid_questions = [q for q in questions if (q.get('categoria') or q.get('category')) in categories]
    orphan_questions = [q for q in questions if (q.get('categoria') or q.get('category')) not in categories]

    print(f'Preguntas válidas: {len(valid_questions)}')
    print(f'Preguntas huérfanas eliminadas: {len(orphan_questions)}')

    if orphan_questions:
        print('Categorías huérfanas encontradas:')
        for cat in sorted(set((q.get("categoria") or q.get("category")) for q in orphan_questions)):
            print(f'  - {cat}')

    # Guardar solo preguntas válidas
    save_json(QUESTIONS_FILE, valid_questions)
    print('Archivo de preguntas actualizado.')

if __name__ == '__main__':
    clean_orphan_questions() 