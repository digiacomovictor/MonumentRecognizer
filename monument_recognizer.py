import json
import os
import io
from typing import Dict, List, Optional
from PIL import Image
import cv2
import numpy as np

from gps_manager import GPSManager, GPSCoordinate, format_distance
from visit_tracker import VisitTracker
from user_system import UserSystem

# Google Cloud Vision
try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    print("Google Cloud Vision non disponibile. Installare con: pip install google-cloud-vision")

class MonumentRecognizer:
    def __init__(self, user_system: UserSystem = None):
        """Inizializza il riconoscitore di monumenti con Google Vision API."""
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
            print("Database dei monumenti non trovato!")
            return {}
    
    def setup_google_vision(self):
        """Configura Google Vision API."""
        if not GOOGLE_VISION_AVAILABLE:
            print("Google Vision API non disponibile. L'app funzionerà in modalità offline.")
            return False
            
        try:
            # Prova prima con le credenziali di default
            self.vision_client = vision.ImageAnnotatorClient()
            print("Google Vision API configurata correttamente!")
            return True
        except Exception as e:
            print(f"Google Vision API non configurata: {e}")
            print("L'app funzionerà in modalità offline con riconoscimento semplificato.")
            return False
    
    def set_api_credentials(self, api_key_path: str) -> bool:
        """Imposta le credenziali per Google Vision API."""
        if not GOOGLE_VISION_AVAILABLE:
            return False
            
        try:
            if os.path.exists(api_key_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = api_key_path
                self.api_key_path = api_key_path
                self.vision_client = vision.ImageAnnotatorClient()
                return True
            else:
                print(f"File credenziali non trovato: {api_key_path}")
                return False
        except Exception as e:
            print(f"Errore nell'impostazione delle credenziali: {e}")
            return False
    
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """Preprocessa l'immagine per l'analisi."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
                
            # Ridimensiona se troppo grande
            height, width = image.shape[:2]
            max_size = 1600  # Google Vision supporta immagini più grandi
            if width > max_size or height > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            return image
        except Exception as e:
            print(f"Errore nel preprocessamento dell'immagine: {e}")
            return None
    
    def recognize_with_google_vision(self, image_path: str) -> Dict:
        """Riconosce monumenti usando Google Vision API."""
        if not self.vision_client:
            return {'success': False, 'error': 'Google Vision API non disponibile'}
        
        try:
            # Carica l'immagine
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Rileva landmark
            landmark_response = self.vision_client.landmark_detection(image=image)
            landmarks = landmark_response.landmark_annotations
            
            if landmark_response.error.message:
                raise Exception(f'Google Vision API error: {landmark_response.error.message}')
            
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
            
            # Se non trova landmark, prova con label detection
            label_response = self.vision_client.label_detection(image=image)
            labels = label_response.label_annotations
            
            if label_response.error.message:
                raise Exception(f'Google Vision API error: {label_response.error.message}')
                
            # Cerca etichette che potrebbero indicare monumenti
            monument_labels = []
            for label in labels:
                if self.is_monument_related_label(label.description):
                    monument_labels.append((label.description, label.score))
            
            if monument_labels:
                # Prova a indovinare il monumento dalle etichette
                monument_info = self.guess_monument_from_labels([l[0] for l in monument_labels])
                if monument_info:
                    return {
                        'success': True,
                        'monument': monument_info,
                        'confidence': int(max([l[1] for l in monument_labels]) * 100),
                        'detected_labels': [l[0] for l in monument_labels],
                        'method': 'Google Vision API - Label Detection'
                    }
            
            return {
                'success': False,
                'error': 'Nessun monumento famoso riconosciuto nell\'immagine.',
                'detected_labels': [label.description for label in labels[:5]]  # Prime 5 etichette
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Errore Google Vision API: {str(e)}'
            }
    
    def is_monument_related_label(self, label: str) -> bool:
        """Verifica se un'etichetta è relativa a monumenti."""
        monument_keywords = [
            'tower', 'cathedral', 'church', 'monument', 'statue', 'landmark',
            'architecture', 'historic', 'ancient', 'building', 'castle',
            'palace', 'temple', 'basilica', 'memorial', 'amphitheatre'
        ]
        
        label_lower = label.lower()
        return any(keyword in label_lower for keyword in monument_keywords)
    
    def guess_monument_from_labels(self, labels: List[str]) -> Optional[Dict]:
        """Prova a indovinare il monumento dalle etichette Google."""
        labels_text = ' '.join(labels).lower()
        
        # Regole semplici per indovinare monumenti
        if 'tower' in labels_text and 'paris' in labels_text:
            return self.monuments_db.get('eiffel_tower')
        elif 'tower' in labels_text and ('leaning' in labels_text or 'pisa' in labels_text):
            return self.monuments_db.get('tower_of_pisa')
        elif 'colosseum' in labels_text or 'amphitheatre' in labels_text:
            return self.monuments_db.get('colosseum')
        elif 'statue' in labels_text and 'liberty' in labels_text:
            return self.monuments_db.get('statue_of_liberty')
        elif 'christ' in labels_text or 'redeemer' in labels_text:
            return self.monuments_db.get('christ_redeemer')
        
        return None
    
    def find_monument_by_name(self, landmark_name: str) -> Optional[Dict]:
        """Trova un monumento nel database usando il nome del landmark."""
        landmark_lower = landmark_name.lower()
        
        for monument_id, monument_data in self.monuments_db.items():
            # Verifica nei nomi Google specifici
            for google_name in monument_data.get('google_names', []):
                if google_name.lower() in landmark_lower or landmark_lower in google_name.lower():
                    return monument_data
            
            # Verifica anche nel nome principale
            if monument_data['name'].lower() in landmark_lower or landmark_lower in monument_data['name'].lower():
                return monument_data
        
        return None
    
    def recognize_with_fallback(self, image_path: str) -> Dict:
        """Riconoscimento fallback senza Google Vision API."""
        try:
            # Carica e analizza l'immagine con OpenCV
            image = self.preprocess_image(image_path)
            if image is None:
                return {'success': False, 'error': 'Impossibile caricare l\'immagine'}
            
            # Analisi semplificata basata su caratteristiche visive
            features = self.extract_simple_features(image)
            monument_id = self.match_simple_features(features)
            
            if monument_id:
                return {
                    'success': True,
                    'monument': self.monuments_db[monument_id],
                    'confidence': 65,  # Confidenza ridotta per modalità offline
                    'method': 'Analisi offline semplificata'
                }
            else:
                return {
                    'success': False,
                    'error': 'Monumento non riconosciuto con il metodo offline. Per migliori risultati, configura Google Vision API.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Errore nell\'analisi offline: {str(e)}'
            }
    
    def extract_simple_features(self, image: np.ndarray) -> Dict:
        """Estrae caratteristiche semplici dall'immagine."""
        # Converte in scala di grigi
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Rileva bordi
        edges = cv2.Canny(gray, 50, 150)
        
        # Conta linee verticali e orizzontali
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        vertical_lines = 0
        horizontal_lines = 0
        
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                angle = theta * 180 / np.pi
                if abs(angle) < 10 or abs(angle - 180) < 10:
                    vertical_lines += 1
                elif abs(angle - 90) < 10:
                    horizontal_lines += 1
        
        # Analizza colori dominanti
        image_small = cv2.resize(image, (100, 100))
        colors = image_small.reshape(-1, 3)
        colors_mean = np.mean(colors, axis=0)
        
        return {
            'vertical_lines': vertical_lines,
            'horizontal_lines': horizontal_lines,
            'dominant_color': colors_mean,
            'brightness': np.mean(gray)
        }
    
    def match_simple_features(self, features: Dict) -> Optional[str]:
        """Confronta le caratteristiche con regole semplici."""
        v_lines = features['vertical_lines']
        h_lines = features['horizontal_lines']
        color = features['dominant_color']
        brightness = features['brightness']
        
        # Regole molto semplificate
        if v_lines > 20 and color[2] < 100:  # Molte linee verticali, colore scuro
            return 'eiffel_tower'
        elif v_lines > 15 and brightness > 150:  # Molte linee verticali, immagine chiara
            return 'tower_of_pisa'
        elif h_lines > 10 and v_lines > 10:  # Mix di linee
            return 'colosseum'
        elif color[1] > color[0] and color[1] > color[2]:  # Dominante verde
            return 'statue_of_liberty'
        
        return None
    
    def recognize_with_fallback_and_gps(self, image_path: str) -> Dict:
        """Riconoscimento fallback che usa GPS per migliorare l'accuratezza."""
        try:
            # Prima prova il metodo normale
            base_result = self.recognize_with_fallback(image_path)
            
            # Se abbiamo GPS, proviamo a raffinare il risultato
            if self.gps_manager.current_position:
                nearby_monuments = self.gps_manager.get_monuments_nearby(
                    self.monuments_db, radius_km=100
                )
                
                if nearby_monuments:
                    # Se il riconoscimento di base ha fallito, prova con i monumenti vicini
                    if not base_result['success'] and nearby_monuments:
                        # Prende il monumento più vicino come candidato
                        closest = nearby_monuments[0]
                        return {
                            'success': True,
                            'monument': closest,
                            'confidence': 50,  # Confidenza ridotta per guess GPS
                            'method': 'GPS Location-based guess',
                            'distance_km': closest.get('distance_km', 'N/A'),
                            'location_note': f'Monumento più vicino a {closest["distance_km"]}km dalla tua posizione'
                        }
                    
                    # Se il riconoscimento ha funzionato, verifica se è coerente con GPS
                    elif base_result['success']:
                        recognized_id = None
                        for mid, mdata in self.monuments_db.items():
                            if mdata['name'] == base_result['monument']['name']:
                                recognized_id = mid
                                break
                        
                        # Verifica se il monumento riconosciuto è tra quelli vicini
                        nearby_ids = [m['id'] for m in nearby_monuments]
                        if recognized_id in nearby_ids:
                            base_result['confidence'] = min(base_result['confidence'] + 20, 95)
                            base_result['method'] += ' + GPS confirmation'
                            
                            # Trova la distanza
                            for monument in nearby_monuments:
                                if monument['id'] == recognized_id:
                                    base_result['distance_km'] = monument['distance_km']
                                    break
                        else:
                            base_result['confidence'] = max(base_result['confidence'] - 10, 10)
                            base_result['method'] += ' (GPS inconsistency)'
                
            return base_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Errore nel riconoscimento GPS-enhanced: {str(e)}'
            }
    
    def enhance_result_with_gps(self, result: Dict) -> Dict:
        """Migliora il risultato aggiungendo informazioni GPS."""
        if not self.gps_manager.current_position or not result.get('success'):
            return result
        
        # Trova le coordinate del monumento
        monument_id = None
        for mid, mdata in self.monuments_db.items():
            if mdata['name'] == result['monument']['name']:
                monument_id = mid
                break
        
        if monument_id and 'coordinates' in self.monuments_db[monument_id]:
            monument_coords = GPSCoordinate(
                latitude=self.monuments_db[monument_id]['coordinates']['latitude'],
                longitude=self.monuments_db[monument_id]['coordinates']['longitude']
            )
            
            distance_m = self.gps_manager.calculate_distance(
                self.gps_manager.current_position, monument_coords
            )
            
            result['distance_km'] = round(distance_m / 1000, 2)
            result['user_location'] = self.gps_manager.get_location_string()
            result['is_nearby'] = self.gps_manager.is_near_location(monument_coords, 5000)  # 5km
            
            if result['is_nearby']:
                result['location_note'] = f'Sei vicino a questo monumento! ({format_distance(distance_m)})'
            else:
                result['location_note'] = f'Distanza dal monumento: {format_distance(distance_m)}'
        
        return result
    
    def register_visit(self, result: Dict, image_path: str):
        """Registra la visita al monumento."""
        if not result.get('success'):
            return
        
        # Trova l'ID del monumento
        monument_id = None
        for mid, mdata in self.monuments_db.items():
            if mdata['name'] == result['monument']['name']:
                monument_id = mid
                break
        
        if monument_id:
            # Determina l'ID utente
            user_id = None
            if self.user_system and self.user_system.is_logged_in():
                user_id = self.user_system.current_user.user_id
            
            # Verifica se è una visita molto vicina (entro 5km) o se l'utente è loggato
            is_real_visit = (
                result.get('is_nearby', False) or 
                result.get('distance_km', float('inf')) < 5 or
                (self.user_system and self.user_system.is_logged_in())  # Gli utenti loggati possono sempre salvare
            )
            
            if is_real_visit:
                self.visit_tracker.add_visit(
                    monument_id=monument_id,
                    monument_name=result['monument']['name'],
                    gps_coords=self.gps_manager.current_position,
                    photo_path=image_path,
                    recognition_method=result.get('method', 'unknown'),
                    confidence_score=result.get('confidence'),
                    user_id=user_id
                )
                result['visit_registered'] = True
                
                if self.user_system and self.user_system.is_logged_in():
                    result['visit_note'] = "✅ Visita salvata nel tuo profilo!"
                else:
                    result['visit_note'] = "✅ Visita registrata (modalità ospite)"
            else:
                result['visit_registered'] = False
                result['visit_note'] = "📍 Troppo lontano per registrare come visita reale"
    
    def get_nearby_monuments(self, radius_km: float = 50) -> List[Dict]:
        """Restituisce monumenti nelle vicinanze."""
        self.gps_manager.update_position()
        return self.gps_manager.get_monuments_nearby(self.monuments_db, radius_km)
    
    def get_visit_stats(self) -> str:
        """Restituisce statistiche delle visite."""
        if self.user_system and self.user_system.is_logged_in():
            user_name = self.user_system.current_user.full_name
            stats = self.visit_tracker.get_visit_summary()
            return f"📊 Statistiche di {user_name}:\n\n{stats}"
        else:
            return self.visit_tracker.get_visit_summary()
    
    def update_user_context(self, user_system: UserSystem = None):
        """Aggiorna il contesto utente e ricrea il visit tracker se necessario."""
        self.user_system = user_system
        
        # Ricrea visit tracker con il nuovo utente
        user_id = None
        if user_system and user_system.is_logged_in():
            user_id = user_system.current_user.user_id
        self.visit_tracker = VisitTracker(user_id)
    
    def recognize_monument(self, image_path: str) -> Dict:
        """Metodo principale per riconoscere monumenti."""
        # Aggiorna la posizione GPS se possibile
        self.gps_manager.update_position()
        
        # Prova prima con Google Vision API
        if self.vision_client:
            result = self.recognize_with_google_vision(image_path)
            if result['success']:
                # Migliora il risultato con informazioni GPS
                result = self.enhance_result_with_gps(result)
                
                # Registra la visita
                self.register_visit(result, image_path)
                return result
            
            # Se Google Vision non riesce, prova il fallback
            print("Google Vision non ha riconosciuto il monumento, provo con analisi offline...")
        
        # Fallback con analisi offline e GPS
        result = self.recognize_with_fallback_and_gps(image_path)
        
        if result['success']:
            result = self.enhance_result_with_gps(result)
            self.register_visit(result, image_path)
        
        return result
