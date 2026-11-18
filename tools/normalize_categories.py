import json

# Mapeo de categorías
category_mapping = {
    'Deporte': 'Deportes',
    'Ciencias': 'Ciencia',
    'Geografia': 'Geografía',
    'Geografía': 'Geografía',  # Para mantener la consistencia con acentos
    'Historia': 'Historia',
    'Arte': 'Arte',
    'Entretenimiento': 'Entretenimiento'
}

# Leer el archivo JSON
with open('data/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Normalizar las categorías
for question in questions:
    if 'categoria' in question:
        old_category = question['categoria']
        if old_category in category_mapping:
            question['categoria'] = category_mapping[old_category]

# Guardar el archivo JSON actualizado
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2) 