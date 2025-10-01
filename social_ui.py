"""
Social UI Components for Monument Recognizer
Interfacce Kivy per la condivisione social delle visite
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.core.window import Window
from datetime import datetime
from typing import Dict, List, Callable, Optional
import os
import threading
from social_sharing import SocialSharingManager


class SocialSharePopup(Popup):
    """Popup per la condivisione di una visita sui social media"""
    
    def __init__(self, visit_data: Dict, social_manager: SocialSharingManager, **kwargs):
        self.visit_data = visit_data
        self.social_manager = social_manager
        
        super().__init__(
            title=f"Condividi: {visit_data.get('monument_name', 'Monumento')}",
            size_hint=(0.9, 0.8),
            auto_dismiss=False,
            **kwargs
        )
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia del popup di condivisione"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # Header con info monumento
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(100))
        
        # Immagine del monumento (se disponibile)
        if self.visit_data.get('image_path') and os.path.exists(self.visit_data['image_path']):
            monument_image = Image(
                source=self.visit_data['image_path'],
                size_hint_x=None,
                width=dp(100)
            )
            header_layout.add_widget(monument_image)
        
        # Info monumento
        info_layout = BoxLayout(orientation='vertical')
        monument_label = Label(
            text=f"[b]{self.visit_data.get('monument_name', 'Sconosciuto')}[/b]",
            markup=True,
            text_size=(None, None),
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        location_label = Label(
            text=f"📍 {self.visit_data.get('location', 'Posizione non disponibile')}",
            text_size=(None, None),
            halign='left',
            size_hint_y=None,
            height=dp(25)
        )
        info_layout.add_widget(monument_label)
        info_layout.add_widget(location_label)
        
        header_layout.add_widget(info_layout)
        main_layout.add_widget(header_layout)
        
        # Anteprima del post generato
        preview_label = Label(
            text="Anteprima del post:",
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        main_layout.add_widget(preview_label)
        
        # Genera anteprima
        content = self.social_manager.generate_post_content(self.visit_data, 'discovery', True)
        
        self.preview_input = TextInput(
            text=content['text'],
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        main_layout.add_widget(self.preview_input)
        
        # Pulsanti per i social media
        social_label = Label(
            text="Condividi su:",
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        main_layout.add_widget(social_label)
        
        # Griglia pulsanti social
        social_grid = GridLayout(cols=3, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Definisce i social media con icone emoji
        social_platforms = [
            ('twitter', '🐦 Twitter', '#1DA1F2'),
            ('facebook', '📘 Facebook', '#4267B2'),
            ('instagram', '📷 Instagram', '#E4405F'),
            ('whatsapp', '💬 WhatsApp', '#25D366'),
            ('telegram', '✈️ Telegram', '#0088CC'),
            ('linkedin', '💼 LinkedIn', '#0077B5')
        ]
        
        for platform, display_name, color in social_platforms:
            btn = Button(
                text=display_name,
                size_hint_y=None,
                height=dp(50)
            )
            btn.bind(on_press=lambda x, p=platform: self.share_to_platform(p))
            
            # Colora il pulsante
            with btn.canvas.before:
                Color(*self.hex_to_rgb(color), 1)
                btn.rect = RoundedRectangle(size=btn.size, pos=btn.pos, radius=[dp(10)])
            btn.bind(pos=self.update_button_rect, size=self.update_button_rect)
            
            social_grid.add_widget(btn)
        
        main_layout.add_widget(social_grid)
        
        # Condivisione nel feed interno
        internal_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        self.internal_btn = Button(
            text="📱 Condividi nel Feed Interno",
            size_hint=(0.7, 1)
        )
        self.internal_btn.bind(on_press=self.share_to_internal_feed)
        
        # Pulsante per aprire il feed
        feed_btn = Button(
            text="👁️ Vedi Feed",
            size_hint=(0.3, 1)
        )
        feed_btn.bind(on_press=self.open_social_feed)
        
        internal_layout.add_widget(self.internal_btn)
        internal_layout.add_widget(feed_btn)
        main_layout.add_widget(internal_layout)
        
        # Pulsanti di controllo
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        close_btn = Button(text="Chiudi")
        close_btn.bind(on_press=self.dismiss)
        
        control_layout.add_widget(close_btn)
        main_layout.add_widget(control_layout)
        
        self.content = main_layout
    
    def hex_to_rgb(self, hex_color):
        """Converte colore hex in RGB normalizzato"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
    
    def update_button_rect(self, instance, value):
        """Aggiorna il rettangolo del pulsante"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def share_to_platform(self, platform: str):
        """Condivide su una piattaforma social specifica"""
        try:
            # Aggiorna il testo del post con quello modificato dall'utente
            self.visit_data['custom_text'] = self.preview_input.text
            
            # Esegue la condivisione in un thread separato per non bloccare l'UI
            def share_worker():
                success = self.social_manager.share_to_platform(
                    self.visit_data, 
                    platform, 
                    'discovery'
                )
                
                # Aggiorna l'UI nel thread principale
                Clock.schedule_once(
                    lambda dt: self.show_share_result(platform, success), 0
                )
            
            threading.Thread(target=share_worker, daemon=True).start()
            
            # Mostra feedback immediato
            self.show_sharing_feedback(platform)
            
        except Exception as e:
            print(f"Errore nella condivisione su {platform}: {e}")
            self.show_error(f"Errore nella condivisione su {platform}")
    
    def share_to_internal_feed(self, instance):
        """Condivide nel feed interno dell'app"""
        try:
            custom_message = self.preview_input.text
            success = self.social_manager.share_to_app_feed(self.visit_data, custom_message)
            
            if success:
                self.internal_btn.text = "✅ Condiviso nel Feed!"
                Clock.schedule_once(lambda dt: setattr(self.internal_btn, 'text', "📱 Condividi nel Feed Interno"), 2)
            else:
                self.show_error("Errore nella condivisione nel feed interno")
                
        except Exception as e:
            print(f"Errore nella condivisione interna: {e}")
            self.show_error("Errore nella condivisione interna")
    
    def open_social_feed(self, instance):
        """Apre il feed social interno"""
        feed_screen = SocialFeedScreen(self.social_manager)
        feed_popup = Popup(
            title="Feed Social Monument Recognizer",
            content=feed_screen,
            size_hint=(0.95, 0.9)
        )
        feed_popup.open()
    
    def show_sharing_feedback(self, platform: str):
        """Mostra feedback durante la condivisione"""
        feedback_popup = Popup(
            title="Condivisione in corso...",
            content=Label(text=f"Aprendo {platform}..."),
            size_hint=(0.6, 0.3),
            auto_dismiss=True
        )
        feedback_popup.open()
        Clock.schedule_once(lambda dt: feedback_popup.dismiss(), 2)
    
    def show_share_result(self, platform: str, success: bool):
        """Mostra il risultato della condivisione"""
        if success:
            message = f"Condivisione su {platform} avviata!"
        else:
            message = f"Errore nella condivisione su {platform}"
        
        result_popup = Popup(
            title="Risultato Condivisione",
            content=Label(text=message),
            size_hint=(0.6, 0.3),
            auto_dismiss=True
        )
        result_popup.open()
        Clock.schedule_once(lambda dt: result_popup.dismiss(), 2)
    
    def show_error(self, message: str):
        """Mostra un messaggio di errore"""
        error_popup = Popup(
            title="Errore",
            content=Label(text=message),
            size_hint=(0.6, 0.3),
            auto_dismiss=True
        )
        error_popup.open()


class SocialFeedScreen(Screen):
    """Schermata per visualizzare il feed social interno"""
    
    def __init__(self, social_manager: SocialSharingManager, **kwargs):
        super().__init__(**kwargs)
        self.social_manager = social_manager
        self.setup_ui()
        self.load_feed()
    
    def setup_ui(self):
        """Configura l'interfaccia del feed social"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Header
        header = Label(
            text="🏛️ Feed Monument Recognizer",
            size_hint_y=None,
            height=dp(40),
            font_size='18sp'
        )
        main_layout.add_widget(header)
        
        # ScrollView per i post
        scroll = ScrollView()
        self.posts_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None
        )
        self.posts_layout.bind(minimum_height=self.posts_layout.setter('height'))
        
        scroll.add_widget(self.posts_layout)
        main_layout.add_widget(scroll)
        
        # Pulsante refresh
        refresh_btn = Button(
            text="🔄 Aggiorna Feed",
            size_hint_y=None,
            height=dp(40)
        )
        refresh_btn.bind(on_press=lambda x: self.load_feed())
        main_layout.add_widget(refresh_btn)
        
        self.add_widget(main_layout)
    
    def load_feed(self):
        """Carica i post del feed sociale"""
        # Pulisce i post esistenti
        self.posts_layout.clear_widgets()
        
        # Carica i post dal database
        posts = self.social_manager.get_social_feed(20)
        
        if not posts:
            no_posts_label = Label(
                text="Nessun post da mostrare.\nInizia a condividere le tue visite!",
                size_hint_y=None,
                height=dp(100),
                halign='center'
            )
            self.posts_layout.add_widget(no_posts_label)
            return
        
        # Crea widget per ogni post
        for post in posts:
            post_widget = self.create_post_widget(post)
            self.posts_layout.add_widget(post_widget)
    
    def create_post_widget(self, post: Dict) -> Widget:
        """Crea un widget per un singolo post"""
        # Layout principale del post
        post_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            padding=dp(10),
            spacing=dp(5)
        )
        
        # Background del post
        with post_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            post_layout.rect = RoundedRectangle(
                size=post_layout.size,
                pos=post_layout.pos,
                radius=[dp(10)]
            )
        post_layout.bind(pos=self.update_rect, size=self.update_rect)
        
        # Header del post (utente e data)
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30)
        )
        
        user_label = Label(
            text=f"👤 {post['user_id']}",
            size_hint_x=0.7,
            halign='left',
            font_size='14sp'
        )
        
        date_str = post['shared_at'][:16] if post['shared_at'] else 'Data non disponibile'
        date_label = Label(
            text=date_str,
            size_hint_x=0.3,
            halign='right',
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        
        header_layout.add_widget(user_label)
        header_layout.add_widget(date_label)
        post_layout.add_widget(header_layout)
        
        # Contenuto del post
        content_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(80)
        )
        
        # Immagine (se disponibile)
        if post['image_path'] and os.path.exists(post['image_path']):
            post_image = Image(
                source=post['image_path'],
                size_hint_x=None,
                width=dp(80)
            )
            content_layout.add_widget(post_image)
        
        # Testo del post
        text_layout = BoxLayout(orientation='vertical')
        
        monument_label = Label(
            text=f"🏛️ {post['monument_name']}",
            size_hint_y=None,
            height=dp(25),
            halign='left',
            font_size='14sp'
        )
        monument_label.bind(texture_size=monument_label.setter('text_size'))
        monument_label.text_size = (None, None)
        
        post_text = post['post_text']
        if len(post_text) > 100:
            post_text = post_text[:97] + "..."
        
        description_label = Label(
            text=post_text,
            halign='left',
            valign='top',
            text_size=(None, None),
            font_size='12sp'
        )
        description_label.bind(texture_size=description_label.setter('text_size'))
        
        text_layout.add_widget(monument_label)
        text_layout.add_widget(description_label)
        content_layout.add_widget(text_layout)
        
        post_layout.add_widget(content_layout)
        
        # Footer con like e commenti
        footer_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        # Pulsante like
        like_btn = Button(
            text=f"👍 {post['likes_count']}",
            size_hint_x=None,
            width=dp(80),
            font_size='12sp'
        )
        like_btn.bind(on_press=lambda x, p=post: self.like_post(p))
        
        # Pulsante commenti
        comment_btn = Button(
            text=f"💬 {post['comments_count']}",
            size_hint_x=None,
            width=dp(80),
            font_size='12sp'
        )
        comment_btn.bind(on_press=lambda x, p=post: self.show_comments(p))
        
        # Posizione
        if post['location']:
            location_label = Label(
                text=f"📍 {post['location']}",
                halign='right',
                font_size='10sp',
                color=(0.6, 0.6, 0.6, 1)
            )
            location_label.text_size = (None, None)
        else:
            location_label = Widget()
        
        footer_layout.add_widget(like_btn)
        footer_layout.add_widget(comment_btn)
        footer_layout.add_widget(location_label)
        
        post_layout.add_widget(footer_layout)
        
        return post_layout
    
    def update_rect(self, instance, value):
        """Aggiorna il rettangolo di background"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def like_post(self, post: Dict):
        """Mette like a un post"""
        try:
            # Per ora usa un user_id fittizio - in futuro si collegherà al sistema utenti
            success = self.social_manager.like_post(post['id'], 'current_user')
            if success:
                # Ricarica il feed per mostrare il like aggiornato
                self.load_feed()
            
        except Exception as e:
            print(f"Errore nel mettere like: {e}")
    
    def show_comments(self, post: Dict):
        """Mostra i commenti di un post"""
        comments_popup = CommentsPopup(post, self.social_manager)
        comments_popup.open()


class CommentsPopup(Popup):
    """Popup per visualizzare e aggiungere commenti"""
    
    def __init__(self, post: Dict, social_manager: SocialSharingManager, **kwargs):
        self.post = post
        self.social_manager = social_manager
        
        super().__init__(
            title=f"Commenti: {post['monument_name']}",
            size_hint=(0.8, 0.7),
            **kwargs
        )
        
        self.setup_ui()
        self.load_comments()
    
    def setup_ui(self):
        """Configura l'interfaccia dei commenti"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # ScrollView per i commenti
        scroll = ScrollView()
        self.comments_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.comments_layout.bind(minimum_height=self.comments_layout.setter('height'))
        
        scroll.add_widget(self.comments_layout)
        main_layout.add_widget(scroll)
        
        # Input per nuovo commento
        input_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        self.comment_input = TextInput(
            hint_text="Scrivi un commento...",
            multiline=False
        )
        
        send_btn = Button(
            text="Invia",
            size_hint_x=None,
            width=dp(80)
        )
        send_btn.bind(on_press=self.add_comment)
        
        input_layout.add_widget(self.comment_input)
        input_layout.add_widget(send_btn)
        main_layout.add_widget(input_layout)
        
        # Pulsante chiudi
        close_btn = Button(
            text="Chiudi",
            size_hint_y=None,
            height=dp(40)
        )
        close_btn.bind(on_press=self.dismiss)
        main_layout.add_widget(close_btn)
        
        self.content = main_layout
    
    def load_comments(self):
        """Carica i commenti del post"""
        self.comments_layout.clear_widgets()
        
        comments = self.social_manager.get_post_comments(self.post['id'])
        
        if not comments:
            no_comments = Label(
                text="Nessun commento ancora.\nSii il primo a commentare!",
                size_hint_y=None,
                height=dp(60),
                halign='center'
            )
            self.comments_layout.add_widget(no_comments)
            return
        
        for comment in comments:
            comment_widget = self.create_comment_widget(comment)
            self.comments_layout.add_widget(comment_widget)
    
    def create_comment_widget(self, comment: Dict) -> Widget:
        """Crea un widget per un singolo commento"""
        comment_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),
            padding=dp(5)
        )
        
        # Background del commento
        with comment_layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            comment_layout.rect = RoundedRectangle(
                size=comment_layout.size,
                pos=comment_layout.pos,
                radius=[dp(5)]
            )
        comment_layout.bind(pos=self.update_rect, size=self.update_rect)
        
        # Header con utente e data
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(20)
        )
        
        user_label = Label(
            text=f"👤 {comment['user_id']}",
            size_hint_x=0.7,
            font_size='12sp',
            halign='left'
        )
        
        date_str = comment['commented_at'][:16] if comment['commented_at'] else 'Data non disponibile'
        date_label = Label(
            text=date_str,
            size_hint_x=0.3,
            font_size='10sp',
            halign='right',
            color=(0.6, 0.6, 0.6, 1)
        )
        
        header.add_widget(user_label)
        header.add_widget(date_label)
        comment_layout.add_widget(header)
        
        # Testo del commento
        text_label = Label(
            text=comment['comment_text'],
            font_size='12sp',
            halign='left',
            valign='center'
        )
        text_label.bind(texture_size=text_label.setter('text_size'))
        text_label.text_size = (None, None)
        
        comment_layout.add_widget(text_label)
        
        return comment_layout
    
    def update_rect(self, instance, value):
        """Aggiorna il rettangolo di background"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def add_comment(self, instance):
        """Aggiunge un nuovo commento"""
        comment_text = self.comment_input.text.strip()
        if not comment_text:
            return
        
        try:
            # Per ora usa un user_id fittizio - in futuro si collegherà al sistema utenti
            success = self.social_manager.add_comment(self.post['id'], 'current_user', comment_text)
            if success:
                self.comment_input.text = ""
                self.load_comments()
            
        except Exception as e:
            print(f"Errore nell'aggiungere commento: {e}")


class QuickShareButton(Button):
    """Pulsante rapido per la condivisione social"""
    
    def __init__(self, visit_data: Dict, social_manager: SocialSharingManager, **kwargs):
        self.visit_data = visit_data
        self.social_manager = social_manager
        
        super().__init__(
            text="📤 Condividi",
            size_hint=(None, None),
            size=(dp(120), dp(40)),
            **kwargs
        )
        
        self.bind(on_press=self.open_share_popup)
    
    def open_share_popup(self, instance):
        """Apre il popup di condivisione"""
        share_popup = SocialSharePopup(self.visit_data, self.social_manager)
        share_popup.open()


def test_social_ui():
    """Test delle interfacce social"""
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    
    class TestApp(App):
        def build(self):
            # Crea istanza del manager
            social_manager = SocialSharingManager("test_social.db")
            
            # Dati di esempio
            visit_data = {
                'id': 1,
                'user_id': 'test_user',
                'monument_name': 'Colosseo',
                'description': 'Anfiteatro romano del I secolo d.C.',
                'location': 'Roma, Italia',
                'image_path': '',
                'timestamp': datetime.now().isoformat()
            }
            
            layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            
            # Pulsante di test
            test_btn = Button(text="Test Condivisione Social", size_hint_y=None, height=dp(50))
            test_btn.bind(on_press=lambda x: SocialSharePopup(visit_data, social_manager).open())
            
            feed_btn = Button(text="Test Feed Social", size_hint_y=None, height=dp(50))
            feed_btn.bind(on_press=lambda x: Popup(
                title="Feed Test",
                content=SocialFeedScreen(social_manager),
                size_hint=(0.9, 0.8)
            ).open())
            
            layout.add_widget(Label(text="Test UI Social Monument Recognizer"))
            layout.add_widget(test_btn)
            layout.add_widget(feed_btn)
            
            return layout
    
    TestApp().run()


if __name__ == "__main__":
    test_social_ui()
