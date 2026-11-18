# 🎮 DesafíoSaber v2.0 - Sistema Completo

## 📋 Descripción

DesafíoSaber es un juego educativo completo de preguntas y respuestas con sistema de administración web, estadísticas avanzadas, logros y múltiples modos de juego. El sistema incluye:

- **🎮 Juego Principal**: Aplicación Tkinter con interfaz moderna
- **🌐 Panel Web**: Administración completa con React
- **🔧 API Backend**: Servidor Flask con endpoints completos
- **📊 Estadísticas**: Sistema de tracking y análisis
- **🏆 Logros**: Sistema de logros desbloqueables
- **⚔️ Modo Duelo**: Competencia entre jugadores
- **🎨 Personalización**: Colores y estilos dinámicos

## 🚀 Inicio Rápido

### Opción 1: Inicio Automático (Recomendado)
```bash
python scripts/quick_start.py
```
Este comando iniciará automáticamente todos los servicios y abrirá los navegadores.

### Opción 2: Inicio Manual
```bash
# 1. Verificar conexiones
python scripts/test_connections.py

# 2. Iniciar sistema completo
python scripts/start/start_complete_system.py

# 3. O iniciar servicios individualmente
python scripts/start/start_backend.py
cd web_admin && npm start
python game/main.py
```

## 📁 Estructura del Proyecto

```
DesafíoSaber_tkinter-definitivo/
├── 🎮 game/                    # Juego principal (Tkinter)
│   ├── main.py                # Aplicación principal
│   ├── achievements.py        # Sistema de logros
│   ├── api_client.py          # Cliente API
│   ├── cloud_sync.py          # Sincronización en nube
│   └── user_registration.py   # Registro de usuarios
├── 🌐 web_admin/              # Panel web de administración
│   ├── server.py              # Servidor Flask (API)
│   ├── src/                   # Frontend React
│   └── package.json           # Dependencias Node.js
├── 📊 data/                   # Base de datos local
│   ├── questions.json         # Preguntas del juego
│   ├── users.json             # Usuarios registrados
│   ├── ranking.json           # Ranking de puntuaciones
│   └── achievements.json      # Logros disponibles
├── 🎨 assets/                 # Recursos del juego
│   ├── images/                # Imágenes e iconos
│   └── sounds/                # Efectos de sonido
├── 🔧 scripts/                # Scripts de utilidad
│   ├── test_connections.py    # Verificación de conexiones
│   ├── prepare_exe_build.py   # Preparación para .exe
│   └── quick_start.py         # Inicio rápido
└── 📚 docs/                   # Documentación
```

## 🎯 Funcionalidades Principales

### 🎮 Modos de Juego
- **Clásico**: 15 preguntas, 30 segundos por pregunta
- **Contrarreloj**: 60 segundos totales, preguntas ilimitadas
- **Duelo**: Competencia entre 2 jugadores

### 🌐 Panel de Administración
- **Gestión de Preguntas**: CRUD completo con filtros
- **Gestión de Usuarios**: Registro, edición y estadísticas
- **Ranking Global**: Tabla de puntuaciones
- **Estadísticas**: Gráficos y análisis detallados
- **Configuración**: Personalización del juego
- **Logros**: Sistema de logros desbloqueables

### 📊 Sistema de Estadísticas
- Puntuaciones por modo de juego
- Precisión y rachas máximas
- Historial de partidas
- Categorías favoritas
- Victorias en duelos

## 🔧 Instalación y Configuración

### Requisitos Previos
- **Python 3.8+**
- **Node.js 14+** (para el panel web)
- **Git** (para clonar el repositorio)

### Instalación de Dependencias

#### Python (Juego y Backend)
```bash
pip install -r requirements.txt
```

#### Node.js (Panel Web)
```bash
cd web_admin
npm install
```

### Configuración Inicial
```bash
# 1. Verificar que todo funcione
python scripts/test_connections.py

# 2. Iniciar el sistema
python scripts/quick_start.py
```

## 🚀 Compilación a Ejecutable (.exe)

### Preparación
```bash
# 1. Verificar dependencias
python scripts/test_connections.py

# 2. Preparar compilación
python scripts/prepare_exe_build.py

# 3. Compilar
cd build
python build_exe.py
```

### Resultado
- El ejecutable se creará en `build/dist/DesafioSaber.exe`
- Incluye todos los recursos necesarios
- No requiere Python instalado en el equipo destino

## 🌐 Acceso a los Servicios

### Panel Web de Administración
- **URL**: http://localhost:3000
- **Funciones**: Gestión completa del sistema

### API Backend
- **URL**: http://localhost:5000
- **Endpoints**: /api/questions, /api/users, /api/ranking, etc.

### Juego Principal
- Se ejecuta como aplicación de escritorio
- Interfaz Tkinter moderna y responsiva

## 📊 Verificación del Sistema

### Script de Verificación
```bash
python scripts/test_connections.py
```

Este script verifica:
- ✅ Conexión al backend Flask
- ✅ Conexión al frontend React
- ✅ Endpoints de la API
- ✅ Archivos del juego
- ✅ Base de datos local

### Reporte de Verificación
El script genera un reporte detallado en `data/connection_test_report.json`

## 🎮 Uso del Juego

### Inicio de Sesión
1. Registra un nuevo usuario o inicia sesión
2. Selecciona modo de juego y categoría
3. ¡Comienza a jugar!

### Modo Duelo
1. Ambos jugadores deben estar registrados
2. Selecciona categoría y modo
3. Los jugadores responden alternadamente
4. Gana quien obtenga más puntos

### Logros
- Se desbloquean automáticamente al cumplir objetivos
- Proporcionan puntos de bonificación
- Se muestran en la sección de logros

## 🔧 Solución de Problemas

### Problemas Comunes

#### El panel web no carga
```bash
# Verificar que Node.js esté instalado
node --version

# Reinstalar dependencias
cd web_admin
npm install
npm start
```

#### El backend no responde
```bash
# Verificar que Flask esté instalado
pip install flask flask-cors flask-socketio

# Iniciar manualmente
cd web_admin
python server.py
```

#### El juego no inicia
```bash
# Verificar dependencias
pip install pygame pillow requests matplotlib numpy

# Ejecutar desde el directorio correcto
cd game
python main.py
```

#### Error de puertos ocupados
```bash
# Verificar puertos en uso
netstat -ano | findstr :3000
netstat -ano | findstr :5000

# Detener procesos si es necesario
taskkill /PID <PID> /F
```

### Logs y Debugging
- Los logs se muestran en la consola
- Errores se guardan en `data/error_logs.json`
- Reportes de conexión en `data/connection_test_report.json`

## 📈 Estadísticas y Análisis

### Métricas Disponibles
- **Puntuaciones**: Por usuario, modo y categoría
- **Precisión**: Porcentaje de respuestas correctas
- **Rachas**: Secuencias de respuestas correctas
- **Tiempo**: Velocidad de respuesta
- **Categorías**: Preferencias por tema

### Exportación de Datos
- Los datos se pueden exportar desde el panel web
- Formato JSON para análisis externos
- Backup automático en `backups/`

## 🎨 Personalización

### Colores de Categorías
- Configurables desde el panel web
- Colores personalizados por categoría
- Iconos y estilos dinámicos

### Estilos de Botones
- Configuración de colores y fuentes
- Efectos hover personalizables
- Temas visuales completos

### Sonidos
- Efectos de sonido configurables
- Música de fondo opcional
- Volumen ajustable

## 🔒 Seguridad

### Autenticación
- Sistema de registro e inicio de sesión
- Contraseñas seguras
- Sesiones persistentes

### Validación de Datos
- Validación en frontend y backend
- Sanitización de entradas
- Protección contra inyección

### Backups Automáticos
- Respaldo automático antes de modificaciones
- Historial de cambios
- Recuperación de datos

## 📚 Documentación Adicional

### Manuales de Usuario
- `docs/manuales/MANUAL_USUARIO_FINAL.md`
- `docs/manuales/MANUAL_RECUPERACION_ADMIN.md`

### Documentación Técnica
- `docs/sistema/SISTEMA_COMPLETO_v2.0.md`
- `docs/optimizaciones/OPTIMIZACIONES_COMPLETAS_FINAL.md`

### Guías de Desarrollo
- `docs/estilos/ESTILOS_BOTONES_DINAMICOS.md`
- `docs/logros_estadisticas/SISTEMA_LOGROS_ESTADISTICAS.md`

## 🤝 Contribución

### Reportar Errores
1. Usa el botón "🐞 Reportar Error" en el juego
2. O crea un issue en el repositorio
3. Incluye detalles del error y pasos para reproducirlo

### Sugerencias
- Envía sugerencias a través del panel web
- O crea un issue con la etiqueta "sugerencia"

## 📞 Soporte

### Contacto
- **Email**: soporte@desafiosaber.com
- **Documentación**: Ver carpeta `docs/`
- **Issues**: Repositorio del proyecto

### Recursos de Ayuda
- `docs/resumenes/RESUMEN_PROYECTO_FINAL.md`
- Scripts de verificación y diagnóstico
- Manuales de usuario y administrador

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.

## 🎉 Créditos

Desarrollado con ❤️ por el equipo DesafíoSaber

**Versión**: 2.0  
**Fecha**: 2024  
**Plataforma**: Windows, macOS, Linux

---

## 🚀 Próximos Pasos

1. **✅ Verificación de conexiones**: Ejecuta `python scripts/test_connections.py`
2. **✅ Ejecución de .exe**: Prepara con `python scripts/prepare_exe_build.py`
3. **🎮 Prueba el juego**: Ejecuta `python scripts/quick_start.py`
4. **🌐 Accede al panel**: http://localhost:3000
5. **📊 Revisa estadísticas**: En la sección de análisis del panel

¡El sistema está listo para usar! 🎉 