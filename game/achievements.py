import json
import time
import tkinter as tk

class Achievement:
    def __init__(self, id, name, description, icon, condition):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.condition = condition
        self.unlocked = False

class AchievementManager:
    def __init__(self, root):
        self.root = root
        self.achievements = [
            Achievement(
                "first_win",
                "¡Primera Victoria!",
                "Gana tu primera partida",
                "🏆",
                lambda stats: stats.get('correctas', 0) > stats.get('incorrectas', 0)
            ),
            Achievement(
                "perfect_game",
                "¡Perfección!",
                "Completa una partida sin errores",
                "⭐",
                lambda stats: stats.get('correctas', 0) >= 10 and stats.get('incorrectas', 0) == 0
            ),
            Achievement(
                "speed_demon",
                "Velocista",
                "Completa una partida en menos de 2 minutos",
                "⚡",
                lambda stats: (time.time() - stats['start_time']) < 120
            ),
            Achievement(
                "streak_master",
                "Racha Perfecta",
                "Consigue una racha de 5 respuestas correctas",
                "🔥",
                lambda stats: stats.get('racha', 0) >= 5
            )
        ]
        self.load_achievements()
    
    def load_achievements(self):
        """Carga los logros desbloqueados"""
        try:
            with open('data/achievements.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                unlocked = data.get('unlocked', [])
                for achievement in self.achievements:
                    achievement.unlocked = achievement.id in unlocked
        except:
            pass
    
    def save_achievements(self):
        """Guarda los logros desbloqueados"""
        try:
            unlocked = [a.id for a in self.achievements if a.unlocked]
            with open('data/achievements.json', 'w', encoding='utf-8') as f:
                json.dump({'unlocked': unlocked}, f, ensure_ascii=False, indent=4)
        except:
            pass
    
    def check_achievements(self, stats):
        """Verifica si se han desbloqueado nuevos logros"""
        newly_unlocked = []
        for achievement in self.achievements:
            if not achievement.unlocked and achievement.condition(stats):
                achievement.unlocked = True
                newly_unlocked.append(achievement)
        
        if newly_unlocked:
            self.save_achievements()
            self.show_unlocked_achievements(newly_unlocked)
    
    def show_unlocked_achievements(self, achievements):
        """Muestra una ventana con los logros desbloqueados"""
        dialog = tk.Toplevel(self.root)
        dialog.title("¡Logros Desbloqueados!")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Configurar tema
        dialog.configure(bg="#2c3e50")
        
        # Centrar en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Contenido
        tk.Label(
            dialog,
            text="¡Felicitaciones!",
            font=("Helvetica", 24, "bold"),
            fg="#f1c40f",
            bg="#2c3e50"
        ).pack(pady=(20, 10))
        
        tk.Label(
            dialog,
            text="Has desbloqueado los siguientes logros:",
            font=("Helvetica", 12),
            fg="white",
            bg="#2c3e50"
        ).pack(pady=(0, 20))
        
        for achievement in achievements:
            frame = tk.Frame(dialog, bg="#34495e")
            frame.pack(fill="x", padx=20, pady=5)
            
            tk.Label(
                frame,
                text=achievement.icon,
                font=("Segoe UI Emoji", 24),
                bg="#34495e",
                fg="white"
            ).pack(side="left", padx=(10, 10))
            
            text_frame = tk.Frame(frame, bg="#34495e")
            text_frame.pack(side="left", fill="x", expand=True, pady=5)
            
            tk.Label(
                text_frame,
                text=achievement.name,
                font=("Helvetica", 12, "bold"),
                bg="#34495e",
                fg="white"
            ).pack(anchor="w")
            
            tk.Label(
                text_frame,
                text=achievement.description,
                font=("Helvetica", 10),
                bg="#34495e",
                fg="#95a5a6"
            ).pack(anchor="w")
        
        btn = tk.Button(
            dialog,
            text="¡Genial!",
            command=dialog.destroy,
            font=("Helvetica", 12),
            bg="#2ecc71",
            fg="white",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn.pack(pady=20)
        
        def on_enter(e):
            btn.configure(bg="#27ae60")
        
        def on_leave(e):
            btn.configure(bg="#2ecc71")
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def show_all_achievements(self):
        """Muestra todos los logros disponibles"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Logros")
        dialog.geometry("500x600")
        dialog.configure(bg="#2c3e50")
        
        # Centrar en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Título
        tk.Label(
            dialog,
            text="🏆 Logros",
            font=("Helvetica", 24, "bold"),
            fg="#f1c40f",
            bg="#2c3e50"
        ).pack(pady=20)
        
        # Frame para los logros con scroll
        container = tk.Frame(dialog, bg="#2c3e50")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        canvas = tk.Canvas(container, bg="#2c3e50", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2c3e50")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar todos los logros
        for achievement in self.achievements:
            frame = tk.Frame(scrollable_frame, bg="#34495e")
            frame.pack(fill="x", pady=5)
            
            icon_label = tk.Label(
                frame,
                text=achievement.icon,
                font=("Segoe UI Emoji", 32),
                bg="#34495e",
                fg="white" if achievement.unlocked else "#95a5a6"
            )
            icon_label.pack(side="left", padx=15, pady=10)
            
            text_frame = tk.Frame(frame, bg="#34495e")
            text_frame.pack(side="left", fill="x", expand=True, pady=10)
            
            name_label = tk.Label(
                text_frame,
                text=achievement.name,
                font=("Helvetica", 14, "bold"),
                bg="#34495e",
                fg="white" if achievement.unlocked else "#95a5a6"
            )
            name_label.pack(anchor="w")
            
            desc_label = tk.Label(
                text_frame,
                text=achievement.description,
                font=("Helvetica", 10),
                bg="#34495e",
                fg="#95a5a6"
            )
            desc_label.pack(anchor="w")
            
            status_label = tk.Label(
                frame,
                text="✓" if achievement.unlocked else "🔒",
                font=("Segoe UI Emoji", 24),
                bg="#34495e",
                fg="#2ecc71" if achievement.unlocked else "#95a5a6"
            )
            status_label.pack(side="right", padx=15)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón cerrar
        btn = tk.Button(
            dialog,
            text="Cerrar",
            command=dialog.destroy,
            font=("Helvetica", 12),
            bg="#95a5a6",
            fg="white",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        btn.pack(pady=20)
        
        def on_enter(e):
            btn.configure(bg="#7f8c8d")
        
        def on_leave(e):
            btn.configure(bg="#95a5a6")
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave) 