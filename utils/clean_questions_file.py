import json
import os
import unicodedata
from datetime import datetime

def normalizar(texto):
    if not texto:
        return ''
    texto = texto.lower().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto.replace('í','i').replace('á','a').replace('é','e').replace('ó','o').replace('ú','u')

CATEGORIAS_VALIDAS = {
    'historia', 'ciencia', 'geografia', 'arte', 'deportes', 'entretenimiento'
}
CATEGORIAS_MAP = {
    'ciencias': 'Ciencia',
    'ciencia': 'Ciencia',
    'historia': 'Historia',
    'geografia': 'Geografía',
    'geografía': 'Geografía',
    'arte': 'Arte',
    'deportes': 'Deportes',
    'entretenimiento': 'Entretenimiento'
}

def backup_file(path):
    backup_dir = os.path.join(os.path.dirname(path), '..', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    base = os.path.basename(path)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'{base}_backup_{timestamp}.json')
    with open(path, 'r', encoding='utf-8') as fsrc, open(backup_path, 'w', encoding='utf-8') as fdst:
        fdst.write(fsrc.read())
    print(f'[BACKUP] Archivo respaldado en: {backup_path}')

def limpiar_questions_json():
    path = os.path.join('data', 'questions.json')
    if not os.path.exists(path):
        print('[ERROR] No se encontró data/questions.json')
        return
    backup_file(path)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    preguntas_limpias = []
    preguntas_descartadas = 0
    for q in data:
        cat = q.get('categoria', '').strip()
        cat_norm = normalizar(cat)
        if cat_norm in CATEGORIAS_MAP:
            cat_final = CATEGORIAS_MAP[cat_norm]
        else:
            preguntas_descartadas += 1
            print(f'[DESCARTADA] Categoría inválida: "{cat}" | Pregunta: {q.get("pregunta","")[:60]}...')
            continue
        q['categoria'] = cat_final
        preguntas_limpias.append(q)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(preguntas_limpias, f, ensure_ascii=False, indent=2)
    print(f'[LIMPIEZA] Preguntas válidas: {len(preguntas_limpias)} | Preguntas descartadas: {preguntas_descartadas}')

if __name__ == '__main__':
    limpiar_questions_json() 