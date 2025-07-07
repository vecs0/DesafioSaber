import json

questions = [
  {
    "modo": "Clásico",
    "categoria": "Historia",
    "dificultad": "Fácil",
    "pregunta": "¿En qué año llegó Colón a América?",
    "opciones": [
      "1492",
      "1521",
      "1607",
      "1776"
    ],
    "respuesta": "1492"
  },
  # ... all questions will be added here
]

with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=2, ensure_ascii=False) 