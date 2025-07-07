import os
import sys
import tkinter as tk
from tkinter import messagebox
import pygame
from PIL import Image, ImageTk

# Agregar el directorio del juego al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

# Importar la aplicación principal del juego
from game.main import DesafioSaberApp

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets', 'sounds'))
        try:
            self.sounds['acierto'] = pygame.mixer.Sound(os.path.join(base_path, 'acierto.mp3'))
        except Exception as e:
            print(f"Error cargando sonido acierto.mp3: {e}")
        try:
            self.sounds['errado'] = pygame.mixer.Sound(os.path.join(base_path, 'errado.mp3'))
        except Exception as e:
            print(f"Error cargando sonido errado.mp3: {e}")
        try:
            self.sounds['despliegue'] = pygame.mixer.Sound(os.path.join(base_path, 'despliegue_opciones.mp3'))
        except Exception as e:
            print(f"Error cargando sonido despliegue_opciones.mp3: {e}")
        try:
            self.sounds['intro_music'] = pygame.mixer.Sound(os.path.join(base_path, 'intro.mp3'))
        except Exception as e:
            print(f"Error cargando sonido intro.mp3: {e}")

    def setup_main_menu(self):
        """Configura el menú principal"""
        self.clear_main_frame()
        main_container = tk.Frame(self.main_frame)
        main_container.pack(expand=True, fill="both")
        canvas = tk.Canvas(main_container)
        canvas.pack(fill="both", expand=True)
        try:
            bg_image = Image.open('assets/images/menu_background.png')
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            bg_image = bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        except Exception as e:
            print(f"Error al cargar imagen de fondo: {e}")
            canvas.configure(bg="#1a2a2e")
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
        # ... resto del método ... 

def main():
    """Función principal para iniciar el juego"""
    try:
        # Inicializar pygame
        pygame.init()
        pygame.mixer.init()
        
        # Crear la ventana principal
        root = tk.Tk()
        root.title("Desafío Saber")
        
        # Configurar la ventana
        root.geometry("1200x800")
        root.minsize(800, 600)
        
        # Centrar la ventana
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Iniciar la aplicación
        app = DesafioSaberApp(root)
        
        # Ejecutar el bucle principal
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar el juego: {str(e)}")
        print(f"Error: {e}")
    finally:
        # Limpiar pygame
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    main() 