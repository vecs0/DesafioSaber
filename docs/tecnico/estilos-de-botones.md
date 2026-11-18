# Estilos de Botones Dinámicos - DesafíoSaber

## Descripción

Se ha implementado un sistema completo de estilos de botones dinámicos que permite modificar la apariencia de los botones del juego desde el panel de administración y ver los cambios reflejados en tiempo real.

## Características

### 🎨 Configuración Visual
- **Forma del Botón**: Redondeado, Circular, Cuadrado
- **Color del Botón**: Color de fondo personalizable
- **Color del Texto**: Color del texto del botón
- **Color Hover**: Color cuando se pasa el mouse por encima
- **Ancho del Borde**: Grosor del borde del botón
- **Relieve**: Tipo de relieve (flat, raised, sunken)
- **Fuente**: Familia, tamaño y peso de la fuente

### ⚡ Actualización en Tiempo Real
- Los cambios se reflejan inmediatamente en el juego
- Notificaciones WebSocket para sincronización instantánea
- Vista previa en el panel de administración

## Archivos Modificados

### Nuevos Archivos
- `data/button_styles.json` - Configuración de estilos de botones
- `test_button_styles.py` - Script de pruebas automatizadas
- `ESTILOS_BOTONES_DINAMICOS.md` - Esta documentación

### Archivos Modificados
- `web_admin/server.py` - Nuevos endpoints API
- `web_admin/src/components/VisualEditor.js` - Interfaz de configuración
- `game/main.py` - Carga y aplicación de estilos dinámicos

## API Endpoints

### GET /api/button-styles
Obtiene la configuración actual de estilos de botones.

**Respuesta:**
```json
{
  "button_shape": "rounded-lg",
  "button_color": "#3498db",
  "button_text_color": "white",
  "button_hover_color": "#2980b9",
  "button_border_width": 0,
  "button_relief": "flat",
  "button_font": "Arial",
  "button_font_size": 14,
  "button_font_weight": "bold"
}
```

### PUT /api/button-styles
Actualiza la configuración de estilos de botones.

**Cuerpo de la petición:**
```json
{
  "button_shape": "rounded-full",
  "button_color": "#ff6b6b",
  "button_text_color": "white",
  "button_hover_color": "#ee5a52",
  "button_border_width": 2,
  "button_relief": "raised",
  "button_font": "Arial",
  "button_font_size": 16,
  "button_font_weight": "bold"
}
```

## Uso en el Panel de Administración

### Acceso
1. Abrir el panel de administración: http://localhost:3000
2. Ir a la sección "Editor Visual"
3. Desplazarse hasta "Estilos de Botones"

### Configuración
1. **Forma del Botón**: Seleccionar entre Redondeado, Circular o Cuadrado
2. **Colores**: Usar el selector de color o escribir el código hexadecimal
3. **Vista Previa**: Ver el resultado en tiempo real
4. **Guardar**: Hacer clic en "Guardar Estilos de Botones"

## Implementación en el Juego

### Carga de Estilos
```python
def load_button_styles(self):
    """Carga los estilos de botones desde la API"""
    try:
        response = requests.get('http://localhost:5000/api/button-styles')
        if response.status_code == 200:
            self.button_styles = response.json()
            print("✅ Estilos de botones actualizados")
    except Exception as e:
        print(f"Error cargando estilos de botones: {e}")
```

### Aplicación de Estilos
```python
def apply_button_style(self, button, style_type="default"):
    """Aplica estilos de botón según la configuración cargada"""
    if not hasattr(self, 'button_styles') or not self.button_styles:
        return
    
    styles = self.button_styles
    
    # Configurar colores y propiedades
    button.configure(
        bg=styles.get('button_color', '#3498db'),
        fg=styles.get('button_text_color', 'white'),
        relief=styles.get('button_relief', 'flat'),
        borderwidth=styles.get('button_border_width', 0),
        font=(styles.get('button_font', 'Arial'), 
              styles.get('button_font_size', 14), 
              styles.get('button_font_weight', 'bold'))
    )
```

## WebSocket Events

### Evento: data_update
Cuando se actualizan los estilos de botones, se emite:
```javascript
socket.emit('data_update', {type: 'button_styles'})
```

### Listener en el Juego
```python
@sio.on('data_update')
def on_data_update(data):
    if data.get('type') == 'button_styles':
        self.app.load_button_styles()
```

## Pruebas

### Ejecutar Pruebas Automatizadas
```bash
python test_button_styles.py
```

### Pruebas Incluidas
1. **API de estilos de botones**: Verifica endpoints GET y PUT
2. **Notificaciones WebSocket**: Prueba sincronización en tiempo real
3. **Integridad del archivo**: Valida estructura del archivo JSON

## Valores por Defecto

```json
{
  "button_shape": "rounded-lg",
  "button_color": "#3498db",
  "button_text_color": "white",
  "button_hover_color": "#2980b9",
  "button_border_width": 0,
  "button_relief": "flat",
  "button_font": "Arial",
  "button_font_size": 14,
  "button_font_weight": "bold"
}
```

## Opciones de Forma

- `rounded-lg`: Bordes redondeados (por defecto)
- `rounded-full`: Bordes completamente circulares
- `rounded-none`: Bordes cuadrados

## Opciones de Relieve

- `flat`: Sin relieve (por defecto)
- `raised`: Relieve elevado
- `sunken`: Relieve hundido
- `groove`: Relieve en surco
- `ridge`: Relieve en cresta

## Compatibilidad

- ✅ Panel de administración web
- ✅ Juego cliente Tkinter
- ✅ Sincronización en tiempo real
- ✅ Persistencia de configuración
- ✅ Pruebas automatizadas

## Troubleshooting

### Problema: Los estilos no se aplican
**Solución**: Verificar que el servidor esté corriendo y el archivo `button_styles.json` exista.

### Problema: No hay actualización en tiempo real
**Solución**: Verificar conexión WebSocket y que el puerto 5000 esté disponible.

### Problema: Error al guardar estilos
**Solución**: Verificar permisos de escritura en la carpeta `data/`.

## Próximas Mejoras

- [ ] Estilos específicos por tipo de botón
- [ ] Temas predefinidos
- [ ] Animaciones personalizables
- [ ] Exportar/importar configuraciones
- [ ] Historial de cambios 