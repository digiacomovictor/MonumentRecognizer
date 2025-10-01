#!/usr/bin/env python3
"""
Demo completa dell'UI migliorata con Material Icons e animazioni
"""

import os
import sys
from pathlib import Path

# Aggiungi directory corrente al path
sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp, sp
from kivy.clock import Clock

# Import nostri moduli
try:
    from modern_ui import MaterialButton, MaterialCard, theme_manager
    from advanced_animations import (
        MaterialIcons, AnimatedMaterialIcon, AnimationController, 
        AnimationType, setup_material_fonts, ParticleSystem
    )
    from enhanced_modern_ui import (
        NavigationBar, FloatingActionButton, SearchBar,
        NotificationCard, EnhancedScreen, ModernScreenManager,
        ModernProgressIndicator
    )
except ImportError as e:
    print(f"❌ Errore import: {e}")
    print("💡 Assicurati che tutti i moduli siano disponibili")
    sys.exit(1)


class EnhancedUIDemo(App):
    """App demo per testare l'UI migliorata"""
    
    def build(self):
        """Costruisce l'app demo"""
        # Setup font Material Icons
        setup_material_fonts()
        
        # Screen manager moderno
        sm = ModernScreenManager()
        sm.set_transition('slide', direction='left')
        
        # Screen principale
        main_screen = EnhancedScreen(name='main')
        main_screen.animate_entrance = self.custom_entrance_animation
        
        # Layout principale
        main_layout = FloatLayout()
        
        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            pos_hint={'top': 1},
            padding=[dp(16), dp(8)],
            spacing=dp(12)
        )
        
        # Titolo con icona
        title_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint=(1, 1)
        )
        
        title_icon = AnimatedMaterialIcon(
            'monument',
            size=(dp(32), dp(32)),
            size_hint=(None, None)
        )
        
        title_label = Label(
            text='Monument Recognizer Demo',
            font_size=sp(18),
            color=theme_manager.get_color('on_surface'),
            size_hint=(1, 1),
            halign='left',
            valign='center'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        title_layout.add_widget(title_icon)
        title_layout.add_widget(title_label)
        
        # Toggle theme button
        theme_btn = Button(
            text='🌙' if theme_manager.is_dark_mode else '☀️',
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            font_size=sp(20)
        )
        theme_btn.bind(on_press=self.toggle_theme)
        
        header.add_widget(title_layout)
        header.add_widget(theme_btn)
        
        # Barra di ricerca
        search_bar = SearchBar(
            hint_text='Cerca monumenti, luoghi, città...',
            pos_hint={'center_x': 0.5, 'top': 0.87}
        )
        search_bar.add_search_callback(self.on_search)
        
        # Area contenuto centrale
        content_area = BoxLayout(
            orientation='vertical',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.9, 0.6),
            spacing=dp(20)
        )
        
        # Cards demo con icone Material
        cards_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(120),
            spacing=dp(15)
        )
        
        # Card Scansiona
        scan_card = MaterialCard()
        scan_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(8),
            padding=dp(15)
        )
        
        scan_icon = AnimatedMaterialIcon(
            'camera_enhanced',
            size=(dp(32), dp(32)),
            size_hint=(None, None),
            pos_hint={'center_x': 0.5}
        )
        
        scan_text = Label(
            text='Scansiona\nMonumento',
            font_size=sp(12),
            color=theme_manager.get_color('on_surface'),
            halign='center',
            valign='center'
        )
        scan_text.bind(size=scan_text.setter('text_size'))
        
        scan_layout.add_widget(scan_icon)
        scan_layout.add_widget(scan_text)
        scan_card.add_widget(scan_layout)
        
        # Bind touch con animazione
        def animate_scan_card(*args):
            scan_icon.animate(AnimationType.PULSE, 0.4)
            main_screen.show_notification(
                'Fotocamera', 
                'Funzione fotocamera attivata!',
                'info'
            )
        
        scan_card.bind(on_touch_down=lambda w, t: animate_scan_card() if w.collide_point(*t.pos) else None)
        
        # Card AR View
        ar_card = MaterialCard()
        ar_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(8),
            padding=dp(15)
        )
        
        ar_icon = AnimatedMaterialIcon(
            'ar_view',
            size=(dp(32), dp(32)),
            size_hint=(None, None),
            pos_hint={'center_x': 0.5}
        )
        
        ar_text = Label(
            text='Vista\nAR',
            font_size=sp(12),
            color=theme_manager.get_color('on_surface'),
            halign='center',
            valign='center'
        )
        ar_text.bind(size=ar_text.setter('text_size'))
        
        ar_layout.add_widget(ar_icon)
        ar_layout.add_widget(ar_text)
        ar_card.add_widget(ar_layout)
        
        def animate_ar_card(*args):
            ar_icon.animate(AnimationType.BOUNCE, 0.5)
            main_screen.show_notification(
                'AR View', 
                'Vista AR disponibile!',
                'success'
            )
        
        ar_card.bind(on_touch_down=lambda w, t: animate_ar_card() if w.collide_point(*t.pos) else None)
        
        # Card Achievement
        achievement_card = MaterialCard()
        achievement_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(8),
            padding=dp(15)
        )
        
        achievement_icon = AnimatedMaterialIcon(
            'achievement',
            size=(dp(32), dp(32)),
            size_hint=(None, None),
            pos_hint={'center_x': 0.5}
        )
        
        achievement_text = Label(
            text='Achievement\n& Premi',
            font_size=sp(12),
            color=theme_manager.get_color('on_surface'),
            halign='center',
            valign='center'
        )
        achievement_text.bind(size=achievement_text.setter('text_size'))
        
        achievement_layout.add_widget(achievement_icon)
        achievement_layout.add_widget(achievement_text)
        achievement_card.add_widget(achievement_layout)
        
        def animate_achievement_card(*args):
            achievement_icon.animate(AnimationType.SCALE_UP, 0.3, scale=1.4)
            # Sistema particelle per celebrare
            particles = ParticleSystem(
                pos_hint={'center_x': 0.7, 'center_y': 0.5},
                size_hint=(None, None),
                size=(dp(100), dp(100))
            )
            main_layout.add_widget(particles)
            particles.start_particles('stars', 15)
            
            # Rimuovi particelle dopo animazione
            Clock.schedule_once(lambda dt: main_layout.remove_widget(particles), 3)
            
            main_screen.show_notification(
                'Achievement!', 
                '🏆 Nuovo traguardo sbloccato!',
                'success'
            )
        
        achievement_card.bind(on_touch_down=lambda w, t: animate_achievement_card() if w.collide_point(*t.pos) else None)
        
        # Assembla cards
        cards_layout.add_widget(scan_card)
        cards_layout.add_widget(ar_card)
        cards_layout.add_widget(achievement_card)
        
        # Progress indicator demo
        progress_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            spacing=dp(20)
        )
        
        # Progress circolare
        circular_progress = ModernProgressIndicator('circular')
        circular_progress.start_indeterminate()
        
        # Progress lineare
        linear_progress = ModernProgressIndicator('linear')
        linear_progress.progress = 0.7
        
        progress_label = Label(
            text='Loading... 70%',
            font_size=sp(12),
            color=theme_manager.get_color('on_surface'),
            size_hint=(1, 1)
        )
        
        progress_layout.add_widget(circular_progress)
        progress_layout.add_widget(linear_progress)
        progress_layout.add_widget(progress_label)
        
        # Test buttons layout
        test_buttons = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(15)
        )
        
        # Test notification
        notif_btn = MaterialButton(
            text='🔔 Test Notifica',
            size_hint=(0.5, 1)
        )
        notif_btn.bind(on_press=self.test_notification)
        
        # Test animazioni
        anim_btn = MaterialButton(
            text='✨ Test Animazioni',
            size_hint=(0.5, 1)
        )
        anim_btn.bind(on_press=self.test_animations)
        
        test_buttons.add_widget(notif_btn)
        test_buttons.add_widget(anim_btn)
        
        # Assembla content area
        content_area.add_widget(cards_layout)
        content_area.add_widget(progress_layout)
        content_area.add_widget(test_buttons)
        
        # FAB principale
        fab = FloatingActionButton(
            'camera',
            pos_hint={'right': 0.95, 'y': 0.15}
        )
        fab.bind(on_press=self.fab_pressed)
        
        # Navigation bar
        nav_bar = NavigationBar(
            pos_hint={'x': 0, 'y': 0}
        )
        
        nav_bar.add_nav_item('home', 'Home', lambda: print('🏠 Home'))
        nav_bar.add_nav_item('search', 'Cerca', lambda: print('🔍 Cerca'))
        nav_bar.add_nav_item('favorite', 'Preferiti', lambda: print('❤️ Preferiti'))
        nav_bar.add_nav_item('person', 'Profilo', lambda: print('👤 Profilo'))
        
        # Assembla layout principale
        main_layout.add_widget(header)
        main_layout.add_widget(search_bar)
        main_layout.add_widget(content_area)
        main_layout.add_widget(fab)
        main_layout.add_widget(nav_bar)
        
        main_screen.add_widget(main_layout)
        sm.add_widget(main_screen)
        
        return sm
    
    def custom_entrance_animation(self):
        """Animazione personalizzata entrata screen"""
        # Anima titolo icon
        def find_and_animate_title_icon(*args):
            if self.root and hasattr(self.root, 'current_screen'):
                for widget in self.root.current_screen.walk():
                    if hasattr(widget, 'icon_name') and widget.icon_name == 'monument':
                        widget.animate(AnimationType.BOUNCE, 0.6)
                        break
        
        # Ritarda l'animazione per permettere al root di essere configurato
        Clock.schedule_once(find_and_animate_title_icon, 0.5)
    
    def toggle_theme(self, *args):
        """Toggle tema scuro/chiaro"""
        theme_manager.toggle_theme()
        
        # Aggiorna icona bottone
        btn = args[0]
        btn.text = '🌙' if theme_manager.is_dark_mode else '☀️'
        
        # Notifica cambio tema
        if hasattr(self.root.current_screen, 'show_notification'):
            mode = 'Scuro' if theme_manager.is_dark_mode else 'Chiaro'
            self.root.current_screen.show_notification(
                'Tema cambiato',
                f'Modalità {mode} attivata',
                'info',
                2.0
            )
    
    def on_search(self, query):
        """Handler ricerca"""
        if query.strip():
            # Notifica ricerca
            if hasattr(self.root.current_screen, 'show_notification'):
                self.root.current_screen.show_notification(
                    'Ricerca',
                    f'Cercando: "{query}"',
                    'info',
                    2.5
                )
            print(f"🔍 Ricerca: {query}")
    
    def fab_pressed(self, *args):
        """Handler FAB pressed"""
        if hasattr(self.root.current_screen, 'show_notification'):
            self.root.current_screen.show_notification(
                'Fotocamera',
                'Fotocamera principale attivata!',
                'success',
                2.0
            )
        print("📷 FAB Camera pressed")
    
    def test_notification(self, *args):
        """Test diversi tipi di notifiche"""
        import random
        
        notifications = [
            ('Info', 'Questa è una notifica informativa', 'info'),
            ('Successo!', 'Operazione completata con successo', 'success'),
            ('Attenzione', 'Controlla le impostazioni', 'warning'),
            ('Errore', 'Si è verificato un errore', 'error')
        ]
        
        title, message, type_ = random.choice(notifications)
        
        if hasattr(self.root.current_screen, 'show_notification'):
            self.root.current_screen.show_notification(title, message, type_)
    
    def test_animations(self, *args):
        """Test varie animazioni"""
        # Trova tutte le icone animate e animale
        for widget in self.root.current_screen.walk():
            if isinstance(widget, AnimatedMaterialIcon):
                import random
                animations = [AnimationType.PULSE, AnimationType.BOUNCE, AnimationType.SHAKE]
                animation = random.choice(animations)
                
                # Delay casuale per effetto stagger
                delay = random.uniform(0, 1.5)
                Clock.schedule_once(lambda dt, w=widget, a=animation: w.animate(a, 0.5), delay)
        
        if hasattr(self.root.current_screen, 'show_notification'):
            self.root.current_screen.show_notification(
                'Animazioni!',
                '✨ Test animazioni in corso...',
                'success'
            )




def main():
    """Avvia demo UI migliorata"""
    try:
        print("🚀 Avvio Demo Enhanced UI...")
        app = EnhancedUIDemo()
        app.run()
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
