"""
UI Avanzata per Gestione Notifiche Push
Interfaccia moderna con Material Design per visualizzare e gestire le notifiche.
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.utils import get_color_from_hex

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Import dei nostri sistemi
from push_notifications import (
    PushNotificationManager, 
    NotificationType, 
    NotificationPriority,
    PushNotification
)

try:
    from enhanced_modern_ui import MaterialCard, MaterialButton, AnimatedMaterialIcon
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False
    print("Enhanced Modern UI non disponibile, uso componenti base")


class NotificationCard(MaterialCard if MODERN_UI_AVAILABLE else BoxLayout):
    """Card per visualizzare una singola notifica"""
    
    def __init__(self, notification: PushNotification, callback=None, **kwargs):
        if not MODERN_UI_AVAILABLE:
            kwargs.pop('elevation', None)
            kwargs.pop('md_bg_color', None)
        
        super().__init__(**kwargs)
        
        self.notification = notification
        self.callback = callback
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(16)
        self.spacing = dp(8)
        
        if not MODERN_UI_AVAILABLE:
            self.orientation = 'vertical'
            # Aggiungi sfondo colorato per le card base
            with self.canvas.before:
                Color(*get_color_from_hex('#FFFFFF'))
                self.rect = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[dp(8)]
                )
                Color(*get_color_from_hex('#E0E0E0'))
                self.line = Line(
                    rounded_rectangle=(
                        self.x, self.y, self.width, self.height, dp(8)
                    ),
                    width=1
                )
            self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        self.setup_ui()
    
    def update_graphics(self, *args):
        """Aggiorna grafica per componenti base"""
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size
        if hasattr(self, 'line'):
            self.line.rounded_rectangle = (
                self.x, self.y, self.width, self.height, dp(8)
            )
    
    def setup_ui(self):
        """Configura UI della notifica card"""
        main_layout = BoxLayout(orientation='horizontal', spacing=dp(12))
        
        # Icona tipo notifica
        icon_text = self.get_notification_icon()
        if MODERN_UI_AVAILABLE:
            icon = AnimatedMaterialIcon(
                icon=icon_text,
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                theme_icon_color="Primary"
            )
        else:
            icon = Label(
                text=icon_text,
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                font_size=dp(24)
            )
        
        main_layout.add_widget(icon)
        
        # Contenuto notifica
        content_layout = BoxLayout(orientation='vertical', spacing=dp(4))
        
        # Header con titolo e timestamp
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(24))
        
        title_label = Label(
            text=self.notification.title,
            font_size=dp(16),
            bold=True,
            color=get_color_from_hex('#212121'),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        header_layout.add_widget(title_label)
        
        # Timestamp
        time_str = self.format_timestamp()
        time_label = Label(
            text=time_str,
            font_size=dp(12),
            color=get_color_from_hex('#757575'),
            size_hint_x=None,
            width=dp(80),
            halign='right',
            valign='middle'
        )
        header_layout.add_widget(time_label)
        
        content_layout.add_widget(header_layout)
        
        # Body della notifica
        body_label = Label(
            text=self.notification.body,
            font_size=dp(14),
            color=get_color_from_hex('#424242'),
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        content_layout.add_widget(body_label)
        
        # Indicatori stato
        status_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(20), spacing=dp(8))
        
        # Badge priorità
        priority_color = self.get_priority_color()
        priority_label = Label(
            text=f"{'🔥' if self.notification.priority.value > 2 else '📌'}",
            size_hint_x=None,
            width=dp(24),
            font_size=dp(12)
        )
        status_layout.add_widget(priority_label)
        
        # Indicatore lettura
        read_icon = "✓" if self.notification.read_at else "○"
        read_label = Label(
            text=read_icon,
            size_hint_x=None,
            width=dp(24),
            font_size=dp(12),
            color=get_color_from_hex('#4CAF50' if self.notification.read_at else '#FFC107')
        )
        status_layout.add_widget(read_label)
        
        status_layout.add_widget(Widget())  # Spacer
        
        content_layout.add_widget(status_layout)
        
        main_layout.add_widget(content_layout)
        
        # Pulsanti azione
        actions_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(80), spacing=dp(4))
        
        if not self.notification.read_at:
            read_btn = MaterialButton(
                text="Letto",
                size_hint_y=None,
                height=dp(32),
                font_size=dp(12)
            ) if MODERN_UI_AVAILABLE else Button(
                text="Letto",
                size_hint_y=None,
                height=dp(32),
                font_size=dp(12)
            )
            read_btn.bind(on_press=self.mark_as_read)
            actions_layout.add_widget(read_btn)
        
        # Pulsante dettagli
        details_btn = MaterialButton(
            text="Info",
            size_hint_y=None,
            height=dp(32),
            font_size=dp(12)
        ) if MODERN_UI_AVAILABLE else Button(
            text="Info",
            size_hint_y=None,
            height=dp(32),
            font_size=dp(12)
        )
        details_btn.bind(on_press=self.show_details)
        actions_layout.add_widget(details_btn)
        
        main_layout.add_widget(actions_layout)
        
        self.add_widget(main_layout)
        
        # Animazione entrata se componenti moderni disponibili
        if MODERN_UI_AVAILABLE:
            self.animate_entrance()
    
    def get_notification_icon(self) -> str:
        """Ottiene icona appropriata per tipo notifica"""
        icons = {
            NotificationType.GENERAL: "📱",
            NotificationType.MONUMENT_VISIT: "🏛️",
            NotificationType.ACHIEVEMENT: "🏆", 
            NotificationType.SOCIAL_INTERACTION: "👥",
            NotificationType.DAILY_CHALLENGE: "🎯",
            NotificationType.NEARBY_MONUMENTS: "📍",
            NotificationType.SYSTEM_UPDATE: "⚙️",
            NotificationType.REMINDER: "⏰",
            NotificationType.PROMOTIONAL: "📢",
            NotificationType.EMERGENCY: "🚨"
        }
        return icons.get(self.notification.notification_type, "📱")
    
    def get_priority_color(self) -> str:
        """Ottiene colore per priorità notifica"""
        colors = {
            NotificationPriority.LOW: "#81C784",
            NotificationPriority.NORMAL: "#64B5F6", 
            NotificationPriority.HIGH: "#FFB74D",
            NotificationPriority.URGENT: "#F06292"
        }
        return colors.get(self.notification.priority, "#64B5F6")
    
    def format_timestamp(self) -> str:
        """Formatta timestamp in formato user-friendly"""
        now = datetime.now()
        created = self.notification.created_at
        
        diff = now - created
        
        if diff.days > 0:
            return f"{diff.days}g fa"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h fa"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m fa"
        else:
            return "Ora"
    
    def animate_entrance(self):
        """Animazione di entrata della card"""
        self.opacity = 0
        self.y += dp(20)
        
        Animation(opacity=1, duration=0.3).start(self)
        Animation(y=self.y - dp(20), duration=0.3, t='out_quad').start(self)
    
    def mark_as_read(self, *args):
        """Marca notifica come letta"""
        if self.callback:
            self.callback('mark_read', self.notification.id)
    
    def show_details(self, *args):
        """Mostra dettagli notifica"""
        if self.callback:
            self.callback('show_details', self.notification)


class NotificationsList(ScrollView):
    """Lista scrollabile di notifiche"""
    
    def __init__(self, manager: PushNotificationManager, user_id: str, **kwargs):
        super().__init__(**kwargs)
        
        self.manager = manager
        self.user_id = user_id
        self.notifications: List[PushNotification] = []
        
        # Layout principale
        self.layout = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=dp(16),
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        self.add_widget(self.layout)
        
        # Carica notifiche iniziali
        self.load_notifications()
    
    def load_notifications(self, notification_type: Optional[NotificationType] = None, unread_only: bool = False):
        """Carica e visualizza notifiche"""
        self.layout.clear_widgets()
        
        try:
            # Ottieni notifiche dal manager
            self.notifications = self.manager.get_user_notifications(
                user_id=self.user_id,
                notification_type=notification_type,
                unread_only=unread_only,
                limit=50
            )
            
            if not self.notifications:
                # Messaggio vuoto
                empty_label = Label(
                    text="📭 Nessuna notifica da visualizzare",
                    font_size=dp(16),
                    color=get_color_from_hex('#757575'),
                    size_hint_y=None,
                    height=dp(100)
                )
                self.layout.add_widget(empty_label)
                return
            
            # Crea cards per ogni notifica
            for notification in self.notifications:
                card = NotificationCard(
                    notification=notification,
                    callback=self.handle_notification_action,
                    size_hint_y=None
                )
                self.layout.add_widget(card)
                
        except Exception as e:
            error_label = Label(
                text=f"❌ Errore nel caricamento notifiche: {str(e)}",
                font_size=dp(14),
                color=get_color_from_hex('#F44336')
            )
            self.layout.add_widget(error_label)
    
    def handle_notification_action(self, action: str, data):
        """Gestisce azioni sulle notifiche"""
        if action == 'mark_read':
            self.manager.mark_as_read(data)
            self.reload_notifications()
        elif action == 'show_details':
            self.show_notification_details(data)
    
    def show_notification_details(self, notification: PushNotification):
        """Mostra popup con dettagli notifica"""
        popup_content = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(20))
        
        # Titolo
        title_label = Label(
            text=notification.title,
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        popup_content.add_widget(title_label)
        
        # Dettagli
        details_text = f"""
📅 Creata: {notification.created_at.strftime('%d/%m/%Y %H:%M')}
📂 Tipo: {notification.notification_type.value.replace('_', ' ').title()}
⚡ Priorità: {notification.priority.name}
👤 Utente: {notification.user_id}
        """
        
        if notification.delivered_at:
            details_text += f"\n📬 Consegnata: {notification.delivered_at.strftime('%d/%m/%Y %H:%M')}"
        
        if notification.read_at:
            details_text += f"\n👁️ Letta: {notification.read_at.strftime('%d/%m/%Y %H:%M')}"
        
        if notification.data:
            details_text += f"\n📊 Dati: {json.dumps(notification.data, indent=2)}"
        
        details_label = Label(
            text=details_text.strip(),
            font_size=dp(12),
            halign='left',
            valign='top'
        )
        details_label.bind(size=details_label.setter('text_size'))
        
        popup_content.add_widget(details_label)
        
        # Pulsante chiudi
        close_btn = MaterialButton(
            text="Chiudi",
            size_hint_y=None,
            height=dp(40)
        ) if MODERN_UI_AVAILABLE else Button(
            text="Chiudi",
            size_hint_y=None,
            height=dp(40)
        )
        popup_content.add_widget(close_btn)
        
        popup = Popup(
            title=f"Dettagli Notifica",
            content=popup_content,
            size_hint=(0.9, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def reload_notifications(self):
        """Ricarica lista notifiche"""
        self.load_notifications()
    
    def filter_notifications(self, notification_type: Optional[NotificationType] = None, unread_only: bool = False):
        """Applica filtri alle notifiche"""
        self.load_notifications(notification_type, unread_only)


class NotificationPreferencesScreen(Screen):
    """Schermata per gestire preferenze notifiche"""
    
    def __init__(self, manager: PushNotificationManager, user_id: str, **kwargs):
        super().__init__(**kwargs)
        
        self.manager = manager
        self.user_id = user_id
        self.preferences = self.manager.get_user_preferences(user_id)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura UI preferenze"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(16))
        
        # Header
        header = Label(
            text="⚙️ Preferenze Notifiche",
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(50),
            halign='center'
        )
        main_layout.add_widget(header)
        
        # Scroll view per preferenze
        scroll = ScrollView()
        prefs_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            padding=dp(10)
        )
        prefs_layout.bind(minimum_height=prefs_layout.setter('height'))
        
        # Interruttore generale
        self.add_preference_switch(
            prefs_layout,
            "🔔 Notifiche Abilitate",
            "notifications_enabled",
            "Abilita/disabilita tutte le notifiche"
        )
        
        # Separatore
        prefs_layout.add_widget(Label(text="", size_hint_y=None, height=dp(10)))
        
        # Preferenze per tipo
        notification_types = [
            ("🏛️ Visite Monumenti", "monument_visit_enabled"),
            ("🏆 Achievement", "achievement_enabled"), 
            ("👥 Interazioni Social", "social_interaction_enabled"),
            ("🎯 Sfide Giornaliere", "daily_challenge_enabled"),
            ("📍 Monumenti Vicini", "nearby_monuments_enabled"),
            ("⚙️ Aggiornamenti Sistema", "system_update_enabled"),
            ("⏰ Promemoria", "reminder_enabled"),
            ("📢 Promozionali", "promotional_enabled"),
            ("🚨 Emergenza", "emergency_enabled")
        ]
        
        for label, key in notification_types:
            self.add_preference_switch(prefs_layout, label, key)
        
        # Separatore
        separator = Label(
            text="🌙 Modalità Non Disturbare",
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        prefs_layout.add_widget(separator)
        
        # Orari quiet hours (placeholder per ora)
        quiet_info = Label(
            text="Configura gli orari in cui non ricevere notifiche\n(eccetto emergenze)",
            font_size=dp(12),
            color=get_color_from_hex('#757575'),
            size_hint_y=None,
            height=dp(40)
        )
        prefs_layout.add_widget(quiet_info)
        
        # Altri controlli audio/vibrazione
        self.add_preference_switch(prefs_layout, "🔊 Suoni", "sound_enabled")
        self.add_preference_switch(prefs_layout, "📳 Vibrazione", "vibration_enabled")
        
        scroll.add_widget(prefs_layout)
        main_layout.add_widget(scroll)
        
        # Pulsanti azione
        actions_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        save_btn = MaterialButton(
            text="💾 Salva Preferenze"
        ) if MODERN_UI_AVAILABLE else Button(
            text="💾 Salva Preferenze"
        )
        save_btn.bind(on_press=self.save_preferences)
        actions_layout.add_widget(save_btn)
        
        reset_btn = MaterialButton(
            text="🔄 Reset Default"
        ) if MODERN_UI_AVAILABLE else Button(
            text="🔄 Reset Default"
        )
        reset_btn.bind(on_press=self.reset_preferences)
        actions_layout.add_widget(reset_btn)
        
        main_layout.add_widget(actions_layout)
        
        self.add_widget(main_layout)
    
    def add_preference_switch(self, layout, label: str, key: str, description: str = ""):
        """Aggiunge switch per una preferenza"""
        pref_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # Label e descrizione
        text_layout = BoxLayout(orientation='vertical')
        
        label_widget = Label(
            text=label,
            font_size=dp(14),
            halign='left',
            valign='bottom',
            size_hint_y=None,
            height=dp(25)
        )
        label_widget.bind(size=label_widget.setter('text_size'))
        text_layout.add_widget(label_widget)
        
        if description:
            desc_widget = Label(
                text=description,
                font_size=dp(10),
                color=get_color_from_hex('#757575'),
                halign='left',
                valign='top',
                size_hint_y=None,
                height=dp(20)
            )
            desc_widget.bind(size=desc_widget.setter('text_size'))
            text_layout.add_widget(desc_widget)
        
        pref_layout.add_widget(text_layout)
        
        # Switch
        switch = Switch(
            active=self.preferences.get(key, True),
            size_hint_x=None,
            width=dp(60)
        )
        switch.key = key
        switch.bind(active=self.on_preference_changed)
        
        pref_layout.add_widget(switch)
        
        layout.add_widget(pref_layout)
    
    def on_preference_changed(self, switch, value):
        """Gestisce cambio preferenza"""
        self.preferences[switch.key] = value
    
    def save_preferences(self, *args):
        """Salva preferenze"""
        try:
            self.manager.set_user_preferences(self.user_id, self.preferences)
            
            # Mostra conferma
            popup = Popup(
                title="✅ Successo",
                content=Label(text="Preferenze salvate correttamente!"),
                size_hint=(0.6, 0.3)
            )
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
            
        except Exception as e:
            popup = Popup(
                title="❌ Errore", 
                content=Label(text=f"Errore nel salvataggio: {str(e)}"),
                size_hint=(0.6, 0.3)
            )
            popup.open()
    
    def reset_preferences(self, *args):
        """Reset alle preferenze predefinite"""
        # Conferma reset
        def do_reset(*args):
            self.preferences = self.manager.get_user_preferences(self.user_id)
            self.manager.get_user_preferences.cache_clear() if hasattr(self.manager.get_user_preferences, 'cache_clear') else None
            
            # Ricarica schermata
            self.clear_widgets()
            self.setup_ui()
            
            confirm_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text="Ripristinare le impostazioni predefinite?"))
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        yes_btn = Button(text="Sì")
        yes_btn.bind(on_press=do_reset)
        buttons.add_widget(yes_btn)
        
        no_btn = Button(text="No")
        buttons.add_widget(no_btn)
        
        content.add_widget(buttons)
        
        confirm_popup = Popup(
            title="Conferma Reset",
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        no_btn.bind(on_press=confirm_popup.dismiss)
        confirm_popup.open()


class NotificationsMainScreen(Screen):
    """Schermata principale per gestione notifiche"""
    
    def __init__(self, manager: PushNotificationManager, user_id: str, **kwargs):
        super().__init__(**kwargs)
        
        self.manager = manager
        self.user_id = user_id
        
        self.setup_ui()
        
        # Auto-refresh ogni 30 secondi
        Clock.schedule_interval(self.auto_refresh, 30)
    
    def setup_ui(self):
        """Configura UI principale"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Header con statistiche e filtri
        header_card = MaterialCard(
            size_hint_y=None,
            height=dp(100),
            padding=dp(16),
            md_bg_color=get_color_from_hex('#E3F2FD')
        ) if MODERN_UI_AVAILABLE else BoxLayout(
            size_hint_y=None,
            height=dp(100),
            padding=dp(16)
        )
        
        stats_layout = BoxLayout(orientation='horizontal')
        
        # Statistiche notifiche
        self.stats_label = Label(
            text="Caricamento statistiche...",
            font_size=dp(14),
            halign='left',
            valign='center'
        )
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        stats_layout.add_widget(self.stats_label)
        
        # Pulsanti azione rapida
        actions_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_x=None,
            width=dp(200)
        )
        
        prefs_btn = MaterialButton(
            text="⚙️",
            size_hint_x=None,
            width=dp(40)
        ) if MODERN_UI_AVAILABLE else Button(
            text="⚙️",
            size_hint_x=None,
            width=dp(40)
        )
        prefs_btn.bind(on_press=self.show_preferences)
        actions_layout.add_widget(prefs_btn)
        
        refresh_btn = MaterialButton(
            text="🔄",
            size_hint_x=None,
            width=dp(40)
        ) if MODERN_UI_AVAILABLE else Button(
            text="🔄",
            size_hint_x=None,
            width=dp(40)
        )
        refresh_btn.bind(on_press=self.manual_refresh)
        actions_layout.add_widget(refresh_btn)
        
        clear_btn = MaterialButton(
            text="🗑️",
            size_hint_x=None,
            width=dp(40)
        ) if MODERN_UI_AVAILABLE else Button(
            text="🗑️",
            size_hint_x=None,
            width=dp(40)
        )
        clear_btn.bind(on_press=self.clear_read_notifications)
        actions_layout.add_widget(clear_btn)
        
        stats_layout.add_widget(actions_layout)
        
        if MODERN_UI_AVAILABLE:
            header_card.add_widget(stats_layout)
        else:
            # Aggiungi sfondo per layout base
            with stats_layout.canvas.before:
                Color(*get_color_from_hex('#E3F2FD'))
                stats_layout.rect = RoundedRectangle(
                    pos=stats_layout.pos,
                    size=stats_layout.size,
                    radius=[dp(8)]
                )
            stats_layout.bind(pos=lambda *args: setattr(stats_layout.rect, 'pos', stats_layout.pos))
            stats_layout.bind(size=lambda *args: setattr(stats_layout.rect, 'size', stats_layout.size))
            header_card = stats_layout
        
        main_layout.add_widget(header_card)
        
        # Filtri
        filters_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40),
            padding=[dp(16), 0]
        )
        
        # Toggle filtri
        all_btn = MaterialButton(
            text="Tutte",
            size_hint_x=None,
            width=dp(80)
        ) if MODERN_UI_AVAILABLE else Button(
            text="Tutte",
            size_hint_x=None,
            width=dp(80)
        )
        all_btn.bind(on_press=lambda x: self.apply_filter())
        filters_layout.add_widget(all_btn)
        
        unread_btn = MaterialButton(
            text="Non lette",
            size_hint_x=None,
            width=dp(100)
        ) if MODERN_UI_AVAILABLE else Button(
            text="Non lette",
            size_hint_x=None,
            width=dp(100)
        )
        unread_btn.bind(on_press=lambda x: self.apply_filter(unread_only=True))
        filters_layout.add_widget(unread_btn)
        
        # Dropdown per tipo (semplificato per ora)
        type_btn = MaterialButton(
            text="Tipo ▼",
            size_hint_x=None,
            width=dp(80)
        ) if MODERN_UI_AVAILABLE else Button(
            text="Tipo ▼",
            size_hint_x=None,
            width=dp(80)
        )
        type_btn.bind(on_press=self.show_type_filter)
        filters_layout.add_widget(type_btn)
        
        filters_layout.add_widget(Widget())  # Spacer
        
        main_layout.add_widget(filters_layout)
        
        # Lista notifiche
        self.notifications_list = NotificationsList(
            manager=self.manager,
            user_id=self.user_id
        )
        main_layout.add_widget(self.notifications_list)
        
        self.add_widget(main_layout)
        
        # Carica statistiche iniziali
        self.update_stats()
    
    def update_stats(self):
        """Aggiorna statistiche notifiche"""
        try:
            stats = self.manager.get_notification_stats(self.user_id)
            general = stats.get('general', {})
            
            stats_text = f"""📊 Statistiche Notifiche
📬 Totali: {general.get('total_notifications', 0)} | 📖 Lette: {general.get('read_notifications', 0)} | 📭 Non lette: {general.get('unread_notifications', 0)}
📈 Tasso lettura: {general.get('read_percentage', 0):.1f}%"""
            
            self.stats_label.text = stats_text
            
        except Exception as e:
            self.stats_label.text = f"❌ Errore nel caricamento statistiche: {str(e)}"
    
    def apply_filter(self, notification_type: Optional[NotificationType] = None, unread_only: bool = False):
        """Applica filtri alla lista notifiche"""
        self.notifications_list.filter_notifications(notification_type, unread_only)
        self.update_stats()
    
    def show_type_filter(self, *args):
        """Mostra popup filtro per tipo"""
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(20))
        
        content.add_widget(Label(
            text="Filtra per tipo notifica:",
            size_hint_y=None,
            height=dp(30)
        ))
        
        types = [
            ("Tutte", None),
            ("🏛️ Visite Monumenti", NotificationType.MONUMENT_VISIT),
            ("🏆 Achievement", NotificationType.ACHIEVEMENT),
            ("👥 Social", NotificationType.SOCIAL_INTERACTION),
            ("🎯 Sfide", NotificationType.DAILY_CHALLENGE),
            ("📍 Vicini", NotificationType.NEARBY_MONUMENTS),
            ("⚙️ Sistema", NotificationType.SYSTEM_UPDATE),
            ("⏰ Promemoria", NotificationType.REMINDER)
        ]
        
        for label, type_enum in types:
            btn = Button(
                text=label,
                size_hint_y=None,
                height=dp(40)
            )
            btn.bind(on_press=lambda x, t=type_enum: self.select_type_filter(t))
            content.add_widget(btn)
        
        self.type_popup = Popup(
            title="Filtro Tipo",
            content=content,
            size_hint=(0.8, 0.8)
        )
        self.type_popup.open()
    
    def select_type_filter(self, notification_type: Optional[NotificationType]):
        """Seleziona filtro tipo"""
        self.apply_filter(notification_type=notification_type)
        self.type_popup.dismiss()
    
    def show_preferences(self, *args):
        """Mostra schermata preferenze"""
        prefs_screen = NotificationPreferencesScreen(
            manager=self.manager,
            user_id=self.user_id,
            name="notification_preferences"
        )
        
        # Aggiunge temporaneamente la schermata al manager
        app = App.get_running_app()
        if hasattr(app.root, 'add_widget'):
            app.root.add_widget(prefs_screen)
            app.root.current = "notification_preferences"
    
    def manual_refresh(self, *args):
        """Refresh manuale"""
        self.notifications_list.reload_notifications()
        self.update_stats()
        
        # Mostra feedback
        popup = Popup(
            title="🔄 Refresh",
            content=Label(text="Notifiche aggiornate!"),
            size_hint=(0.5, 0.2)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
    
    def auto_refresh(self, *args):
        """Auto-refresh periodico"""
        self.notifications_list.reload_notifications()
        self.update_stats()
    
    def clear_read_notifications(self, *args):
        """Cancella notifiche lette"""
        def do_clear(*args):
            try:
                self.manager.clear_user_notifications(self.user_id, read_only=True)
                self.notifications_list.reload_notifications()
                self.update_stats()
                
                confirm_popup.dismiss()
                
                success_popup = Popup(
                    title="✅ Fatto",
                    content=Label(text="Notifiche lette cancellate!"),
                    size_hint=(0.5, 0.2)
                )
                success_popup.open()
                Clock.schedule_once(lambda dt: success_popup.dismiss(), 2)
                
            except Exception as e:
                confirm_popup.dismiss()
                
                error_popup = Popup(
                    title="❌ Errore",
                    content=Label(text=f"Errore: {str(e)}"),
                    size_hint=(0.6, 0.3)
                )
                error_popup.open()
        
        # Conferma cancellazione
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text="Cancellare tutte le notifiche lette?"))
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        yes_btn = Button(text="Sì")
        yes_btn.bind(on_press=do_clear)
        buttons.add_widget(yes_btn)
        
        no_btn = Button(text="No")
        buttons.add_widget(no_btn)
        
        content.add_widget(buttons)
        
        confirm_popup = Popup(
            title="Conferma Cancellazione",
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        no_btn.bind(on_press=confirm_popup.dismiss)
        confirm_popup.open()


class NotificationsApp(App):
    """App demo per sistema notifiche"""
    
    def build(self):
        # Inizializza manager notifiche
        self.notification_manager = PushNotificationManager()
        
        # Crea alcune notifiche di test
        self.create_test_notifications()
        
        # Schermata principale
        main_screen = NotificationsMainScreen(
            manager=self.notification_manager,
            user_id="demo_user",
            name="notifications_main"
        )
        
        sm = ScreenManager()
        sm.add_widget(main_screen)
        
        return sm
    
    def create_test_notifications(self):
        """Crea notifiche di test"""
        test_notifications = [
            {
                'title': '🏛️ Colosseo Visitato!',
                'body': 'Hai scoperto il Colosseo! Guadagnati 100 punti!',
                'type': NotificationType.MONUMENT_VISIT,
                'priority': NotificationPriority.HIGH
            },
            {
                'title': '🏆 Achievement Sbloccato!',
                'body': 'Hai ottenuto: Esploratore Romano',
                'type': NotificationType.ACHIEVEMENT,
                'priority': NotificationPriority.HIGH
            },
            {
                'title': '👥 Nuovo Like!',
                'body': 'Marco ha messo like al tuo post del Pantheon',
                'type': NotificationType.SOCIAL_INTERACTION,
                'priority': NotificationPriority.NORMAL
            },
            {
                'title': '🎯 Sfida Giornaliera',
                'body': 'Visita 3 monumenti oggi. Ricompensa: 50 punti',
                'type': NotificationType.DAILY_CHALLENGE,
                'priority': NotificationPriority.NORMAL
            },
            {
                'title': '📍 Monumenti Vicini',
                'body': 'Ci sono 5 monumenti entro 2km da te!',
                'type': NotificationType.NEARBY_MONUMENTS,
                'priority': NotificationPriority.LOW
            }
        ]
        
        for notif in test_notifications:
            self.notification_manager.create_notification(
                title=notif['title'],
                body=notif['body'],
                user_id="demo_user",
                notification_type=notif['type'],
                priority=notif['priority']
            )
    
    def on_stop(self):
        """Cleanup quando app si chiude"""
        if hasattr(self, 'notification_manager'):
            self.notification_manager.stop()


if __name__ == "__main__":
    NotificationsApp().run()
