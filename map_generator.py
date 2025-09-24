"""
🗺️ Map Generator per Monument Recognizer
Crea mappe interattive per visualizzare monumenti e visite
"""

import os
import json
import webbrowser
from typing import Dict, List, Optional
from datetime import datetime, date

from gps_manager import GPSCoordinate
from visit_tracker import VisitTracker, MonumentVisit


class MapGenerator:
    """Generatore di mappe interattive."""
    
    def __init__(self, monuments_db: Dict, visit_tracker: VisitTracker):
        self.monuments_db = monuments_db
        self.visit_tracker = visit_tracker
        self.maps_dir = "generated_maps"
        os.makedirs(self.maps_dir, exist_ok=True)
    
    def create_visited_monuments_map(self, 
                                    start_date: Optional[date] = None,
                                    end_date: Optional[date] = None,
                                    monument_styles: Optional[List[str]] = None,
                                    user_id: Optional[int] = None) -> str:
        """
        Crea una mappa HTML con i monumenti visitati con filtri opzionali.
        
        Args:
            start_date: Data di inizio per filtrare le visite
            end_date: Data di fine per filtrare le visite  
            monument_styles: Lista di stili architettonici da includere
            user_id: ID utente specifico (per amministratori)
        
        Returns:
            Path del file HTML generato
        """
        try:
            import folium
            from folium import plugins
        except ImportError:
            return self.create_simple_html_map()
        
        # Crea mappa centrata sul primo monumento visitato o Europa
        if self.visit_tracker.visits:
            first_visit = self.visit_tracker.visits[0]
            if first_visit.gps_coordinates:
                center_lat = first_visit.gps_coordinates.latitude
                center_lon = first_visit.gps_coordinates.longitude
            else:
                center_lat, center_lon = 48.8566, 2.3522  # Parigi
        else:
            center_lat, center_lon = 48.8566, 2.3522  # Parigi
        
        # Crea la mappa
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Filtra le visite se specificato
        filtered_visits = self.visit_tracker.visits
        
        if start_date or end_date:
            filtered_visits = [
                visit for visit in filtered_visits
                if (not start_date or visit.visit_date.date() >= start_date) and
                   (not end_date or visit.visit_date.date() <= end_date)
            ]
        
        if user_id is not None:
            filtered_visits = [
                visit for visit in filtered_visits
                if visit.user_id == user_id
            ]
        
        # Filtra per stili se specificato
        if monument_styles:
            filtered_visits = [
                visit for visit in filtered_visits
                if self.monuments_db.get(visit.monument_id, {}).get('style') in monument_styles
            ]
        
        # Aggiungi monumenti visitati (filtrati)
        visited_monuments = set()
        for visit in filtered_visits:
            if visit.monument_id not in visited_monuments:
                visited_monuments.add(visit.monument_id)
                
                # Ottieni info monumento
                monument_data = self.monuments_db.get(visit.monument_id, {})
                coords = monument_data.get('coordinates')
                
                if coords:
                    # Conta visite multiple (dalle visite filtrate)
                    visit_count = len([v for v in filtered_visits if v.monument_id == visit.monument_id])
                    
                    # Calcola statistiche visite per questo monumento (dalle visite filtrate)
                    monument_visits = [v for v in filtered_visits if v.monument_id == visit.monument_id]
                    last_visit = max(monument_visits, key=lambda x: x.visit_date)
                    
                    # Trova se ci sono foto
                    photos_count = len([v for v in monument_visits if v.photo_path])
                    
                    # Popup info migliorato
                    popup_html = f"""
                    <div style="width:300px; font-family: Arial, sans-serif;">
                        <div style="background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 12px; margin: -10px -10px 15px -10px; border-radius: 8px 8px 0 0;">
                            <h3 style="margin: 0; font-size: 18px;">✅ {monument_data.get('name', 'Monumento')}</h3>
                            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 12px;">🎯 Monumento Visitato</p>
                        </div>
                        
                        <div style="padding: 5px 0;">
                            <p style="margin: 8px 0; color: #333;"><strong>📍 Località:</strong> {monument_data.get('location', 'N/A')}</p>
                            <p style="margin: 8px 0; color: #333;"><strong>🏗️ Costruito:</strong> {monument_data.get('year_built', 'N/A')}</p>
                            <p style="margin: 8px 0; color: #333;"><strong>🎨 Stile:</strong> {monument_data.get('style', 'N/A')}</p>
                        </div>
                        
                        <div style="background: #f0f8f0; padding: 10px; border-radius: 5px; margin-top: 15px;">
                            <h4 style="margin: 0 0 8px 0; color: #2e7d32; font-size: 14px;">📊 Le Tue Visite:</h4>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>🎯 Totale visite:</strong> {visit_count}</p>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>📅 Prima visita:</strong> {visit.visit_date.strftime('%d/%m/%Y %H:%M')}</p>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>🕒 Ultima visita:</strong> {last_visit.visit_date.strftime('%d/%m/%Y %H:%M')}</p>
                            <p style="margin: 5px 0; font-size: 13px;"><strong>📸 Foto scattate:</strong> {photos_count}</p>
                        </div>
                        
                        {monument_data.get('description', '')[:150] + '...' if monument_data.get('description') else ''}
                    </div>
                    """
                    
                    # Icona diversa per monumenti visitati
                    folium.Marker(
                        location=[coords['latitude'], coords['longitude']],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"✅ {monument_data.get('name', 'Monumento')} (Visitato)",
                        icon=folium.Icon(color='green', icon='star', prefix='fa')
                    ).add_to(m)
        
        # Aggiungi altri monumenti (non visitati)
        for monument_id, monument_data in self.monuments_db.items():
            if monument_id not in visited_monuments and 'coordinates' in monument_data:
                coords = monument_data['coordinates']
                
                # Popup per monumenti non visitati
                popup_html = f"""
                <div style="width:300px; font-family: Arial, sans-serif;">
                    <div style="background: linear-gradient(135deg, #2196F3, #1976D2); color: white; padding: 12px; margin: -10px -10px 15px -10px; border-radius: 8px 8px 0 0;">
                        <h3 style="margin: 0; font-size: 18px;">🏛️ {monument_data.get('name', 'Monumento')}</h3>
                        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 12px;">⏳ Da Esplorare</p>
                    </div>
                    
                    <div style="padding: 5px 0;">
                        <p style="margin: 8px 0; color: #333;"><strong>📍 Località:</strong> {monument_data.get('location', 'N/A')}</p>
                        <p style="margin: 8px 0; color: #333;"><strong>🏗️ Costruito:</strong> {monument_data.get('year_built', 'N/A')}</p>
                        <p style="margin: 8px 0; color: #333;"><strong>🎨 Stile:</strong> {monument_data.get('style', 'N/A')}</p>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 10px; border-radius: 5px; margin-top: 15px;">
                        <p style="margin: 0; color: #1565C0; font-style: italic; font-size: 13px;">💡 Visita questo monumento e scatta una foto per aggiungerlo al tuo diario di viaggio!</p>
                    </div>
                    
                    {monument_data.get('description', '')[:150] + '...' if monument_data.get('description') else ''}
                </div>
                """
                
                folium.Marker(
                    location=[coords['latitude'], coords['longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"⏳ {monument_data.get('name', 'Monumento')} (Da visitare)",
                    icon=folium.Icon(color='blue', icon='camera', prefix='fa')
                ).add_to(m)
        
        # Aggiungi heatmap delle visite filtrate
        heat_data = []
        for visit in filtered_visits:
            if visit.gps_coordinates:
                heat_data.append({
                    'lat': visit.gps_coordinates.latitude,
                    'lng': visit.gps_coordinates.longitude,
                    'weight': 1
                })
        
        if heat_data:
            heat_points = [[point['lat'], point['lng'], point['weight']] for point in heat_data]
            plugins.HeatMap(heat_points, radius=20, blur=15, max_zoom=1).add_to(m)
        
        # Aggiungi layer control
        folium.LayerControl().add_to(m)
        
        # Aggiungi legenda per i filtri
        filter_info = []
        if start_date or end_date:
            date_filter = f"Date: {start_date or 'inizio'} - {end_date or 'oggi'}"
            filter_info.append(date_filter)
        if monument_styles:
            style_filter = f"Stili: {', '.join(monument_styles)}"
            filter_info.append(style_filter)
        if user_id:
            filter_info.append(f"Utente ID: {user_id}")
        
        if filter_info:
            legend_html = f'''
            <div style="position: fixed; 
                        top: 10px; right: 10px; width: 200px; height: auto; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:12px; padding: 10px">
            <h4>📊 Filtri Applicati:</h4>
            <ul style="margin: 5px 0; padding-left: 15px;">
                {"<li>" + "</li><li>".join(filter_info) + "</li>"}
            </ul>
            <p><small>Totale visite mostrate: {len(filtered_visits)}</small></p>
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
        
        # Salva mappa
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filter_suffix = '_filtered' if filter_info else ''
        filename = os.path.join(self.maps_dir, f"monument_visits_map{filter_suffix}_{timestamp}.html")
        m.save(filename)
        
        return filename
    
    def create_simple_html_map(self) -> str:
        """
        Crea una mappa HTML semplice usando Google Maps (fallback).
        """
        # Prima parte dell'HTML
        html_start = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🗺️ Mappa Monumenti Visitati</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #e3f2fd; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #1976d2; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .monuments-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .monument-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: #fafafa; }}
        .monument-card.visited {{ border-color: #4caf50; background: #e8f5e8; }}
        .monument-name {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }}
        .monument-info {{ color: #666; margin-bottom: 5px; }}
        .visited-badge {{ background: #4caf50; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; }}
        .not-visited-badge {{ background: #ff9800; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; }}
        .google-maps-link {{ display: inline-block; margin-top: 10px; padding: 5px 10px; background: #2196f3; color: white; text-decoration: none; border-radius: 4px; font-size: 0.9em; }}
        .google-maps-link:hover {{ background: #1976d2; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ Il Tuo Viaggio nei Monumenti</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{self.visit_tracker.stats.total_visits}</div>
                <div class="stat-label">Visite Totali</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.visit_tracker.stats.unique_monuments}</div>
                <div class="stat-label">Monumenti Unici</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(self.visit_tracker.stats.countries_visited)}</div>
                <div class="stat-label">Paesi Esplorati</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.visit_tracker.stats.total_photos}</div>
                <div class="stat-label">Foto Scattate</div>
            </div>
        </div>
        
        <div class="monuments-list">
"""
        
        # Aggiungi monumenti
        visited_ids = set(visit.monument_id for visit in self.visit_tracker.visits)
        monuments_html = ""
        
        for monument_id, monument_data in self.monuments_db.items():
            is_visited = monument_id in visited_ids
            coords = monument_data.get('coordinates', {})
            
            if coords:
                maps_link = f"https://www.google.com/maps/search/?api=1&query={coords['latitude']},{coords['longitude']}"
            else:
                maps_link = f"https://www.google.com/maps/search/?api=1&query={monument_data.get('name', '')}"
            
            visit_info = ""
            if is_visited:
                visits = [v for v in self.visit_tracker.visits if v.monument_id == monument_id]
                visit_count = len(visits)
                first_visit = min(visits, key=lambda x: x.visit_date)
                visit_info = f"""
                <div class="monument-info">🎯 Visite: {visit_count}</div>
                <div class="monument-info">📅 Prima visita: {first_visit.visit_date.strftime('%d/%m/%Y')}</div>
                """
            
            badge = '<span class="visited-badge">✅ Visitato</span>' if is_visited else '<span class="not-visited-badge">⏳ Da visitare</span>'
            card_class = 'monument-card visited' if is_visited else 'monument-card'
            
            monuments_html += f"""
            <div class="{card_class}">
                <div class="monument-name">🏛️ {monument_data.get('name', 'Monumento')} {badge}</div>
                <div class="monument-info">📍 {monument_data.get('location', 'N/A')}</div>
                <div class="monument-info">🏗️ {monument_data.get('year_built', 'N/A')}</div>
                <div class="monument-info">🎨 {monument_data.get('style', 'N/A')}</div>
                {visit_info}
                <a href="{maps_link}" target="_blank" class="google-maps-link">📍 Vedi su Google Maps</a>
            </div>
            """
        
        # Parte finale dell'HTML
        html_end = """
        </div>
    </div>
    
    <script>
        // Animazione semplice al caricamento
        window.onload = function() {
            const cards = document.querySelectorAll('.monument-card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    card.style.transition = 'all 0.5s ease';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                }, index * 100);
            });
        };
    </script>
</body>
</html>
        """
        
        html_content = html_start + monuments_html + html_end
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.maps_dir, f"monument_visits_simple_{timestamp}.html")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def create_nearby_monuments_map(self, user_location: GPSCoordinate, 
                                   nearby_monuments: List[Dict]) -> str:
        """
        Crea una mappa con monumenti nelle vicinanze dell'utente.
        """
        try:
            import folium
        except ImportError:
            return self.create_simple_nearby_html_map(user_location, nearby_monuments)
        
        # Crea mappa centrata sulla posizione utente
        m = folium.Map(
            location=[user_location.latitude, user_location.longitude],
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Marcatore posizione utente
        folium.Marker(
            location=[user_location.latitude, user_location.longitude],
            popup="📍 La tua posizione",
            tooltip="Tu sei qui!",
            icon=folium.Icon(color='red', icon='user', prefix='fa')
        ).add_to(m)
        
        # Aggiungi monumenti vicini
        for monument in nearby_monuments:
            coords = monument.get('coordinates', {})
            if coords:
                # Verifica se il monumento è già stato visitato
                is_visited = self.visit_tracker.has_visited_monument(monument.get('id', ''), user_id=None)
                
                popup_html = f"""
                <div style="width:300px; font-family: Arial, sans-serif;">
                    <div style="background: linear-gradient(135deg, {'#FF9800' if not is_visited else '#4CAF50'}, {'#F57C00' if not is_visited else '#45a049'}); color: white; padding: 12px; margin: -10px -10px 15px -10px; border-radius: 8px 8px 0 0;">
                        <h3 style="margin: 0; font-size: 18px;">{'🏛️' if not is_visited else '✅'} {monument.get('name', 'Monumento')}</h3>
                        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 12px;">📍 {monument.get('distance_km', 'N/A')} km da te</p>
                    </div>
                    
                    <div style="padding: 5px 0;">
                        <p style="margin: 8px 0; color: #333;"><strong>📍 Località:</strong> {monument.get('location', 'N/A')}</p>
                        <p style="margin: 8px 0; color: #333;"><strong>🏗️ Costruito:</strong> {monument.get('year_built', 'N/A')}</p>
                        <p style="margin: 8px 0; color: #333;"><strong>🎨 Stile:</strong> {monument.get('style', 'N/A')}</p>
                    </div>
                    
                    <div style="background: {'#fff3e0' if not is_visited else '#e8f5e8'}; padding: 10px; border-radius: 5px; margin-top: 15px;">
                        <p style="margin: 0; color: {'#E65100' if not is_visited else '#2e7d32'}; font-size: 13px;">
                            {'🚗 Pianifica una visita! È abbastanza vicino per essere raggiunto.' if not is_visited else '🎉 Hai già visitato questo monumento!'}
                        </p>
                    </div>
                    
                    {monument.get('description', '')[:120] + '...' if monument.get('description') else ''}
                </div>
                """
                
                folium.Marker(
                    location=[coords['latitude'], coords['longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"🏛️ {monument.get('name', 'Monumento')} ({monument.get('distance_km', 'N/A')} km)",
                    icon=folium.Icon(color='blue', icon='camera', prefix='fa')
                ).add_to(m)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.maps_dir, f"nearby_monuments_{timestamp}.html")
        m.save(filename)
        
        return filename
    
    def create_simple_nearby_html_map(self, user_location: GPSCoordinate, 
                                     nearby_monuments: List[Dict]) -> str:
        """Fallback per mappa monumenti vicini."""
        # Implementazione simile a create_simple_html_map ma per monumenti vicini
        # ... codice semplificato per brevità
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.maps_dir, f"nearby_monuments_simple_{timestamp}.html")
        
        # Crea HTML semplificato (implementazione base)
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🗺️ Monumenti Nelle Vicinanze</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>📍 Monumenti Vicini alla Tua Posizione</h1>
    <p>Posizione: {user_location.latitude:.4f}, {user_location.longitude:.4f}</p>
    <ul>
        {"".join([f'<li>{m.get("name", "Monumento")} - {m.get("distance_km", "N/A")} km</li>' for m in nearby_monuments])}
    </ul>
</body>
</html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def export_map_data(self, output_format: str = 'json') -> str:
        """
        Esporta i dati delle visite in vari formati.
        
        Args:
            output_format: Formato di output ('json', 'csv', 'gpx')
            
        Returns:
            Path del file esportato
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format.lower() == 'json':
            return self._export_json(timestamp)
        elif output_format.lower() == 'csv':
            return self._export_csv(timestamp)
        elif output_format.lower() == 'gpx':
            return self._export_gpx(timestamp)
        else:
            raise ValueError(f"Formato non supportato: {output_format}")
    
    def _export_json(self, timestamp: str) -> str:
        """Esporta in formato JSON."""
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_visits': len(self.visit_tracker.visits),
            'unique_monuments': len(set(v.monument_id for v in self.visit_tracker.visits)),
            'statistics': self.visit_tracker.stats.to_dict(),
            'visits': [visit.to_dict() for visit in self.visit_tracker.visits],
            'monuments_database': self.monuments_db
        }
        
        filename = os.path.join(self.maps_dir, f"monument_visits_export_{timestamp}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def _export_csv(self, timestamp: str) -> str:
        """Esporta in formato CSV."""
        filename = os.path.join(self.maps_dir, f"monument_visits_export_{timestamp}.csv")
        
        try:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'monument_name', 'monument_id', 'location', 'visit_date',
                    'latitude', 'longitude', 'recognition_method', 
                    'confidence_score', 'user_notes', 'photo_path'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for visit in self.visit_tracker.visits:
                    monument_data = self.monuments_db.get(visit.monument_id, {})
                    row = {
                        'monument_name': visit.monument_name,
                        'monument_id': visit.monument_id,
                        'location': monument_data.get('location', 'N/A'),
                        'visit_date': visit.visit_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'latitude': visit.gps_coordinates.latitude if visit.gps_coordinates else '',
                        'longitude': visit.gps_coordinates.longitude if visit.gps_coordinates else '',
                        'recognition_method': visit.recognition_method,
                        'confidence_score': visit.confidence_score or '',
                        'user_notes': visit.user_notes,
                        'photo_path': visit.photo_path or ''
                    }
                    writer.writerow(row)
        except ImportError:
            # Fallback senza modulo csv
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('monument_name,visit_date,latitude,longitude\n')
                for visit in self.visit_tracker.visits:
                    coords = visit.gps_coordinates
                    f.write(f'"{visit.monument_name}",{visit.visit_date.strftime("%Y-%m-%d %H:%M:%S")}')
                    f.write(f',{coords.latitude if coords else ""},{coords.longitude if coords else ""}\n')
        
        return filename
    
    def _export_gpx(self, timestamp: str) -> str:
        """Esporta in formato GPX per GPS."""
        filename = os.path.join(self.maps_dir, f"monument_visits_export_{timestamp}.gpx")
        
        gpx_content = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Monument Recognizer">
  <metadata>
    <name>Monument Visits</name>
    <desc>Exported monument visits from Monument Recognizer</desc>
  </metadata>
'''
        
        # Aggiungi waypoint per ogni visita
        for visit in self.visit_tracker.visits:
            if visit.gps_coordinates:
                gpx_content += f'''  <wpt lat="{visit.gps_coordinates.latitude}" lon="{visit.gps_coordinates.longitude}">
    <name>{visit.monument_name}</name>
    <desc>Visited on {visit.visit_date.strftime('%Y-%m-%d %H:%M:%S')}</desc>
    <time>{visit.visit_date.isoformat()}Z</time>
  </wpt>
'''
        
        gpx_content += '</gpx>'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(gpx_content)
        
        return filename
    
    def create_shareable_map(self, title: str = "My Monument Journey") -> str:
        """
        Crea una mappa ottimizzata per la condivisione.
        """
        # Usa il metodo base ma con personalizzazioni per condivisione
        map_file = self.create_visited_monuments_map()
        
        # Leggi il file e personalizzalo
        with open(map_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Personalizza titolo e aggiungi informazioni
        personal_header = f'''
        <div style="position: absolute; top: 20px; left: 50%; transform: translateX(-50%); 
                    background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; 
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1); z-index: 1000; text-align: center;">
            <h2 style="margin: 0; color: #333;">{title}</h2>
            <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
                {len(self.visit_tracker.visits)} visite \u2022 {len(set(v.monument_id for v in self.visit_tracker.visits))} monumenti unici
            </p>
            <p style="margin: 5px 0 0 0; color: #888; font-size: 12px;">
                Generato con Monument Recognizer il {datetime.now().strftime('%d/%m/%Y')}
            </p>
        </div>
        '''
        
        # Inserisci header personalizzato
        html_content = html_content.replace('<body>', f'<body>{personal_header}')
        
        # Crea nuovo file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shareable_file = os.path.join(self.maps_dir, f"shareable_monument_map_{timestamp}.html")
        
        with open(shareable_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return shareable_file
    
    def open_map_in_browser(self, map_file: str) -> bool:
        """Apre la mappa nel browser predefinito."""
        try:
            abs_path = os.path.abspath(map_file)
            webbrowser.open(f'file://{abs_path}')
            return True
        except Exception as e:
            print(f"❌ Errore nell'aprire la mappa: {e}")
            return False
