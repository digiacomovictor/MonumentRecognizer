"""
🔐 Interfacce di Autenticazione per Monument Recognizer
Sistema completo di login, registrazione e profilo utente con Kivy
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.metrics import dp
from kivy.clock import Clock
import threading
import os

from user_system import UserSystem, User


class LoginScreen(Screen):
    """Schermata di login."""
    
    def __init__(self, user_system: UserSystem, **kwargs):
        super().__init__(**kwargs)
        self.user_system = user_system
        self.build_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia di login."""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(30))
        
        # Header
        header = BoxLayout(orientation='vertical', size_hint_y=0.3, spacing=dp(10))
        
        title = Label(
            text='🏛️ Monument Recognizer',
            font_size=dp(32),
            bold=True,
            color=(0.2, 0.6, 0.8, 1),
            size_hint_y=0.6
        )
        
        subtitle = Label(
            text='Accedi al tuo account',
            font_size=dp(18),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.4
        )
        
        header.add_widget(title)
        header.add_widget(subtitle)
        
        # Form di login
        form_layout = BoxLayout(orientation='vertical', size_hint_y=0.5, spacing=dp(15))
        
        self.username_input = TextInput(
            hint_text='Username o Email',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        
        self.password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        
        # Remember me
        remember_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.remember_checkbox = CheckBox(size_hint_x=0.1)
        remember_label = Label(
            text='Ricordami',
            font_size=dp(14),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=0.9,
            halign='left'
        )
        remember_label.bind(size=remember_label.setter('text_size'))
        remember_layout.add_widget(self.remember_checkbox)
        remember_layout.add_widget(remember_label)
        
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.password_input)
        form_layout.add_widget(remember_layout)
        
        # Pulsanti
        buttons_layout = BoxLayout(orientation='vertical', size_hint_y=0.2, spacing=dp(10))
        
        self.login_button = Button(
            text='🔓 Accedi',
            font_size=dp(18),
            background_color=(0.2, 0.7, 0.2, 1),
            size_hint_y=None,
            height=dp(50)
        )
        self.login_button.bind(on_press=self.on_login)
        
        register_button = Button(
            text='📝 Crea Account',
            font_size=dp(16),
            background_color=(0.3, 0.5, 0.9, 1),
            size_hint_y=None,
            height=dp(45)
        )
        register_button.bind(on_press=self.go_to_register)
        
        guest_button = Button(
            text='🚪 Continua senza account',
            font_size=dp(14),
            background_color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(40)
        )
        guest_button.bind(on_press=self.guest_access)
        
        buttons_layout.add_widget(self.login_button)
        buttons_layout.add_widget(register_button)
        buttons_layout.add_widget(guest_button)
        
        # Assembly
        main_layout.add_widget(header)
        main_layout.add_widget(form_layout)
        main_layout.add_widget(buttons_layout)
        
        self.add_widget(main_layout)
    
    def on_login(self, instance):
        """Gestisce il login."""
        username = self.username_input.text.strip()
        password = self.password_input.text
        
        if not username or not password:
            self.show_popup("Errore", "Inserisci username e password", "error")
            return
        
        # Disabilita pulsante durante login
        self.login_button.disabled = True
        self.login_button.text = '⏳ Accesso in corso...'
        
        # Esegui login in thread separato
        threading.Thread(target=self._do_login, args=(username, password)).start()
    
    def _do_login(self, username: str, password: str):
        """Esegue il login in background."""
        success, message, user = self.user_system.login_user(username, password)
        
        # Torna al thread principale
        Clock.schedule_once(lambda dt: self._login_complete(success, message, user), 0)
    
    def _login_complete(self, success: bool, message: str, user: User):
        """Completa il processo di login."""
        self.login_button.disabled = False
        self.login_button.text = '🔓 Accedi'
        
        if success:
            # Salva sessione se richiesto
            if self.remember_checkbox.active:
                self.save_session()
            
            self.show_popup("Successo", f"Benvenuto, {user.full_name}!", "success", self.go_to_main)
        else:
            self.show_popup("Errore", message, "error")
    
    def save_session(self):
        """Salva la sessione per il ricordami."""
        try:
            if self.user_system.session_token:
                with open('session.txt', 'w') as f:
                    f.write(self.user_system.session_token)
        except Exception as e:
            print(f"⚠️ Errore salvataggio sessione: {e}")
    
    def go_to_register(self, instance):
        """Vai alla schermata di registrazione."""
        self.manager.current = 'register'
    
    def guest_access(self, instance):
        """Accesso come ospite."""
        self.go_to_main()
    
    def go_to_main(self, instance=None):
        """Vai alla schermata principale."""
        if hasattr(self.manager, 'go_to_main'):
            self.manager.go_to_main()
        else:
            print("🚀 Vai alla schermata principale")
    
    def show_popup(self, title: str, message: str, popup_type: str = "info", callback=None):
        """Mostra popup generico."""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Colori per tipo
        colors = {
            "error": (0.8, 0.2, 0.2, 1),
            "success": (0.2, 0.7, 0.2, 1),
            "info": (0.3, 0.5, 0.9, 1)
        }
        
        # Emoji per tipo
        emojis = {
            "error": "❌",
            "success": "✅",
            "info": "ℹ️"
        }
        
        color = colors.get(popup_type, colors["info"])
        emoji = emojis.get(popup_type, emojis["info"])
        
        label = Label(
            text=f"{emoji} {message}",
            color=color,
            font_size=dp(16),
            text_size=(dp(300), None),
            halign='center',
            valign='middle'
        )
        
        button_text = "Continua" if popup_type == "success" else "OK"
        ok_button = Button(
            text=button_text,
            size_hint_y=None,
            height=dp(40),
            background_color=color
        )
        
        content.add_widget(label)
        content.add_widget(ok_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def on_ok(instance):
            popup.dismiss()
            if callback:
                callback(instance)
        
        ok_button.bind(on_press=on_ok)
        popup.open()


class RegisterScreen(Screen):
    """Schermata di registrazione."""
    
    def __init__(self, user_system: UserSystem, **kwargs):
        super().__init__(**kwargs)
        self.user_system = user_system
        self.build_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia di registrazione."""
        main_layout = ScrollView()
        
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(30))
        content.bind(minimum_height=content.setter('height'))
        content.size_hint_y = None
        
        # Header
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(10))
        
        title = Label(
            text='📝 Crea Account',
            font_size=dp(28),
            bold=True,
            color=(0.3, 0.5, 0.9, 1),
            size_hint_y=0.6
        )
        
        subtitle = Label(
            text='Unisciti alla community di esploratori',
            font_size=dp(16),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.4
        )
        
        header.add_widget(title)
        header.add_widget(subtitle)
        
        # Form
        form_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        self.fullname_input = TextInput(
            hint_text='Nome e Cognome',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        
        self.username_input = TextInput(
            hint_text='Username (3-20 caratteri)',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        
        self.email_input = TextInput(
            hint_text='Email',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        
        self.password_input = TextInput(
            hint_text='Password (min 8 caratteri)',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        
        self.confirm_password_input = TextInput(
            hint_text='Conferma Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        
        form_layout.add_widget(self.fullname_input)
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.email_input)
        form_layout.add_widget(self.password_input)
        form_layout.add_widget(self.confirm_password_input)
        
        # Password requirements
        requirements_label = Label(
            text='Password deve contenere:\\n• Almeno 8 caratteri\\n• Una maiuscola e minuscola\\n• Un numero\\n• Un simbolo (!@#$%^&*)',
            font_size=dp(12),
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=dp(80),
            text_size=(dp(350), None),
            halign='left'
        )
        
        # Terms
        terms_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.terms_checkbox = CheckBox(size_hint_x=0.1)
        terms_label = Label(
            text='Accetto i termini di servizio',
            font_size=dp(14),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=0.9,
            text_size=(dp(250), None),
            halign='left'
        )
        terms_layout.add_widget(self.terms_checkbox)
        terms_layout.add_widget(terms_label)
        
        # Pulsanti
        buttons_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(10))
        
        self.register_button = Button(
            text='✨ Registrati',
            font_size=dp(18),
            background_color=(0.3, 0.5, 0.9, 1),
            size_hint_y=None,
            height=dp(50)
        )
        self.register_button.bind(on_press=self.on_register)
        
        back_button = Button(
            text='← Torna al Login',
            font_size=dp(16),
            background_color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=dp(45)
        )
        back_button.bind(on_press=self.go_to_login)
        
        buttons_layout.add_widget(self.register_button)
        buttons_layout.add_widget(back_button)
        
        # Assembly
        content.add_widget(header)
        content.add_widget(form_layout)
        content.add_widget(requirements_label)
        content.add_widget(terms_layout)
        content.add_widget(buttons_layout)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def on_register(self, instance):
        """Gestisce la registrazione."""
        fullname = self.fullname_input.text.strip()
        username = self.username_input.text.strip()
        email = self.email_input.text.strip()
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text
        
        # Validazione
        if not all([fullname, username, email, password, confirm_password]):
            self.show_popup("Errore", "Compila tutti i campi")
            return
        
        if password != confirm_password:
            self.show_popup("Errore", "Le password non coincidono")
            return
        
        if not self.terms_checkbox.active:
            self.show_popup("Errore", "Devi accettare i termini di servizio")
            return
        
        # Disabilita pulsante
        self.register_button.disabled = True
        self.register_button.text = '⏳ Registrazione in corso...'
        
        # Esegui registrazione in thread separato
        threading.Thread(target=self._do_register, args=(username, email, fullname, password)).start()
    
    def _do_register(self, username: str, email: str, fullname: str, password: str):
        """Esegue la registrazione in background."""
        success, message, user = self.user_system.register_user(username, email, fullname, password)
        
        # Torna al thread principale
        Clock.schedule_once(lambda dt: self._register_complete(success, message, user), 0)
    
    def _register_complete(self, success: bool, message: str, user: User):
        """Completa il processo di registrazione."""
        self.register_button.disabled = False
        self.register_button.text = '✨ Registrati'
        
        if success:
            self.clear_form()
            self.show_popup("Successo", f"Registrazione completata!\\nBenvenuto {user.full_name}", "success", self.go_to_login)
        else:
            self.show_popup("Errore", message)
    
    def clear_form(self):
        """Pulisce il form di registrazione."""
        self.fullname_input.text = ''
        self.username_input.text = ''
        self.email_input.text = ''
        self.password_input.text = ''
        self.confirm_password_input.text = ''
        self.terms_checkbox.active = False
    
    def go_to_login(self, instance):
        """Torna alla schermata di login."""
        self.manager.current = 'login'
    
    def show_popup(self, title: str, message: str, popup_type: str = "error", callback=None):
        """Mostra popup."""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        colors = {
            "error": (0.8, 0.2, 0.2, 1),
            "success": (0.2, 0.7, 0.2, 1)
        }
        
        color = colors.get(popup_type, colors["error"])
        emoji = "✅" if popup_type == "success" else "❌"
        
        label = Label(
            text=f"{emoji} {message}",
            color=color,
            font_size=dp(16),
            text_size=(dp(350), None),
            halign='center'
        )
        
        ok_button = Button(
            text='OK',
            size_hint_y=None,
            height=dp(40),
            background_color=color
        )
        
        content.add_widget(label)
        content.add_widget(ok_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.5)
        )
        
        def on_ok(instance):
            popup.dismiss()
            if callback:
                callback(instance)
        
        ok_button.bind(on_press=on_ok)
        popup.open()


class ProfileScreen(Screen):
    """Schermata del profilo utente."""
    
    def __init__(self, user_system: UserSystem, **kwargs):
        super().__init__(**kwargs)
        self.user_system = user_system
        self.build_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia profilo."""
        main_layout = ScrollView()
        
        self.content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        self.content.bind(minimum_height=self.content.setter('height'))
        self.content.size_hint_y = None
        
        self.update_ui()
        
        main_layout.add_widget(self.content)
        self.add_widget(main_layout)
    
    def update_ui(self):
        """Aggiorna l'interfaccia in base allo stato login."""
        self.content.clear_widgets()
        
        if self.user_system.is_logged_in():
            self.build_logged_in_ui()
        else:
            self.build_guest_ui()
    
    def build_logged_in_ui(self):
        """UI per utente loggato."""
        user = self.user_system.current_user
        
        # Header utente
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(10))
        
        avatar = Label(
            text='👤',
            font_size=dp(50),
            size_hint_y=0.5
        )
        
        user_info = Label(
            text=f"Ciao, {user.full_name}!\\n@{user.username}",
            font_size=dp(18),
            bold=True,
            color=(0.2, 0.6, 0.8, 1),
            size_hint_y=0.5
        )
        
        header.add_widget(avatar)
        header.add_widget(user_info)
        
        # Sezioni
        sections = [
            ("👤 Account", [
                ("✏️ Modifica Profilo", self.edit_profile),
                ("🔑 Cambia Password", self.change_password),
            ]),
            ("📊 Statistiche", [
                ("🏛️ Monumenti Visitati", self.view_visits),
                ("🗺️ Mappa Visite", self.view_map),
                ("🏆 Achievement", self.view_achievements),
            ]),
            ("ℹ️ Generale", [
                ("📚 Info App", self.app_info),
                ("🆘 Supporto", self.support),
            ]),
            ("🚪 Sessione", [
                ("👋 Logout", self.logout),
            ])
        ]
        
        self.content.add_widget(header)
        
        for section_title, items in sections:
            section = self.create_section(section_title, items)
            self.content.add_widget(section)
    
    def build_guest_ui(self):
        """UI per utente ospite."""
        guest_info = Label(
            text="🚪 Modalità Ospite\\nAccedi per salvare i progressi e sincronizzare i dati",
            font_size=dp(18),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(100),
            text_size=(dp(350), None),
            halign='center'
        )
        
        login_button = Button(
            text="🔓 Accedi",
            font_size=dp(18),
            background_color=(0.2, 0.7, 0.2, 1),
            size_hint_y=None,
            height=dp(50)
        )
        login_button.bind(on_press=self.go_to_login)
        
        register_button = Button(
            text="📝 Registrati",
            font_size=dp(16),
            background_color=(0.3, 0.5, 0.9, 1),
            size_hint_y=None,
            height=dp(45)
        )
        register_button.bind(on_press=self.go_to_register)
        
        # Sezioni per ospiti
        general_section = self.create_section("ℹ️ Generale", [
            ("📚 Info App", self.app_info),
            ("🆘 Supporto", self.support),
        ])
        
        self.content.add_widget(guest_info)
        self.content.add_widget(login_button)
        self.content.add_widget(register_button)
        self.content.add_widget(general_section)
    
    def create_section(self, title: str, items: list) -> BoxLayout:
        """Crea una sezione del profilo."""
        section = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        section.bind(minimum_height=section.setter('height'))
        
        # Titolo
        title_label = Label(
            text=title,
            font_size=dp(16),
            bold=True,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(35),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        section.add_widget(title_label)
        
        # Items
        for item_text, callback in items:
            item_button = Button(
                text=item_text,
                font_size=dp(14),
                background_color=(0.9, 0.9, 0.9, 0.3),
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(45)
            )
            item_button.bind(on_press=callback)
            section.add_widget(item_button)
        
        # Separatore
        separator = Label(text='', size_hint_y=None, height=dp(15))
        section.add_widget(separator)
        
        return section
    
    def edit_profile(self, instance):
        """Modifica profilo."""
        self.show_info("In Sviluppo", "La modifica profilo sarà disponibile presto")
    
    def change_password(self, instance):
        """Cambia password."""
        self.show_info("In Sviluppo", "Il cambio password sarà disponibile presto")
    
    def view_visits(self, instance):
        """Visualizza visite."""
        self.show_info("In Sviluppo", "La cronologia visite sarà disponibile presto")
    
    def view_map(self, instance):
        """Visualizza mappa."""
        self.show_info("In Sviluppo", "La mappa visite sarà disponibile presto")
    
    def view_achievements(self, instance):
        """Visualizza achievement."""
        self.show_info("In Sviluppo", "Gli achievement saranno disponibili presto")
    
    def app_info(self, instance):
        """Info app."""
        self.show_info("Monument Recognizer v2.0", "App per riconoscimento monumenti con GPS e AI")
    
    def support(self, instance):
        """Supporto."""
        self.show_info("Supporto", "Per assistenza consulta README.md e setup_google_vision.md")
    
    def logout(self, instance):
        """Logout."""
        self.user_system.logout_user()
        
        # Pulisci sessione
        try:
            if os.path.exists('session.txt'):
                os.remove('session.txt')
        except Exception:
            pass
        
        self.update_ui()
        self.show_info("Logout", "Logout effettuato con successo")
        
        # Torna al login dopo 1 secondo
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 1)
    
    def go_to_login(self, instance):
        """Vai al login."""
        self.manager.current = 'login'
    
    def go_to_register(self, instance):
        """Vai alla registrazione."""
        self.manager.current = 'register'
    
    def show_info(self, title: str, message: str):
        """Mostra popup informativo."""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        label = Label(
            text=message,
            font_size=dp(14),
            text_size=(dp(300), None),
            halign='center'
        )
        
        ok_button = Button(
            text='OK',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.5, 0.9, 1)
        )
        
        content.add_widget(label)
        content.add_widget(ok_button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


class AuthManager:
    """Manager per le schermate di autenticazione."""
    
    def __init__(self, user_system: UserSystem):
        self.user_system = user_system
        self.screen_manager = ScreenManager()
        self.setup_screens()
        self.try_restore_session()
    
    def setup_screens(self):
        """Configura le schermate."""
        login_screen = LoginScreen(self.user_system, name='login')
        register_screen = RegisterScreen(self.user_system, name='register')
        profile_screen = ProfileScreen(self.user_system, name='profile')
        
        self.screen_manager.add_widget(login_screen)
        self.screen_manager.add_widget(register_screen)
        self.screen_manager.add_widget(profile_screen)
        
        # Callback per main app
        self.screen_manager.go_to_main = self.go_to_main
    
    def try_restore_session(self):
        """Prova a ripristinare sessione salvata."""
        try:
            if os.path.exists('session.txt'):
                with open('session.txt', 'r') as f:
                    session_token = f.read().strip()
                
                if self.user_system.restore_session(session_token):
                    print("🔄 Sessione ripristinata automaticamente")
                    self.screen_manager.current = 'profile'
                else:
                    os.remove('session.txt')
        except Exception as e:
            print(f"⚠️ Errore ripristino sessione: {e}")
    
    def go_to_main(self):
        """Callback per andare all'app principale."""
        print("🚀 Andando all'app principale...")
        # Qui l'app principale prende il controllo
    
    def get_screen_manager(self) -> ScreenManager:
        """Restituisce il screen manager."""
        return self.screen_manager
