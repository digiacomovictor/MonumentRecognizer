import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

from kivy.logger import Logger
from kivy.utils import platform

try:
    from plyer import camera
    from plyer.utils import whereis_exe
    CAMERA_AVAILABLE = True
except ImportError:
    Logger.warning("Camera: plyer non disponibile. Installare con: pip install plyer")
    CAMERA_AVAILABLE = False


class CameraInterface:
    """Interfaccia per gestire l'accesso alla fotocamera su mobile."""
    
    def __init__(self):
        """Inizializza l'interfaccia fotocamera."""
        self.temp_dir = Path(tempfile.gettempdir()) / "monument_recognizer"
        self.temp_dir.mkdir(exist_ok=True)
        self.last_photo_path: Optional[str] = None
        
    def is_camera_available(self) -> bool:
        """Verifica se la fotocamera è disponibile su questa piattaforma."""
        if not CAMERA_AVAILABLE:
            return False
            
        # Su desktop, verifica se ci sono strumenti fotografici
        if platform in ['win', 'linux', 'macosx']:
            return True  # Assumiamo webcam disponibile
            
        # Su mobile (Android/iOS) la camera è sempre disponibile
        return platform in ['android', 'ios']
    
    def get_temp_photo_path(self) -> str:
        """Genera un percorso temporaneo per la foto."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monument_photo_{timestamp}.jpg"
        return str(self.temp_dir / filename)
    
    def take_photo(self, callback: Callable[[str], None], error_callback: Callable[[str], None]):
        """
        Scatta una foto usando la fotocamera.
        
        Args:
            callback: Funzione chiamata con il percorso della foto scattata
            error_callback: Funzione chiamata in caso di errore
        """
        if not self.is_camera_available():
            error_callback("Fotocamera non disponibile su questa piattaforma")
            return
            
        try:
            # Genera percorso per la foto
            photo_path = self.get_temp_photo_path()
            self.last_photo_path = photo_path
            
            # Configura callback interno
            def on_camera_complete(photo_path_result):
                """Chiamato quando la foto è stata scattata."""
                if photo_path_result and os.path.exists(photo_path_result):
                    Logger.info(f"Camera: Foto scattata: {photo_path_result}")
                    callback(photo_path_result)
                else:
                    Logger.warning("Camera: Foto non salvata correttamente")
                    error_callback("Errore nel salvataggio della foto")
            
            # Avvia la fotocamera
            Logger.info("Camera: Avvio fotocamera...")
            
            if platform == 'android':
                # Android: usa l'intent della fotocamera
                self._take_photo_android(photo_path, on_camera_complete, error_callback)
            elif platform == 'ios':
                # iOS: usa l'interfaccia nativa
                self._take_photo_ios(photo_path, on_camera_complete, error_callback)
            else:
                # Desktop: simula scatto fotografico
                self._take_photo_desktop(photo_path, on_camera_complete, error_callback)
                
        except Exception as e:
            Logger.exception("Camera: Errore nell'avvio della fotocamera")
            error_callback(f"Errore fotocamera: {str(e)}")
    
    def _take_photo_android(self, photo_path: str, success_callback: Callable, error_callback: Callable):
        """Scatta foto su Android."""
        try:
            # Usa Plyer per Android
            camera.take_picture(
                filename=photo_path,
                on_complete=success_callback
            )
        except Exception as e:
            error_callback(f"Errore Android camera: {str(e)}")
    
    def _take_photo_ios(self, photo_path: str, success_callback: Callable, error_callback: Callable):
        """Scatta foto su iOS."""
        try:
            # Usa Plyer per iOS
            camera.take_picture(
                filename=photo_path,
                on_complete=success_callback
            )
        except Exception as e:
            error_callback(f"Errore iOS camera: {str(e)}")
    
    def _take_photo_desktop(self, photo_path: str, success_callback: Callable, error_callback: Callable):
        """Simula scatto fotografico su desktop (per testing)."""
        try:
            import cv2
            import numpy as np
            
            # Prova ad aprire la webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                error_callback("Webcam non disponibile")
                return
            
            # Scatta una foto
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Salva l'immagine
                cv2.imwrite(photo_path, frame)
                success_callback(photo_path)
            else:
                error_callback("Impossibile catturare immagine dalla webcam")
                
        except ImportError:
            # Se OpenCV non è disponibile, crea un'immagine di esempio
            error_callback("OpenCV non disponibile per webcam desktop")
        except Exception as e:
            error_callback(f"Errore desktop camera: {str(e)}")
    
    def cleanup_temp_photos(self):
        """Pulisce le foto temporanee."""
        try:
            for temp_file in self.temp_dir.glob("monument_photo_*.jpg"):
                if temp_file.exists():
                    temp_file.unlink()
                    Logger.info(f"Camera: Eliminata foto temporanea {temp_file}")
        except Exception as e:
            Logger.warning(f"Camera: Errore pulizia file temporanei: {e}")
    
    def get_camera_instructions(self) -> str:
        """Restituisce le istruzioni per l'uso della fotocamera per la piattaforma corrente."""
        if platform == 'android':
            return """📱 ANDROID:
• Assicurati che l'app abbia permesso fotocamera
• Tocca 'Scatta Foto' per aprire la camera
• Scatta la foto del monumento
• La foto verrà automaticamente caricata nell'app"""
        
        elif platform == 'ios':
            return """📱 iOS:
• Assicurati che l'app abbia permesso fotocamera
• Tocca 'Scatta Foto' per aprire la camera
• Scatta la foto del monumento  
• La foto verrà automaticamente caricata nell'app"""
        
        else:
            return """💻 DESKTOP:
• Assicurati di avere una webcam funzionante
• Tocca 'Scatta Foto' per catturare da webcam
• Posiziona il monumento davanti alla camera
• La foto verrà automaticamente salvata e caricata"""
