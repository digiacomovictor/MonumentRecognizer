"""
Enhanced Modern UI per Monument Recognizer
UI moderna potenziata con Material Icons, animazioni avanzate e miglioramenti UX
"""

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
# Card widget sostituito con ModernCard
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.graphics.instructions import InstructionGroup
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from advanced_animations import (
    MaterialIcons, AnimatedMaterialIcon, AnimationController, 
    AnimationType, EasingType, ParticleSystem, RippleEffect,
    setup_material_fonts
)
from modern_ui import theme_manager, MaterialButton, MaterialCard
from typing import Optional, Callable, Dict, Any
import threading


class NavigationBar(BoxLayout):
    """Barra di navigazione bottom con icone Material animate"""
    
    def __init__(self, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            spacing=0,
            **kwargs
        )
        
        self.selected_index = 0
        self.nav_items = []
        self.callbacks = {}
        
        # Setup sfondo
        with self.canvas.before:
            Color(*theme_manager.get_color('surface')[:3], 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20), dp(20), 0, 0]
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        """Aggiorna grafica sfondo"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def add_nav_item(self, icon_name: str, label: str, callback: Callable):
        """Aggiunge item navigazione"""
        index = len(self.nav_items)
        
        # Container per item
        item_layout = FloatLayout(size_hint=(1, 1))
        
        # Icona animata
        icon = AnimatedMaterialIcon(
            icon_name,
            pos_hint={'center_x': 0.5, 'center_y': 0.65},
            size=(dp(24), dp(24))
        )
        
        # Label
        label_widget = Label(
            text=label,
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            font_size=sp(10),
            color=theme_manager.get_color('on_surface'),
            size_hint=(None, None),
            size=(dp(60), dp(15))
        )
        
        # Indicatore selezione
        indicator = FloatLayout(
            pos_hint={'center_x': 0.5, 'center_y': 0.9},
            size_hint=(None, None),
            size=(dp(30), dp(3))
        )
        
        with indicator.canvas:
            Color(*theme_manager.get_color('primary')[:3], 0)
            indicator.bg = RoundedRectangle(
                pos=indicator.pos,
                size=indicator.size,
                radius=[dp(2)]
            )
        
        # Touch handler
        def on_touch_down(widget, touch):
            if widget.collide_point(*touch.pos):
                self.select_item(index)
                if callback:
                    callback()
                return True
            return False
        
        item_layout.bind(on_touch_down=on_touch_down)
        
        # Aggiungi elementi
        item_layout.add_widget(indicator)
        item_layout.add_widget(icon)
        item_layout.add_widget(label_widget)
        
        # Registra item
        nav_item = {
            'layout': item_layout,
            'icon': icon,
            'label': label_widget,
            'indicator': indicator,
            'callback': callback
        }
        
        self.nav_items.append(nav_item)
        self.add_widget(item_layout)
        
        # Seleziona primo item
        if index == 0:
            self.select_item(0)
    
    def select_item(self, index: int):
        """Seleziona item navigazione"""
        if index >= len(self.nav_items):
            return
        
        # Deseleziona tutti
        for i, item in enumerate(self.nav_items):
            is_selected = i == index
            
            # Anima icona
            if is_selected and i != self.selected_index:
                item['icon'].animate(AnimationType.BOUNCE, 0.4)
            
            # Aggiorna colori
            alpha = 1.0 if is_selected else 0.6
            item['icon'].color = (*theme_manager.get_color('primary' if is_selected else 'on_surface')[:3], alpha)
            item['label'].color = (*theme_manager.get_color('primary' if is_selected else 'on_surface')[:3], alpha)
            
            # Anima indicatore
            indicator_alpha = 1.0 if is_selected else 0.0
            with item['indicator'].canvas:
                item['indicator'].canvas.clear()
                Color(*theme_manager.get_color('primary')[:3], indicator_alpha)
                item['indicator'].bg = RoundedRectangle(
                    pos=item['indicator'].pos,
                    size=item['indicator'].size,
                    radius=[dp(2)]
                )
        
        self.selected_index = index


class FloatingActionButton(MaterialButton):
    """FAB Material Design con animazioni avanzate"""
    
    def __init__(self, icon_name: str = 'add', **kwargs):
        self.icon_name = icon_name
        
        super().__init__(
            text='',
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            **kwargs
        )
        
        # Icona centrale
        self.icon = AnimatedMaterialIcon(
            icon_name,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size=(dp(24), dp(24)),
            color=theme_manager.get_color('on_primary')
        )
        self.add_widget(self.icon)
        
        # Effetto ripple
        self.ripple = RippleEffect(
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.ripple)
        
        # Override stili
        self.update_style()
        
        # Eventi
        self.bind(on_press=self._on_press)
    
    def update_style(self):
        """Aggiorna stile FAB"""
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*theme_manager.get_color('primary')[:3], 1)
            self.bg = Ellipse(
                pos=(self.x + dp(4), self.y + dp(4)),
                size=(self.width - dp(8), self.height - dp(8))
            )
    
    def _on_press(self, *args):
        """Handler pressione"""
        # Effetto ripple
        self.ripple.add_ripple(self.center)
        
        # Anima icona
        self.icon.animate(AnimationType.PULSE, 0.3)
    
    def set_icon(self, icon_name: str):
        """Cambia icona FAB"""
        self.icon_name = icon_name
        self.icon.text = MaterialIcons.get_icon(icon_name)
        self.icon.animate(AnimationType.SCALE_UP, 0.2)


class NotificationCard(MaterialCard):
    """Card notifica con icona Material e azioni"""
    
    def __init__(self, title: str, message: str, icon: str = 'info', 
                 notification_type: str = 'info', actions: list = None, **kwargs):
        # Rimuovi size_hint dai kwargs se presente per evitare conflitti
        kwargs.pop('size_hint', None)
        
        super().__init__(
            size_hint=(1, None),
            height=dp(80),
            **kwargs
        )
        
        self.notification_type = notification_type
        self.actions = actions or []
        
        # Layout principale
        main_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            padding=[dp(16), dp(12), dp(16), dp(12)]
        )
        
        # Icona colorata per tipo
        type_colors = {
            'info': theme_manager.get_color('primary'),
            'success': (0.3, 0.8, 0.3, 1),
            'warning': (1.0, 0.6, 0.0, 1),
            'error': (0.9, 0.2, 0.2, 1)
        }
        
        icon_widget = AnimatedMaterialIcon(
            icon,
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            color=type_colors.get(notification_type, theme_manager.get_color('primary'))
        )
        
        # Contenuto testo
        text_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=dp(2)
        )
        
        title_label = Label(
            text=title,
            font_size=sp(14),
            color=theme_manager.get_color('on_surface'),
            text_size=(None, None),
            halign='left',
            size_hint=(1, None),
            height=dp(20)
        )
        
        message_label = Label(
            text=message,
            font_size=sp(12),
            color=(*theme_manager.get_color('on_surface')[:3], 0.7),
            text_size=(None, None),
            halign='left',
            size_hint=(1, 1)
        )
        
        text_layout.add_widget(title_label)
        text_layout.add_widget(message_label)
        
        # Actions layout
        actions_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            width=dp(80),
            spacing=dp(8)
        )
        
        # Pulsanti azione
        for action in self.actions:
            btn = Button(
                text=action.get('text', ''),
                size_hint=(None, None),
                size=(dp(60), dp(32)),
                font_size=sp(11)
            )
            if action.get('callback'):
                btn.bind(on_press=action['callback'])
            actions_layout.add_widget(btn)
        
        # Assembla layout
        main_layout.add_widget(icon_widget)
        main_layout.add_widget(text_layout)
        if self.actions:
            main_layout.add_widget(actions_layout)
        
        self.add_widget(main_layout)
        
        # Animazione entrata
        self.opacity = 0
        AnimationController.animate_widget(self, AnimationType.FADE_IN, 0.3)


class SearchBar(BoxLayout):
    """Barra ricerca Material Design con animazioni"""
    
    def __init__(self, hint_text: str = 'Cerca...', **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(48),
            spacing=dp(8),
            padding=[dp(16), 0, dp(16), 0],
            **kwargs
        )
        
        self.is_expanded = False
        self.search_callbacks = []
        
        # Container principale
        self.search_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 1),
            spacing=dp(8)
        )
        
        with self.search_container.canvas.before:
            Color(*theme_manager.get_color('surface')[:3], 1)
            self.search_bg = RoundedRectangle(
                pos=self.search_container.pos,
                size=self.search_container.size,
                radius=[dp(24)]
            )
        
        # Icona ricerca
        self.search_icon = AnimatedMaterialIcon(
            'search',
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_y': 0.5}
        )
        
        # Input ricerca
        self.search_input = TextInput(
            hint_text=hint_text,
            size_hint=(1, None),
            height=dp(40),
            multiline=False,
            background_color=(0, 0, 0, 0),
            foreground_color=theme_manager.get_color('on_surface'),
            padding=[dp(12), dp(10)],
            font_size=sp(14)
        )
        
        # Icona clear
        self.clear_icon = AnimatedMaterialIcon(
            'close',
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_y': 0.5},
            opacity=0
        )
        
        # Binding eventi
        self.search_input.bind(text=self._on_text_change)
        self.search_input.bind(focus=self._on_focus)
        self.clear_icon.bind(on_touch_down=self._clear_search)
        
        # Assembla layout
        self.search_container.add_widget(self.search_icon)
        self.search_container.add_widget(self.search_input)
        self.search_container.add_widget(self.clear_icon)
        
        self.add_widget(self.search_container)
        
        # Bind aggiornamento grafica
        self.search_container.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        """Aggiorna grafica sfondo"""
        self.search_bg.pos = self.search_container.pos
        self.search_bg.size = self.search_container.size
    
    def _on_text_change(self, instance, text):
        """Handler cambio testo"""
        has_text = len(text.strip()) > 0
        
        # Mostra/nascondi clear icon
        target_opacity = 1.0 if has_text else 0.0
        if self.clear_icon.opacity != target_opacity:
            Animation(opacity=target_opacity, duration=0.2).start(self.clear_icon)
        
        # Callback ricerca
        for callback in self.search_callbacks:
            callback(text)
    
    def _on_focus(self, instance, focused):
        """Handler focus"""
        if focused:
            self.search_icon.animate(AnimationType.PULSE, 0.3)
    
    def _clear_search(self, widget, touch):
        """Pulisce ricerca"""
        if widget.collide_point(*touch.pos):
            self.search_input.text = ''
            self.clear_icon.animate(AnimationType.SCALE_UP, 0.2)
            return True
        return False
    
    def add_search_callback(self, callback: Callable):
        """Aggiunge callback ricerca"""
        self.search_callbacks.append(callback)
    
    def set_text(self, text: str):
        """Imposta testo ricerca"""
        self.search_input.text = text


class ModernProgressIndicator(FloatLayout):
    """Indicatore progresso Material Design"""
    
    def __init__(self, progress_type: str = 'circular', **kwargs):
        super().__init__(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            **kwargs
        )
        
        self.progress_type = progress_type
        self.is_animating = False
        self._progress = 0
        
        if progress_type == 'circular':
            self._create_circular_progress()
        else:
            self._create_linear_progress()
    
    def _create_circular_progress(self):
        """Crea progress circolare"""
        with self.canvas:
            Color(*theme_manager.get_color('primary')[:3], 0.3)
            self.bg_circle = Line(
                circle=(self.center_x, self.center_y, dp(20)), 
                width=dp(3)
            )
            
            Color(*theme_manager.get_color('primary')[:3], 1)
            self.progress_circle = Line(
                circle=(self.center_x, self.center_y, dp(20), 0, 90), 
                width=dp(3)
            )
        
        self.bind(pos=self._update_circular_graphics)
    
    def _update_circular_graphics(self, *args):
        """Aggiorna grafica circolare"""
        self.bg_circle.circle = (self.center_x, self.center_y, dp(20))
        angle = 360 * self._progress
        self.progress_circle.circle = (self.center_x, self.center_y, dp(20), 0, angle)
    
    def _create_linear_progress(self):
        """Crea progress lineare"""
        self.size = (dp(200), dp(4))
        
        with self.canvas:
            Color(*theme_manager.get_color('primary')[:3], 0.3)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(2)]
            )
            
            Color(*theme_manager.get_color('primary')[:3], 1)
            self.progress_rect = RoundedRectangle(
                pos=self.pos,
                size=(0, self.height),
                radius=[dp(2)]
            )
    
    @property
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = max(0, min(1, value))
        
        if self.progress_type == 'circular':
            self._update_circular_graphics()
        else:
            width = self.width * self._progress
            self.progress_rect.size = (width, self.height)
    
    def start_indeterminate(self):
        """Avvia animazione indeterminata"""
        if self.is_animating:
            return
        
        self.is_animating = True
        
        def animate_loop():
            if not self.is_animating:
                return
            
            anim1 = Animation(progress=1, duration=1.0, t='in_out_quad')
            anim2 = Animation(progress=0, duration=1.0, t='in_out_quad')
            
            sequence = anim1 + anim2
            sequence.bind(on_complete=lambda *args: Clock.schedule_once(lambda dt: animate_loop(), 0))
            sequence.start(self)
        
        animate_loop()
    
    def stop_indeterminate(self):
        """Ferma animazione indeterminata"""
        self.is_animating = False


class EnhancedPopup(Popup):
    """Popup migliorato con Material Design"""
    
    def __init__(self, popup_type: str = 'info', **kwargs):
        # Dimensioni responsive
        size_hint = kwargs.pop('size_hint', (0.8, None))
        height = kwargs.pop('height', dp(300))
        
        super().__init__(
            size_hint=size_hint,
            height=height,
            separator_color=theme_manager.get_color('primary'),
            separator_height=dp(2),
            **kwargs
        )
        
        self.popup_type = popup_type
        self._setup_enhanced_content()
        
        # Animazione entrata
        self.opacity = 0
        Clock.schedule_once(self._animate_in, 0.1)
    
    def _setup_enhanced_content(self):
        """Setup contenuto migliorato"""
        # Background personalizzato
        with self.canvas.before:
            Color(*theme_manager.get_color('surface')[:3], 1)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(16)]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, *args):
        """Aggiorna background"""
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def _animate_in(self, dt):
        """Animazione entrata"""
        AnimationController.animate_widget(self, AnimationType.FADE_IN, 0.3)
        
        # Scale up effect
        original_size = self.size
        self.size = (0, 0)
        Animation(size=original_size, duration=0.3, t='out_back').start(self)
    
    def dismiss_with_animation(self):
        """Chiude con animazione"""
        def close_popup(*args):
            self.dismiss()
        
        AnimationController.animate_widget(
            self, AnimationType.FADE_OUT, 0.2, callback=close_popup
        )


class EnhancedScreen(Screen):
    """Screen base migliorata con animazioni"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_background()
        self.notification_layer = FloatLayout()
        self.add_widget(self.notification_layer)
    
    def setup_background(self):
        """Setup background personalizzato"""
        with self.canvas.before:
            # Gradient background
            Color(*theme_manager.get_color('background')[:3], 1)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[0]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, *args):
        """Aggiorna background"""
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def on_enter(self, *args):
        """Override entrata screen"""
        super().on_enter(*args)
        # Animazione entrata personalizzabile
        self.animate_entrance()
    
    def animate_entrance(self):
        """Anima entrata screen (da override)"""
        pass
    
    def show_notification(self, title: str, message: str, 
                         notification_type: str = 'info', duration: float = 3.0):
        """Mostra notifica temporanea"""
        notification = NotificationCard(
            title=title,
            message=message,
            notification_type=notification_type,
            pos_hint={'center_x': 0.5, 'top': 0.95},
            size_hint=(0.9, None)
        )
        
        self.notification_layer.add_widget(notification)
        
        # Auto-dismiss
        def remove_notification(*args):
            AnimationController.animate_widget(
                notification, AnimationType.FADE_OUT, 0.3,
                callback=lambda: self.notification_layer.remove_widget(notification)
            )
        
        Clock.schedule_once(remove_notification, duration)
        
        return notification


class ModernScreenManager(ScreenManager):
    """ScreenManager potenziato con transizioni"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Transizioni personalizzate
        self.transition_types = {
            'slide': SlideTransition(),
            'fade': FadeTransition(),
        }
        
        # Default
        self.transition = self.transition_types['slide']
    
    def set_transition(self, transition_type: str, **kwargs):
        """Imposta tipo transizione"""
        if transition_type in self.transition_types:
            self.transition = self.transition_types[transition_type]
        
        # Applica parametri aggiuntivi
        for key, value in kwargs.items():
            if hasattr(self.transition, key):
                setattr(self.transition, key, value)


def create_demo_app():
    """Crea app demo UI migliorata"""
    from kivy.app import App
    
    class EnhancedUIDemo(App):
        def build(self):
            # Setup font Material Icons
            setup_material_fonts()
            
            # Screen manager
            sm = ModernScreenManager()
            
            # Main screen
            main_screen = EnhancedScreen(name='main')
            
            # Layout principale
            main_layout = FloatLayout()
            
            # Navigation bar
            nav_bar = NavigationBar(
                pos_hint={'x': 0, 'y': 0}
            )
            
            nav_bar.add_nav_item('home', 'Home', lambda: print('Home'))
            nav_bar.add_nav_item('search', 'Cerca', lambda: print('Search'))
            nav_bar.add_nav_item('favorite', 'Preferiti', lambda: print('Favorites'))
            nav_bar.add_nav_item('person', 'Profilo', lambda: print('Profile'))
            
            # Search bar
            search_bar = SearchBar(
                pos_hint={'center_x': 0.5, 'top': 0.95}
            )
            search_bar.add_search_callback(lambda text: print(f'Cercando: {text}'))
            
            # FAB
            fab = FloatingActionButton(
                'camera',
                pos_hint={'right': 0.95, 'y': 0.15}
            )
            
            # Test notifications
            def show_test_notification():
                main_screen.show_notification(
                    'Test Notifica', 
                    'Questa è una notifica di test!',
                    'success'
                )
            
            test_btn = MaterialButton(
                text='Test Notifica',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(None, None),
                size=(dp(150), dp(50))
            )
            test_btn.bind(on_press=lambda x: show_test_notification())
            
            # Progress indicator
            progress = ModernProgressIndicator(
                pos_hint={'center_x': 0.3, 'center_y': 0.5}
            )
            progress.start_indeterminate()
            
            # Assembla layout
            main_layout.add_widget(search_bar)
            main_layout.add_widget(test_btn) 
            main_layout.add_widget(progress)
            main_layout.add_widget(fab)
            main_layout.add_widget(nav_bar)
            
            main_screen.add_widget(main_layout)
            sm.add_widget(main_screen)
            
            return sm
    
    return EnhancedUIDemo()


if __name__ == "__main__":
    create_demo_app().run()
