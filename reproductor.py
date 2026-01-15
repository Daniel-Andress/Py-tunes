import customtkinter as ctk
import keyboard
import math
from PIL import Image, ImageDraw

class CompactMediaApp:
    def __init__(self):
        # --- Configuración de la Ventana Principal ---
        self.app = ctk.CTk()
        self.app.title("")
        # --- ¡NUEVO GEOMETRÍA! Pequeña y vertical ---
        self.app.geometry("80x220") # Ancho x Alto (más alto para la barra)
        self.app.minsize(80, 220)
        self.app.maxsize(100, 300) # Máximo 100px de ancho, como pediste
        self.app.resizable(True, True)

        # Estilo de ventana sin bordes
        self.app.overrideredirect(True)
        self.app.attributes('-topmost', True)
        self.app.attributes('-alpha', 0.95)

        # Estado de la aplicación
        self.is_playing = False
        self.current_progress = 0.0  # Progreso de 0.0 a 1.0
        self.progress_direction = 1  # 1 para avanzar, -1 para retroceder

        # Estilo
        ctk.set_appearance_mode("dark")

        self.create_widgets()

    def create_gradient_image(self, width, height, color1, color2):
        """Crea una imagen PIL con un gradiente lineal."""
        image = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(image)
        
        for i in range(height):
            r1, g1, b1, a1 = color1
            r2, g2, b2, a2 = color2
            ratio = i / height
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            a = int(a1 + (a2 - a1) * ratio)
            
            draw.line([(0, i), (width, i)], fill=(r, g, b, a))
            
        return image

    def create_widgets(self):
        # --- 1. Frame principal ---
        self.main_frame = ctk.CTkFrame(self.app, corner_radius=12, fg_color="#1e1e1e")
        self.main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # --- 2. Fondo con Gradiente ---
        pil_image = self.create_gradient_image(100, 300, (25, 25, 25, 255), (45, 45, 45, 255))
        self.gradient_image = ctk.CTkImage(pil_image, pil_image)

        self.bg_label = ctk.CTkLabel(self.main_frame, text="", image=self.gradient_image)
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        
        # --- 3. Frame para los controles (ahora vertical) ---
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        
        # --- Botón de Cerrar (arriba a la derecha) ---
        ctk.CTkButton(
            self.main_frame, text="✕", command=self.app.quit, 
            width=18, height=18, corner_radius=9, 
            fg_color="transparent", hover_color="#ff4757", text_color="#707070", 
            font=("Segoe UI", 9)
        ).place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

        # --- Ícono musical (arriba) ---
        ctk.CTkLabel(content_frame, text="♫", font=("Segoe UI Emoji", 20), text_color="#00d4ff").pack(pady=(10, 5))

        # --- Controles de Reproducción (apilados verticalmente) ---
        controls_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        controls_frame.pack(expand=True, fill="both", padx=10, pady=5)

        # Estilo para los botones pequeños
        btn_style = {
            "fg_color": "transparent", 
            "hover_color": ("#2a2a2a", "#1a1a1a"),
            "text_color": "#a0a0a0", 
            "font": ("Segoe UI", 14), 
            "width": 40, 
            "height": 35, 
            "corner_radius": 8
        }

        # Botón Anterior
        ctk.CTkButton(controls_frame, text="⏮", command=self.prev_song, **btn_style).pack(pady=2)
        
        # Botón Play/Pausa (el más grande y central)
        self.play_pause_button = ctk.CTkButton(
            controls_frame, text="▶", command=self.toggle_play_pause, 
            fg_color="transparent", hover_color="#00d4ff", text_color="#00d4ff", 
            font=("Segoe UI", 16), width=45, height=40, corner_radius=10
        )
        self.play_pause_button.pack(pady=5)

        # Botón Siguiente
        ctk.CTkButton(controls_frame, text="⏭", command=self.next_song, **btn_style).pack(pady=2)

        # --- Barra de Progreso ---
        progress_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=30)
        progress_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame, 
            width=50, 
            height=4,
            corner_radius=2,
            fg_color="#2a2a2a",
            progress_color="#00d4ff"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        # Hacer la ventana arrastrable desde cualquier parte
        content_frame.bind('<Button-1>', self.start_move)
        self.bg_label.bind('<Button-1>', self.start_move) # También hacerlo arrastrable desde el fondo
        self.main_frame.bind('<Button-1>', self.start_move)

        content_frame.bind('<B1-Motion>', self.do_move)
        self.bg_label.bind('<B1-Motion>', self.do_move)
        self.main_frame.bind('<B1-Motion>', self.do_move)


    # --- Funciones de Control ---
    def toggle_play_pause(self):
        self.is_playing = not self.is_playing
        self.play_pause_button.configure(text="⏸" if self.is_playing else "▶")
        keyboard.press_and_release('play/pause media')
        if self.is_playing:
            self.animate_progress()

    def next_song(self):
        keyboard.press_and_release('next track')
        self.current_progress = 0.0
        self.progress_bar.set(0)

    def prev_song(self):
        keyboard.press_and_release('prev track')
        self.current_progress = 0.0
        self.progress_bar.set(0)

    # --- Funciones de Movimiento ---
    def start_move(self, event):
        self.app.x = event.x
        self.app.y = event.y

    def do_move(self, event):
        deltax = event.x - self.app.x
        deltay = event.y - self.app.y
        x = self.app.winfo_x() + deltax
        y = self.app.winfo_y() + deltay
        self.app.geometry(f"+{x}+{y}")

    # --- Animación de la Barra de Progreso ---
    def animate_progress(self):
        """Anima la barra de progreso mientras está reproduciendo"""
        if self.is_playing:
            # Incrementar progreso (simula una canción de ~3 minutos)
            self.current_progress += 0.005
            
            # Si llega al final, reiniciar
            if self.current_progress >= 1.0:
                self.current_progress = 0.0
            
            self.progress_bar.set(self.current_progress)
            
            # Llamar de nuevo después de 50ms
            self.app.after(50, self.animate_progress)

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = CompactMediaApp()
    app.run()