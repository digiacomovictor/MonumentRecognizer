"""
Modern UI System per Monument Recognizer
Implementa Material Design 3 con theme engine e componenti avanzati
"""

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import RoundedRectangle, Color, Ellipse, Line
from kivy.core.window import Window
from kivy.clock import Clock
from typing import Dict, Tuple, Optional, Callable
from enum import Enum
import json
import os


class ThemeMode(Enum):
    """Modalità tema dell'app"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Basato su sistema


class MaterialColors:
    """Palette colori Material Design 3"""
    
    # Light theme colors
    LIGHT = {
        'primary': '#6750A4',
        'on_primary': '#FFFFFF',
        'primary_container': '#EADDFF',
        'on_primary_container': '#21005D',
        
        'secondary': '#625B71',
        'on_secondary': '#FFFFFF',
        'secondary_container': '#E8DEF8',
        'on_secondary_container': '#1D192B',
        
        'tertiary': '#7D5260',
        'on_tertiary': '#FFFFFF',
        'tertiary_container': '#FFD8E4',
        'on_tertiary_container': '#31111D',
        
        'error': '#BA1A1A',
        'on_error': '#FFFFFF',
        'error_container': '#FFDAD6',
        'on_error_container': '#410002',
        
        'background': '#FFFBFE',
        'on_background': '#1C1B1F',
        'surface': '#FFFBFE',
        'on_surface': '#1C1B1F',
        'surface_variant': '#E7E0EC',
        'on_surface_variant': '#49454F',
        
        'outline': '#79747E',
        'outline_variant': '#CAC4D0',
        'shadow': '#000000',
        'surface_tint': '#6750A4',
        'inverse_surface': '#313033',
        'inverse_on_surface': '#F4EFF4',
        'inverse_primary': '#D0BCFF',
    }
    
    # Dark theme colors
    DARK = {
        'primary': '#D0BCFF',
        'on_primary': '#381E72',
        'primary_container': '#4F378B',
        'on_primary_container': '#EADDFF',
        
        'secondary': '#CCC2DC',
        'on_secondary': '#332D41',
        'secondary_container': '#4A4458',
        'on_secondary_container': '#E8DEF8',
        
        'tertiary': '#EFB8C8',
        'on_tertiary': '#492532',
        'tertiary_container': '#633B48',
        'on_tertiary_container': '#FFD8E4',
        
        'error': '#FFB4AB',
        'on_error': '#690005',
        'error_container': '#93000A',
        'on_error_container': '#FFDAD6',
        
        'background': '#1C1B1F',
        'on_background': '#E6E1E5',
        'surface': '#1C1B1F',
        'on_surface': '#E6E1E5',
        'surface_variant': '#49454F',
        'on_surface_variant': '#CAC4D0',
        
        'outline': '#938F99',
        'outline_variant': '#49454F',
        'shadow': '#000000',
        'surface_tint': '#D0BCFF',
        'inverse_surface': '#E6E1E5',
        'inverse_on_surface': '#313033',
        'inverse_primary': '#6750A4',
    }


class ThemeManager:
    """Manager centrale per i temi dell'applicazione"""
    
    def __init__(self):
        self.current_mode = ThemeMode.LIGHT
        self.theme_file = "user_theme.json"
        self.callbacks = []
        self.load_theme_preference()
    
    def get_color(self, color_name: str) -> Tuple[float, float, float, float]:
        """Ottiene un colore dal tema attuale"""
        colors = MaterialColors.LIGHT if self.current_mode == ThemeMode.LIGHT else MaterialColors.DARK
        hex_color = colors.get(color_name, colors['primary'])
        rgba = get_color_from_hex(hex_color)
        return rgba
    
    def get_colors(self) -> Dict[str, str]:
        """Ottiene tutti i colori del tema attuale"""
        return MaterialColors.LIGHT if self.current_mode == ThemeMode.LIGHT else MaterialColors.DARK
    
    def set_theme(self, mode: ThemeMode):
        """Cambia il tema dell'applicazione"""
        if mode != self.current_mode:
            self.current_mode = mode
            self.save_theme_preference()
            self.notify_theme_changed()
    
    def toggle_theme(self):
        """Alterna tra tema chiaro e scuro"""
        new_mode = ThemeMode.DARK if self.current_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        self.set_theme(new_mode)
    
    @property
    def is_dark_mode(self) -> bool:
        """Controlla se è attiva la modalità scura"""
        return self.current_mode == ThemeMode.DARK
    
    def register_callback(self, callback: Callable):
        """Registra callback per cambiamenti tema"""
        self.callbacks.append(callback)
    
    def notify_theme_changed(self):
        """Notifica tutti i callback registrati"""
        for callback in self.callbacks:
            try:
                callback(self.current_mode)
            except Exception as e:
                print(f"Errore in theme callback: {e}")
    
    def save_theme_preference(self):
        """Salva preferenza tema su file"""
        try:
            with open(self.theme_file, 'w') as f:
                json.dump({'theme_mode': self.current_mode.value}, f)
        except Exception as e:
            print(f"Errore salvataggio tema: {e}")
    
    def load_theme_preference(self):
        """Carica preferenza tema da file"""
        try:
            if os.path.exists(self.theme_file):
                with open(self.theme_file, 'r') as f:
                    data = json.load(f)
                    mode_str = data.get('theme_mode', 'light')
                    self.current_mode = ThemeMode(mode_str)
        except Exception as e:
            print(f"Errore caricamento tema: {e}")
            self.current_mode = ThemeMode.LIGHT


# Istanza globale del theme manager
theme_manager = ThemeManager()


class MaterialCard(FloatLayout):
    """Card Material Design con ombra e bordi arrotondati"""
    
    def __init__(self, elevation=2, corner_radius=12, **kwargs):
        super().__init__(**kwargs)
        self.elevation = elevation
        self.corner_radius = corner_radius
        
        # Registra per aggiornamenti tema
        theme_manager.register_callback(self.update_theme)
        
        # Costruisce grafica iniziale
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        Clock.schedule_once(lambda dt: self.update_graphics(), 0)
    
    def update_graphics(self, *args):
        """Aggiorna la grafica della card"""
        self.canvas.before.clear()
        with self.canvas.before:
            # Ombra (solo in light mode)
            if theme_manager.current_mode == ThemeMode.LIGHT:
                Color(*get_color_from_hex('#00000020'))
                RoundedRectangle(
                    pos=(self.pos[0] + self.elevation, self.pos[1] - self.elevation),
                    size=self.size,
                    radius=[self.corner_radius] * 4
                )
            
            # Background della card
            Color(*theme_manager.get_color('surface'))
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.corner_radius] * 4
            )
            
            # Bordo (più visibile in dark mode)
            if theme_manager.current_mode == ThemeMode.DARK:
                Color(*theme_manager.get_color('outline_variant'))
                Line(
                    rounded_rectangle=[*self.pos, *self.size, self.corner_radius],
                    width=dp(1)
                )
    
    def update_theme(self, mode):
        """Callback per aggiornamento tema"""
        self.update_graphics()


class MaterialButton(ButtonBehavior, FloatLayout):
    """Pulsante Material Design con ripple effect"""
    
    def __init__(self, text='', button_type='filled', icon='', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.button_type = button_type  # filled, outlined, text
        self.icon = icon
        self.size_hint = kwargs.get('size_hint', (None, None))
        self.size = kwargs.get('size', (dp(120), dp(40)))
        
        # Registra per aggiornamenti tema
        theme_manager.register_callback(self.update_theme)
        
        # Label per il testo
        self.label = Label(
            text=self.text,
            color=self.get_text_color(),
            font_size=sp(14),
            bold=True
        )
        self.add_widget(self.label)
        
        # Costruisce grafica
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        Clock.schedule_once(lambda dt: self.update_graphics(), 0)
    
    def get_text_color(self):
        """Ottiene colore testo basato su tipo pulsante"""
        if self.button_type == 'filled':
            return theme_manager.get_color('on_primary')
        elif self.button_type == 'outlined':
            return theme_manager.get_color('primary')
        else:  # text
            return theme_manager.get_color('primary')
    
    def get_bg_color(self):
        """Ottiene colore background basato su tipo pulsante"""
        if self.button_type == 'filled':
            return theme_manager.get_color('primary')
        elif self.button_type == 'outlined':
            return (*theme_manager.get_color('surface')[:3], 0)  # Trasparente
        else:  # text
            return (*theme_manager.get_color('surface')[:3], 0)  # Trasparente
    
    def update_graphics(self, *args):
        """Aggiorna grafica del pulsante"""
        self.canvas.before.clear()
        with self.canvas.before:
            # Background
            Color(*self.get_bg_color())
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)] * 4
            )
            
            # Bordo per outlined button
            if self.button_type == 'outlined':
                Color(*theme_manager.get_color('outline'))
                Line(
                    rounded_rectangle=[*self.pos, *self.size, dp(20)],
                    width=dp(1)
                )
        
        # Aggiorna colore testo
        self.label.color = self.get_text_color()
    
    def update_theme(self, mode):
        """Callback per aggiornamento tema"""
        self.update_graphics()
    
    def on_press(self):
        """Animazione press con ripple effect"""
        # Scaling animation
        anim = Animation(
            size=(self.size[0] * 0.95, self.size[1] * 0.95),
            duration=0.1,
            t='out_quad'
        ) + Animation(
            size=self.size,
            duration=0.1,
            t='out_quad'
        )
        anim.start(self)
        
        # Ripple effect
        self.add_ripple_effect()
    
    def add_ripple_effect(self):
        """Aggiunge effetto ripple al press"""
        # Crea cerchio che si espande
        with self.canvas.after:
            Color(*theme_manager.get_color('on_primary')[:3], 0.1)
            ripple = Ellipse(
                pos=(self.center_x - dp(10), self.center_y - dp(10)),
                size=(dp(20), dp(20))
            )
        
        # Animazione espansione
        max_size = max(self.size) * 1.5
        anim = Animation(
            size=(max_size, max_size),
            pos=(self.center_x - max_size/2, self.center_y - max_size/2),
            duration=0.3,
            t='out_quad'
        )
        
        def remove_ripple(*args):
            self.canvas.after.remove(ripple)
        
        anim.bind(on_complete=remove_ripple)
        anim.start(ripple)


class MaterialIcon(Label):
    """Icona Material Design"""
    
    def __init__(self, icon_name='', size_hint=(None, None), size=(dp(24), dp(24)), **kwargs):
        # Mapping icone comuni (in produzione usare font Material Icons)
        icons_map = {
            'home': '🏠',
            'search': '🔍',
            'camera': '📷',
            'map': '🗺️',
            'profile': '👤',
            'settings': '⚙️',
            'share': '📤',
            'like': '❤️',
            'star': '⭐',
            'location': '📍',
            'trophy': '🏆',
            'dark_mode': '🌙',
            'light_mode': '☀️',
            'menu': '☰',
            'back': '←',
            'close': '✕',
            'check': '✓',
            'add': '+',
            'remove': '−'
        }
        
        text = icons_map.get(icon_name, icon_name)
        
        # Rimuovi 'color' dai kwargs per evitare conflitti
        icon_color = kwargs.pop('color', theme_manager.get_color('on_surface'))
        
        super().__init__(
            text=text,
            size_hint=size_hint,
            size=size,
            font_size=sp(18),
            color=icon_color,
            **kwargs
        )
        
        # Registra per aggiornamenti tema
        theme_manager.register_callback(self.update_theme)
    
    def update_theme(self, mode):
        """Callback per aggiornamento tema"""
        self.color = theme_manager.get_color('on_surface')


class MaterialAppBar(BoxLayout):
    """App bar Material Design"""
    
    def __init__(self, title='', show_back=False, actions=None, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), 0],
            spacing=dp(16),
            **kwargs
        )
        
        self.title = title
        self.actions = actions or []
        
        # Registra per aggiornamenti tema
        theme_manager.register_callback(self.update_theme)
        
        # Back button (opzionale)
        if show_back:
            back_btn = MaterialButton(
                button_type='text',
                size=(dp(40), dp(40)),
                size_hint=(None, None)
            )
            back_btn.add_widget(MaterialIcon('back'))
            self.add_widget(back_btn)
        
        # Titolo
        title_label = Label(
            text=self.title,
            font_size=sp(20),
            bold=True,
            color=theme_manager.get_color('on_surface'),
            size_hint_x=1,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)
        self.title_label = title_label
        
        # Action buttons
        for action in self.actions:
            action_btn = MaterialButton(
                button_type='text',
                size=(dp(40), dp(40)),
                size_hint=(None, None)
            )
            action_btn.add_widget(MaterialIcon(action.get('icon', '')))
            if 'callback' in action:
                action_btn.bind(on_press=action['callback'])
            self.add_widget(action_btn)
        
        # Background
        self.update_graphics()
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def update_graphics(self, *args):
        """Aggiorna background dell'app bar"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*theme_manager.get_color('surface'))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
            
            # Ombra sotto l'app bar
            Color(*get_color_from_hex('#00000010'))
            RoundedRectangle(
                pos=(self.pos[0], self.pos[1] - dp(4)),
                size=(self.size[0], dp(4)),
                radius=[0]
            )
    
    def update_theme(self, mode):
        """Callback per aggiornamento tema"""
        self.update_graphics()
        self.title_label.color = theme_manager.get_color('on_surface')


class FloatingActionButton(MaterialButton):
    """Floating Action Button Material Design"""
    
    def __init__(self, icon='add', **kwargs):
        super().__init__(
            button_type='filled',
            size=(dp(56), dp(56)),
            size_hint=(None, None),
            **kwargs
        )
        
        # Rimuovi label di testo e aggiungi icona
        self.clear_widgets()
        icon_widget = MaterialIcon(icon)
        icon_widget.color = theme_manager.get_color('on_primary')
        self.add_widget(icon_widget)
        self.icon_widget = icon_widget
    
    def get_bg_color(self):
        """Override per colore FAB"""
        return theme_manager.get_color('primary_container')
    
    def update_graphics(self, *args):
        """Override per forma circolare"""
        self.canvas.before.clear()
        with self.canvas.before:
            # Ombra
            Color(*get_color_from_hex('#00000030'))
            Ellipse(
                pos=(self.pos[0] + dp(3), self.pos[1] - dp(3)),
                size=self.size
            )
            
            # Background circolare
            Color(*self.get_bg_color())
            Ellipse(pos=self.pos, size=self.size)
        
        # Aggiorna colore icona
        self.icon_widget.color = theme_manager.get_color('on_primary_container')
    
    def update_theme(self, mode):
        """Callback per aggiornamento tema"""
        self.update_graphics()


def demo_modern_ui():
    """Demo del sistema UI moderno"""
    from kivy.app import App
    
    class ModernUIDemo(App):
        def build(self):
            root = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(16))
            
            # App Bar
            app_bar = MaterialAppBar(
                title="Modern UI Demo",
                actions=[
                    {'icon': 'search', 'callback': self.search_pressed},
                    {'icon': 'settings', 'callback': self.settings_pressed}
                ]
            )
            root.add_widget(app_bar)
            
            # Cards e pulsanti
            content = BoxLayout(orientation='vertical', spacing=dp(16))
            
            # Card con contenuto
            card1 = MaterialCard(size_hint_y=None, height=dp(120))
            card_content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
            card_content.add_widget(Label(
                text="Monument Card",
                font_size=sp(18),
                bold=True,
                color=theme_manager.get_color('on_surface'),
                size_hint_y=None,
                height=dp(24)
            ))
            card_content.add_widget(Label(
                text="Informazioni dettagliate sul monumento visitato",
                font_size=sp(14),
                color=theme_manager.get_color('on_surface_variant'),
                text_size=(None, None),
                size_hint_y=1
            ))
            card1.add_widget(card_content)
            content.add_widget(card1)
            
            # Pulsanti di diversi tipi
            buttons_layout = BoxLayout(orientation='horizontal', spacing=dp(16), size_hint_y=None, height=dp(50))
            
            filled_btn = MaterialButton(text="Filled", button_type='filled')
            outlined_btn = MaterialButton(text="Outlined", button_type='outlined')
            text_btn = MaterialButton(text="Text", button_type='text')
            
            buttons_layout.add_widget(filled_btn)
            buttons_layout.add_widget(outlined_btn)
            buttons_layout.add_widget(text_btn)
            content.add_widget(buttons_layout)
            
            # Theme toggle
            theme_layout = BoxLayout(orientation='horizontal', spacing=dp(16), size_hint_y=None, height=dp(50))
            theme_btn = MaterialButton(text="Toggle Theme", button_type='outlined')
            theme_btn.bind(on_press=lambda x: theme_manager.toggle_theme())
            theme_layout.add_widget(Label(text="Theme Mode:", color=theme_manager.get_color('on_surface')))
            theme_layout.add_widget(theme_btn)
            content.add_widget(theme_layout)
            
            root.add_widget(content)
            
            # FAB
            fab = FloatingActionButton(
                icon='add',
                pos_hint={'right': 1, 'y': 0},
                pos=(Window.width - dp(72), dp(16))
            )
            root.add_widget(fab)
            
            # Aggiorna tema quando cambia
            def update_demo_theme(mode):
                # Re-color labels che non sono auto-updating
                pass
            
            theme_manager.register_callback(update_demo_theme)
            
            return root
        
        def search_pressed(self, instance):
            print("🔍 Search pressed")
        
        def settings_pressed(self, instance):
            print("⚙️ Settings pressed")
    
    return ModernUIDemo()


if __name__ == "__main__":
    demo_modern_ui().run()
