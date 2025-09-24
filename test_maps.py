#!/usr/bin/env python3
"""
🗺️ Test Integrazione Mappe Interattive
Verifica che le mappe funzionino correttamente con il sistema utenti
"""

import os
import sys
import tempfile
import json
from datetime import datetime, date, timedelta

# Importazioni globali per i test
try:
    from user_system import UserSystem
    from visit_tracker import VisitTracker
    from monument_recognizer import MonumentRecognizer
    from map_generator import MapGenerator
    from gps_manager import GPSCoordinate
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Errore import globale: {e}")
    IMPORTS_OK = False

def test_map_generator_creation():
    """Test creazione MapGenerator."""
    if not IMPORTS_OK:
        return False
    
    try:
        # Crea database monumenti di test
        test_monuments_db = {
            "test_monument_1": {
                "name": "Test Monument 1",
                "location": "Test City",
                "year_built": "2000",
                "style": "Modern",
                "description": "A test monument for testing purposes",
                "coordinates": {
                    "latitude": 41.9028,
                    "longitude": 12.4964
                }
            },
            "test_monument_2": {
                "name": "Test Monument 2", 
                "location": "Another Test City",
                "year_built": "1800",
                "style": "Classical",
                "description": "Another test monument",
                "coordinates": {
                    "latitude": 48.8566,
                    "longitude": 2.3522
                }
            }
        }
        
        # Crea visit tracker di test
        visit_tracker = VisitTracker(user_id=999)
        
        # Aggiungi alcune visite di test
        visit_tracker.add_visit(
            monument_id="test_monument_1",
            monument_name="Test Monument 1",
            gps_coords=GPSCoordinate(41.9028, 12.4964),
            user_notes="Test visit",
            recognition_method="test"
        )
        
        visit_tracker.add_visit(
            monument_id="test_monument_2",
            monument_name="Test Monument 2",
            gps_coords=GPSCoordinate(48.8566, 2.3522),
            user_notes="Another test visit",
            recognition_method="test"
        )
        
        # Crea MapGenerator
        map_generator = MapGenerator(test_monuments_db, visit_tracker)
        print("✅ MapGenerator creato con successo")
        
        return True
    except Exception as e:
        print(f"❌ Errore creazione MapGenerator: {e}")
        return False

def test_map_generation():
    """Test generazione mappe."""
    if not IMPORTS_OK:
        return False
    
    try:
        # Setup come nel test precedente
        test_monuments_db = {
            "test_monument_1": {
                "name": "Test Monument 1",
                "location": "Rome, Italy",
                "year_built": "2000",
                "style": "Modern",
                "description": "A test monument in Rome",
                "coordinates": {
                    "latitude": 41.9028,
                    "longitude": 12.4964
                }
            }
        }
        
        visit_tracker = VisitTracker(user_id=998)
        visit_tracker.add_visit(
            monument_id="test_monument_1",
            monument_name="Test Monument 1",
            gps_coords=GPSCoordinate(41.9028, 12.4964),
            recognition_method="test"
        )
        
        map_generator = MapGenerator(test_monuments_db, visit_tracker)
        
        # Test generazione mappa base
        map_file = map_generator.create_visited_monuments_map()
        if os.path.exists(map_file):
            print(f"✅ Mappa base generata: {map_file}")
        else:
            print("❌ Mappa base non generata")
            return False
        
        # Test generazione mappa con filtri
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)
        
        filtered_map = map_generator.create_visited_monuments_map(
            start_date=yesterday,
            end_date=tomorrow,
            monument_styles=["Modern"]
        )
        
        if os.path.exists(filtered_map):
            print(f"✅ Mappa filtrata generata: {filtered_map}")
        else:
            print("❌ Mappa filtrata non generata")
            return False
        
        # Test mappa condivisibile
        shareable_map = map_generator.create_shareable_map("Test Journey")
        if os.path.exists(shareable_map):
            print(f"✅ Mappa condivisibile generata: {shareable_map}")
        else:
            print("❌ Mappa condivisibile non generata")
            return False
        
        # Cleanup
        for map_path in [map_file, filtered_map, shareable_map]:
            try:
                if os.path.exists(map_path):
                    os.remove(map_path)
            except:
                pass
        
        return True
    except Exception as e:
        print(f"❌ Errore generazione mappe: {e}")
        return False

def test_map_export():
    """Test esportazione dati mappe."""
    if not IMPORTS_OK:
        return False
    
    try:
        test_monuments_db = {
            "test_monument": {
                "name": "Export Test Monument",
                "location": "Test Location",
                "coordinates": {"latitude": 40.0, "longitude": 8.0}
            }
        }
        
        visit_tracker = VisitTracker(user_id=997)
        visit_tracker.add_visit(
            monument_id="test_monument",
            monument_name="Export Test Monument",
            gps_coords=GPSCoordinate(40.0, 8.0),
            recognition_method="test"
        )
        
        map_generator = MapGenerator(test_monuments_db, visit_tracker)
        
        # Test esportazione JSON
        json_file = map_generator.export_map_data('json')
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'visits' in data and 'total_visits' in data:
                    print("✅ Esportazione JSON riuscita")
                else:
                    print("❌ JSON esportato ma formato non valido")
                    return False
        else:
            print("❌ Esportazione JSON fallita")
            return False
        
        # Test esportazione CSV
        csv_file = map_generator.export_map_data('csv')
        if os.path.exists(csv_file):
            with open(csv_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'monument_name' in content and 'visit_date' in content:
                    print("✅ Esportazione CSV riuscita")
                else:
                    print("❌ CSV esportato ma formato non valido")
                    return False
        else:
            print("❌ Esportazione CSV fallita")
            return False
        
        # Test esportazione GPX
        gpx_file = map_generator.export_map_data('gpx')
        if os.path.exists(gpx_file):
            with open(gpx_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '<gpx' in content and '<wpt' in content:
                    print("✅ Esportazione GPX riuscita")
                else:
                    print("❌ GPX esportato ma formato non valido")
                    return False
        else:
            print("❌ Esportazione GPX fallita")
            return False
        
        # Cleanup
        for file_path in [json_file, csv_file, gpx_file]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        
        return True
    except Exception as e:
        print(f"❌ Errore esportazione: {e}")
        return False

def test_nearby_monuments_map():
    """Test mappa monumenti vicini."""
    if not IMPORTS_OK:
        return False
    
    try:
        test_monuments_db = {
            "nearby_monument": {
                "name": "Nearby Monument",
                "location": "Close Location",
                "coordinates": {"latitude": 41.9, "longitude": 12.5}
            }
        }
        
        visit_tracker = VisitTracker(user_id=996)
        map_generator = MapGenerator(test_monuments_db, visit_tracker)
        
        user_position = GPSCoordinate(41.8, 12.4)
        nearby_monuments = [{
            "name": "Nearby Monument",
            "distance_km": 15.2,
            "location": "Close Location",
            "coordinates": {"latitude": 41.9, "longitude": 12.5}
        }]
        
        nearby_map = map_generator.create_nearby_monuments_map(
            user_position, nearby_monuments
        )
        
        if os.path.exists(nearby_map):
            print("✅ Mappa monumenti vicini generata")
            os.remove(nearby_map)
            return True
        else:
            print("❌ Mappa monumenti vicini non generata")
            return False
            
    except Exception as e:
        print(f"❌ Errore mappa monumenti vicini: {e}")
        return False

def test_integration_with_user_system():
    """Test integrazione con sistema utenti."""
    if not IMPORTS_OK:
        return False
    
    try:
        # Crea sistema utenti temporaneo
        user_system = UserSystem("test_map_users.db")
        
        # Registra utente di test
        success, message, user = user_system.register_user(
            "map_test_user", "test@maps.com", "Map Test User", "TestPassword123!"
        )
        
        if not success:
            print(f"❌ Registrazione utente fallita: {message}")
            return False
        
        # Login
        success, message, user = user_system.login_user("map_test_user", "TestPassword123!")
        if not success:
            print(f"❌ Login utente fallito: {message}")
            return False
        
        # Crea recognizer con sistema utenti
        recognizer = MonumentRecognizer(user_system)
        
        # Test che il visit tracker sia associato all'utente
        if recognizer.visit_tracker.user_id == user.user_id:
            print("✅ Visit tracker correttamente associato all'utente")
        else:
            print("❌ Visit tracker non associato correttamente")
            return False
        
        # Test creazione mappa con dati utente
        map_generator = MapGenerator(
            recognizer.monuments_db,
            recognizer.visit_tracker
        )
        
        # Aggiungi una visita di test
        recognizer.visit_tracker.add_visit(
            monument_id="user_test_monument",
            monument_name="User Test Monument",
            gps_coords=GPSCoordinate(45.0, 9.0),
            user_id=user.user_id,
            recognition_method="user_test"
        )
        
        # Genera mappa
        user_map = map_generator.create_visited_monuments_map()
        if os.path.exists(user_map):
            print("✅ Mappa utente generata correttamente")
            os.remove(user_map)
        else:
            print("❌ Mappa utente non generata")
            return False
        
        # Cleanup
        if os.path.exists("test_map_users.db"):
            os.remove("test_map_users.db")
        
        # Cleanup visit tracker files
        for pattern in ["monument_visits_user_", "visit_photos_user_"]:
            for file in os.listdir("."):
                if file.startswith(pattern):
                    try:
                        if os.path.isfile(file):
                            os.remove(file)
                        elif os.path.isdir(file):
                            os.rmdir(file)
                    except:
                        pass
        
        return True
    except Exception as e:
        print(f"❌ Errore integrazione sistema utenti: {e}")
        return False

def cleanup_test_files():
    """Pulisce i file di test rimasti."""
    try:
        # Pulisce directory mappe generate
        if os.path.exists("generated_maps"):
            for file in os.listdir("generated_maps"):
                file_path = os.path.join("generated_maps", file)
                if file.startswith("monument_visits_") or file.startswith("shareable_"):
                    try:
                        os.remove(file_path)
                    except:
                        pass
        
        # Pulisce file database di test
        for file in os.listdir("."):
            if file.startswith("monument_visits_user_") and file.endswith(".json"):
                try:
                    os.remove(file)
                except:
                    pass
        
        print("🧹 File di test puliti")
    except Exception as e:
        print(f"⚠️ Errore pulizia: {e}")

def main():
    """Esegue tutti i test delle mappe."""
    print("🗺️ TESTING INTEGRAZIONE MAPPE INTERATTIVE")
    print("=" * 50)
    
    tests = [
        ("Creazione MapGenerator", test_map_generator_creation),
        ("Generazione Mappe", test_map_generation),
        ("Esportazione Dati", test_map_export),
        ("Mappa Monumenti Vicini", test_nearby_monuments_map),
        ("Integrazione Sistema Utenti", test_integration_with_user_system)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔬 Test: {name}")
        print("-" * 30)
        result = test_func()
        results.append((name, result))
    
    print("\n📊 RISULTATI FINALI")
    print("=" * 50)
    
    success_count = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<25} {status}")
        if result:
            success_count += 1
    
    print(f"\n🎯 Test riusciti: {success_count}/{len(tests)}")
    
    # Cleanup
    cleanup_test_files()
    
    if success_count == len(tests):
        print("🎉 TUTTI I TEST DELLE MAPPE SONO RIUSCITI!")
        print("🗺️ L'integrazione delle mappe interattive è completa!")
    else:
        print("⚠️ Alcuni test sono falliti. Controlla i log sopra.")
    
    return success_count == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
