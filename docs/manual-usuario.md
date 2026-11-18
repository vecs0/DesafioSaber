# 🎮 Manual de Usuario - DesafíoSaber v2.0

## 📋 Índice
1. [Instalación](#instalación)
2. [Primera vez](#primera-vez)
3. [Registro de Usuario](#registro-de-usuario)
4. [Iniciar Sesión](#iniciar-sesión)
5. [Jugar](#jugar)
6. [Estadísticas y Logros](#estadísticas-y-logros)
7. [Sincronización](#sincronización)
8. [Modo Duelo](#modo-duelo)
9. [Solución de Problemas](#solución-de-problemas)

---

## 🚀 Instalación

### Requisitos:
- Windows 10/11
- Python 3.8 o superior
- Conexión a internet (para sincronización)

### Pasos:
1. Descargar el archivo del juego
2. Extraer en una carpeta
3. Ejecutar `python game/main.py`

---

## 🆕 Primera vez

Al abrir el juego por primera vez:

1. **Pantalla de introducción** - Se mostrará automáticamente
2. **Menú principal** - Aparecerá después de la intro
3. **Botones de registro** - En la parte superior derecha del header

---

## 🔐 Registro de Usuario

### Pasos para registrarse:

1. **Hacer clic en "🔐 Registrarse"** en el header superior
2. **Completar el formulario:**
   - **Nombre completo:** Tu nombre real
   - **Nombre de usuario:** Único (3-20 caracteres, solo letras, números, guiones y guiones bajos)
   - **Contraseña:** Mínimo 6 caracteres
   - **Confirmar contraseña:** Debe coincidir
   - **Email:** Opcional (para recuperación)

3. **Hacer clic en "Registrarse"**
4. **¡Listo!** Tu cuenta se creará y sincronizará automáticamente

### Validaciones:
- ✅ Nombre de usuario único
- ✅ Contraseña segura (mínimo 6 caracteres)
- ✅ Contraseñas coinciden
- ✅ Campos obligatorios completados

---

## 👤 Iniciar Sesión

### Para usuarios ya registrados:

1. **Hacer clic en "👤 Iniciar Sesión"** en el header superior
2. **Ingresar credenciales:**
   - **Usuario:** Tu nombre de usuario
   - **Contraseña:** Tu contraseña
3. **Hacer clic en "🔐 Iniciar Sesión"**
4. **¡Bienvenido de vuelta!** Tus datos se sincronizarán automáticamente

### Información mostrada:
- ✅ Usuario actual en el header
- ✅ Botón "🚪 Cerrar Sesión" disponible
- ✅ Datos sincronizados desde el servidor

---

## 🎮 Jugar

### Una vez registrado/logueado:

1. **Hacer clic en "JUGAR"** en el menú principal
2. **Seleccionar modo:**
   - **Clásico:** 15 preguntas, 30 segundos cada una
   - **Contrarreloj:** 1 minuto total
   - **Duelo:** 2 jugadores, 10 preguntas
3. **Seleccionar categoría**
4. **Ingresar nombre de usuario** (se pre-llena si estás logueado)
5. **¡Jugar!**

### Características:
- ✅ Puntuaciones se guardan automáticamente
- ✅ Estadísticas se actualizan en tiempo real
- ✅ Logros se desbloquean automáticamente
- ✅ Datos se sincronizan con el servidor

---

## 📊 Estadísticas y Logros

### Ver estadísticas:
1. **Hacer clic en "ESTADÍSTICAS"** en el menú principal
2. **Seleccionar usuario** (si estás logueado, se selecciona automáticamente)
3. **Ver información:**
   - Resumen general
   - Rendimiento por modo
   - Rendimiento por categoría
   - Logros desbloqueados
   - Historial de partidas
   - Gráficos de rendimiento

### Ver logros:
1. **Hacer clic en "LOGROS"** en el menú principal
2. **Ver todos los logros disponibles:**
   - Logros pendientes (izquierda)
   - Logros desbloqueados (derecha)
   - Progreso de cada logro
   - Descripción detallada

---

## 🔄 Sincronización

### Funcionamiento automático:
- ✅ **Sincronización cada 30 segundos**
- ✅ **Funciona en segundo plano**
- ✅ **No interrumpe el juego**
- ✅ **Cola offline** si no hay conexión

### Datos sincronizados:
- 📊 Estadísticas de usuario
- 🏆 Puntuaciones y ranking
- 🏅 Logros y progreso
- 📈 Historial de partidas
- 👤 Información de perfil

### Sin conexión:
- ✅ El juego funciona normalmente
- ✅ Los datos se guardan localmente
- ✅ Se sincronizan cuando hay conexión
- ✅ No se pierde información

---

## ⚔️ Modo Duelo

### Para jugar en duelo:

1. **Seleccionar "Duelo"** en el menú de juego
2. **Seleccionar categoría**
3. **Ingresar nombres de jugadores:**
   - **Jugador 1:** Puede seleccionar usuario registrado o escribir nuevo
   - **Jugador 2:** Puede seleccionar usuario registrado o escribir nuevo
4. **¡Comenzar duelo!**

### Características del duelo:
- 🎯 10 preguntas (5 por jugador)
- ⏱️ 15 segundos por pregunta
- 🏆 Sistema de puntos (+100 correcta, -50 incorrecta)
- 🔄 Turnos alternados
- 🏅 Desempate automático si hay empate
- 💀 Muerte súbita si es necesario

### Usuarios registrados en duelo:
- ✅ Aparecen en el combo box
- ✅ Se pueden seleccionar fácilmente
- ✅ Sus estadísticas se actualizan
- ✅ Se sincronizan automáticamente

---

## 🚪 Cerrar Sesión

### Para cerrar sesión:

1. **Hacer clic en "🚪 Cerrar Sesión"** en el header
2. **Confirmar** el mensaje
3. **¡Listo!** Has cerrado sesión

### Después de cerrar sesión:
- ✅ Puedes seguir jugando como "Anónimo"
- ✅ Los datos se mantienen en el servidor
- ✅ Puedes volver a iniciar sesión cuando quieras
- ✅ Los botones de registro/login vuelven a aparecer

---

## 🔧 Solución de Problemas

### Error de conexión:
- ✅ Verificar conexión a internet
- ✅ Los datos se guardan localmente
- ✅ Se sincronizarán cuando haya conexión

### Error de login:
- ✅ Verificar usuario y contraseña
- ✅ Verificar que la cuenta existe
- ✅ Intentar registrarse si no tienes cuenta

### Error de registro:
- ✅ Verificar que el usuario no existe
- ✅ Verificar formato del usuario (solo letras, números, guiones)
- ✅ Verificar que la contraseña tenga 6+ caracteres

### Datos no sincronizados:
- ✅ Esperar 30 segundos para sincronización automática
- ✅ Verificar conexión a internet
- ✅ Reiniciar el juego si es necesario

### Juego lento:
- ✅ Cerrar otras aplicaciones
- ✅ Verificar espacio en disco
- ✅ Reiniciar el juego

---

## 📞 Soporte

### Si necesitas ayuda:
1. **Hacer clic en "🐞 Reportar error"** en el header
2. **Describir el problema** en el formulario
3. **Enviar reporte** automáticamente

### Información incluida en reportes:
- ✅ Versión del juego
- ✅ Sistema operativo
- ✅ Descripción del error
- ✅ Pasos para reproducir
- ✅ Logs del sistema

---

## 🎯 Consejos

### Para mejores puntuaciones:
- 🎯 Practica en modo Clásico
- ⏱️ Usa el tiempo eficientemente
- 📚 Estudia diferentes categorías
- 🏆 Compite en el ranking

### Para desbloquear logros:
- 🎮 Juega todos los modos
- 📊 Completa diferentes categorías
- 🏅 Alcanza puntuaciones altas
- 🔄 Juega regularmente

### Para sincronización óptima:
- 🌐 Mantén conexión estable
- 🔄 No cierres el juego abruptamente
- 📱 Usa la misma cuenta en diferentes dispositivos
- 💾 Los datos se guardan automáticamente

---

## 🎉 ¡Disfruta del juego!

**DesafíoSaber v2.0** te ofrece:
- 🎮 Experiencia de juego profesional
- 🔐 Sistema de cuentas seguro
- ☁️ Sincronización en la nube
- 📊 Estadísticas detalladas
- 🏅 Sistema de logros
- ⚔️ Modo duelo emocionante
- 🏆 Ranking global

**¡Que tengas mucha diversión aprendiendo!** 🚀 