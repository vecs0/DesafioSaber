# 🎮 Desafío Saber - Sistema de Trivia Interactivo

Un sistema completo de trivia con panel de administración web y juego de escritorio.

## 🚀 Inicio Rápido

### Opción 1: Lanzamiento Automático (Recomendado)
```bash
python launch.py
```

### Opción 2: Lanzamiento Manual
```bash
# Para el panel de administración (solo una ventana, sesión persistente)
python start_admin_single.py

# Para el panel de administración (versión estándar)
python start_admin.py

# Para el sistema completo
python start_system.py

# Para solo el juego
python game/main.py
```

## 📋 Requisitos del Sistema

- **Python 3.8 o superior**
- **Node.js 14 o superior** (para el panel de administración)
- **npm** (viene con Node.js)

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd DesafíoSaber_tkinter-definitivo
```

### 2. Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

### 3. Instalar dependencias de Node.js
```bash
cd web_admin
npm install
cd ..
```

### 4. Verificar y corregir el sistema
```bash
python fix_system.py
```

## 🎯 Características

### Juego de Trivia
- **3 modos de juego**: Clásico, Contrarreloj, Duelo
- **Múltiples categorías**: Historia, Ciencia, Geografía, etc.
- **Sistema de sonidos** con efectos y música
- **Ranking de jugadores** con persistencia
- **Interfaz moderna** con animaciones

### Panel de Administración
- **Gestión de preguntas** (crear, editar, eliminar)
- **Gestión de categorías** con colores personalizados
- **Estadísticas en tiempo real**
- **Gestión de jugadores** y rankings
- **Subida de archivos** (imágenes, sonidos)
- **Reportes de errores**

## 📁 Estructura del Proyecto

```
DesafíoSaber_tkinter-definitivo/
├── game/                   # Juego principal (Tkinter)
│   ├── main.py            # Aplicación principal del juego
│   ├── achievements.py    # Sistema de logros
│   ├── api_client.py      # Cliente para API
│   └── wheel_animation.py # Animaciones
├── web_admin/             # Panel de administración (React + Flask)
│   ├── server.py          # Servidor Flask (API)
│   ├── src/               # Código React
│   └── package.json       # Dependencias Node.js
├── data/                  # Datos del juego
│   ├── questions.json     # Preguntas
│   ├── ranking.json       # Rankings
│   ├── config.json        # Configuración
│   └── categories.json    # Categorías
├── assets/                # Recursos multimedia
│   ├── images/            # Imágenes
│   └── sounds/            # Sonidos
├── sounds/                # Sonidos adicionales
├── uploads/               # Archivos subidos
├── main.py                # Punto de entrada del juego
├── start_system.py        # Iniciador del sistema
├── fix_system.py          # Verificación y corrección
├── launch.py              # Lanzador automático
└── requirements.txt       # Dependencias Python
```

## 🎮 Modos de Juego

### 1. Modo Clásico
- 15 preguntas por partida
- 30 segundos por pregunta
- Puntuación acumulativa

### 2. Modo Contrarreloj
- 60 segundos totales
- Máximo número de preguntas posibles
- Puntuación por velocidad

### 3. Modo Duelo
- 2 jugadores
- 10 preguntas (5 por jugador)
- 15 segundos por pregunta
- Sistema de puntos positivo/negativo

## 🌐 Panel de Administración

### Acceso
- **URL**: http://localhost:3000
- **API**: http://localhost:5000/api/

### Funcionalidades
- **Dashboard**: Estadísticas generales
- **Preguntas**: CRUD completo de preguntas
- **Categorías**: Gestión de categorías
- **Jugadores**: Gestión de usuarios
- **Ranking**: Visualización de puntuaciones
- **Recursos**: Gestión de archivos multimedia
- **Configuración**: Ajustes del sistema

## 🔧 Solución de Problemas

### Error: "pygame no encontrado"
```bash
pip install pygame==2.5.2
```

### Error: "flask no encontrado"
```bash
pip install flask flask-cors
```

### Error: "Node.js no encontrado"
Descargar e instalar desde: https://nodejs.org/

### Error: "Puerto 3000/5000 ocupado"
```bash
# En Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# En Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Error: "Archivos de assets no encontrados"
```bash
python fix_system.py
```

### Error: "No se puede conectar a la API"
1. Verificar que el servidor Flask esté ejecutándose
2. Verificar que no haya firewall bloqueando el puerto 5000
3. Verificar la conectividad de red

## 📊 Configuración Avanzada

### Variables de Entorno
```bash
# Puerto del servidor Flask
FLASK_PORT=5000

# Puerto de la aplicación React
REACT_PORT=3000

# Modo de desarrollo
FLASK_ENV=development
```

### Personalización de Temas
Editar `data/config.json`:
```json
{
  "theme": "oscuro",
  "difficulty": "difícil",
  "sound": true,
  "music": true
}
```

## 🚀 Despliegue

### Desarrollo Local
```bash
python launch.py
```

### Producción
```bash
# Construir aplicación React
cd web_admin
npm run build

# Ejecutar servidor Flask en producción
cd ..
python web_admin/server.py
```

## 📝 Logs y Debugging

### Habilitar logs detallados
```python
# En game/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verificar conectividad API
```bash
curl http://localhost:5000/api/questions
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras problemas:

1. Ejecuta `python fix_system.py` para verificación automática
2. Revisa la sección de "Solución de Problemas"
3. Verifica que todas las dependencias estén instaladas
4. Consulta los logs de error

---

**¡Disfruta jugando Desafío Saber! 🎮** 