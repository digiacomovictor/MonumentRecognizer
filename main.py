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
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

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
from advanced_animations import (MaterialIcons, AnimatedMaterialIcon, 
                               AnimationController, AnimationType, setup_material_fonts)
from enhanced_modern_ui import (NavigationBar, FloatingActionButton, SearchBar,
                               NotificationCard, EnhancedScreen, ModernScreenManager)

class MainScreen(Screen):
    """Schermata principale dell'app con riconoscimento monumenti."""
    
    def __init__(self, user_system: UserSystem, **kwargs):
        super().__init__(**kwargs)
        self.user_system = user_system
        
        # Inizializza il riconoscitore con il sistema utenti PRIMA di build_ui
        self.recognizer = MonumentRecognizer(user_system)
        self.selected_image_path = None
        
        # Inizializza l'interfaccia fotocamera
        self.camera_interface = CameraInterface()
        
        # Inizializza il manager di condivisione social
        self.social_manager = SocialSharingManager()
        
        # Inizializza il manager di gamification
        self.gamification_manager = GamificationManager()
        
        # Costruisce UI dopo aver inizializzato tutto
        self.build_ui()
        
        # Messaggio di benvenuto
        self.show_welcome_message()
    
    def build_ui(self):
        """Costruisce l'interfaccia principale dell'app."""
        # Layout principale
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # Header con titolo e profilo utente
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=dp(10))
        
        # Titolo dell'app
        title = Label(
            text='🏛️ Monument Recognizer',
            size_hint_x=0.7,
            font_size=dp(22),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)
        )
        
        # Pulsante profilo utente
        self.profile_button = Button(
            text='👤 Profilo',
            size_hint_x=0.3,
            font_size=dp(12),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        self.profile_button.bind(on_press=self.show_profile)
        
        header_layout.add_widget(title)
        header_layout.add_widget(self.profile_button)
        
        # Info utente (se loggato)
        self.user_info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=0, spacing=dp(5))
        self.user_info_label = Label(
            text='',
            font_size=dp(12),
            color=(0.3, 0.7, 0.3, 1),
            size_hint_y=None,
            height=0
        )
        self.user_info_layout.add_widget(self.user_info_label)
        
        # Area per mostrare l'immagine selezionata
        self.image_display = Image(
            source='',
            size_hint_y=0.4,
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Riga pulsanti input immagine (Seleziona / Scatta)
        buttons_row = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=dp(10))

        # Pulsante per selezionare un'immagine dalla galleria/file
        select_button = Button(
            text='🖼️ Scegli Immagine',
            font_size=dp(18),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        select_button.bind(on_press=self.select_image)

        # Pulsante per scattare una foto con la fotocamera
        camera_button = Button(
            text='📷 Scatta Foto',
            font_size=dp(18),
            background_color=(0.3, 0.5, 0.9, 1)
        )
        camera_button.bind(on_press=self.capture_photo)

        buttons_row.add_widget(select_button)
        buttons_row.add_widget(camera_button)
        
        # Pulsante per analizzare l'immagine
        self.analyze_button = Button(
            text='🔍 Riconosci Monumento',
            size_hint_y=0.08,
            font_size=dp(18),
            background_color=(0.2, 0.6, 0.8, 1),
            disabled=True
        )
        self.analyze_button.bind(on_press=self.analyze_image)
        
        # Layout pulsanti aggiuntivi (primo set)
        extra_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        
        # Pulsante per visualizzare la mappa
        self.map_button = Button(
            text='🗺️ Mappa',
            font_size=dp(14),
            background_color=(0.7, 0.3, 0.7, 1)
        )
        self.map_button.bind(on_press=self.show_visits_map)
        
        # Pulsante per monumenti vicini
        self.nearby_button = Button(
            text='📍 Vicini',
            font_size=dp(14),
            background_color=(0.8, 0.6, 0.2, 1)
        )
        self.nearby_button.bind(on_press=self.show_nearby_monuments)
        
        # Pulsante per dashboard statistiche
        self.dashboard_button = Button(
            text='📊 Dashboard',
            font_size=dp(14),
            background_color=(0.2, 0.8, 0.5, 1)
        )
        self.dashboard_button.bind(on_press=self.show_dashboard)
        
        extra_buttons_layout.add_widget(self.map_button)
        extra_buttons_layout.add_widget(self.nearby_button)
        extra_buttons_layout.add_widget(self.dashboard_button)
        
        # Secondo layout pulsanti (Social e altro)
        social_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(10))
        
        # Pulsante per feed social
        self.social_feed_button = Button(
            text='👥 Feed Social',
            font_size=dp(14),
            background_color=(0.9, 0.3, 0.5, 1)
        )
        self.social_feed_button.bind(on_press=self.show_social_feed)
        
        # Pulsante per statistiche social
        self.social_stats_button = Button(
            text='📈 Social Stats',
            font_size=dp(14),
            background_color=(0.5, 0.3, 0.9, 1)
        )
        self.social_stats_button.bind(on_press=self.show_social_stats)
        
        # Pulsante gamification
        self.gamification_button = Button(
            text='\ud83c\udfae Gamification',
            font_size=dp(14),
            background_color=(0.8, 0.2, 0.8, 1)
        )
        self.gamification_button.bind(on_press=self.show_gamification_dashboard)
        
        social_buttons_layout.add_widget(self.social_feed_button)
        social_buttons_layout.add_widget(self.social_stats_button)
        social_buttons_layout.add_widget(self.gamification_button)
        
        # Area di testo scorrevole per i risultati
        self.result_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        
        self.result_scroll = ScrollView(size_hint_y=0.24)
        self.result_scroll.add_widget(self.result_layout)
        
        # Aggiungi tutti i widget al layout principale
        main_layout.add_widget(header_layout)
        main_layout.add_widget(self.user_info_layout)
        main_layout.add_widget(self.image_display)
        main_layout.add_widget(buttons_row)
        main_layout.add_widget(self.analyze_button)
        main_layout.add_widget(extra_buttons_layout)
        main_layout.add_widget(social_buttons_layout)
        main_layout.add_widget(self.result_scroll)
        
        # Aggiorna info utente
        self.update_user_info()
        
        self.add_widget(main_layout)
    
    def update_user_info(self):
        """Aggiorna le informazioni utente nell'header."""
        if self.user_system.is_logged_in():
            user = self.user_system.current_user
            self.user_info_label.text = f'✅ Ciao, {user.full_name}!'
            self.user_info_layout.height = dp(25)
            self.user_info_label.height = dp(25)
            self.profile_button.text = '👤 Profilo'
            self.profile_button.background_color = (0.3, 0.7, 0.3, 1)
            
            # Aggiorna il contesto utente nel recognizer
            self.recognizer.update_user_context(self.user_system)
        else:
            self.user_info_label.text = '🚪 Modalità Ospite - Le visite verranno salvate localmente'
            self.user_info_layout.height = dp(25)
            self.user_info_label.height = dp(25)
            self.profile_button.text = '🔓 Login'
            self.profile_button.background_color = (0.8, 0.5, 0.2, 1)
            
            # Aggiorna il contesto utente nel recognizer per ospite
            self.recognizer.update_user_context(None)
    
    def show_profile(self, instance):
        """Mostra schermata profilo/login."""
        # Naviga verso la schermata profilo attraverso il manager principale
        screen_manager = self.parent  # Questo è il ScreenManager principale
        if screen_manager and hasattr(screen_manager, 'current'):
            screen_manager.current = 'auth_profile'
    
    def show_welcome_message(self):
        """Mostra il messaggio di benvenuto."""
        # Determina quale modalità è attiva
        mode_info = "🔥 Google Vision API" if self.recognizer.vision_client else "💻 Modalità Offline"
        accuracy = "90%+" if self.recognizer.vision_client else "65%"
        
        user_greeting = ""
        if self.user_system.is_logged_in():
            user_greeting = f"Ciao {self.user_system.current_user.full_name}! 👋\n\n"
        
        welcome_text = f'''{user_greeting}Benvenuto in Monument Recognizer! 🏛️

🎯 Modalità attiva: {mode_info}
📊 Accuratezza: {accuracy}

Seleziona un'immagine di un monumento famoso
per scoprire la sua storia.

Monumenti supportati:
• Torre Eiffel • Torre di Pisa
• Colosseo • Big Ben
• Statua della Libertà • Cristo Redentore
• Taj Mahal • Machu Picchu
• Notre-Dame • Sagrada Família
{"• Migliaia di altri monumenti!" if self.recognizer.vision_client else ""}

💡 Per migliori risultati, vedi setup_google_vision.md
{"📊 Le tue visite saranno salvate nel profilo" if self.user_system.is_logged_in() else "🔓 Accedi per salvare le visite"}'''
        
        welcome_label = Label(
            text=welcome_text,
            text_size=(None, None),
            halign='center',
            valign='middle',
            font_size=dp(13),
            size_hint_y=None
        )
        welcome_label.bind(texture_size=welcome_label.setter('size'))
        self.result_layout.add_widget(welcome_label)
    
    def select_image(self, instance):
        """Apre un dialog per selezionare un'immagine."""
        # Layout per il file chooser
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # File chooser
        file_chooser = FileChooserIconView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif'],
            size_hint_y=0.8
        )
        
        # Pulsanti
        button_layout = BoxLayout(size_hint_y=0.2, spacing=dp(10))
        
        select_btn = Button(text='Seleziona', size_hint_x=0.5)
        cancel_btn = Button(text='Annulla', size_hint_x=0.5)
        
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(button_layout)
        
        # Popup
        popup = Popup(
            title='Seleziona un\'immagine',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def on_select(btn):
            if file_chooser.selection:
                self.selected_image_path = file_chooser.selection[0]
                self.image_display.source = self.selected_image_path
                self.analyze_button.disabled = False
                self.clear_results()
            popup.dismiss()
        
        def on_cancel(btn):
            popup.dismiss()
        
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=on_cancel)
        
        popup.open()
    
    def capture_photo(self, instance):
        """Avvia la fotocamera per scattare una foto."""
        if not self.camera_interface.is_camera_available():
            self.show_error_popup(
                "Fotocamera Non Disponibile",
                "La fotocamera non è disponibile su questo dispositivo.\n\n" +
                self.camera_interface.get_camera_instructions()
            )
            return
        
        # Mostra messaggio di attesa
        loading_popup = Popup(
            title='Fotocamera',
            content=Label(text='📷 Avvio fotocamera...\nSegui le istruzioni del sistema'),
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        loading_popup.open()
        
        def on_photo_success(photo_path: str):
            """Chiamato quando la foto è stata scattata con successo."""
            loading_popup.dismiss()
            self.selected_image_path = photo_path
            self.image_display.source = photo_path
            self.analyze_button.disabled = False
            self.clear_results()
            
            # Mostra conferma
            self.show_info_popup(
                "Foto Scattata!",
                f"📷 Foto salvata con successo!\n\nOra puoi procedere con il riconoscimento del monumento."
            )
        
        def on_photo_error(error_message: str):
            """Chiamato in caso di errore durante lo scatto."""
            loading_popup.dismiss()
            self.show_error_popup(
                "Errore Fotocamera",
                f"❌ {error_message}\n\n💡 Suggerimenti:\n• Verifica i permessi dell'app\n• Riprova dopo qualche secondo\n• Usa 'Scegli Immagine' come alternativa"
            )
        
        # Avvia la cattura
        self.camera_interface.take_photo(on_photo_success, on_photo_error)
    
    def show_error_popup(self, title: str, message: str):
        """Mostra un popup di errore."""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        error_label = Label(
            text=message,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        ok_button = Button(text='OK', size_hint_y=0.3)
        
        content.add_widget(error_label)
        content.add_widget(ok_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.6)
        )
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_info_popup(self, title: str, message: str):
        """Mostra un popup informativo."""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        info_label = Label(
            text=message,
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        ok_button = Button(text='Perfetto!', size_hint_y=0.3, background_color=(0.3, 0.7, 0.3, 1))
        
        content.add_widget(info_label)
        content.add_widget(ok_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.5)
        )
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def clear_results(self):
        """Pulisce l'area dei risultati."""
        self.result_layout.clear_widgets()
    
    def analyze_image(self, instance):
        """Analizza l'immagine selezionata."""
        if not self.selected_image_path:
            return
        
        # Disabilita il pulsante durante l'analisi
        self.analyze_button.disabled = True
        self.analyze_button.text = '⏳ Analizzando...'
        
        # Pulisce i risultati precedenti
        self.clear_results()
        
        # Mostra messaggio di caricamento
        loading_label = Label(
            text='🔄 Analizzando l\'immagine...\nAttendi qualche secondo.',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(80)
        )
        self.result_layout.add_widget(loading_label)
        
        # Avvia l'analisi in un thread separato
        threading.Thread(target=self._analyze_image_thread).start()
    
    def _analyze_image_thread(self):
        """Esegue l'analisi in un thread separato."""
        try:
            # Esegue il riconoscimento
            result = self.recognizer.recognize_monument(self.selected_image_path)
            
            # Aggiorna l'UI nel thread principale
            Clock.schedule_once(lambda dt: self._show_results(result), 0)
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f'Errore durante l\'analisi: {str(e)}'
            }
            Clock.schedule_once(lambda dt: self._show_results(error_result), 0)
    
    def _show_results(self, result):
        """Mostra i risultati dell'analisi."""
        # Riabilita il pulsante
        self.analyze_button.disabled = False
        self.analyze_button.text = '🔍 Riconosci Monumento'
        
        # Pulisce i risultati precedenti
        self.clear_results()
        
        if result['success']:
            # Monumento riconosciuto con successo
            monument = result['monument']
            confidence = result['confidence']
            
            # Titolo del risultato
            title_label = Label(
                text='🎉 Monumento Riconosciuto!',
                font_size=dp(18),
                bold=True,
                color=(0.2, 0.8, 0.2, 1),
                size_hint_y=None,
                height=dp(40)
            )
            self.result_layout.add_widget(title_label)
            
            # Nome del monumento
            name_label = Label(
                text=f'📍 {monument["name"]}',
                font_size=dp(20),
                bold=True,
                size_hint_y=None,
                height=dp(50)
            )
            self.result_layout.add_widget(name_label)
            
            # Località
            location_label = Label(
                text=f'🌍 {monument["location"]}',
                font_size=dp(16),
                size_hint_y=None,
                height=dp(40)
            )
            self.result_layout.add_widget(location_label)
            
            # Anno di costruzione
            year_label = Label(
                text=f'🏗️ Costruito: {monument["year_built"]}',
                font_size=dp(16),
                size_hint_y=None,
                height=dp(40)
            )
            self.result_layout.add_widget(year_label)
            
            # Stile architettonico
            style_label = Label(
                text=f'🏛️ Stile: {monument["style"]}',
                font_size=dp(16),
                size_hint_y=None,
                height=dp(40)
            )
            self.result_layout.add_widget(style_label)
            
            # Separatore
            separator = Label(
                text='─' * 30,
                font_size=dp(16),
                size_hint_y=None,
                height=dp(30)
            )
            self.result_layout.add_widget(separator)
            
            # Descrizione storica
            description_title = Label(
                text='📚 Storia del Monumento:',
                font_size=dp(18),
                bold=True,
                size_hint_y=None,
                height=dp(40)
            )
            self.result_layout.add_widget(description_title)
            
            description_label = Label(
                text=monument['description'],
                text_size=(Window.width - dp(40), None),
                font_size=dp(14),
                halign='left',
                valign='top',
                size_hint_y=None
            )
            description_label.bind(texture_size=description_label.setter('size'))
            self.result_layout.add_widget(description_label)
            
            # Livello di confidenza
            confidence_label = Label(
                text=f'🎯 Confidenza: {confidence:.0f}%',
                font_size=dp(12),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(30)
            )
            self.result_layout.add_widget(confidence_label)
            
            # Informazioni visita
            if result.get('visit_registered'):
                visit_info = Label(
                    text=result.get('visit_note', ''),
                    font_size=dp(12),
                    color=(0.2, 0.7, 0.2, 1),
                    size_hint_y=None,
                    height=dp(40)
                )
                self.result_layout.add_widget(visit_info)
            
            # Informazioni GPS se disponibili
            if result.get('distance_km'):
                distance_info = Label(
                    text=result.get('location_note', ''),
                    font_size=dp(12),
                    color=(0.3, 0.5, 0.9, 1),
                    size_hint_y=None,
                    height=dp(40)
                )
                self.result_layout.add_widget(distance_info)
            
            # Pulsanti di condivisione social
            if result['success']:
                self.add_social_sharing_buttons(result)
                
                # Elaborazione gamification per la visita
                self.process_gamification_visit(result)
            
        else:
            # Errore o monumento non riconosciuto
            error_label = Label(
                text=f'❌ {result["error"]}',
                font_size=dp(16),
                color=(0.8, 0.2, 0.2, 1),
                text_size=(Window.width - dp(40), None),
                halign='center',
                size_hint_y=None
            )
            error_label.bind(texture_size=error_label.setter('size'))
            self.result_layout.add_widget(error_label)
            
            # Suggerimenti
            suggestion_label = Label(
                text='💡 Suggerimenti:\n• Assicurati che il monumento sia ben visibile\n• Usa un\'immagine con buona illuminazione\n• Il monumento deve essere famoso e nel nostro database',
                font_size=dp(14),
                text_size=(Window.width - dp(40), None),
                halign='left',
                valign='top',
                size_hint_y=None
            )
            suggestion_label.bind(texture_size=suggestion_label.setter('size'))
            self.result_layout.add_widget(suggestion_label)
    
    def show_visits_map(self, instance):
        """Mostra la mappa delle visite dell'utente."""
        try:
            # Crea il map generator
            map_generator = MapGenerator(
                monuments_db=self.recognizer.monuments_db,
                visit_tracker=self.recognizer.visit_tracker
            )
            
            # Genera la mappa
            map_file = map_generator.create_visited_monuments_map()
            
            # Apri nel browser
            success = map_generator.open_map_in_browser(map_file)
            
            if success:
                self.show_info_popup(
                    "Mappa Generata!",
                    f"🗺️ Mappa delle tue visite aperta nel browser!\n\nFile salvato: {map_file}"
                )
            else:
                self.show_error_popup(
                    "Errore Mappa", 
                    "Impossibile aprire la mappa nel browser. Controlla i permessi."
                )
                
        except Exception as e:
            self.show_error_popup(
                "Errore Generazione Mappa",
                f"Errore nella generazione della mappa: {str(e)}"
            )
    
    def show_nearby_monuments(self, instance):
        """Mostra monumenti nelle vicinanze dell'utente."""
        try:
            # Ottieni monumenti vicini
            nearby_monuments = self.recognizer.get_nearby_monuments(radius_km=100)
            
            if not nearby_monuments:
                self.show_info_popup(
                    "Nessun Monumento Vicino",
                    "📍 Non ci sono monumenti noti entro 100km dalla tua posizione.\n\nProva ad aggiornare la posizione GPS o espandi il raggio di ricerca."
                )
                return
            
            # Crea mappa monumenti vicini se abbiamo la posizione GPS
            if self.recognizer.gps_manager.current_position:
                map_generator = MapGenerator(
                    monuments_db=self.recognizer.monuments_db,
                    visit_tracker=self.recognizer.visit_tracker
                )
                
                map_file = map_generator.create_nearby_monuments_map(
                    user_location=self.recognizer.gps_manager.current_position,
                    nearby_monuments=nearby_monuments
                )
                
                success = map_generator.open_map_in_browser(map_file)
                
                if success:
                    self.show_info_popup(
                        "Monumenti Vicini",
                        f"🗺️ Mappa dei monumenti vicini aperta!\n\n📍 Trovati {len(nearby_monuments)} monumenti entro 100km"
                    )
                else:
                    self.show_nearby_list(nearby_monuments)
            else:
                self.show_nearby_list(nearby_monuments)
                
        except Exception as e:
            self.show_error_popup(
                "Errore Monumenti Vicini",
                f"Errore nella ricerca: {str(e)}"
            )
    
    def show_nearby_list(self, nearby_monuments):
        """Mostra lista monumenti vicini in un popup."""
        monuments_text = "\n".join([
            f"• {m['name']} ({m['distance_km']}km) - {m['location']}"
            for m in nearby_monuments[:10]  # Mostra max 10
        ])
        
        if len(nearby_monuments) > 10:
            monuments_text += f"\n\n... e altri {len(nearby_monuments) - 10} monumenti"
        
        self.show_info_popup(
            f"📍 Monumenti Vicini ({len(nearby_monuments)})",
            monuments_text
        )
    
    def show_dashboard(self, instance):
        """Mostra dashboard statistiche dell'utente."""
        try:
            # Crea dashboard manager
            dashboard_manager = DashboardManager(
                visit_tracker=self.recognizer.visit_tracker,
                monuments_db=self.recognizer.monuments_db,
                user_system=self.user_system
            )
            
            # Calcola statistiche
            stats = dashboard_manager.calculate_comprehensive_stats()
            
            if stats.total_visits == 0:
                self.show_info_popup(
                    "Dashboard Vuota",
                    "📊 Non hai ancora visitato nessun monumento!\n\nInizia a scattare foto e riconoscere monumenti per vedere statistiche interessanti nella dashboard."
                )
                return
            
            # Genera grafici se disponibili
            chart_files = dashboard_manager.generate_matplotlib_charts(stats)
            
            # Genera report HTML
            html_report = dashboard_manager.generate_html_report(stats, chart_files)
            
            # Prova anche dashboard interattiva Plotly
            interactive_dashboard = dashboard_manager.generate_plotly_interactive_dashboard(stats)
            
            # Apri nel browser
            success = dashboard_manager.open_dashboard_in_browser(html_report)
            
            if success:
                dashboard_info = f"📊 Dashboard aperta nel browser!\n\n" \
                               f"📈 Statistiche generate:\n" \
                               f"• {stats.total_visits} visite totali\n" \
                               f"• {stats.unique_monuments} monumenti unici\n" \
                               f"• {stats.countries_visited} paesi visitati\n" \
                               f"• {len([a for a in stats.achievement_progress.values() if a['completed']])} achievement completati"
                
                if interactive_dashboard:
                    dashboard_info += f"\n\n🎯 Dashboard interattiva salvata: {interactive_dashboard}"
                
                self.show_info_popup("Dashboard Generata!", dashboard_info)
            else:
                self.show_error_popup(
                    "Errore Dashboard",
                    "Impossibile aprire la dashboard nel browser. Controlla i permessi."
                )
                
        except Exception as e:
            self.show_error_popup(
                "Errore Dashboard",
                f"Errore nella generazione della dashboard: {str(e)}\n\nVerifica che matplotlib sia installato correttamente."
            )
    
    def add_social_sharing_buttons(self, result):
        """Aggiunge i pulsanti di condivisione social ai risultati."""
        try:
            # Separatore prima dei pulsanti social
            social_separator = Label(
                text='═' * 20 + ' CONDIVIDI ' + '═' * 20,
                font_size=dp(14),
                color=(0.5, 0.3, 0.9, 1),
                size_hint_y=None,
                height=dp(30)
            )
            self.result_layout.add_widget(social_separator)
            
            # Layout per pulsanti social
            social_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10),
                padding=dp(10)
            )
            
            # Prepara dati visita per condivisione
            visit_data = {
                'id': result.get('visit_id', 0),
                'user_id': self.user_system.current_user.username if self.user_system.is_logged_in() else 'guest',
                'monument_name': result['monument']['name'],
                'description': result['monument']['description'][:150] + '...' if len(result['monument']['description']) > 150 else result['monument']['description'],
                'location': result['monument']['location'],
                'image_path': self.selected_image_path,
                'timestamp': result.get('timestamp', '')
            }
            
            # Pulsante condivisione completa
            share_full_btn = Button(
                text='📤 Condividi',
                font_size=dp(12),
                background_color=(0.3, 0.7, 0.9, 1)
            )
            share_full_btn.bind(on_press=lambda x: SocialSharePopup(visit_data, self.social_manager).open())
            
            # Pulsante condivisione rapida su Twitter
            twitter_btn = Button(
                text='🐦 Tweet',
                font_size=dp(12),
                background_color=(0.11, 0.63, 0.95, 1)
            )
            twitter_btn.bind(on_press=lambda x: self.quick_share_to_platform(visit_data, 'twitter'))
            
            # Pulsante feed interno
            feed_btn = Button(
                text='📱 Feed App',
                font_size=dp(12),
                background_color=(0.9, 0.3, 0.5, 1)
            )
            feed_btn.bind(on_press=lambda x: self.quick_share_to_internal(visit_data))
            
            social_layout.add_widget(share_full_btn)
            social_layout.add_widget(twitter_btn)
            social_layout.add_widget(feed_btn)
            
            self.result_layout.add_widget(social_layout)
            
        except Exception as e:
            print(f"Errore nell'aggiunta pulsanti social: {e}")
    
    def quick_share_to_platform(self, visit_data, platform):
        """Condivisione rapida su una piattaforma specifica."""
        try:
            success = self.social_manager.share_to_platform(visit_data, platform, 'discovery')
            if success:
                # Elabora gamification per condivisione
                self.process_social_share_gamification(visit_data, platform)
                
                self.show_info_popup(
                    "Condivisione Avviata!",
                    f"🚀 Condivisione su {platform} in corso...\n\nIl browser dovrebbe aprirsi automaticamente."
                )
            else:
                self.show_error_popup(
                    "Errore Condivisione",
                    f"❌ Impossibile condividere su {platform}."
                )
        except Exception as e:
            print(f"Errore condivisione rapida: {e}")
            self.show_error_popup(
                "Errore Condivisione",
                f"Errore durante la condivisione: {str(e)}"
            )
    
    def quick_share_to_internal(self, visit_data):
        """Condivisione rapida nel feed interno."""
        try:
            success = self.social_manager.share_to_app_feed(
                visit_data, 
                f"🏛️ Ho appena visitato {visit_data['monument_name']}! Un'esperienza fantastica con Monument Recognizer! 📱"
            )
            if success:
                # Elabora gamification per condivisione interna
                self.process_social_share_gamification(visit_data, 'internal_feed')
                
                self.show_info_popup(
                    "Condiviso nel Feed!",
                    "📱 La tua visita è stata condivisa nel feed interno!\n\nOra altri utenti possono vedere la tua scoperta."
                )
            else:
                self.show_error_popup(
                    "Errore Condivisione",
                    "❌ Impossibile condividere nel feed interno."
                )
        except Exception as e:
            print(f"Errore condivisione interna: {e}")
            self.show_error_popup(
                "Errore Condivisione",
                f"Errore durante la condivisione: {str(e)}"
            )
    
    def show_social_feed(self, instance):
        """Mostra il feed social interno dell'app."""
        try:
            from social_ui import SocialFeedScreen
            
            feed_screen = SocialFeedScreen(self.social_manager)
            
            # Crea popup con feed
            feed_popup = Popup(
                title="🏛️ Feed Social Monument Recognizer",
                content=feed_screen,
                size_hint=(0.95, 0.9)
            )
            
            feed_popup.open()
            
        except Exception as e:
            print(f"Errore nell'apertura del feed social: {e}")
            self.show_error_popup(
                "Errore Feed Social",
                f"Impossibile aprire il feed social: {str(e)}"
            )
    
    def show_social_stats(self, instance):
        """Mostra le statistiche social dell'utente."""
        try:
            user_id = self.user_system.current_user.username if self.user_system.is_logged_in() else 'guest'
            stats = self.social_manager.get_share_stats(user_id)
            
            if not stats or stats.get('total_shares', 0) == 0:
                self.show_info_popup(
                    "📈 Statistiche Social",
                    "📊 Non hai ancora condiviso nessun monumento sui social media!\n\nInizia a condividere le tue visite per vedere statistiche interessanti qui."
                )
                return
            
            # Formatta le statistiche
            platform_text = ""
            if stats.get('platform_stats'):
                platform_text = "\n\n📱 Condivisioni per piattaforma:\n"
                for platform, count in stats['platform_stats'].items():
                    platform_text += f"• {platform}: {count}\n"
            
            stats_text = f"📊 Le tue statistiche social:\n\n" \
                        f"📤 Condivisioni totali: {stats.get('total_shares', 0)}\n" \
                        f"📱 Post nel feed interno: {stats.get('internal_posts', 0)}\n" \
                        f"👍 Like ricevuti: {stats.get('total_likes_received', 0)}" \
                        f"{platform_text}"
            
            self.show_info_popup(
                "📈 Statistiche Social",
                stats_text
            )
            
        except Exception as e:
            print(f"Errore nel recupero statistiche social: {e}")
            self.show_error_popup(
                "Errore Statistiche",
                f"Impossibile recuperare le statistiche: {str(e)}"
            )
    
    def process_gamification_visit(self, result):
        """Elabora una visita per il sistema gamification"""
        try:
            user_id = self.user_system.current_user.username if self.user_system.is_logged_in() else 'guest'
            
            # Prepara dati visita
            visit_data = {
                'monument_name': result['monument']['name'],
                'location': result['monument']['location'],
                'style': result['monument'].get('style', ''),
                'year_built': result['monument'].get('year_built', ''),
                'timestamp': result.get('timestamp', '')
            }
            
            # Elabora visita nel sistema gamification
            gamification_result = self.gamification_manager.process_monument_visit(user_id, visit_data)
            
            # Mostra feedback gamification se ci sono ricompense
            if gamification_result.get('points_awarded', 0) > 0:
                self.show_gamification_feedback(gamification_result)
            
            # Mostra achievement sbloccati
            if gamification_result.get('achievements_unlocked'):
                for achievement_id in gamification_result['achievements_unlocked']:
                    achievement = self.gamification_manager.achievements.get(achievement_id)
                    if achievement:
                        Clock.schedule_once(
                            lambda dt, ach=achievement: AchievementUnlockedPopup(ach).open(), 
                            1.0
                        )
            
            # Mostra level up
            if gamification_result.get('level_up'):
                old_level = gamification_result.get('old_level', 1)
                new_level = gamification_result.get('new_level', 1)
                Clock.schedule_once(
                    lambda dt: LevelUpPopup(old_level, new_level).open(), 
                    2.0
                )
            
        except Exception as e:
            print(f"❌ Errore elaborazione gamification: {e}")
    
    def show_gamification_feedback(self, gamification_result):
        """Mostra feedback per punti e bonus ottenuti"""
        try:
            points = gamification_result.get('points_awarded', 0)
            streak = gamification_result.get('streak_updated', False)
            challenges = gamification_result.get('challenges_completed', [])
            
            feedback_text = f"💎 +{points} Punti!\n\n"
            
            if streak:
                progress = self.gamification_manager.get_user_progress(
                    self.user_system.current_user.username if self.user_system.is_logged_in() else 'guest'
                )
                feedback_text += f"🔥 Streak: {progress.visits_streak} giorni!\n"
            
            if challenges:
                feedback_text += f"🎯 {len(challenges)} sfide completate!\n"
            
            # Popup con animazione
            feedback_popup = Popup(
                title="🎮 Ricompense Gamification!",
                content=Label(
                    text=feedback_text,
                    font_size='16sp',
                    halign='center'
                ),
                size_hint=(0.7, 0.4),
                auto_dismiss=True
            )
            
            feedback_popup.open()
            Clock.schedule_once(lambda dt: feedback_popup.dismiss(), 3.0)
            
        except Exception as e:
            print(f"❌ Errore feedback gamification: {e}")
    
    def show_gamification_dashboard(self, instance):
        """Mostra la dashboard gamification"""
        try:
            user_id = self.user_system.current_user.username if self.user_system.is_logged_in() else 'guest'
            
            # Crea dashboard
            dashboard = GamificationDashboard(self.gamification_manager, user_id)
            
            # Crea popup con dashboard
            dashboard_popup = Popup(
                title="🎮 Dashboard Gamification",
                content=dashboard,
                size_hint=(0.95, 0.9)
            )
            
            # Override del metodo close per chiudere il popup
            original_close = dashboard.close_dashboard
            dashboard.close_dashboard = lambda instance: dashboard_popup.dismiss()
            
            dashboard_popup.open()
            
        except Exception as e:
            print(f"❌ Errore apertura dashboard gamification: {e}")
            self.show_error_popup(
                "Errore Gamification",
                f"Impossibile aprire la dashboard: {str(e)}"
            )
    
    def process_social_share_gamification(self, visit_data, platform):
        """Elabora una condivisione social per gamification"""
        try:
            user_id = self.user_system.current_user.username if self.user_system.is_logged_in() else 'guest'
            
            share_data = {
                'platform': platform,
                'monument_name': visit_data.get('monument_name', ''),
                'timestamp': visit_data.get('timestamp', '')
            }
            
            # Elabora condivisione
            result = self.gamification_manager.process_social_share(user_id, share_data)
            
            # Mostra feedback se ci sono punti
            if result.get('points_awarded', 0) > 0:
                points_text = f"📤 +{result['points_awarded']} punti per condivisione!"
                
                if result.get('achievements_unlocked'):
                    points_text += f"\n🏆 {len(result['achievements_unlocked'])} achievement sbloccati!"
                
                # Popup rapido
                feedback = Popup(
                    title="🎮 Condivisione Ricompensata!",
                    content=Label(text=points_text, halign='center'),
                    size_hint=(0.6, 0.3),
                    auto_dismiss=True
                )
                feedback.open()
                Clock.schedule_once(lambda dt: feedback.dismiss(), 2.0)
            
        except Exception as e:
            print(f"❌ Errore gamification condivisione: {e}")
    
    def on_stop(self):
        """Chiamato quando l'app viene chiusa."""
        # Pulisce le foto temporanee
        if hasattr(self, 'camera_interface'):
            self.camera_interface.cleanup_temp_photos()


class MonumentApp(App):
    """Applicazione principale con sistema di autenticazione integrato."""
    
    def build(self):
        """Costruisce l'app completa con autenticazione."""
        Window.size = (400, 700)  # Dimensioni simili a uno smartphone
        
        # Inizializza sistema utenti
        self.user_system = UserSystem()
        
        # Crea screen manager principale
        self.screen_manager = ScreenManager()
        
        # Crea auth manager per le schermate di autenticazione
        self.auth_manager = AuthManager(self.user_system)
        self.auth_manager.go_to_main = self.go_to_main
        
        # Crea schermata principale
        self.main_screen = MainScreen(self.user_system, name='main')
        
        # Aggiungi schermate auth al main screen manager
        auth_screens = self.auth_manager.get_screen_manager().children[:]
        for screen in auth_screens:
            self.auth_manager.get_screen_manager().remove_widget(screen)
            # Rinomina per evitare conflitti
            if screen.name == 'login':
                screen.name = 'auth_login'
            elif screen.name == 'register':
                screen.name = 'auth_register' 
            elif screen.name == 'profile':
                screen.name = 'auth_profile'
            self.screen_manager.add_widget(screen)
        
        # Aggiungi schermata principale
        self.screen_manager.add_widget(self.main_screen)
        
        # Determina schermata iniziale
        initial_screen = 'main'
        if self.try_restore_session():
            initial_screen = 'main'
        else:
            # Se non c'è sessione, mostra direttamente l'app in modalità ospite
            initial_screen = 'main'
        
        self.screen_manager.current = initial_screen
        return self.screen_manager
    
    def try_restore_session(self) -> bool:
        """Prova a ripristinare una sessione salvata."""
        try:
            if os.path.exists('session.txt'):
                with open('session.txt', 'r') as f:
                    session_token = f.read().strip()
                
                if self.user_system.restore_session(session_token):
                    print("🔄 Sessione utente ripristinata")
                    # Aggiorna info utente nella schermata principale
                    if hasattr(self, 'main_screen'):
                        self.main_screen.update_user_info()
                        self.main_screen.show_welcome_message()
                    return True
                else:
                    # Rimuovi sessione non valida
                    os.remove('session.txt')
        except Exception as e:
            print(f"⚠️ Errore ripristino sessione: {e}")
        
        return False
    
    def go_to_main(self):
        """Vai alla schermata principale dopo login."""
        # Aggiorna le info utente
        self.main_screen.update_user_info()
        self.main_screen.clear_results()
        self.main_screen.show_welcome_message()
        
        # Cambia schermata
        self.screen_manager.current = 'main'
        
        # Mostra messaggio di benvenuto
        if self.user_system.is_logged_in():
            self.show_welcome_popup()
    
    def show_welcome_popup(self):
        """Mostra popup di benvenuto dopo login."""
        user = self.user_system.current_user
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        welcome_label = Label(
            text=f'🎉 Benvenuto, {user.full_name}!\n\nOra puoi:\n• Salvare le visite ai monumenti\n• Visualizzare statistiche personali\n• Esplorare la mappa dei tuoi viaggi',
            font_size=dp(14),
            color=(0.2, 0.7, 0.2, 1),
            text_size=(dp(300), None),
            halign='center'
        )
        
        ok_button = Button(
            text='🚀 Inizia a esplorare!',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.7, 0.2, 1)
        )
        
        content.add_widget(welcome_label)
        content.add_widget(ok_button)
        
        popup = Popup(
            title='🏛️ Monument Recognizer',
            content=content,
            size_hint=(0.9, 0.6)
        )
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def on_stop(self):
        """Chiamato quando l'app viene chiusa."""
        # Cleanup foto temporanee
        if hasattr(self, 'main_screen') and hasattr(self.main_screen, 'camera_interface'):
            self.main_screen.camera_interface.cleanup_temp_photos()
        
        # Cleanup database utenti
        if hasattr(self, 'user_system'):
            self.user_system.cleanup_expired_sessions()
        
        return super().on_stop()


if __name__ == '__main__':
    MonumentApp().run()
