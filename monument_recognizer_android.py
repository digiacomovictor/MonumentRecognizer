"""
Versione Android-Compatibile di Monument Recognizer
Rimuove dipendenze problematiche (OpenCV, NumPy) e usa solo PIL/Pillow
"""

import json
import os
import io
from typing import Dict, List, Optional
from PIL import Image

from gps_manager import GPSManager, GPSCoordinate, format_distance
from visit_tracker import VisitTracker
from user_system import UserSystem

# Google Cloud Vision - Import condizionale
try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    print("Google Cloud Vision non disponibile. L'app funzionerà in modalità offline.")

class MonumentRecognizer:
    def __init__(self, user_system: UserSystem = None):
        """Inizializza il riconoscitore di monumenti (versione Android)."""
        self.monuments_db = self.load_monuments_database()
        self.vision_client = None
        self.api_key_path = None
        self.gps_manager = GPSManager()
        self.user_system = user_system
        
        # Crea visit tracker per l'utente corrente
        user_id = None
        if user_system and user_system.is_logged_in():
            user_id = user_system.current_user.user_id
        self.visit_tracker = VisitTracker(user_id)
        
        self.setup_google_vision()
        
    def load_monuments_database(self) -> Dict:
        """Carica il database dei monumenti."""
        try:
            with open('monuments_db.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Database dei monumenti non trovato! Creando database demo.")
            return self.create_demo_database()
    
    def create_demo_database(self) -> Dict:
        """Crea un database demo per scopi di testing."""
        return {
            'colosseum': {
                'name': 'Colosseo',
                'city': 'Roma',
                'country': 'Italia',
                'description': 'Il più grande anfiteatro mai costruito, simbolo di Roma.',
                'year_built': '72-80 d.C.',
                'coordinates': {'lat': 41.8902, 'lon': 12.4922},
                'category': 'Anfiteatro Romano'
            },
            'eiffel_tower': {
                'name': 'Torre Eiffel',
                'city': 'Parigi',
                'country': 'Francia',
                'description': 'Torre in ferro battuto alta 330 metri, simbolo di Parigi.',
                'year_built': '1887-1889',
                'coordinates': {'lat': 48.8584, 'lon': 2.2945},
                'category': 'Torre'
            },
            'statue_of_liberty': {
                'name': 'Statua della Libertà',
                'city': 'New York',
                'country': 'Stati Uniti',
                'description': 'Statua neoclassica su Liberty Island nel porto di New York.',
                'year_built': '1886',
                'coordinates': {'lat': 40.6892, 'lon': -74.0445},
                'category': 'Statua Monumentale'
            }
        }
    
    def setup_google_vision(self):
        """Configura Google Vision API (se disponibile)."""
        if not GOOGLE_VISION_AVAILABLE:
            print("Google Vision API non disponibile su Android. Usando riconoscimento offline.")
            return False
            
        try:
            # Su Android potrebbe non funzionare, ma proviamo
            self.vision_client = vision.ImageAnnotatorClient()
            print("Google Vision API configurata!")
            return True
        except Exception as e:
            print(f"Google Vision API non configurata: {e}")
            print("Usando modalità offline.")
            return False
    
    def preprocess_image_android(self, image_path: str) -> Optional[Image.Image]:
        """Preprocessa l'immagine usando solo PIL (Android-compatibile)."""
        try:
            # Usa PIL invece di OpenCV
            image = Image.open(image_path)
            if image is None:
                return None
                
            # Ridimensiona se troppo grande
            width, height = image.size
            max_size = 1600
            if width > max_size or height > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return image
        except Exception as e:
            print(f"Errore nel preprocessamento dell'immagine: {e}")
            return None
    
    def analyze_image_offline(self, image_path: str) -> Dict:
        """Analizza l'immagine in modalità offline (Android-friendly)."""
        try:
            # Preprocessa l'immagine
            image = self.preprocess_image_android(image_path)
            if image is None:
                return {
                    'success': False,
                    'error': 'Impossibile caricare l\'immagine'
                }
            
            # Riconoscimento semplificato basato sul nome del file
            file_name = os.path.basename(image_path).lower()
            
            # Cerca parole chiave nel nome del file
            monument_matches = []
            for key, monument in self.monuments_db.items():
                monument_name_words = monument['name'].lower().split()
                if any(word in file_name for word in monument_name_words):
                    monument_matches.append((key, monument))
            
            if monument_matches:
                # Prende il primo match
                monument_key, monument_info = monument_matches[0]
                return {
                    'success': True,
                    'monument': monument_info,
                    'confidence': 75,  # Confidence simulata
                    'method': 'Riconoscimento Offline (nome file)',
                    'android_mode': True
                }
            
            # Se non trova match, ritorna un risultato generico
            return {
                'success': False,
                'error': 'Monumento non riconosciuto in modalità offline',
                'suggestion': 'Prova a rinominare il file con il nome del monumento',
                'android_mode': True,
                'available_monuments': list(self.monuments_db.keys())
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Errore nell\'analisi offline: {str(e)}',
                'android_mode': True
            }
    
    def recognize_with_google_vision(self, image_path: str) -> Dict:
        """Riconosce monumenti usando Google Vision API (se disponibile)."""
        if not self.vision_client or not GOOGLE_VISION_AVAILABLE:
            # Fallback alla modalità offline su Android
            print("Google Vision non disponibile, usando modalità offline")
            return self.analyze_image_offline(image_path)
        
        try:
            # Carica l'immagine
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Rileva landmark
            landmark_response = self.vision_client.landmark_detection(image=image)
            landmarks = landmark_response.landmark_annotations
            
            if landmark_response.error.message:
                # Fallback offline se API fallisce
                print(f"Google Vision error: {landmark_response.error.message}")
                return self.analyze_image_offline(image_path)
            
            if landmarks:
                # Trova il landmark con il punteggio più alto
                best_landmark = max(landmarks, key=lambda x: x.score)
                
                # Cerca nel nostro database
                monument_info = self.find_monument_by_name(best_landmark.description)
                
                if monument_info:
                    return {
                        'success': True,
                        'monument': monument_info,
                        'confidence': int(best_landmark.score * 100),
                        'google_landmark': best_landmark.description,
                        'method': 'Google Vision API - Landmark Detection'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Landmark riconosciuto ({best_landmark.description}) ma non nel nostro database.',
                        'detected_landmark': best_landmark.description,
                        'confidence': int(best_landmark.score * 100)
                    }
            
            # Se non trova landmark, fallback offline
            return self.analyze_image_offline(image_path)
            
        except Exception as e:
            print(f"Errore Google Vision API: {str(e)}")
            # Fallback alla modalità offline
            return self.analyze_image_offline(image_path)
    
    def find_monument_by_name(self, name: str) -> Optional[Dict]:
        """Trova un monumento per nome nel database."""
        name_lower = name.lower()
        
        for key, monument in self.monuments_db.items():
            if monument['name'].lower() in name_lower or name_lower in monument['name'].lower():
                return monument
                
        return None
    
    def analyze_image(self, image_path: str) -> Dict:
        """Analizza un'immagine per riconoscere monumenti (entry point principale)."""
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': 'File immagine non trovato'
            }
        
        # Su Android, usa principalmente modalità offline
        # Google Vision come fallback se disponibile
        try:
            # Prova prima offline (più veloce su Android)
            offline_result = self.analyze_image_offline(image_path)
            
            if offline_result['success']:
                return offline_result
            
            # Se offline fallisce e Google Vision è disponibile, prova quello
            if self.vision_client and GOOGLE_VISION_AVAILABLE:
                return self.recognize_with_google_vision(image_path)
            
            return offline_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Errore generale nell\'analisi: {str(e)}',
                'android_mode': True
            }
    
    def get_nearby_monuments(self, user_location: GPSCoordinate, radius_km: float = 50.0) -> List[Dict]:
        """Trova monumenti vicini alla posizione dell'utente."""
        nearby = []
        
        for key, monument in self.monuments_db.items():
            if 'coordinates' in monument:
                monument_location = GPSCoordinate(
                    monument['coordinates']['lat'],
                    monument['coordinates']['lon']
                )
                
                distance = self.gps_manager.calculate_distance(user_location, monument_location)
                
                if distance <= radius_km:
                    monument_with_distance = monument.copy()
                    monument_with_distance['distance'] = distance
                    monument_with_distance['distance_formatted'] = format_distance(distance)
                    monument_with_distance['key'] = key
                    nearby.append(monument_with_distance)
        
        # Ordina per distanza
        nearby.sort(key=lambda x: x['distance'])
        return nearby
    
    def record_visit(self, monument_key: str, monument_data: Dict, image_path: str = None):
        """Registra una visita a un monumento."""
        if self.visit_tracker:
            self.visit_tracker.record_visit(monument_key, monument_data, image_path)
    
    def get_visit_stats(self) -> Dict:
        """Ottiene statistiche delle visite."""
        if self.visit_tracker:
            return self.visit_tracker.get_stats()
        return {"total_visits": 0, "unique_monuments": 0, "total_countries": 0}
