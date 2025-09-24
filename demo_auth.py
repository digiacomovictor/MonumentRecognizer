#!/usr/bin/env python3
"""
🚀 Demo Sistema Autenticazione - Monument Recognizer
App di test per interfacce di login, registrazione e profilo utente
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from user_system import UserSystem
from auth_ui import AuthManager

class MainDemoLayout(BoxLayout):
    """Layout principale dell'app demo."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20
        self.padding = [40, 40, 40, 40]
        
        # Inizializza sistema utenti
        self.user_system = UserSystem("demo_users.db")
        
        # Crea AuthManager
        self.auth_manager = AuthManager(self.user_system)
        
        # Callback quando login è completato
        self.auth_manager.on_login_success = self.on_login_success
        self.auth_manager.on_logout = self.on_logout
        
        # Titolo
        self.title_label = Label(
            text='🏛️ Monument Recognizer - Demo Autenticazione',
            size_hint_y=None,
            height=50,
            font_size=24
        )
        self.add_widget(self.title_label)
        
        # Status utente
        self.status_label = Label(
            text='👤 Nessun utente loggato',
            size_hint_y=None,
            height=30,
            font_size=16
        )
        self.add_widget(self.status_label)
        
        # Area pulsanti
        self.button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=20
        )
        
        # Pulsante Login
        self.login_btn = Button(
            text='🔑 Login',
            size_hint_x=0.25
        )
        self.login_btn.bind(on_press=self.show_login)
        self.button_layout.add_widget(self.login_btn)
        
        # Pulsante Registrazione
        self.register_btn = Button(
            text='📝 Registrazione',
            size_hint_x=0.25
        )
        self.register_btn.bind(on_press=self.show_register)
        self.button_layout.add_widget(self.register_btn)
        
        # Pulsante Profilo
        self.profile_btn = Button(
            text='👤 Profilo',
            size_hint_x=0.25,
            disabled=True
        )
        self.profile_btn.bind(on_press=self.show_profile)
        self.button_layout.add_widget(self.profile_btn)
        
        # Pulsante Logout
        self.logout_btn = Button(
            text='🚪 Logout',
            size_hint_x=0.25,
            disabled=True
        )
        self.logout_btn.bind(on_press=self.logout_user)
        self.button_layout.add_widget(self.logout_btn)
        
        self.add_widget(self.button_layout)
        
        # Area ScreenManager per l'autenticazione
        self.add_widget(self.auth_manager.screen_manager)
        
        # Controlla se c'è una sessione attiva al startup
        self.check_existing_session()
    
    def check_existing_session(self):
        """Controlla se esiste già una sessione attiva."""
        if self.user_system.is_logged_in():
            self.on_login_success()
    
    def show_login(self, instance):
        """Mostra schermata di login."""
        self.auth_manager.screen_manager.current = 'login'
    
    def show_register(self, instance):
        """Mostra schermata di registrazione."""
        self.auth_manager.screen_manager.current = 'register'
    
    def show_profile(self, instance):
        """Mostra schermata profilo."""
        self.auth_manager.screen_manager.current = 'profile'
    
    def logout_user(self, instance):
        """Effettua logout."""
        self.user_system.logout_user()
        self.on_logout()
    
    def on_login_success(self):
        """Callback chiamato quando login ha successo."""
        user = self.user_system.current_user
        if user:
            self.status_label.text = f'👤 Utente loggato: {user.full_name} (@{user.username})'
            self.login_btn.disabled = True
            self.register_btn.disabled = True
            self.profile_btn.disabled = False
            self.logout_btn.disabled = False
            
            # Torna alla schermata profilo
            self.auth_manager.screen_manager.current = 'profile'
            
            # Mostra popup di benvenuto
            self.show_welcome_popup(user)
    
    def on_logout(self):
        """Callback chiamato quando viene effettuato logout."""
        self.status_label.text = '👤 Nessun utente loggato'
        self.login_btn.disabled = False
        self.register_btn.disabled = False
        self.profile_btn.disabled = True
        self.logout_btn.disabled = True
        
        # Torna alla schermata di login
        self.auth_manager.screen_manager.current = 'login'
        
        # Mostra popup di logout
        self.show_info_popup("Logout", "👋 Logout effettuato con successo!")
    
    def show_welcome_popup(self, user):
        """Mostra popup di benvenuto."""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        welcome_label = Label(
            text=f'🎉 Benvenuto, {user.full_name}!',
            font_size=18
        )
        content.add_widget(welcome_label)
        
        info_label = Label(
            text=f'Login effettuato come: {user.username}\\nEmail: {user.email}',
            font_size=14
        )
        content.add_widget(info_label)
        
        close_btn = Button(
            text='OK',
            size_hint_y=None,
            height=40
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Login Riuscito',
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_info_popup(self, title, message):
        """Mostra popup informativo."""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        info_label = Label(text=message, font_size=16)
        content.add_widget(info_label)
        
        close_btn = Button(
            text='OK',
            size_hint_y=None,
            height=40
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.5, 0.3),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

class AuthDemoApp(App):
    """App principale per la demo del sistema di autenticazione."""
    
    def build(self):
        return MainDemoLayout()
    
    def on_stop(self):
        """Chiamato quando l'app viene chiusa."""
        # Pulizia eventuali risorse
        print("👋 Demo chiusa")

if __name__ == '__main__':
    print("🚀 Avvio Monument Recognizer - Demo Autenticazione")
    print("=" * 60)
    print("💡 Funzionalità disponibili:")
    print("   • 🔑 Login utente esistente")
    print("   • 📝 Registrazione nuovo utente")
    print("   • 👤 Gestione profilo utente")
    print("   • 🚪 Logout con persistenza sessione")
    print("=" * 60)
    
    AuthDemoApp().run()
