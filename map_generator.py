"""
Map Generator Android-Compatible
Rimuove dipendenze folium, usa solo coordinate testuali
"""
import json
from typing import List, Dict, Tuple

class MapGenerator:
    def __init__(self):
        self.android_mode = True
    
    def generate_visits_map_data(self, visits_data: List[Dict]) -> Dict:
        """Genera dati per mappa Android-friendly (solo coordinate)"""
        if not visits_data:
            return {
                'message': 'Nessuna visita da visualizzare',
                'android_mode': True
            }
        
        map_points = []
        countries_visited = set()
        cities_visited = set()
        
        for visit in visits_data:
            if 'coordinates' in visit:
                coords = visit['coordinates']
                point = {
                    'name': visit.get('name', 'Monumento'),
                    'city': visit.get('city', 'Città sconosciuta'),
                    'country': visit.get('country', 'Paese sconosciuto'),
                    'lat': coords.get('lat', 0),
                    'lon': coords.get('lon', 0),
                    'date': visit.get('date', 'Data sconosciuta')
                }
                map_points.append(point)
                countries_visited.add(point['country'])
                cities_visited.add(point['city'])
        
        return {
            'points': map_points,
            'total_points': len(map_points),
            'countries_count': len(countries_visited),
            'cities_count': len(cities_visited),
            'countries_list': list(countries_visited),
            'cities_list': list(cities_visited),
            'android_mode': True,
            'message': 'Modalità Android: Mappa interattiva non disponibile'
        }
    
    def create_text_map_summary(self, map_data: Dict) -> str:
        """Crea riassunto testuale della mappa"""
        if not map_data.get('points'):
            return "🗺️ Nessuna visita da mostrare sulla mappa"
        
        summary = f"🗺️ MAPPA DELLE VISITE\n\n"
        summary += f"📍 Punti totali: {map_data['total_points']}\n"
        summary += f"🌍 Paesi visitati: {map_data['countries_count']}\n"
        summary += f"🏙️ Città visitate: {map_data['cities_count']}\n\n"
        
        summary += "🌍 PAESI:\n"
        for country in sorted(map_data['countries_list']):
            summary += f"  • {country}\n"
        
        summary += "\n🏙️ CITTÀ:\n"
        for city in sorted(map_data['cities_list']):
            summary += f"  • {city}\n"
        
        summary += "\n📱 Modalità Android - Mappa interattiva non disponibile"
        return summary
    
    def get_coordinates_list(self, map_data: Dict) -> List[Tuple[float, float, str]]:
        """Restituisce lista di coordinate per uso esterno"""
        coordinates = []
        for point in map_data.get('points', []):
            coordinates.append((point['lat'], point['lon'], point['name']))
        return coordinates
