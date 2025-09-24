"""
📍 GPS Manager per Monument Recognizer
Gestisce la posizione dell'utente per migliorare il riconoscimento monumenti
"""

import json
import math
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GPSCoordinate:
    """Rappresenta una coordinata GPS."""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Converte in dizionario per serializzazione."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GPSCoordinate':
        """Crea da dizionario."""
        return cls(
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy'),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None
        )

class GPSManager:
    """Manager per la gestione della posizione GPS."""
    
    def __init__(self):
        self.current_position: Optional[GPSCoordinate] = None
        self.position_cache_file = "user_position_cache.json"
        self.last_update_time = 0
        self.cache_duration = 300  # 5 minuti
        self.load_cached_position()
    
    def load_cached_position(self):
        """Carica la posizione dalla cache se disponibile."""
        try:
            with open(self.position_cache_file, 'r') as f:
                data = json.load(f)
                self.current_position = GPSCoordinate.from_dict(data)
                print(f"📍 Posizione caricata dalla cache: {self.get_location_string()}")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            print("📍 Nessuna posizione in cache")
    
    def save_position_cache(self):
        """Salva la posizione corrente in cache."""
        if self.current_position:
            try:
                with open(self.position_cache_file, 'w') as f:
                    json.dump(self.current_position.to_dict(), f)
            except Exception as e:
                print(f"⚠️ Errore nel salvare la posizione: {e}")
    
    def get_location_via_ip(self) -> Optional[GPSCoordinate]:
        """
        Ottiene la posizione approssimativa tramite IP.
        Metodo di fallback quando GPS non è disponibile.
        """
        try:
            print("🌐 Rilevamento posizione tramite IP...")
            
            # Usa un servizio gratuito per la geolocalizzazione IP
            response = requests.get('http://ipapi.co/json/', timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'latitude' in data and 'longitude' in data:
                    coord = GPSCoordinate(
                        latitude=float(data['latitude']),
                        longitude=float(data['longitude']),
                        accuracy=10000,  # Accuratezza bassa per IP
                        timestamp=datetime.now()
                    )
                    
                    print(f"✅ Posizione IP rilevata: {data.get('city', 'Sconosciuta')}, {data.get('country_name', 'Sconosciuto')}")
                    return coord
                
        except requests.RequestException as e:
            print(f"❌ Errore nella geolocalizzazione IP: {e}")
        except Exception as e:
            print(f"❌ Errore generico nella geolocalizzazione: {e}")
        
        return None
    
    def get_location_via_windows_api(self) -> Optional[GPSCoordinate]:
        """
        Tenta di ottenere la posizione tramite Windows Location API.
        Richiede permessi di localizzazione su Windows.
        """
        try:
            # Prova ad usare le API Windows per la posizione
            # Questo funziona solo se l'utente ha abilitato i servizi di localizzazione
            import winrt.windows.devices.geolocation as geo
            
            print("📱 Rilevamento posizione tramite Windows...")
            
            # Crea il geolocator
            geolocator = geo.Geolocator()
            
            # Controlla se la posizione è disponibile
            if geolocator.location_status == geo.PositionStatus.DISABLED:
                print("❌ Servizi di localizzazione disabilitati in Windows")
                return None
            
            # Ottieni la posizione (questo è asincrono, ma semplifichiamo)
            # Nota: In una vera implementazione asincrona, useresti await
            print("📍 Richiesta posizione in corso...")
            
            return None  # Per ora non implementiamo WinRT completo
            
        except ImportError:
            print("📍 Windows Location API non disponibile")
            return None
        except Exception as e:
            print(f"❌ Errore Windows Location API: {e}")
            return None
    
    def update_position(self, force_update: bool = False) -> bool:
        """
        Aggiorna la posizione corrente.
        
        Args:
            force_update: Se True, forza l'aggiornamento ignorando la cache
            
        Returns:
            True se la posizione è stata aggiornata con successo
        """
        current_time = time.time()
        
        # Controlla se abbiamo una posizione recente in cache
        if (not force_update and 
            self.current_position and 
            (current_time - self.last_update_time) < self.cache_duration):
            print("📍 Uso posizione dalla cache")
            return True
        
        print("📍 Aggiornamento posizione in corso...")
        
        # Prova prima con Windows Location API
        position = self.get_location_via_windows_api()
        
        # Se non funziona, usa geolocalizzazione IP
        if position is None:
            position = self.get_location_via_ip()
        
        if position:
            self.current_position = position
            self.last_update_time = current_time
            self.save_position_cache()
            print(f"✅ Posizione aggiornata: {self.get_location_string()}")
            return True
        else:
            print("❌ Impossibile ottenere la posizione")
            return False
    
    def get_current_position(self) -> Optional[GPSCoordinate]:
        """Restituisce la posizione corrente."""
        return self.current_position
    
    def get_location_string(self) -> str:
        """Restituisce una stringa descrittiva della posizione corrente."""
        if not self.current_position:
            return "Posizione sconosciuta"
        
        return f"{self.current_position.latitude:.4f}, {self.current_position.longitude:.4f}"
    
    def calculate_distance(self, coord1: GPSCoordinate, coord2: GPSCoordinate) -> float:
        """
        Calcola la distanza tra due coordinate in metri usando la formula dell'haversine.
        
        Args:
            coord1: Prima coordinata
            coord2: Seconda coordinata
            
        Returns:
            Distanza in metri
        """
        # Raggio della Terra in metri
        R = 6371000
        
        # Converte gradi in radianti
        lat1_rad = math.radians(coord1.latitude)
        lat2_rad = math.radians(coord2.latitude)
        delta_lat_rad = math.radians(coord2.latitude - coord1.latitude)
        delta_lon_rad = math.radians(coord2.longitude - coord1.longitude)
        
        # Formula dell'haversine
        a = (math.sin(delta_lat_rad / 2) * math.sin(delta_lat_rad / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon_rad / 2) * math.sin(delta_lon_rad / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def is_near_location(self, target_coord: GPSCoordinate, radius_meters: float = 1000) -> bool:
        """
        Verifica se l'utente si trova vicino a una posizione specifica.
        
        Args:
            target_coord: Coordinata target
            radius_meters: Raggio in metri per considerare "vicino"
            
        Returns:
            True se l'utente è entro il raggio specificato
        """
        if not self.current_position:
            return False
        
        distance = self.calculate_distance(self.current_position, target_coord)
        return distance <= radius_meters
    
    def get_monuments_nearby(self, monuments_db: Dict, radius_km: float = 50) -> List[Dict]:
        """
        Trova monumenti nelle vicinanze della posizione corrente.
        
        Args:
            monuments_db: Database dei monumenti
            radius_km: Raggio di ricerca in chilometri
            
        Returns:
            Lista dei monumenti nelle vicinanze ordinati per distanza
        """
        if not self.current_position:
            return []
        
        nearby_monuments = []
        
        for monument_id, monument_data in monuments_db.items():
            # Controlla se il monumento ha coordinate GPS
            if 'coordinates' in monument_data:
                monument_coord = GPSCoordinate(
                    latitude=monument_data['coordinates']['latitude'],
                    longitude=monument_data['coordinates']['longitude']
                )
                
                distance_m = self.calculate_distance(self.current_position, monument_coord)
                distance_km = distance_m / 1000
                
                if distance_km <= radius_km:
                    monument_info = monument_data.copy()
                    monument_info['id'] = monument_id
                    monument_info['distance_km'] = round(distance_km, 2)
                    nearby_monuments.append(monument_info)
        
        # Ordina per distanza
        nearby_monuments.sort(key=lambda x: x['distance_km'])
        
        return nearby_monuments
    
    def request_location_permission(self) -> bool:
        """
        Richiede i permessi di localizzazione all'utente.
        Per Windows, guida l'utente ad abilitare i servizi.
        """
        print("📍 Per un'esperienza migliore, abilita i servizi di localizzazione:")
        print("   1. Apri Impostazioni Windows")
        print("   2. Vai su Privacy e sicurezza > Posizione")
        print("   3. Abilita 'Servizi di posizione'")
        print("   4. Assicurati che le app desktop possano accedere alla posizione")
        
        # Per ora restituiamo sempre True e usiamo geolocalizzazione IP
        return True

# Funzioni di utilità globali
def format_distance(distance_meters: float) -> str:
    """Formatta la distanza in modo user-friendly."""
    if distance_meters < 1000:
        return f"{distance_meters:.0f}m"
    else:
        return f"{distance_meters/1000:.1f}km"

def get_compass_direction(coord1: GPSCoordinate, coord2: GPSCoordinate) -> str:
    """Calcola la direzione della bussola tra due coordinate."""
    lat1_rad = math.radians(coord1.latitude)
    lat2_rad = math.radians(coord2.latitude)
    delta_lon_rad = math.radians(coord2.longitude - coord1.longitude)
    
    x = math.sin(delta_lon_rad) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon_rad))
    
    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)
    bearing_deg = (bearing_deg + 360) % 360
    
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(bearing_deg / 45) % 8
    return directions[index]
