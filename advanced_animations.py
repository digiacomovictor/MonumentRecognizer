"""
Advanced Animations & Material Icons per Monument Recognizer
Sistema avanzato di animazioni fluide e icone Material Design autentiche
"""

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle, PushMatrix, PopMatrix, Rotate, Scale, Translate
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp, sp
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
import os
from typing import Callable, Optional, Dict, Any
from enum import Enum
import math
from modern_ui import theme_manager


class AnimationType(Enum):
    """Tipi di animazioni disponibili"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SLIDE_IN_LEFT = "slide_in_left"
    SLIDE_IN_RIGHT = "slide_in_right"
    SLIDE_IN_UP = "slide_in_up"
    SLIDE_IN_DOWN = "slide_in_down"
    BOUNCE = "bounce"
    SHAKE = "shake"
    PULSE = "pulse"
    ROTATE = "rotate"
    FLIP = "flip"


class EasingType(Enum):
    """Tipi di easing per animazioni"""
    LINEAR = "linear"
    IN_QUAD = "in_quad" 
    OUT_QUAD = "out_quad"
    IN_OUT_QUAD = "in_out_quad"
    IN_CUBIC = "in_cubic"
    OUT_CUBIC = "out_cubic"
    IN_OUT_CUBIC = "in_out_cubic"
    IN_BOUNCE = "in_bounce"
    OUT_BOUNCE = "out_bounce"
    IN_OUT_BOUNCE = "in_out_bounce"
    IN_ELASTIC = "in_elastic"
    OUT_ELASTIC = "out_elastic"


class MaterialIcons:
    """Icone Material Design con font TTF autentico"""
    
    # Extended icon set con unicode Material Icons
    ICONS = {
        # Navigation
        'home': '\ue88a',
        'arrow_back': '\ue5c4',
        'arrow_forward': '\ue5c8', 
        'arrow_upward': '\ue5d8',
        'arrow_downward': '\ue5db',
        'menu': '\ue5d2',
        'close': '\ue5cd',
        'more_vert': '\ue5d4',
        'more_horiz': '\ue5d3',
        'expand_less': '\ue5ce',
        'expand_more': '\ue5cf',
        'refresh': '\ue5d5',
        
        # Action
        'search': '\ue8b6',
        'add': '\ue145',
        'remove': '\ue15b',
        'edit': '\ue3c9',
        'delete': '\ue872',
        'save': '\ue161',
        'favorite': '\ue87d',
        'share': '\ue80d',
        'visibility': '\ue8f4',
        'visibility_off': '\ue8f5',
        'thumb_up': '\ue8db',
        'thumb_down': '\ue8dc',
        'star': '\ue838',
        'star_border': '\ue83a',
        
        # Communication
        'chat': '\ue0b7',
        'message': '\ue0c9',
        'call': '\ue0b0',
        'mail': '\ue0be',
        'forum': '\ue0bf',
        
        # Content
        'copy': '\ue14d',
        'cut': '\ue14e',
        'paste': '\ue14f',
        'create': '\ue150',
        'flag': '\ue153',
        'reply': '\ue15e',
        'sort': '\ue164',
        'filter_list': '\ue152',
        
        # Device
        'camera': '\ue3af',
        'camera_alt': '\ue3b0',
        'photo_camera': '\ue412',
        'videocam': '\ue04b',
        'mic': '\ue3c9',
        'location_on': '\ue0c8',
        'gps_fixed': '\ue1b3',
        
        # File
        'folder': '\ue2c7',
        'folder_open': '\ue2c8',
        'insert_drive_file': '\ue2c6',
        'image': '\ue3f4',
        'photo': '\ue410',
        'video_library': '\ue04a',
        'music_note': '\ue405',
        
        # Hardware
        'phone': '\ue325',
        'tablet': '\ue32f',
        'laptop': '\ue31e',
        'desktop': '\ue30a',
        'watch': '\ue334',
        
        # Image
        'photo_library': '\ue411',
        'panorama': '\ue40b',
        'palette': '\ue40a',
        'brush': '\ue3a6',
        'color_lens': '\ue3b7',
        
        # Maps
        'map': '\ue55b',
        'place': '\ue55f',
        'navigation': '\ue55d',
        'directions': '\ue52e',
        'my_location': '\ue55c',
        'layers': '\ue53b',
        
        # Social
        'people': '\ue7fb',
        'person': '\ue7fd',
        'person_add': '\ue7fe',
        'group': '\ue7ef',
        'public': '\ue80b',
        
        # Toggle
        'check_box': '\ue834',
        'check_box_outline_blank': '\ue835',
        'radio_button_checked': '\ue837',
        'radio_button_unchecked': '\ue836',
        'toggle_on': '\ue9f7',
        'toggle_off': '\ue9f6',
        
        # AV
        'play_arrow': '\ue037',
        'pause': '\ue034',
        'stop': '\ue047',
        'skip_next': '\ue044',
        'skip_previous': '\ue045',
        'volume_up': '\ue050',
        'volume_down': '\ue04d',
        'volume_mute': '\ue04e',
        
        # Notification
        'notifications': '\ue7f4',
        'notifications_off': '\ue7f6',
        'warning': '\ue002',
        'error': '\ue000',
        'info': '\ue88e',
        
        # Theme
        'brightness_high': '\ue1ac',
        'brightness_low': '\ue1ad',
        'brightness_medium': '\ue1ab',
        'dark_mode': '\ue51c',
        'light_mode': '\ue518',
        
        # Shopping
        'shopping_cart': '\ue8cc',
        'add_shopping_cart': '\ue854',
        'remove_shopping_cart': '\ue928',
        'local_offer': '\ue54c',
        
        # Custom app-specific
        'monument': '\ue0c8',  # location_on per monumenti
        'achievement': '\ue838',  # star per achievement
        'leaderboard': '\ue8e8',  # emoji_events per leaderboard
        'camera_enhanced': '\ue3af',
        'ar_view': '\ue8c8',  # 3d_rotation per AR
        'analytics': '\ue1c7',  # trending_up
        'gamification': '\ue021',  # games
    }
    
    @classmethod
    def get_icon(cls, name: str, fallback: str = '?') -> str:
        """Ottiene l'icona per nome"""
        return cls.ICONS.get(name, fallback)
    
    @classmethod
    def is_available(cls, name: str) -> bool:
        """Verifica se l'icona è disponibile"""
        return name in cls.ICONS


class AnimatedMaterialIcon(Label):
    """Icona Material animata"""
    
    def __init__(self, icon_name: str = '', size_hint=(None, None), size=(dp(24), dp(24)), **kwargs):
        # Ottieni l'icona dal set Material
        icon_text = MaterialIcons.get_icon(icon_name, '?')
        
        # Estrai color dai kwargs se presente, altrimenti usa default
        icon_color = kwargs.pop('color', theme_manager.get_color('on_surface'))
        
        super().__init__(
            text=icon_text,
            font_name='MaterialIcons-Regular',  # Nome font Material Icons
            size_hint=size_hint,
            size=size,
            font_size=sp(18),
            color=icon_color,
            **kwargs
        )
        
        self.icon_name = icon_name
        self.original_color = self.color
        self.is_animating = False
        
        # Registra per aggiornamenti tema
        theme_manager.register_callback(self.update_theme)
    
    def update_theme(self, mode):
        """Callback per aggiornamento tema"""
        if not self.is_animating:
            self.color = theme_manager.get_color('on_surface')
            self.original_color = self.color
    
    def animate(self, animation_type: AnimationType, duration: float = 0.3, 
                callback: Optional[Callable] = None, **kwargs):
        """Anima l'icona"""
        if self.is_animating:
            return
        
        self.is_animating = True
        animation = self._create_animation(animation_type, duration, **kwargs)
        
        def on_complete(*args):
            self.is_animating = False
            if callback:
                callback()
        
        animation.bind(on_complete=on_complete)
        animation.start(self)
    
    def _create_animation(self, animation_type: AnimationType, duration: float, **kwargs) -> Animation:
        """Crea l'animazione specifica"""
        if animation_type == AnimationType.PULSE:
            return self._create_pulse_animation(duration)
        elif animation_type == AnimationType.BOUNCE:
            return self._create_bounce_animation(duration)
        elif animation_type == AnimationType.SHAKE:
            return self._create_shake_animation(duration)
        elif animation_type == AnimationType.ROTATE:
            return self._create_rotate_animation(duration)
        elif animation_type == AnimationType.FADE_IN:
            return Animation(opacity=1, duration=duration, t='out_cubic')
        elif animation_type == AnimationType.FADE_OUT:
            return Animation(opacity=0, duration=duration, t='out_cubic')
        elif animation_type == AnimationType.SCALE_UP:
            scale = kwargs.get('scale', 1.2)
            return Animation(size=(self.size[0] * scale, self.size[1] * scale), 
                           duration=duration, t='out_back')
        else:
            return Animation(duration=duration)
    
    def _create_pulse_animation(self, duration: float) -> Animation:
        """Animazione pulse"""
        original_size = self.size
        pulse_size = (original_size[0] * 1.3, original_size[1] * 1.3)
        
        pulse_out = Animation(size=pulse_size, duration=duration/2, t='out_quad')
        pulse_in = Animation(size=original_size, duration=duration/2, t='in_quad')
        
        return pulse_out + pulse_in
    
    def _create_bounce_animation(self, duration: float) -> Animation:
        """Animazione bounce"""
        original_pos = self.pos
        bounce_height = dp(20)
        
        up = Animation(y=original_pos[1] + bounce_height, duration=duration/2, t='out_quad')
        down = Animation(y=original_pos[1], duration=duration/2, t='in_bounce')
        
        return up + down
    
    def _create_shake_animation(self, duration: float) -> Animation:
        """Animazione shake"""
        original_x = self.x
        shake_distance = dp(5)
        
        # Serie di movimenti per shake
        right = Animation(x=original_x + shake_distance, duration=duration/8)
        left = Animation(x=original_x - shake_distance, duration=duration/4)
        center = Animation(x=original_x, duration=duration/8)
        
        return right + left + right + left + center
    
    def _create_rotate_animation(self, duration: float) -> Animation:
        """Animazione rotazione"""
        # Note: Kivy rotation animation requires custom implementation with canvas
        return Animation(duration=duration)


class AnimationController:
    """Controller centrale per animazioni avanzate"""
    
    @staticmethod
    def animate_widget(widget: Widget, animation_type: AnimationType, 
                      duration: float = 0.3, easing: EasingType = EasingType.OUT_CUBIC,
                      callback: Optional[Callable] = None, **params):
        """Anima un widget generico"""
        
        # Converti easing enum in stringa Kivy
        easing_map = {
            EasingType.LINEAR: 'linear',
            EasingType.OUT_CUBIC: 'out_cubic',
            EasingType.IN_CUBIC: 'in_cubic',
            EasingType.OUT_QUAD: 'out_quad',
            EasingType.IN_QUAD: 'in_quad',
            EasingType.OUT_BOUNCE: 'out_bounce',
            EasingType.IN_BOUNCE: 'in_bounce',
        }
        
        easing_str = easing_map.get(easing, 'out_cubic')
        
        if animation_type == AnimationType.FADE_IN:
            widget.opacity = 0
            anim = Animation(opacity=1, duration=duration, t=easing_str)
        
        elif animation_type == AnimationType.FADE_OUT:
            anim = Animation(opacity=0, duration=duration, t=easing_str)
        
        elif animation_type == AnimationType.SLIDE_IN_LEFT:
            original_x = widget.x
            widget.x = -widget.width
            anim = Animation(x=original_x, duration=duration, t=easing_str)
        
        elif animation_type == AnimationType.SLIDE_IN_RIGHT:
            original_x = widget.x
            widget.x = widget.parent.width if widget.parent else 800
            anim = Animation(x=original_x, duration=duration, t=easing_str)
        
        elif animation_type == AnimationType.SLIDE_IN_UP:
            original_y = widget.y
            widget.y = -widget.height
            anim = Animation(y=original_y, duration=duration, t=easing_str)
        
        elif animation_type == AnimationType.SLIDE_IN_DOWN:
            original_y = widget.y
            widget.y = widget.parent.height if widget.parent else 600
            anim = Animation(y=original_y, duration=duration, t=easing_str)
        
        elif animation_type == AnimationType.SCALE_UP:
            scale = params.get('scale', 1.2)
            original_size = widget.size
            widget.size = (0, 0)
            anim = Animation(size=original_size, duration=duration, t=easing_str)
        
        elif animation_type == AnimationType.BOUNCE:
            return AnimationController._create_bounce_sequence(widget, duration, easing_str, callback)
        
        elif animation_type == AnimationType.PULSE:
            return AnimationController._create_pulse_sequence(widget, duration, callback)
        
        else:
            # Fallback animation
            anim = Animation(duration=duration, t=easing_str)
        
        if callback:
            anim.bind(on_complete=callback)
        
        anim.start(widget)
        return anim
    
    @staticmethod
    def _create_bounce_sequence(widget: Widget, duration: float, easing: str, callback: Optional[Callable]):
        """Crea sequenza bounce complessa"""
        original_size = widget.size
        
        # Sequenza di rimbalzi
        bounce1 = Animation(size=(original_size[0] * 1.3, original_size[1] * 1.3), 
                          duration=duration * 0.3, t='out_quad')
        bounce2 = Animation(size=(original_size[0] * 0.9, original_size[1] * 0.9), 
                          duration=duration * 0.2, t='in_quad')
        bounce3 = Animation(size=(original_size[0] * 1.1, original_size[1] * 1.1), 
                          duration=duration * 0.2, t='out_quad')
        bounce4 = Animation(size=original_size, duration=duration * 0.3, t='in_quad')
        
        sequence = bounce1 + bounce2 + bounce3 + bounce4
        
        if callback:
            sequence.bind(on_complete=callback)
        
        sequence.start(widget)
        return sequence
    
    @staticmethod
    def _create_pulse_sequence(widget: Widget, duration: float, callback: Optional[Callable]):
        """Crea sequenza pulse"""
        original_opacity = widget.opacity
        
        pulse_out = Animation(opacity=0.3, duration=duration/2, t='out_sine')
        pulse_in = Animation(opacity=original_opacity, duration=duration/2, t='in_sine')
        
        sequence = pulse_out + pulse_in
        
        if callback:
            sequence.bind(on_complete=callback)
        
        sequence.start(widget)
        return sequence
    
    @staticmethod
    def chain_animations(*animations) -> Animation:
        """Concatena più animazioni in sequenza"""
        if not animations:
            return Animation(duration=0)
        
        result = animations[0]
        for anim in animations[1:]:
            result = result + anim
        
        return result
    
    @staticmethod
    def parallel_animations(*animations) -> list:
        """Esegue animazioni in parallelo"""
        return list(animations)
    
    @staticmethod
    def create_stagger_animation(widgets: list, animation_type: AnimationType,
                                delay: float = 0.1, **params) -> list:
        """Crea animazioni sfalsate per una lista di widget"""
        animations = []
        
        for i, widget in enumerate(widgets):
            def create_delayed_animation(w, d):
                def start_animation(*args):
                    AnimationController.animate_widget(w, animation_type, **params)
                Clock.schedule_once(start_animation, d)
                return start_animation
            
            delayed_anim = create_delayed_animation(widget, delay * i)
            animations.append(delayed_anim)
        
        return animations


class ParticleSystem(Widget):
    """Sistema particelle per effetti speciali"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self.is_active = False
        
    def start_particles(self, particle_type: str = "stars", count: int = 20):
        """Avvia sistema particelle"""
        self.is_active = True
        self.particles = []
        
        for i in range(count):
            particle = self.create_particle(particle_type)
            self.particles.append(particle)
        
        # Avvia animazione particelle
        Clock.schedule_interval(self.update_particles, 1/60)  # 60 FPS
    
    def create_particle(self, particle_type: str) -> dict:
        """Crea una singola particella"""
        import random
        
        return {
            'x': random.uniform(0, self.width),
            'y': random.uniform(0, self.height),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'life': 1.0,
            'decay': random.uniform(0.01, 0.03),
            'size': random.uniform(2, 6),
            'color': theme_manager.get_color('primary')
        }
    
    def update_particles(self, dt):
        """Aggiorna particelle"""
        if not self.is_active:
            return False
        
        alive_particles = []
        
        for particle in self.particles:
            # Aggiorna posizione
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Aggiorna vita
            particle['life'] -= particle['decay']
            
            # Mantieni particelle vive
            if particle['life'] > 0:
                alive_particles.append(particle)
        
        self.particles = alive_particles
        
        # Ridisegna
        self.canvas.clear()
        with self.canvas:
            for particle in self.particles:
                Color(*particle['color'][:3], particle['life'])
                Ellipse(
                    pos=(particle['x'], particle['y']),
                    size=(particle['size'], particle['size'])
                )
        
        # Ferma se non ci sono più particelle
        if not self.particles:
            self.is_active = False
            return False
        
        return True
    
    def stop_particles(self):
        """Ferma sistema particelle"""
        self.is_active = False
        self.particles = []
        self.canvas.clear()


class RippleEffect(Widget):
    """Effetto ripple Material Design avanzato"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ripples = []
        
    def add_ripple(self, pos: tuple, color: tuple = None, max_radius: float = None):
        """Aggiunge un effetto ripple"""
        if color is None:
            color = theme_manager.get_color('primary')
        
        if max_radius is None:
            max_radius = max(self.width, self.height) * 0.7
        
        ripple = {
            'pos': pos,
            'radius': 0,
            'max_radius': max_radius,
            'color': color,
            'opacity': 0.3
        }
        
        self.ripples.append(ripple)
        
        # Anima il ripple
        def animate_ripple():
            anim = Animation(
                radius=max_radius,
                opacity=0,
                duration=0.6,
                t='out_cubic'
            )
            
            def remove_ripple(*args):
                if ripple in self.ripples:
                    self.ripples.remove(ripple)
                self.redraw()
            
            anim.bind(on_complete=remove_ripple)
            
            # Usa un oggetto temporaneo per l'animazione
            temp_obj = type('TempRipple', (), ripple)()
            anim.start(temp_obj)
            
            # Update ripple data durante animazione
            def update_ripple(obj, value):
                ripple['radius'] = temp_obj.radius
                ripple['opacity'] = temp_obj.opacity
                self.redraw()
            
            temp_obj.bind(radius=update_ripple, opacity=update_ripple)
        
        Clock.schedule_once(lambda dt: animate_ripple(), 0)
    
    def redraw(self):
        """Ridisegna tutti i ripples"""
        self.canvas.clear()
        
        with self.canvas:
            for ripple in self.ripples:
                Color(*ripple['color'][:3], ripple['opacity'])
                Ellipse(
                    pos=(ripple['pos'][0] - ripple['radius']/2,
                         ripple['pos'][1] - ripple['radius']/2),
                    size=(ripple['radius'], ripple['radius'])
                )


def setup_material_fonts():
    """Setup dei font Material Icons"""
    try:
        # Cerca font Material Icons
        font_paths = [
            'MaterialIcons-Regular.ttf',
            'fonts/MaterialIcons-Regular.ttf',
            os.path.join(os.path.dirname(__file__), 'fonts', 'MaterialIcons-Regular.ttf')
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                LabelBase.register(name='MaterialIcons-Regular', fn_regular=font_path)
                print(f"✅ Font Material Icons caricato: {font_path}")
                return True
        
        print("⚠️ Font Material Icons non trovato, uso fallback emoji")
        return False
        
    except Exception as e:
        print(f"❌ Errore caricamento font Material Icons: {e}")
        return False


def demo_advanced_animations():
    """Demo sistema animazioni avanzate"""
    from kivy.app import App
    from kivy.uix.button import Button
    
    class AnimationDemo(App):
        def build(self):
            root = FloatLayout()
            
            # Setup font (optional)
            setup_material_fonts()
            
            # Test icon animata
            icon = AnimatedMaterialIcon(
                'favorite',
                pos_hint={'center_x': 0.2, 'center_y': 0.8},
                size=(dp(48), dp(48))
            )
            
            # Pulsante per animare icon
            animate_btn = Button(
                text='Animate Icon',
                pos_hint={'center_x': 0.2, 'center_y': 0.6},
                size_hint=(None, None),
                size=(dp(120), dp(40))
            )
            animate_btn.bind(on_press=lambda x: icon.animate(AnimationType.PULSE))
            
            # Test altri widget
            test_widget = Button(
                text='Test Widget',
                pos_hint={'center_x': 0.5, 'center_y': 0.8},
                size_hint=(None, None),
                size=(dp(120), dp(40))
            )
            
            # Pulsanti per diverse animazioni
            fade_btn = Button(
                text='Fade',
                pos_hint={'center_x': 0.5, 'center_y': 0.6},
                size_hint=(None, None),
                size=(dp(80), dp(40))
            )
            fade_btn.bind(on_press=lambda x: AnimationController.animate_widget(
                test_widget, AnimationType.FADE_OUT
            ))
            
            bounce_btn = Button(
                text='Bounce',
                pos_hint={'center_x': 0.6, 'center_y': 0.6},
                size_hint=(None, None),
                size=(dp(80), dp(40))
            )
            bounce_btn.bind(on_press=lambda x: AnimationController.animate_widget(
                test_widget, AnimationType.BOUNCE
            ))
            
            # Sistema particelle
            particles = ParticleSystem(
                pos_hint={'center_x': 0.8, 'center_y': 0.7},
                size_hint=(None, None),
                size=(dp(200), dp(200))
            )
            
            particles_btn = Button(
                text='Particles',
                pos_hint={'center_x': 0.8, 'center_y': 0.5},
                size_hint=(None, None),
                size=(dp(80), dp(40))
            )
            particles_btn.bind(on_press=lambda x: particles.start_particles())
            
            # Aggiungi tutto al root
            root.add_widget(icon)
            root.add_widget(animate_btn)
            root.add_widget(test_widget)
            root.add_widget(fade_btn)
            root.add_widget(bounce_btn)
            root.add_widget(particles)
            root.add_widget(particles_btn)
            
            return root
    
    return AnimationDemo()


if __name__ == "__main__":
    demo_advanced_animations().run()
