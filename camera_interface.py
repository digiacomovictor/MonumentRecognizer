"""
Camera Interface Android-Compatible
Rimuove dipendenze OpenCV, usa solo Kivy
"""
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import tempfile
import os

class CameraInterface:
    def __init__(self):
        self.camera = None
        self.capture_callback = None
        self.is_android = True
    
    def open_camera_popup(self, capture_callback):
        """Apre popup fotocamera (Android-friendly)"""
        self.capture_callback = capture_callback
        
        # Layout principale
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Camera widget
        self.camera = Camera(play=True, resolution=(640, 480))
        layout.add_widget(self.camera)
        
        # Pulsanti
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        capture_btn = Button(text='📷 Scatta', size_hint_x=0.5)
        capture_btn.bind(on_press=self.capture_photo)
        
        cancel_btn = Button(text='❌ Annulla', size_hint_x=0.5)
        cancel_btn.bind(on_press=self.close_camera)
        
        buttons_layout.add_widget(capture_btn)
        buttons_layout.add_widget(cancel_btn)
        
        layout.add_widget(buttons_layout)
        
        # Popup
        self.camera_popup = Popup(
            title='📷 Fotocamera',
            content=layout,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        self.camera_popup.open()
    
    def capture_photo(self, *args):
        """Scatta una foto"""
        if self.camera:
            # Genera nome file temporaneo
            temp_file = tempfile.mktemp(suffix='.png')
            
            try:
                # Esporta texture della camera
                self.camera.export_to_png(temp_file)
                
                # Chiama callback con il percorso del file
                if self.capture_callback:
                    Clock.schedule_once(lambda dt: self.capture_callback(temp_file), 0.5)
                
                self.close_camera()
                
            except Exception as e:
                print(f"Errore nella cattura: {e}")
                self.close_camera()
    
    def close_camera(self, *args):
        """Chiude la fotocamera"""
        if hasattr(self, 'camera_popup'):
            self.camera_popup.dismiss()
        
        if self.camera:
            self.camera.play = False
            self.camera = None
    
    def is_camera_available(self) -> bool:
        """Controlla se la fotocamera è disponibile"""
        return True  # Su Android assumiamo sempre disponibile
