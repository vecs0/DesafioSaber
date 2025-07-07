# DesafíoSaber

¡Bienvenido a **DesafíoSaber**! Un sistema completo de juego de preguntas y respuestas con panel de administración web, sincronización en tiempo real y estadísticas avanzadas.

---

## Descripción General

DesafíoSaber es una plataforma educativa y de entretenimiento que permite gestionar y jugar partidas de trivia, con soporte para múltiples modos de juego, usuarios, categorías, logros y estadísticas. Incluye:
- **Juego de escritorio** (Tkinter + Pygame)
- **Panel de administración web** (React + Flask)
- **Sincronización en tiempo real** (WebSocket)
- **Gestión de usuarios, preguntas, categorías y ranking**
- **Sistema de logros y estadísticas**

---

## Estructura del Proyecto

```
DesafioSaber-main/
├── assets/           # Imágenes y sonidos del juego
├── config/           # Configuración avanzada
├── data/             # Archivos de datos (usuarios, preguntas, ranking, etc.)
├── docs/             # Documentación y manuales
├── game/             # Código fuente del juego de escritorio (Python)
├── scripts/          # Scripts de instalación, arranque y utilidades
├── sounds/           # Sonidos adicionales
├── tests/            # Pruebas automáticas
├── utils/            # Utilidades y scripts de mantenimiento
├── web_admin/        # Panel de administración web (React + Flask)
└── README.md         # Este archivo
```

---

## Requisitos

- **Python 3.8+** (recomendado 3.10+)
- **Node.js 16+** y **npm**
- **pip** (gestor de paquetes Python)
- Sistema operativo: Windows, Linux o MacOS

---

## Instalación

1. **Clona el repositorio**
   ```
   git clone <url-del-repo>
   cd DesafioSaber-main
   ```

2. **Instala dependencias del backend y juego**
   ```
   pip install -r scripts/requirements.txt
   ```

3. **Instala dependencias del panel web**
   ```
   cd web_admin
   npm install
   cd ..
   ```

---

## Ejecución

### 1. Iniciar el backend (API y WebSocket)
```
python scripts/start/start_backend.py
```

### 2. Iniciar el panel de administración web
```
cd web_admin
npm run start
```

### 3. Iniciar el juego de escritorio
```
python game/main.py
```

---

## Funcionalidades Principales

- **Panel de administración web**
  - Gestión de usuarios, categorías y preguntas
  - Visualización de estadísticas y ranking
  - Editor visual de estilos y colores
  - Sincronización en tiempo real (WebSocket)
- **Juego de escritorio**
  - Modos: Clásico, Contrarreloj, Duelo
  - Selección de categorías y dificultad
  - Logros, ranking y estadísticas personales
  - Sonidos y animaciones
- **Sincronización total**
  - Cambios en el panel se reflejan en el juego y viceversa
  - Nuevas categorías, preguntas y usuarios disponibles al instante
- **Sistema de logros y estadísticas**
  - Desbloqueo de logros por hitos
  - Estadísticas detalladas por usuario y modo

---

## Notas de Uso

- El sistema está pensado para uso educativo, ferias, competencias o aprendizaje lúdico.
- El backend y el panel deben estar corriendo para que la sincronización sea total.
- Los datos se almacenan en archivos JSON en la carpeta `data/`.
- El sistema realiza backups automáticos antes de modificar archivos críticos.
- El panel web requiere tener el puerto 3000 libre y el backend el 5000.

---

## Créditos y Licencia

Desarrollado por el equipo DesafíoSaber.
Licencia MIT.

---

## Contacto y soporte

Para soporte, sugerencias o reportar errores, utiliza el panel de administración o contacta al equipo de desarrollo.
