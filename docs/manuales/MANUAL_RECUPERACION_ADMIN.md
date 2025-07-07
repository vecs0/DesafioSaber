# Manual de Recuperación de Contraseña para Administrador Único

## ¿Cuándo usar este procedimiento?
Utiliza este método solo si:
- Hay un solo administrador registrado en el sistema.
- Se ha olvidado la contraseña y no hay otro administrador que pueda restablecerla desde el panel.

---

## Pasos para restablecer la contraseña del administrador único

1. **Accede al servidor donde está instalado el sistema.**
   - Esto puede ser de forma local o remota (por ejemplo, usando Escritorio Remoto, SSH, etc.).

2. **Crea un archivo vacío llamado `reset_admin.txt` en la raíz del backend.**
   - Ubicación típica:
     ```
     /ruta/del/proyecto/reset_admin.txt
     ```
   - Puedes crearlo con un editor de texto o con el siguiente comando en terminal:
     - **En Windows:**
       ```bat
       type nul > reset_admin.txt
       ```
     - **En Linux/Mac:**
       ```bash
       touch reset_admin.txt
       ```

3. **Abre la pantalla de login del panel de administración en tu navegador.**
   - Verás un nuevo enlace:
     > **"Recuperar acceso como único administrador"**

4. **Haz clic en el enlace y sigue las instrucciones del modal.**
   - Ingresa la nueva contraseña para el administrador principal.
   - Confirma el cambio.

5. **¡Listo!**
   - El sistema restablecerá la contraseña y eliminará automáticamente el archivo `reset_admin.txt` por seguridad.
   - Ahora puedes iniciar sesión con la nueva contraseña.

---

## Notas de seguridad
- Este procedimiento solo debe usarse en caso de emergencia.
- El archivo `reset_admin.txt` debe ser eliminado automáticamente, pero si no es así, elimínalo manualmente después del proceso.
- Solo personas autorizadas con acceso al servidor deben realizar este procedimiento.

---

**Este manual puede ser convertido a PDF para su resguardo y evidencia.** 