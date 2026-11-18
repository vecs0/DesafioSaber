<div align="center">

<img src="assets/images/logo.png" alt="Logo de DesafíoSaber" width="120">

# DesafíoSaber

Juego de trivia de escritorio con **panel de administración web** y **sincronización en tiempo real**.
Ruleta de categorías, 3 modos de juego, 760 preguntas, ranking y logros.

[![Descargar para Windows](https://img.shields.io/badge/Descargar_para_Windows-.exe-2ea44f?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/vecs0/DesafioSaber/releases/latest)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-3776AB)
![Pygame](https://img.shields.io/badge/Pygame-audio-1b8a3a)
![Flask](https://img.shields.io/badge/Flask-API-000000?logo=flask&logoColor=white)
![Socket.IO](https://img.shields.io/badge/Socket.IO-tiempo_real-010101?logo=socketdotio&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3-06B6D4?logo=tailwindcss&logoColor=white)
![Licencia MIT](https://img.shields.io/badge/licencia-MIT-green)

<img src="docs/screenshots/juego-menu.webp" alt="Menú principal de DesafíoSaber" width="820">

</div>

---

## <img src="docs/icons/descargar.svg" width="22" align="top" alt=""> Descarga y demo

**[Descargar la última versión para Windows](https://github.com/vecs0/DesafioSaber/releases/latest)**

1. Descargá `DesafioSaber-v1.1.0-windows.zip` desde **Releases**.
2. Descomprimí la carpeta completa.
3. Ejecutá `DesafioSaber.exe`. No hace falta instalar Python.

> Windows puede mostrar el aviso "Windows protegió su PC" porque el ejecutable no está firmado. Elegí **Más información → Ejecutar de todas formas**.

El ejecutable incluye el juego completo. El panel de administración web se ejecuta desde el código fuente: ver [Correr en local](#-correr-en-local).

## <img src="docs/icons/funcionalidades.svg" width="22" align="top" alt=""> Funcionalidades

**Juego de escritorio**
- **3 modos de juego**:
  - **Clásico**: 15 preguntas, 20 s cada una.
  - **Contrarreloj**: 60 s totales y preguntas ilimitadas.
  - **Duelo**: 2 jugadores por turnos, con penalización por error.
- **6 categorías**: Historia, Ciencia, Geografía, Arte, Deportes y Entretenimiento, con 760 preguntas en 3 niveles de dificultad.
- **Ruleta animada** para elegir categoría, con música y efectos de sonido.
- **Puntuación dinámica** según el tiempo de respuesta, con resultados detallados.
- **Ranking global** filtrable por modo y categoría.
- **Registro de jugadores**, logros desbloqueables y estadísticas personales.

**Panel de administración web**
- **Dashboard** con métricas de preguntas, jugadores y partidas.
- **CRUD** de preguntas, categorías, modos de juego y jugadores.
- **Editor visual** de colores por categoría y estilos de botones.
- **Gestión de recursos** (imágenes y sonidos) y reportes de error.
- **Sincronización en tiempo real**: los cambios del panel llegan al juego al instante por WebSocket.

## <img src="docs/icons/capturas.svg" width="22" align="top" alt=""> Capturas

### Juego de escritorio

| Modos de juego | Pregunta |
|---|---|
| ![Selección de modo](docs/screenshots/juego-modos.webp) | ![Pregunta en curso](docs/screenshots/juego-pregunta.webp) |
| **Resultados** | **Ranking global** |
| ![Resultados finales](docs/screenshots/juego-resultado.webp) | ![Ranking global](docs/screenshots/juego-ranking.webp) |

### Panel de administración

| Inicio de sesión | Dashboard |
|---|---|
| ![Login del panel](docs/screenshots/panel-login.webp) | ![Dashboard](docs/screenshots/panel-dashboard.webp) |
| **Gestión de preguntas** | **Editor visual** |
| ![Gestión de preguntas](docs/screenshots/panel-preguntas.webp) | ![Editor visual](docs/screenshots/panel-editor-visual.webp) |
| **Categorías** | **Ranking** |
| ![Categorías](docs/screenshots/panel-categorias.webp) | ![Ranking en el panel](docs/screenshots/panel-ranking.webp) |

## <img src="docs/icons/arquitectura.svg" width="22" align="top" alt=""> Arquitectura

```
┌────────────────────────┐   HTTP / REST    ┌─────────────────────────┐   HTTP + WebSocket   ┌──────────────────────┐
│  Juego de escritorio   │ ◄──────────────► │   Backend Flask         │ ◄──────────────────► │  Panel de admin      │
│  Python · Tkinter      │   WebSocket      │   API REST + Socket.IO  │                      │  React · Tailwind    │
│  Pygame (audio)        │ ◄─────────────── │   puerto 5000           │                      │  puerto 3000         │
└───────────┬────────────┘   (cambios)      └────────────┬────────────┘                      └──────────────────────┘
            │                                            │
            └──────────────►  data/*.json  ◄─────────────┘
                     (preguntas, usuarios, ranking, logros, configuración)
```

- El **juego** funciona solo, leyendo los JSON de `data/`. Si el backend está activo, además sincroniza estadísticas y recibe cambios al instante.
- El **backend** expone 47 endpoints REST y emite eventos por Socket.IO cada vez que cambia un dato.
- El **panel** consume la API y se actualiza en vivo al recibir esos eventos.

## <img src="docs/icons/tecnologias.svg" width="22" align="top" alt=""> Tecnologías

| Capa | Tecnologías |
|---|---|
| **Juego** | Python 3.10+, Tkinter, Pygame (audio), Pillow |
| **Backend** | Flask, Flask-SocketIO, Flask-CORS |
| **Panel web** | React 18, Tailwind CSS, Chart.js, Socket.IO Client |
| **Datos** | Archivos JSON con backups automáticos |
| **Distribución** | PyInstaller (ejecutable de Windows) y GitHub Releases |
| **Pruebas** | pytest |

## <img src="docs/icons/estructura.svg" width="22" align="top" alt=""> Estructura

```
DesafioSaber/
├── game/                  # Juego de escritorio (Tkinter)
│   ├── main.py            # Punto de entrada y pantallas del juego
│   ├── paths.py           # Rutas del proyecto (código fuente y .exe)
│   ├── wheel_animation.py # Ruleta de categorías
│   ├── achievements.py    # Sistema de logros
│   ├── user_registration.py
│   ├── api_client.py      # Cliente de la API
│   └── cloud_sync.py      # Sincronización con el backend
├── web_admin/             # Panel de administración
│   ├── server.py          # Backend Flask + Socket.IO
│   └── src/components/    # Componentes React
├── data/                  # Datos del juego en JSON
├── assets/                # Imágenes y sonidos
├── scripts/               # Iniciar, instalar y compilar
├── tools/                 # Utilidades de mantenimiento de datos
├── tests/                 # Pruebas con pytest
└── docs/                  # Manuales, documentación técnica y capturas
```

## <img src="docs/icons/local.svg" width="22" align="top" alt=""> Correr en local

**Requisitos:** Python 3.10+ y Node.js 18+.

```bash
git clone https://github.com/vecs0/DesafioSaber.git
cd DesafioSaber
python -m venv venv
venv\Scripts\activate          # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

| Qué iniciar | Comando |
|---|---|
| Todo (backend + panel + juego) | `python scripts/start_all.py` |
| Solo el juego | `python game/main.py` |
| Solo el backend | `python scripts/start_backend.py` |
| Solo el panel web | `python scripts/start_frontend.py` |

El panel queda en http://localhost:3000 y el backend en http://localhost:5000. En Windows también podés usar `scripts\install_windows.bat` para instalar todo de una vez.

**Credenciales de demo del panel:** usuario `admin`, contraseña `admin123`. Son datos ficticios incluidos en `data/admins.json`.

### Compilar el ejecutable

```bash
pip install -r requirements-dev.txt
python scripts/build_exe.py
```

Genera `release/DesafioSaber-v<versión>-windows.zip`, listo para subir a un Release.

## <img src="docs/icons/pruebas.svg" width="22" align="top" alt=""> Pruebas

```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

Hay 40 pruebas: flujos de preguntas, categorías, modos de juego, usuarios, puntuación, logros y sincronización. Algunas pruebas de integración necesitan el backend corriendo en el puerto 5000.

## <img src="docs/icons/documentacion.svg" width="22" align="top" alt=""> Documentación

| Documento | Contenido |
|---|---|
| [Manual de usuario](docs/manual-usuario.md) | Cómo jugar y usar el panel |
| [Recuperar el acceso de admin](docs/recuperacion-admin.md) | Restablecer la contraseña del administrador |
| [Documentación técnica](docs/tecnico/) | Arquitectura, puntuación, logros, usuarios, estilos y rendimiento |
| [Historial de desarrollo](docs/historial/) | Correcciones, checklists y notas de versiones anteriores |

## <img src="docs/icons/seguridad.svg" width="22" align="top" alt=""> Notas de seguridad

DesafíoSaber es un **proyecto local y educativo**: el backend escucha solo en `127.0.0.1` y no está pensado para publicarse en internet.

- El inicio de sesión del panel se verifica en el servidor, y la API nunca envía contraseñas al navegador.
- El modo debug y el acceso desde la red local se activan solo si se pide, con `DESAFIO_DEBUG=1` y `DESAFIO_HOST=0.0.0.0`.
- Para usarlo en producción faltaría guardar las contraseñas con hash y sal, usar sesiones con tokens y proteger todos los endpoints.

## <img src="docs/icons/versiones.svg" width="22" align="top" alt=""> Versiones

| Versión | Fecha | Cambios |
|---|---|---|
| **v1.1.0** | 2026 | Reorganización del repositorio, rutas que funcionan desde cualquier carpeta y desde el `.exe`, menú que se adapta al tamaño de la ventana, login verificado en el servidor, backend local por defecto, dependencias unificadas y ejecutable para Windows |
| **v1.0.0** | Julio 2025 | Juego de escritorio, panel de administración y sincronización en tiempo real |

## <img src="docs/icons/autor.svg" width="22" align="top" alt=""> Autor

<table>
  <tr>
    <td><img src="https://github.com/vecs0.png" width="80" alt="Foto de perfil de vecs0"></td>
    <td>
      <strong>Victor Emmanuel Cabrera Sosa</strong><br>
      <a href="https://github.com/vecs0">vecs0 · github.com/vecs0</a>
    </td>
  </tr>
</table>

## <img src="docs/icons/licencia.svg" width="22" align="top" alt=""> Licencia

Distribuido bajo la licencia **MIT**. Consultá el archivo [LICENSE](LICENSE) para el texto completo.

| Permisos | Condiciones | Limitaciones |
|---|---|---|
| ✔ Uso comercial<br>✔ Modificación<br>✔ Distribución<br>✔ Uso privado | Incluir el aviso de copyright y la licencia | ✖ Sin garantía<br>✖ Sin responsabilidad |

**Contenido de terceros:** Flask, React, Tailwind CSS, Pygame y las demás dependencias se distribuyen bajo sus propias licencias de código abierto. Los sonidos e imágenes de `assets/` pertenecen a sus respectivos autores.

© 2025 Victor Emmanuel Cabrera Sosa
