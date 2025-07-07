import tkinter as tk
import math
import random

class WheelAnimation(tk.Canvas):
    def __init__(self, parent, size=200, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self.size = size
        self.configure(bg="#1a2a2e", highlightthickness=0)
        
        # Colores para los segmentos de la ruleta
        self.colors = ["#2ecc71", "#3498db", "#e74c3c", "#f1c40f", "#9b59b6", "#1abc9c"]
        self.num_segments = len(self.colors)
        
        # Ángulo actual para la animación
        self.current_angle = 0
        self.spinning = False
        self.speed = 0
        
        # Dibujar la ruleta inicial
        self.draw_wheel()
        
    def draw_wheel(self):
        """Dibuja la ruleta con los segmentos de colores"""
        self.delete("wheel")  # Limpiar dibujos anteriores
        
        # Calcular el centro
        center = self.size / 2
        radius = (self.size * 0.8) / 2  # 80% del tamaño para dejar margen
        
        # Dibujar cada segmento
        segment_angle = 360 / self.num_segments
        for i in range(self.num_segments):
            start_angle = (i * segment_angle + self.current_angle) % 360
            end_angle = ((i + 1) * segment_angle + self.current_angle) % 360
            
            # Convertir ángulos a radianes para las coordenadas
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            # Crear el arco
            self.create_arc(
                center - radius,
                center - radius,
                center + radius,
                center + radius,
                start=start_angle,
                extent=segment_angle,
                fill=self.colors[i],
                tags="wheel"
            )
            
            # Agregar un círculo pequeño en el centro
            inner_radius = radius * 0.15
            self.create_oval(
                center - inner_radius,
                center - inner_radius,
                center + inner_radius,
                center + inner_radius,
                fill="#2c3e50",
                outline="#ffffff",
                tags="wheel"
            )
            
            # Agregar líneas decorativas
            line_angle = math.radians(start_angle)
            x = center + radius * math.cos(line_angle)
            y = center + radius * math.sin(line_angle)
            self.create_line(
                center, center,
                x, y,
                fill="#ffffff",
                width=2,
                tags="wheel"
            )
    
    def spin(self):
        """Inicia el giro de la ruleta"""
        if not self.spinning:
            self.spinning = True
            self.speed = random.uniform(5, 10)  # Velocidad inicial aleatoria
            self.animate()
    
    def animate(self):
        """Anima el giro de la ruleta"""
        if self.spinning:
            self.current_angle = (self.current_angle + self.speed) % 360
            self.draw_wheel()
            
            # Reducir gradualmente la velocidad
            self.speed *= 0.99
            
            # Detener cuando la velocidad sea muy baja
            if self.speed < 0.1:
                self.spinning = False
            else:
                self.after(20, self.animate)

class MotivationalText(tk.Label):
    def __init__(self, parent, **kwargs):
        # Remover argumentos que podrían estar duplicados
        if 'font' in kwargs:
            del kwargs['font']
        if 'fg' in kwargs:
            del kwargs['fg']
        if 'bg' in kwargs:
            del kwargs['bg']
            
        super().__init__(
            parent,
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#3498db",
            **kwargs
        )
        
        self.phrases = [
            "¡Demuestra tu conocimiento!",
            "¡Cada pregunta es una oportunidad!",
            "¡El saber no ocupa lugar!",
            "¡Aprende mientras te diviertes!",
            "¡El conocimiento es poder!",
            "¡Supérate a ti mismo!",
            "¡La curiosidad es la clave del éxito!",
            "¡Cada error es una lección!",
            "¡Tú puedes ser el próximo campeón!",
            "¡El aprendizaje nunca termina!"
        ]
        
        self.current_index = random.randint(0, len(self.phrases) - 1)
        self.fade_counter = 20
        self.fading_out = False
        self.configure(text=self.phrases[self.current_index])
        
        # Iniciar la animación
        self.animate_text()
    
    def animate_text(self):
        """Anima el cambio de texto con efecto de fade"""
        if self.fading_out:
            self.fade_counter -= 1
            opacity = self.fade_counter / 20
        else:
            self.fade_counter += 1
            opacity = self.fade_counter / 20
        
        # Ajustar el color del texto según la opacidad
        color = f"#{int(opacity * 255):02x}{int(opacity * 255):02x}{int(opacity * 255):02x}"
        self.configure(fg=color)
        
        if self.fading_out and self.fade_counter <= 0:
            self.fading_out = False
            # Seleccionar una nueva frase aleatoria diferente a la actual
            new_index = self.current_index
            while new_index == self.current_index:
                new_index = random.randint(0, len(self.phrases) - 1)
            self.current_index = new_index
            self.configure(text=self.phrases[self.current_index])
        elif not self.fading_out and self.fade_counter >= 20:
            self.fading_out = True
            self.after(2000, lambda: self.fading_out or setattr(self, 'fading_out', True))  # Mantener visible por 2 segundos
        
        # Continuar la animación
        self.after(50, self.animate_text) 