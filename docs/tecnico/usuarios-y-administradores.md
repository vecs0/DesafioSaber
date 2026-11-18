# Documentación: Separación de Usuarios (Jugadores y Administradores) en DesafíoSaber

## Objetivo
Garantizar que los datos, formularios y accesos de jugadores y administradores estén completamente separados, evitando cualquier cruce de información o permisos entre ambos roles.

---

## 1. Jugadores
- **Registro e inicio de sesión:**
  - Solo pueden registrarse e iniciar sesión desde el juego (Tkinter).
  - No existe formulario de login/registro de jugadores en el panel web.
- **Datos almacenados en:** `data/usuarios.json`
- **Aparición en el sistema:**
  - Solo visibles en el panel web en las secciones de "Gestión de Jugadores" y "Ranking".
  - No pueden acceder al panel de administración ni a sus rutas, aunque editen la URL.
- **Gestión:**
  - Los administradores pueden ver, editar o eliminar jugadores desde el panel, pero los jugadores no pueden autogestionarse desde el panel.

---

## 2. Administradores
- **Registro e inicio de sesión:**
  - Solo pueden registrarse e iniciar sesión desde el panel web (React).
  - No existe formulario de login/registro de administradores en el juego.
- **Datos almacenados en:** `data/admins.json`
- **Aparición en el sistema:**
  - Solo visibles en el panel web en la sección "Gestión de Usuarios Administradores" (Configuración).
  - Solo los administradores pueden acceder al panel y gestionar el sistema.
- **Gestión:**
  - Los administradores pueden agregar, editar o eliminar otros administradores desde el panel.

---

## 3. Endpoints y archivos de datos
- **Jugadores:**
  - Endpoints: `/api/players`, `/api/players/<id>`
  - Archivo: `usuarios.json`
- **Administradores:**
  - Endpoints: `/api/admin-users`, `/api/admin-users/<id>`
  - Archivo: `admins.json`

---

## 4. Protección de rutas y roles
- El panel web solo permite acceso a administradores autenticados.
- El juego solo permite acceso a jugadores autenticados.
- No hay cruce de roles ni de formularios.
- Si un usuario intenta acceder a una ruta que no le corresponde, se le deniega el acceso.

---

## 5. Interfaces
- **Visualmente:**
  - Los formularios de login/registro de jugadores y administradores son completamente independientes y no comparten código ni rutas.
  - El panel web nunca muestra formularios de jugadores.
  - El juego nunca muestra formularios de administradores.

---

## 6. Resumen gráfico

```
Juego (Tkinter)
  └─ Registro/Login de Jugadores
      └─ usuarios.json
      └─ Acceso solo a juego

Panel Web (React)
  └─ Registro/Login de Administradores
      └─ admins.json
      └─ Acceso solo a panel
  └─ Gestión de Jugadores (solo visualización/edición)
  └─ Gestión de Administradores (solo visualización/edición)
```

---

## 7. Buenas prácticas
- Mantener siempre separados los endpoints, archivos y formularios de ambos roles.
- Revisar y proteger rutas tanto en backend como en frontend.
- Documentar cualquier cambio en la lógica de acceso o gestión de usuarios.

---

**Este flujo garantiza máxima seguridad, claridad y mantenibilidad en el sistema DesafíoSaber.** 