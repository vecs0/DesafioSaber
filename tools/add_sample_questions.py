import json
import os
from datetime import datetime

base_dir = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, 'data')
questions_file = os.path.join(data_dir, 'questions.json')

sample_questions = [
    {
        "categoria": "Historia",
        "pregunta": "¿Quién fue el primer presidente de Estados Unidos?",
        "opciones": ["George Washington", "Abraham Lincoln", "Thomas Jefferson", "John Adams"],
        "respuesta": "George Washington",
        "dificultad": "Fácil",
        "modo": "Clásico",
        "fecha_creacion": datetime.now().isoformat(),
        "id": 10001
    },
    {
        "categoria": "Ciencia",
        "pregunta": "¿Cuál es el elemento químico con símbolo O?",
        "opciones": ["Oro", "Oxígeno", "Osmio", "Oganesón"],
        "respuesta": "Oxígeno",
        "dificultad": "Fácil",
        "modo": "Clásico",
        "fecha_creacion": datetime.now().isoformat(),
        "id": 10002
    },
    {
        "categoria": "Geografía",
        "pregunta": "¿Cuál es la capital de Francia?",
        "opciones": ["París", "Londres", "Roma", "Berlín"],
        "respuesta": "París",
        "dificultad": "Fácil",
        "modo": "Clásico",
        "fecha_creacion": datetime.now().isoformat(),
        "id": 10003
    }
]

try:
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
    else:
        data = []
    # Agregar solo si no existen
    added = 0
    for q in sample_questions:
        if not any(existing.get('pregunta') == q['pregunta'] for existing in data):
            data.append(q)
            added += 1
    with open(questions_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'✅ {added} preguntas de prueba agregadas a questions.json')
except Exception as e:
    print(f'❌ Error actualizando questions.json: {e}') 