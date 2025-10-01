#!/usr/bin/env python3
"""
Script per Applicare Patch Android-Compatibili
Sostituisce temporaneamente file con dipendenze problematiche
"""

import os
import shutil
from pathlib import Path

def backup_file(file_path: str):
    """Crea backup di un file aggiungendo .desktop_backup"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.desktop_backup"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup creato: {backup_path}")
        return True
    return False

def restore_file(file_path: str):
    """Ripristina un file dal backup"""
    backup_path = f"{file_path}.desktop_backup"
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        print(f"✅ File ripristinato: {file_path}")
        return True
    return False

def create_android_stub_files():
    """Crea file stub Android-compatibili per sostituire quelli problematici"""
    
    # Dashboard Manager Android-compatible (rimuove matplotlib/plotly)
    dashboard_android = '''"""
Dashboard Manager Android-Compatible
Rimuove dipendenze matplotlib, plotly, pandas
"""
import json
from typing import Dict, List
from datetime import datetime

class DashboardManager:
    def __init__(self):
        self.stats = {}
    
    def generate_charts_data(self, visit_data: List[Dict]) -> Dict:
        """Genera dati per chart Android-compatibili"""
        if not visit_data:
            return {"message": "Nessuna visita registrata"}
        
        # Conta visite per paese
        countries = {}
        cities = {}
        monthly_visits = {}
        
        for visit in visit_data:
            country = visit.get('country', 'Sconosciuto')
            city = visit.get('city', 'Sconosciuta')
            date = visit.get('date', datetime.now().isoformat())
            
            countries[country] = countries.get(country, 0) + 1
            cities[city] = cities.get(city, 0) + 1
            
            month_key = date[:7]  # YYYY-MM
            monthly_visits[month_key] = monthly_visits.get(month_key, 0) + 1
        
        return {
            'countries_count': countries,
            'cities_count': cities,
            'monthly_visits': monthly_visits,
            'total_visits': len(visit_data),
            'android_mode': True
        }
    
    def create_text_summary(self, data: Dict) -> str:
        """Crea riassunto testuale delle statistiche"""
        summary = "📊 STATISTICHE VISITE\\n\\n"
        
        if data.get('total_visits', 0) > 0:
            summary += f"🏛️ Visite totali: {data['total_visits']}\\n"
            
            if 'countries_count' in data:
                top_country = max(data['countries_count'].items(), key=lambda x: x[1])
                summary += f"🌍 Paese più visitato: {top_country[0]} ({top_country[1]} visite)\\n"
            
            if 'cities_count' in data:
                top_city = max(data['cities_count'].items(), key=lambda x: x[1])
                summary += f"🏙️ Città più visitata: {top_city[0]} ({top_city[1]} visite)\\n"
        else:
            summary += "Nessuna visita registrata ancora.\\n"
        
        summary += "\\n📱 Modalità Android - Grafici non disponibili"
        return summary
'''
    
    # Camera Interface Android-compatible (rimuove OpenCV)
    camera_android = '''"""
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
'''
    
    # Map Generator Android-compatible (rimuove folium)
    map_android = '''"""
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
        
        summary = f"🗺️ MAPPA DELLE VISITE\\n\\n"
        summary += f"📍 Punti totali: {map_data['total_points']}\\n"
        summary += f"🌍 Paesi visitati: {map_data['countries_count']}\\n"
        summary += f"🏙️ Città visitate: {map_data['cities_count']}\\n\\n"
        
        summary += "🌍 PAESI:\\n"
        for country in sorted(map_data['countries_list']):
            summary += f"  • {country}\\n"
        
        summary += "\\n🏙️ CITTÀ:\\n"
        for city in sorted(map_data['cities_list']):
            summary += f"  • {city}\\n"
        
        summary += "\\n📱 Modalità Android - Mappa interattiva non disponibile"
        return summary
    
    def get_coordinates_list(self, map_data: Dict) -> List[Tuple[float, float, str]]:
        """Restituisce lista di coordinate per uso esterno"""
        coordinates = []
        for point in map_data.get('points', []):
            coordinates.append((point['lat'], point['lon'], point['name']))
        return coordinates
'''
    
    return {
        'dashboard_manager.py': dashboard_android,
        'camera_interface.py': camera_android,
        'map_generator.py': map_android
    }

def apply_android_patches():
    """Applica le patch Android sostituendo i file problematici"""
    print("🔧 === APPLICANDO PATCH ANDROID ===")
    
    android_files = create_android_stub_files()
    
    patched_files = []
    
    for filename, content in android_files.items():
        if os.path.exists(filename):
            # Crea backup
            if backup_file(filename):
                # Sostituisce con versione Android
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Patch applicata: {filename}")
                    patched_files.append(filename)
                except Exception as e:
                    print(f"❌ Errore nella patch di {filename}: {e}")
                    # Ripristina backup in caso di errore
                    restore_file(filename)
        else:
            print(f"⚠️ File non trovato: {filename}")
    
    print(f"\\n🎯 Patch applicate a {len(patched_files)} file")
    return patched_files

def restore_desktop_files():
    """Ripristina i file originali dai backup"""
    print("🔄 === RIPRISTINANDO FILE ORIGINALI ===")
    
    files_to_restore = [
        'dashboard_manager.py',
        'camera_interface.py', 
        'map_generator.py'
    ]
    
    restored_files = []
    
    for filename in files_to_restore:
        if restore_file(filename):
            restored_files.append(filename)
    
    print(f"\\n🎯 File ripristinati: {len(restored_files)}")
    return restored_files

def main():
    """Funzione principale"""
    print("🏛️ === ANDROID PATCHES MANAGER ===\\n")
    
    print("Cosa vuoi fare?")
    print("1. 🔧 Applica patch Android (per build)")
    print("2. 🔄 Ripristina file originali (per desktop)")
    print("3. 📊 Mostra stato backup")
    
    try:
        choice = input("\\nScegli opzione (1-3): ").strip()
        
        if choice == '1':
            patched = apply_android_patches()
            print("\\n🚀 Ora puoi eseguire la build Android!")
            print("💡 Ricorda di ripristinare i file originali dopo la build")
            
        elif choice == '2':
            restored = restore_desktop_files()
            print("\\n💻 File desktop ripristinati!")
            
        elif choice == '3':
            print("\\n📊 === STATO BACKUP ===")
            backup_files = [
                'dashboard_manager.py.desktop_backup',
                'camera_interface.py.desktop_backup',
                'map_generator.py.desktop_backup'
            ]
            
            for backup_file in backup_files:
                if os.path.exists(backup_file):
                    print(f"✅ {backup_file} (esistente)")
                else:
                    print(f"❌ {backup_file} (mancante)")
        else:
            print("❌ Opzione non valida")
            
    except KeyboardInterrupt:
        print("\\n👋 Uscita dall'utente")
    except Exception as e:
        print(f"\\n❌ Errore: {e}")

if __name__ == "__main__":
    main()
