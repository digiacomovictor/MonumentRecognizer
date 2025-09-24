"""
📚 Visit Tracker per Monument Recognizer
Sistema per registrare e gestire le visite ai monumenti
"""

import json
import os
import shutil
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path

from gps_manager import GPSCoordinate


@dataclass
class MonumentVisit:
    """Rappresenta una visita a un monumento."""
    monument_id: str
    monument_name: str
    visit_date: datetime
    user_id: Optional[int] = None  # ID dell'utente che ha fatto la visita
    gps_coordinates: Optional[GPSCoordinate] = None
    photo_path: Optional[str] = None
    user_notes: str = ""
    recognition_method: str = "unknown"
    confidence_score: Optional[float] = None
    weather: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Converte in dizionario per serializzazione."""
        return {
            'monument_id': self.monument_id,
            'monument_name': self.monument_name,
            'visit_date': self.visit_date.isoformat(),
            'user_id': self.user_id,
            'gps_coordinates': self.gps_coordinates.to_dict() if self.gps_coordinates else None,
            'photo_path': self.photo_path,
            'user_notes': self.user_notes,
            'recognition_method': self.recognition_method,
            'confidence_score': self.confidence_score,
            'weather': self.weather
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MonumentVisit':
        """Crea da dizionario."""
        gps_coords = None
        if data.get('gps_coordinates'):
            gps_coords = GPSCoordinate.from_dict(data['gps_coordinates'])
        
        return cls(
            monument_id=data['monument_id'],
            monument_name=data['monument_name'],
            visit_date=datetime.fromisoformat(data['visit_date']),
            user_id=data.get('user_id'),
            gps_coordinates=gps_coords,
            photo_path=data.get('photo_path'),
            user_notes=data.get('user_notes', ''),
            recognition_method=data.get('recognition_method', 'unknown'),
            confidence_score=data.get('confidence_score'),
            weather=data.get('weather')
        )


@dataclass
class UserStats:
    """Statistiche dell'utente."""
    total_visits: int = 0
    unique_monuments: int = 0
    countries_visited: Set[str] = None
    cities_visited: Set[str] = None
    favorite_style: Optional[str] = None
    total_photos: int = 0
    first_visit_date: Optional[date] = None
    last_visit_date: Optional[date] = None
    
    def __post_init__(self):
        if self.countries_visited is None:
            self.countries_visited = set()
        if self.cities_visited is None:
            self.cities_visited = set()
    
    def to_dict(self) -> Dict:
        """Converte in dizionario per serializzazione."""
        return {
            'total_visits': self.total_visits,
            'unique_monuments': self.unique_monuments,
            'countries_visited': list(self.countries_visited),
            'cities_visited': list(self.cities_visited),
            'favorite_style': self.favorite_style,
            'total_photos': self.total_photos,
            'first_visit_date': self.first_visit_date.isoformat() if self.first_visit_date else None,
            'last_visit_date': self.last_visit_date.isoformat() if self.last_visit_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserStats':
        """Crea da dizionario."""
        return cls(
            total_visits=data.get('total_visits', 0),
            unique_monuments=data.get('unique_monuments', 0),
            countries_visited=set(data.get('countries_visited', [])),
            cities_visited=set(data.get('cities_visited', [])),
            favorite_style=data.get('favorite_style'),
            total_photos=data.get('total_photos', 0),
            first_visit_date=date.fromisoformat(data['first_visit_date']) if data.get('first_visit_date') else None,
            last_visit_date=date.fromisoformat(data['last_visit_date']) if data.get('last_visit_date') else None
        )


class VisitTracker:
    """Gestore per il tracking delle visite ai monumenti."""
    
    def __init__(self, user_id: Optional[int] = None):
        self.user_id = user_id
        # File di visite specifico per utente o generale per ospiti
        if user_id:
            self.visits_file = f"monument_visits_user_{user_id}.json"
            self.photos_dir = f"visit_photos_user_{user_id}"
        else:
            self.visits_file = "monument_visits_guest.json"
            self.photos_dir = "visit_photos_guest"
        
        self.visits: List[MonumentVisit] = []
        self.stats = UserStats()
        
        # Crea la directory per le foto se non esiste
        os.makedirs(self.photos_dir, exist_ok=True)
        
        self.load_visits()
        self.calculate_stats()
    
    def load_visits(self):
        """Carica le visite dal file."""
        try:
            if os.path.exists(self.visits_file):
                with open(self.visits_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.visits = [MonumentVisit.from_dict(visit_data) for visit_data in data.get('visits', [])]
                    
                    if 'stats' in data:
                        self.stats = UserStats.from_dict(data['stats'])
                    
                print(f"📚 Caricate {len(self.visits)} visite dal database")
            else:
                print("📚 Nuovo database visite creato")
                
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️ Errore nel caricamento delle visite: {e}")
            self.visits = []
            self.stats = UserStats()
    
    def save_visits(self):
        """Salva le visite nel file."""
        try:
            data = {
                'visits': [visit.to_dict() for visit in self.visits],
                'stats': self.stats.to_dict(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.visits_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"💾 Database visite salvato ({len(self.visits)} visite)")
            
        except Exception as e:
            print(f"❌ Errore nel salvataggio: {e}")
    
    def add_visit(self, monument_id: str, monument_name: str, 
                  gps_coords: Optional[GPSCoordinate] = None,
                  photo_path: Optional[str] = None,
                  user_notes: str = "",
                  recognition_method: str = "unknown",
                  confidence_score: Optional[float] = None,
                  user_id: Optional[int] = None) -> MonumentVisit:
        """
        Aggiunge una nuova visita.
        
        Args:
            monument_id: ID del monumento
            monument_name: Nome del monumento
            gps_coords: Coordinate GPS della visita
            photo_path: Percorso della foto scattata
            user_notes: Note dell'utente
            recognition_method: Metodo usato per il riconoscimento
            confidence_score: Punteggio di confidenza
            
        Returns:
            L'oggetto MonumentVisit creato
        """
        # Copia la foto nella directory delle visite se specificata
        saved_photo_path = None
        if photo_path and os.path.exists(photo_path):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{monument_id}_{timestamp}.jpg"
                saved_photo_path = os.path.join(self.photos_dir, filename)
                shutil.copy2(photo_path, saved_photo_path)
                print(f"📸 Foto salvata: {saved_photo_path}")
            except Exception as e:
                print(f"⚠️ Errore nel salvare la foto: {e}")
        
        visit = MonumentVisit(
            monument_id=monument_id,
            monument_name=monument_name,
            visit_date=datetime.now(),
            user_id=user_id or self.user_id,
            gps_coordinates=gps_coords,
            photo_path=saved_photo_path,
            user_notes=user_notes,
            recognition_method=recognition_method,
            confidence_score=confidence_score
        )
        
        self.visits.append(visit)
        self.calculate_stats()
        self.save_visits()
        
        print(f"✅ Visita registrata: {monument_name}")
        return visit
    
    def get_visits_for_monument(self, monument_id: str, user_id: Optional[int] = None) -> List[MonumentVisit]:
        """Restituisce tutte le visite per un monumento specifico."""
        user_filter = user_id or self.user_id
        if user_filter:
            return [visit for visit in self.visits 
                   if visit.monument_id == monument_id and visit.user_id == user_filter]
        else:
            # Se nessun utente specificato, restituisce tutte le visite per il monumento
            return [visit for visit in self.visits if visit.monument_id == monument_id]
    
    def has_visited_monument(self, monument_id: str, user_id: Optional[int] = None) -> bool:
        """Verifica se l'utente ha già visitato un monumento."""
        user_filter = user_id or self.user_id
        if user_filter:
            return any(visit.monument_id == monument_id and visit.user_id == user_filter 
                      for visit in self.visits)
        else:
            # Per utenti ospite, verifica solo ID monumento
            return any(visit.monument_id == monument_id for visit in self.visits)
    
    def get_recent_visits(self, limit: int = 10) -> List[MonumentVisit]:
        """Restituisce le visite più recenti."""
        sorted_visits = sorted(self.visits, key=lambda x: x.visit_date, reverse=True)
        return sorted_visits[:limit]
    
    def get_visits_by_date_range(self, start_date: date, end_date: date) -> List[MonumentVisit]:
        """Restituisce visite in un range di date."""
        return [visit for visit in self.visits 
                if start_date <= visit.visit_date.date() <= end_date]
    
    def get_visits_by_country(self, monuments_db: Dict) -> Dict[str, List[MonumentVisit]]:
        """Raggruppa le visite per paese."""
        visits_by_country = {}
        
        for visit in self.visits:
            # Trova il paese del monumento dal database
            monument_data = monuments_db.get(visit.monument_id, {})
            country = monument_data.get('country', 'Sconosciuto')
            
            if country not in visits_by_country:
                visits_by_country[country] = []
            
            visits_by_country[country].append(visit)
        
        return visits_by_country
    
    def calculate_stats(self):
        """Ricalcola le statistiche dell'utente."""
        if not self.visits:
            self.stats = UserStats()
            return
        
        # Statistiche base
        self.stats.total_visits = len(self.visits)
        unique_monuments = set(visit.monument_id for visit in self.visits)
        self.stats.unique_monuments = len(unique_monuments)
        
        # Date
        visit_dates = [visit.visit_date.date() for visit in self.visits]
        self.stats.first_visit_date = min(visit_dates)
        self.stats.last_visit_date = max(visit_dates)
        
        # Foto
        self.stats.total_photos = len([visit for visit in self.visits if visit.photo_path])
    
    def get_achievement_progress(self) -> Dict[str, Dict]:
        """Calcola il progresso verso i vari achievement."""
        achievements = {
            'first_monument': {
                'name': '🎯 Primo Monumento',
                'description': 'Riconosci il tuo primo monumento',
                'progress': min(self.stats.total_visits, 1),
                'target': 1,
                'completed': self.stats.total_visits >= 1
            },
            'explorer': {
                'name': '🗺️ Esploratore',
                'description': 'Visita 5 monumenti diversi',
                'progress': min(self.stats.unique_monuments, 5),
                'target': 5,
                'completed': self.stats.unique_monuments >= 5
            },
            'historian': {
                'name': '📚 Storico',
                'description': 'Visita 10 monumenti diversi',
                'progress': min(self.stats.unique_monuments, 10),
                'target': 10,
                'completed': self.stats.unique_monuments >= 10
            },
            'photographer': {
                'name': '📸 Fotografo',
                'description': 'Scatta foto a 5 monumenti',
                'progress': min(self.stats.total_photos, 5),
                'target': 5,
                'completed': self.stats.total_photos >= 5
            },
            'world_traveler': {
                'name': '🌍 Viaggiatore del Mondo',
                'description': 'Visita monumenti in 3 paesi diversi',
                'progress': min(len(self.stats.countries_visited), 3),
                'target': 3,
                'completed': len(self.stats.countries_visited) >= 3
            }
        }
        
        return achievements
    
    def get_visit_summary(self) -> str:
        """Restituisce un riassunto testuale delle visite."""
        if not self.visits:
            return "🏛️ Non hai ancora visitato nessun monumento.\nInizia la tua avventura!"
        
        summary = f"""📊 **Il Tuo Diario di Viaggio**

🎯 **Statistiche Principali:**
• {self.stats.total_visits} visite totali
• {self.stats.unique_monuments} monumenti unici
• {len(self.stats.countries_visited)} paesi esplorati
• {self.stats.total_photos} foto scattate

📅 **Periodo:**
• Prima visita: {self.stats.first_visit_date.strftime('%d/%m/%Y') if self.stats.first_visit_date else 'N/A'}
• Ultima visita: {self.stats.last_visit_date.strftime('%d/%m/%Y') if self.stats.last_visit_date else 'N/A'}
"""

        # Visite recenti
        recent = self.get_recent_visits(3)
        if recent:
            summary += "\n🕒 **Visite Recenti:**\n"
            for visit in recent:
                date_str = visit.visit_date.strftime('%d/%m/%Y')
                summary += f"• {visit.monument_name} ({date_str})\n"
        
        return summary
    
    def export_visits_to_csv(self, filename: Optional[str] = None) -> str:
        """Esporta le visite in formato CSV."""
        if filename is None:
            filename = f"monument_visits_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['monument_name', 'visit_date', 'latitude', 'longitude', 
                            'recognition_method', 'confidence_score', 'user_notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for visit in self.visits:
                    row = {
                        'monument_name': visit.monument_name,
                        'visit_date': visit.visit_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'latitude': visit.gps_coordinates.latitude if visit.gps_coordinates else '',
                        'longitude': visit.gps_coordinates.longitude if visit.gps_coordinates else '',
                        'recognition_method': visit.recognition_method,
                        'confidence_score': visit.confidence_score or '',
                        'user_notes': visit.user_notes
                    }
                    writer.writerow(row)
            
            print(f"📊 Visite esportate in: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Errore nell'esportazione: {e}")
            return ""
    
    def cleanup_old_photos(self, days_old: int = 30):
        """Rimuove le foto più vecchie di un certo numero di giorni."""
        if not os.path.exists(self.photos_dir):
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        for filename in os.listdir(self.photos_dir):
            filepath = os.path.join(self.photos_dir, filename)
            
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_date:
                    os.remove(filepath)
                    cleaned_count += 1
            except Exception as e:
                print(f"⚠️ Errore nella pulizia di {filename}: {e}")
        
        if cleaned_count > 0:
            print(f"🧹 Rimosse {cleaned_count} foto vecchie")
    
    def get_visit_heatmap_data(self) -> List[Dict]:
        """Restituisce dati per creare una heatmap delle visite."""
        heatmap_data = []
        
        for visit in self.visits:
            if visit.gps_coordinates:
                heatmap_data.append({
                    'lat': visit.gps_coordinates.latitude,
                    'lng': visit.gps_coordinates.longitude,
                    'weight': 1,  # Peso per la heatmap
                    'monument': visit.monument_name,
                    'date': visit.visit_date.isoformat()
                })
        
        return heatmap_data
