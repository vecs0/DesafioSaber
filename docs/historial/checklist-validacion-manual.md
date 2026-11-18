# ✅ Checklist de Validación Manual: Juego y Panel Web

## 1. Sincronización Panel Web ↔ Juego
- [ ] Crear una nueva pregunta en el panel web y verificar que aparece en el juego (tras recargar/reiniciar el juego).
- [ ] Editar una pregunta existente en el panel web y comprobar que el cambio se refleja en el juego.
- [ ] Eliminar una pregunta en el panel web y confirmar que ya no aparece en el juego.
- [ ] Crear, editar y eliminar categorías en el panel web y verificar que el juego muestra la lista actualizada.
- [ ] Cambiar la configuración de modos de juego (si aplica) y comprobar que el juego usa la nueva configuración.

## 2. Lógica de Preguntas y Categorías
- [ ] Al seleccionar una categoría en el juego, solo deben aparecer preguntas de esa categoría.
- [ ] No deben mezclarse preguntas de diferentes categorías bajo ninguna circunstancia.
- [ ] Si una categoría no tiene preguntas, el juego debe mostrar un mensaje de advertencia y no iniciar la partida.

## 3. Lógica de Puntuación y Temporizador
- [ ] Responder correctamente suma los puntos indicados en la configuración del modo.
- [ ] Responder incorrectamente resta los puntos indicados (o no suma, según el modo).
- [ ] El temporizador cuenta correctamente el tiempo por pregunta o global, según el modo.
- [ ] Si el tiempo se agota, la pregunta se marca como incorrecta y se avanza o termina la partida según el modo.
- [ ] Las bonificaciones (racha, perfecto, velocidad) se aplican correctamente si están configuradas.

## 4. Flujo de Usuario y Navegación
- [ ] El registro e inicio de sesión funcionan correctamente en ambos sistemas.
- [ ] El menú principal del juego permite acceder a todas las secciones (jugar, ranking, logros, estadísticas, etc.).
- [ ] Cada botón realiza la acción esperada y navega a la pantalla correcta.
- [ ] El ranking muestra los datos actualizados tras jugar una partida.
- [ ] El historial y las estadísticas se actualizan correctamente después de cada partida.

## 5. Gestión de Errores y Feedback
- [ ] Si ocurre un error (por ejemplo, sin conexión a la API), se muestra un mensaje claro al usuario.
- [ ] Los mensajes de éxito, advertencia y error son comprensibles y aparecen en el momento adecuado.
- [ ] El reporte de errores desde el juego y el panel web funciona y se registra correctamente.

## 6. Pruebas de Integración
- [ ] Realizar cambios en el panel web y comprobar que se reflejan en el juego sin reiniciar el backend.
- [ ] Jugar en diferentes modos y categorías para asegurar que la lógica se mantiene en todos los casos.
- [ ] Probar con varios usuarios y sesiones para verificar la persistencia y sincronización de datos.

---

**Sugerencia:** Marca cada ítem a medida que lo vayas validando. Si encuentras algún fallo, anótalo para corregirlo o reportarlo. 