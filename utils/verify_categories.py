import json

# Categorías permitidas
ALLOWED_CATEGORIES = {
    "Historia",
    "Ciencia",
    "Geografía",
    "Arte",
    "Deportes",
    "Entretenimiento"
}

# Leer el archivo JSON
with open('data/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Verificar categorías
categories_found = set()
invalid_categories = set()
category_counts = {cat: 0 for cat in ALLOWED_CATEGORIES}
total_questions = 0

for question in questions:
    total_questions += 1
    category = question.get('categoria')
    if category:
        categories_found.add(category)
        if category not in ALLOWED_CATEGORIES:
            invalid_categories.add(category)
        else:
            category_counts[category] += 1

print(f"\nTotal de preguntas: {total_questions}")
print("\nCategorías encontradas:", sorted(list(categories_found)))
if invalid_categories:
    print("\nCategorías inválidas encontradas:", sorted(list(invalid_categories)))
else:
    print("\nTodas las categorías son válidas")

print("\nNúmero de preguntas por categoría:")
total_valid = 0
for category in sorted(category_counts.keys()):
    count = category_counts[category]
    total_valid += count
    print(f"{category}: {count} preguntas")

print(f"\nTotal de preguntas válidas: {total_valid}")
if total_questions != total_valid:
    print(f"¡ADVERTENCIA! Hay {total_questions - total_valid} preguntas con categorías inválidas") 