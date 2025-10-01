"""
Monument Recognizer - Main Enhanced
Versione modernizzata dell'app con integrazione completa dei nuovi sistemi
"""

import os
import threading
from pathlib import Path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from datetime import datetime

# Import moduli esistenti
from monument_recognizer import MonumentRecognizer
from camera_interface import CameraInterface
from user_system import UserSystem
from auth_ui import AuthManager
from visit_tracker import VisitTracker
from map_generator import MapGenerator
from dashboard_manager import DashboardManager
from social_sharing import SocialSharingManager
from social_ui import SocialSharePopup, QuickShareButton
from gamification import GamificationManager
from gamification_ui import GamificationDashboard, AchievementUnlockedPopup, LevelUpPopup

# Import nuovi sistemi
from modern_ui import (
    theme_manager, MaterialCard, MaterialButton, MaterialIcon, 
    MaterialAppBar, FloatingActionButton, ThemeMode
)
from advanced_search import (
    AdvancedSearchEngine, SearchQuery, SearchCategory, SearchFilter
)
from intelligent_cache import (
    IntelligentCache, CacheType, cached, app_cache
)


class ModernSearchWidget(BoxLayout):
    """Widget di ricerca moderno con autocompletamento"""
    
    def __init__(self, search_engine, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(8), **kwargs)
        self.search_engine = search_engine
        self.suggestions_visible = False
        
        # Container per search bar
        search_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(8))
        
        # Input di ricerca
        self.search_input = TextInput(
            hint_text='🔍 Cerca monumenti, città, stili...',
            size_hint_x=0.85,
            multiline=False,
            font_size=sp(16)
        )
        self.search_input.bind(text=self.on_text_change)
        self.search_input.bind(on_text_validate=self.perform_search)
        
        # Pulsante ricerca
        search_btn = MaterialButton(
            text='',
            button_type='filled',
            size=(dp(48), dp(48)),
            size_hint=(None, None)
        )
        search_btn.add_widget(MaterialIcon('search'))
        search_btn.bind(on_press=self.perform_search)
        
        search_container.add_widget(self.search_input)
        search_container.add_widget(search_btn)
        
        # Container per suggerimenti
        self.suggestions_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=0,
            spacing=dp(2)
        )
        
        # Container per filtri rapidi
        filters_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(32),
            spacing=dp(8)
        )
        
        # Filtri rapidi
        filter_buttons = [
            ('Tutto', None),
            ('Antica', 'Antica'),
            ('Medievale', 'Medievale'),
            ('Moderna', 'Moderna'),
            ('⭐ Top', 'popular')
        ]
        
        for name, filter_value in filter_buttons:
            btn = MaterialButton(
                text=name,
                button_type='outlined',
                size_hint_x=None,
                width=dp(80)
            )
            btn.filter_value = filter_value
            btn.bind(on_press=self.apply_filter)
            filters_container.add_widget(btn)
        
        self.add_widget(search_container)
        self.add_widget(self.suggestions_container)
        self.add_widget(filters_container)
        
        # Callback per risultati
        self.on_search_result = None
    
    def on_text_change(self, instance, text):
        """Gestisce cambiamento testo per autocompletamento"""
        if len(text) >= 2:
            self.show_suggestions(text)
        else:
            self.hide_suggestions()
    
    def show_suggestions(self, partial_text):
        """Mostra suggerimenti autocompletamento"""
        suggestions = self.search_engine.get_autocomplete_suggestions(partial_text, limit=5)
        
        # Pulisce suggerimenti esistenti
        self.suggestions_container.clear_widgets()
        
        if suggestions:
            self.suggestions_container.height = len(suggestions) * dp(36)
            
            for suggestion in suggestions:
                suggestion_btn = Button(
                    text=suggestion,
                    size_hint_y=None,
                    height=dp(32),
                    background_color=(0.95, 0.95, 0.95, 1),
                    color=(0.2, 0.2, 0.2, 1)
                )
                suggestion_btn.bind(on_press=lambda btn, s=suggestion: self.select_suggestion(s))
                self.suggestions_container.add_widget(suggestion_btn)
                
            self.suggestions_visible = True
        else:
            self.hide_suggestions()
    
    def hide_suggestions(self):
        """Nascondi suggerimenti"""
        if self.suggestions_visible:
            self.suggestions_container.clear_widgets()
            self.suggestions_container.height = 0
            self.suggestions_visible = False
    
    def select_suggestion(self, suggestion):
        """Seleziona un suggerimento"""
        self.search_input.text = suggestion
        self.hide_suggestions()
        self.perform_search()
    
    def apply_filter(self, instance):
        """Applica filtro rapido"""
        filter_value = instance.filter_value
        
        if filter_value == 'popular':
            # Ricerca monumenti popolari
            query = SearchQuery(
                text="",
                filters={SearchFilter.POPULARITY: 50000},
                limit=10
            )
        elif filter_value:
            # Filtro per era
            query = SearchQuery(
                text="",
                filters={SearchFilter.ERA: filter_value},
                limit=10
            )
        else:
            # Mostra tutto
            query = SearchQuery(text="", limit=10)
        
        results = self.search_engine.search(query)
        if self.on_search_result:
            self.on_search_result(results)
    
    def perform_search(self, *args):
        """Esegue ricerca completa"""
        query_text = self.search_input.text.strip()
        self.hide_suggestions()
        
        if query_text:
            query = SearchQuery(text=query_text, limit=15)
            results = self.search_engine.search(query)
            
            if self.on_search_result:
                self.on_search_result(results)
        
        # Nasconde la tastiera
        self.search_input.focus = False


class ModernMainScreen(Screen):
    """Schermata principale modernizzata con nuovi sistemi integrati"""
    
    def __init__(self, user_system: UserSystem, **kwargs):
        super().__init__(**kwargs)
        self.user_system = user_system
        
        # Inizializza sistemi core
        self.recognizer = MonumentRecognizer(user_system)
        self.selected_image_path = None
        
        # Nuovi sistemi
        self.search_engine = AdvancedSearchEngine()
        self.cache = app_cache  # Cache globale
        
        # Sistemi esistenti
        self.camera_interface = CameraInterface()
        self.social_manager = SocialSharingManager()
        self.gamification_manager = GamificationManager()
        
        # Registra callback per tema
        theme_manager.register_callback(self.on_theme_changed)
        
        # Build UI
        self.build_modern_ui()
        
        # Welcome
        Clock.schedule_once(lambda dt: self.show_welcome_message(), 0.1)
    
    def build_modern_ui(self):
        """Costruisce l'interfaccia moderna"""
        # Layout principale
        main_layout = BoxLayout(orientation='vertical', spacing=dp(0))
        
        # App Bar moderna
        self.app_bar = MaterialAppBar(
            title='Monument Recognizer',
            actions=[
                {'icon': 'search', 'callback': self.toggle_search},
                {'icon': 'dark_mode' if theme_manager.current_mode == ThemeMode.LIGHT else 'light_mode', 
                 'callback': self.toggle_theme}
            ]
        )
        
        # Container scrollabile per contenuto
        content_scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(16))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Widget di ricerca (inizialmente nascosto)
        self.search_widget = ModernSearchWidget(self.search_engine, size_hint_y=None)
        self.search_widget.height = 0
        self.search_widget.opacity = 0
        self.search_widget.on_search_result = self.display_search_results
        
        # Info utente card
        self.user_card = self.create_user_info_card()
        
        # Image display card
        self.image_card = self.create_image_display_card()
        
        # Action buttons card
        self.actions_card = self.create_actions_card()
        
        # Results card
        self.results_card = self.create_results_card()
        
        # Aggiungi widget al layout
        content_layout.add_widget(self.search_widget)
        content_layout.add_widget(self.user_card)
        content_layout.add_widget(self.image_card)
        content_layout.add_widget(self.actions_card)
        content_layout.add_widget(self.results_card)
        
        content_scroll.add_widget(content_layout)
        
        # Layout principale
        main_layout.add_widget(self.app_bar)
        main_layout.add_widget(content_scroll)
        
        # FAB per azioni rapide
        self.fab = FloatingActionButton(
            icon='camera',
            pos_hint={'right': 1, 'y': 0},
            pos=(Window.width - dp(72), dp(16))
        )
        self.fab.bind(on_press=self.capture_photo)
        
        main_layout.add_widget(self.fab)
        
        self.add_widget(main_layout)
    
    def create_user_info_card(self):
        """Crea card info utente"""
        card = MaterialCard(size_hint_y=None, height=dp(80))
        
        layout = BoxLayout(orientation='horizontal', padding=dp(16), spacing=dp(16))
        
        # Avatar placeholder
        avatar = MaterialIcon('profile', size=(dp(48), dp(48)))
        
        # Info layout
        info_layout = BoxLayout(orientation='vertical')
        
        self.user_name_label = Label(
            text='',
            font_size=sp(18),
            bold=True,
            color=theme_manager.get_color('on_surface'),
            size_hint_y=None,
            height=dp(24),
            halign='left'
        )
        self.user_name_label.bind(size=self.user_name_label.setter('text_size'))
        
        self.user_status_label = Label(
            text='',
            font_size=sp(14),
            color=theme_manager.get_color('on_surface_variant'),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        self.user_status_label.bind(size=self.user_status_label.setter('text_size'))
        
        info_layout.add_widget(self.user_name_label)
        info_layout.add_widget(self.user_status_label)
        
        # Profile button
        self.profile_btn = MaterialButton(
            text='Profilo',
            button_type='outlined',
            size=(dp(80), dp(36)),
            size_hint=(None, None)
        )
        self.profile_btn.bind(on_press=self.show_profile)
        
        layout.add_widget(avatar)
        layout.add_widget(info_layout)
        layout.add_widget(self.profile_btn)
        
        card.add_widget(layout)
        
        self.update_user_info()
        return card
    
    def create_image_display_card(self):
        """Crea card per display immagine"""
        card = MaterialCard(size_hint_y=None, height=dp(300))
        
        layout = BoxLayout(orientation='vertical', padding=dp(16))
        
        self.image_display = Image(
            source='',
            allow_stretch=True,
            keep_ratio=True
        )
        
        layout.add_widget(self.image_display)
        card.add_widget(layout)
        
        return card
    
    def create_actions_card(self):
        """Crea card con azioni principali"""
        card = MaterialCard(size_hint_y=None, height=dp(200))
        
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        
        # Titolo
        title = Label(
            text='Azioni',
            font_size=sp(18),
            bold=True,
            color=theme_manager.get_color('on_surface'),
            size_hint_y=None,
            height=dp(24)
        )
        
        # Pulsanti principali
        main_buttons = BoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=dp(48))
        
        self.select_btn = MaterialButton(
            text='Scegli Immagine',
            button_type='outlined'
        )
        self.select_btn.bind(on_press=self.select_image)
        
        self.analyze_btn = MaterialButton(
            text='Riconosci',
            button_type='filled',
            disabled=True
        )
        self.analyze_btn.bind(on_press=self.analyze_image)
        
        main_buttons.add_widget(self.select_btn)
        main_buttons.add_widget(self.analyze_btn)
        
        # Pulsanti secondari
        secondary_buttons = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(36))
        
        secondary_btns_data = [
            ('Mappa', 'map', self.show_visits_map),
            ('Vicini', 'location', self.show_nearby_monuments),
            ('Dashboard', 'trophy', self.show_dashboard),
            ('Social', 'share', self.show_social_feed)
        ]
        
        for text, icon, callback in secondary_btns_data:
            btn = MaterialButton(
                text=text,
                button_type='text',
                size_hint_x=None,
                width=dp(80)
            )
            btn.bind(on_press=callback)
            secondary_buttons.add_widget(btn)
        
        layout.add_widget(title)
        layout.add_widget(main_buttons)
        layout.add_widget(secondary_buttons)
        
        card.add_widget(layout)
        return card
    
    def create_results_card(self):
        """Crea card per risultati"""
        self.results_card = MaterialCard(size_hint_y=None, height=dp(200))
        
        self.results_layout = BoxLayout(orientation='vertical', padding=dp(16))
        self.results_card.add_widget(self.results_layout)
        
        return self.results_card
    
    def toggle_search(self, instance):
        """Toggle widget ricerca"""
        if self.search_widget.height == 0:
            # Mostra search
            self.search_widget.height = dp(120)
            self.search_widget.opacity = 1
        else:
            # Nascondi search
            self.search_widget.height = 0
            self.search_widget.opacity = 0
    
    def toggle_theme(self, instance):
        """Toggle tema scuro/chiaro"""
        theme_manager.toggle_theme()
        
        # Aggiorna icona nel app bar
        new_icon = 'dark_mode' if theme_manager.current_mode == ThemeMode.LIGHT else 'light_mode'
        # TODO: Aggiorna icona nell'app bar
    
    def on_theme_changed(self, new_theme):
        """Callback per cambio tema"""
        # Aggiorna colori labels
        self.user_name_label.color = theme_manager.get_color('on_surface')
        self.user_status_label.color = theme_manager.get_color('on_surface_variant')
    
    def update_user_info(self):
        """Aggiorna info utente"""
        if self.user_system.is_logged_in():
            user = self.user_system.current_user
            self.user_name_label.text = f'Ciao, {user.full_name}!'
            self.user_status_label.text = '✅ Account attivo'
            self.profile_btn.text = 'Profilo'
            
            self.recognizer.update_user_context(self.user_system)
        else:
            self.user_name_label.text = 'Modalità Ospite'
            self.user_status_label.text = '🚪 Accedi per salvare i progressi'
            self.profile_btn.text = 'Login'
            
            self.recognizer.update_user_context(None)
    
    @cached(CacheType.RECOGNITION_RESULT, ttl_seconds=3600)
    def cached_recognition(self, image_path):
        """Riconoscimento con cache intelligente"""
        return self.recognizer.recognize_monument(image_path)
    
    def show_welcome_message(self):
        """Mostra messaggio di benvenuto moderno"""
        self.results_layout.clear_widgets()
        
        welcome_card_inner = BoxLayout(orientation='vertical', spacing=dp(12))
        
        # Titolo
        title = Label(
            text='🏛️ Benvenuto in Monument Recognizer!',
            font_size=sp(20),
            bold=True,
            color=theme_manager.get_color('primary'),
            size_hint_y=None,
            height=dp(32)
        )
        
        # Descrizione
        mode_info = "🔥 Google Vision AI" if self.recognizer.vision_client else "💻 Modalità Offline"
        accuracy = "90%+" if self.recognizer.vision_client else "65%"
        
        description = Label(
            text=f'Modalità: {mode_info} | Accuratezza: {accuracy}\n\nScopri la storia dei monumenti del mondo!',
            font_size=sp(14),
            color=theme_manager.get_color('on_surface'),
            size_hint_y=None,
            height=dp(60),
            halign='center'
        )
        description.bind(size=description.setter('text_size'))
        
        # Features
        features_text = '''🎯 Funzionalità Principali:
• Riconoscimento AI avanzato
• Ricerca intelligente con autocompletamento
• Cache per performance ottimali
• Tema scuro/chiaro
• Gamification completa
• Social sharing integrato'''
        
        features = Label(
            text=features_text,
            font_size=sp(12),
            color=theme_manager.get_color('on_surface_variant'),
            size_hint_y=None,
            height=dp(120),
            halign='left'
        )
        features.bind(size=features.setter('text_size'))
        
        welcome_card_inner.add_widget(title)
        welcome_card_inner.add_widget(description)
        welcome_card_inner.add_widget(features)
        
        self.results_layout.add_widget(welcome_card_inner)
    
    def display_search_results(self, results):
        """Mostra risultati di ricerca"""
        self.results_layout.clear_widgets()
        
        if not results:
            no_results = Label(
                text='🔍 Nessun risultato trovato',
                font_size=sp(16),
                color=theme_manager.get_color('on_surface_variant')
            )
            self.results_layout.add_widget(no_results)
            return
        
        # Titolo risultati
        title = Label(
            text=f'🔍 Risultati di ricerca ({len(results)})',
            font_size=sp(18),
            bold=True,
            color=theme_manager.get_color('on_surface'),
            size_hint_y=None,
            height=dp(32)
        )
        self.results_layout.add_widget(title)
        
        # Lista risultati
        for result in results[:5]:  # Mostra solo primi 5
            result_card = self.create_search_result_item(result)
            self.results_layout.add_widget(result_card)
    
    def create_search_result_item(self, result):
        """Crea item per risultato ricerca"""
        item_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=dp(8),
            spacing=dp(12)
        )
        
        # Icona
        icon = MaterialIcon('location', size=(dp(32), dp(32)))
        
        # Info
        info_layout = BoxLayout(orientation='vertical')
        
        title_label = Label(
            text=result.title,
            font_size=sp(16),
            bold=True,
            color=theme_manager.get_color('on_surface'),
            size_hint_y=None,
            height=dp(24),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        subtitle_label = Label(
            text=result.subtitle,
            font_size=sp(12),
            color=theme_manager.get_color('on_surface_variant'),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        subtitle_label.bind(size=subtitle_label.setter('text_size'))
        
        info_layout.add_widget(title_label)
        info_layout.add_widget(subtitle_label)
        
        # Score
        score_label = Label(
            text=f'{result.score:.2f}',
            font_size=sp(12),
            color=theme_manager.get_color('primary'),
            size_hint_x=None,
            width=dp(40)
        )
        
        item_layout.add_widget(icon)
        item_layout.add_widget(info_layout)
        item_layout.add_widget(score_label)
        
        return item_layout
    
    # Metodi esistenti con cache integrata
    def select_image(self, instance):
        """Seleziona immagine con UI moderna"""
        # TODO: Implementare file chooser moderno
        # Per ora usa quello esistente
        self.original_select_image(instance)
    
    def capture_photo(self, instance):
        """Scatta foto con cache"""
        # TODO: Implementare camera moderna con overlay
        # Per ora usa quella esistente
        self.original_capture_photo(instance)
    
    def analyze_image(self, instance):
        """Analizza immagine con cache intelligente"""
        if not self.selected_image_path:
            return
        
        # Mostra loading
        self.results_layout.clear_widgets()
        loading_label = Label(
            text='🔍 Analizzando immagine...\n\nCache intelligente attiva per risultati più veloci!',
            font_size=sp(16),
            color=theme_manager.get_color('primary')
        )
        self.results_layout.add_widget(loading_label)
        
        def analyze_async():
            try:
                # Usa cache intelligente
                result = self.cached_recognition(self.selected_image_path)
                Clock.schedule_once(lambda dt: self.display_recognition_result(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.display_error(str(e)), 0)
        
        threading.Thread(target=analyze_async, daemon=True).start()
    
    def display_recognition_result(self, result):
        """Mostra risultato riconoscimento con UI moderna"""
        self.results_layout.clear_widgets()
        
        if result and 'monument_name' in result:
            # Success card
            success_layout = BoxLayout(orientation='vertical', spacing=dp(12))
            
            # Titolo
            title = Label(
                text=f"🏛️ {result['monument_name']}",
                font_size=sp(20),
                bold=True,
                color=theme_manager.get_color('primary'),
                size_hint_y=None,
                height=dp(32)
            )
            
            # Confidence
            confidence = result.get('confidence', 0)
            conf_color = theme_manager.get_color('primary') if confidence > 0.7 else theme_manager.get_color('on_surface_variant')
            
            conf_label = Label(
                text=f"🎯 Confidenza: {confidence:.1%}",
                font_size=sp(14),
                color=conf_color,
                size_hint_y=None,
                height=dp(24)
            )
            
            # Descrizione
            description = result.get('description', 'Informazioni non disponibili')
            desc_label = Label(
                text=description,
                font_size=sp(14),
                color=theme_manager.get_color('on_surface'),
                text_size=(None, None),
                size_hint_y=None
            )
            desc_label.bind(texture_size=desc_label.setter('size'))
            
            # Azioni rapide
            actions_layout = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(36))
            
            share_btn = MaterialButton(text='Condividi', button_type='outlined')
            share_btn.bind(on_press=lambda x: self.quick_share_result(result))
            
            map_btn = MaterialButton(text='Mappa', button_type='outlined')
            map_btn.bind(on_press=self.show_visits_map)
            
            actions_layout.add_widget(share_btn)
            actions_layout.add_widget(map_btn)
            
            success_layout.add_widget(title)
            success_layout.add_widget(conf_label)
            success_layout.add_widget(desc_label)
            success_layout.add_widget(actions_layout)
            
            self.results_layout.add_widget(success_layout)
            
            # Processa gamification
            self.process_gamification(result)
            
        else:
            # Error card
            error_label = Label(
                text='❌ Monumento non riconosciuto\n\nProva con un\'altra immagine o verifica la qualità della foto.',
                font_size=sp(16),
                color=theme_manager.get_color('error')
            )
            self.results_layout.add_widget(error_label)
    
    def display_error(self, error_msg):
        """Mostra errore con UI moderna"""
        self.results_layout.clear_widgets()
        
        error_label = Label(
            text=f'❌ Errore: {error_msg}\n\nVerifica la connessione e riprova.',
            font_size=sp(16),
            color=theme_manager.get_color('error')
        )
        self.results_layout.add_widget(error_label)
    
    def quick_share_result(self, result):
        """Condivisione rapida risultato"""
        # Integrazione con social sharing esistente
        if hasattr(self, 'social_manager'):
            monument_name = result.get('monument_name', 'Monumento sconosciuto')
            # TODO: Implementare condivisione rapida moderna
    
    def process_gamification(self, result):
        """Processa gamification per risultato"""
        if hasattr(self, 'gamification_manager') and self.user_system.is_logged_in():
            user_id = self.user_system.current_user.id
            
            visit_data = {
                'monument_name': result.get('monument_name'),
                'confidence': result.get('confidence', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Processa in background
            def process_async():
                try:
                    gam_result = self.gamification_manager.process_monument_visit(user_id, visit_data)
                    
                    # Mostra achievement se sbloccati
                    if gam_result.get('achievements_unlocked'):
                        Clock.schedule_once(lambda dt: self.show_achievement_popup(gam_result), 0)
                    
                    # Mostra level up se avvenuto
                    if gam_result.get('level_up'):
                        Clock.schedule_once(lambda dt: self.show_levelup_popup(gam_result), 0)
                
                except Exception as e:
                    print(f"Errore gamification: {e}")
            
            threading.Thread(target=process_async, daemon=True).start()
    
    def show_achievement_popup(self, gam_result):
        """Mostra popup achievement con UI moderna"""
        achievements = gam_result.get('achievements_unlocked', [])
        if achievements:
            # TODO: Implementare popup achievement moderno
            pass
    
    def show_levelup_popup(self, gam_result):
        """Mostra popup level up con UI moderna"""
        new_level = gam_result.get('new_level')
        if new_level:
            # TODO: Implementare popup level up moderno
            pass
    
    # Metodi wrapper per compatibilità
    def show_profile(self, instance):
        """Wrapper per profilo"""
        screen_manager = self.parent
        if screen_manager and hasattr(screen_manager, 'current'):
            screen_manager.current = 'auth_profile'
    
    def show_visits_map(self, instance):
        """Wrapper per mappa"""
        # TODO: Implementare mappa moderna
        pass
    
    def show_nearby_monuments(self, instance):
        """Wrapper per monumenti vicini"""
        # TODO: Implementare con ricerca avanzata
        pass
    
    def show_dashboard(self, instance):
        """Wrapper per dashboard"""
        # TODO: Implementare dashboard moderna
        pass
    
    def show_social_feed(self, instance):
        """Wrapper per social feed"""
        # TODO: Implementare feed moderno
        pass
    
    # Metodi di compatibilità (da rimuovere dopo migrazione completa)
    def original_select_image(self, instance):
        """Metodo originale select_image"""
        # Copia del codice originale
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        file_chooser = FileChooserIconView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif'],
            size_hint_y=0.8
        )
        
        button_layout = BoxLayout(size_hint_y=0.2, spacing=dp(10))
        select_btn = Button(text='Seleziona', size_hint_x=0.5)
        cancel_btn = Button(text='Annulla', size_hint_x=0.5)
        
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Seleziona un\'immagine',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def on_select(btn):
            if file_chooser.selection:
                self.selected_image_path = file_chooser.selection[0]
                self.image_display.source = self.selected_image_path
                self.analyze_btn.disabled = False
            popup.dismiss()
        
        def on_cancel(btn):
            popup.dismiss()
        
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=on_cancel)
        
        popup.open()
    
    def original_capture_photo(self, instance):
        """Metodo originale capture_photo"""
        if not self.camera_interface.is_camera_available():
            return
        
        loading_popup = Popup(
            title='Fotocamera',
            content=Label(text='📷 Avvio fotocamera...'),
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        loading_popup.open()
        
        def on_photo_success(photo_path):
            loading_popup.dismiss()
            self.selected_image_path = photo_path
            self.image_display.source = photo_path
            self.analyze_btn.disabled = False
        
        def on_photo_error(error_message):
            loading_popup.dismiss()
        
        self.camera_interface.take_photo(on_photo_success, on_photo_error)


class ModernMonumentRecognizerApp(App):
    """App principale modernizzata"""
    
    def build(self):
        Window.clearcolor = theme_manager.get_color('background')
        
        # Sistema utenti
        user_system = UserSystem()
        
        # Screen manager
        sm = ScreenManager()
        
        # Schermata principale moderna
        main_screen = ModernMainScreen(user_system, name='main')
        sm.add_widget(main_screen)
        
        # TODO: Aggiungere altre schermate modernizzate
        
        # Aggiorna background quando cambia tema
        def update_bg(theme):
            Window.clearcolor = theme_manager.get_color('background')
        
        theme_manager.register_callback(update_bg)
        
        return sm


if __name__ == '__main__':
    ModernMonumentRecognizerApp().run()
