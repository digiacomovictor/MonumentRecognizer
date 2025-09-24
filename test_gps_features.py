#!/usr/bin/env python3
"""
🧪 Test per le funzionalità GPS e Mapping
Testa tutti i componenti GPS, visite e mappe del Monument Recognizer
"""

import os
import sys
import json
from pathlib import Path

def test_gps_manager():
    """Testa il GPS Manager."""
    print("🔍 Test GPS Manager...")
    
    try:
        from gps_manager import GPSManager, GPSCoordinate
        
        gps = GPSManager()
        
        # Test coordinate
        coord1 = GPSCoordinate(48.8584, 2.2945)  # Torre Eiffel
        coord2 = GPSCoordinate(41.8902, 12.4922)  # Colosseo
        
        distance = gps.calculate_distance(coord1, coord2)
        print(f"   📏 Distanza Torre Eiffel - Colosseo: {distance/1000:.1f} km")
        
        # Test aggiornamento posizione
        if gps.update_position():
            print(f"   📍 Posizione corrente: {gps.get_location_string()}")
        else:
            print("   ⚠️  Posizione non disponibile (normale senza GPS/internet)")
        
        print("   ✅ GPS Manager funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore GPS Manager: {e}")
        return False

def test_visit_tracker():
    """Testa il Visit Tracker."""
    print("\n🔍 Test Visit Tracker...")
    
    try:
        from visit_tracker import VisitTracker, MonumentVisit
        from gps_manager import GPSCoordinate
        
        # Crea tracker temporaneo
        tracker = VisitTracker()
        original_file = tracker.visits_file
        tracker.visits_file = "test_visits.json"
        
        # Test aggiunta visita
        coord = GPSCoordinate(48.8584, 2.2945)
        visit = tracker.add_visit(
            monument_id="eiffel_tower",
            monument_name="Torre Eiffel",
            gps_coords=coord,
            recognition_method="test",
            confidence_score=95.0
        )
        
        print(f"   ✅ Visita aggiunta: {visit.monument_name}")
        
        # Test statistiche
        stats = tracker.get_visit_summary()
        print(f"   📊 Statistiche generate: {len(stats)} caratteri")
        
        # Test achievements
        achievements = tracker.get_achievement_progress()
        completed = sum(1 for a in achievements.values() if a['completed'])
        print(f"   🏆 Achievement completati: {completed}/{len(achievements)}")
        
        # Pulisci file di test
        if os.path.exists(tracker.visits_file):
            os.remove(tracker.visits_file)
        
        print("   ✅ Visit Tracker funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore Visit Tracker: {e}")
        return False

def test_map_generator():
    """Testa il Map Generator."""
    print("\n🔍 Test Map Generator...")
    
    try:
        from map_generator import MapGenerator
        from visit_tracker import VisitTracker
        from gps_manager import GPSCoordinate
        
        # Carica database monumenti
        with open('monuments_db.json', 'r', encoding='utf-8') as f:
            monuments_db = json.load(f)
        
        # Crea tracker e generator
        tracker = VisitTracker()
        tracker.visits_file = "test_visits.json"
        
        # Aggiungi visita di test
        coord = GPSCoordinate(48.8584, 2.2945)
        tracker.add_visit(
            monument_id="eiffel_tower",
            monument_name="Torre Eiffel",
            gps_coords=coord,
            recognition_method="test"
        )
        
        generator = MapGenerator(monuments_db, tracker)
        
        # Test generazione mappa
        map_file = generator.create_simple_html_map()
        
        if os.path.exists(map_file):
            print(f"   ✅ Mappa generata: {map_file}")
            file_size = os.path.getsize(map_file)
            print(f"   📊 Dimensione file: {file_size} bytes")
            
            # Pulisci file di test
            os.remove(map_file)
            if os.path.exists(tracker.visits_file):
                os.remove(tracker.visits_file)
        else:
            print("   ❌ Mappa non generata")
            return False
        
        print("   ✅ Map Generator funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore Map Generator: {e}")
        return False

def test_monument_recognizer_integration():
    """Testa l'integrazione GPS nel riconoscitore."""
    print("\n🔍 Test integrazione Monument Recognizer...")
    
    try:
        from monument_recognizer import MonumentRecognizer
        
        recognizer = MonumentRecognizer()
        
        # Test funzioni GPS
        nearby = recognizer.get_nearby_monuments(radius_km=1000)
        print(f"   🗺️  Monumenti nelle vicinanze: {len(nearby)}")
        
        # Test statistiche
        stats = recognizer.get_visit_stats()
        print(f"   📈 Statistiche visite: {len(stats)} caratteri")
        
        print("   ✅ Integrazione GPS funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore integrazione: {e}")
        return False

def test_database_coordinates():
    """Testa che tutti i monumenti abbiano coordinate GPS."""
    print("\n🔍 Test database coordinate...")
    
    try:
        with open('monuments_db.json', 'r', encoding='utf-8') as f:
            monuments_db = json.load(f)
        
        total_monuments = len(monuments_db)
        with_coordinates = 0
        
        for monument_id, monument_data in monuments_db.items():
            if 'coordinates' in monument_data:
                coords = monument_data['coordinates']
                if 'latitude' in coords and 'longitude' in coords:
                    with_coordinates += 1
                    print(f"   📍 {monument_data.get('name', monument_id)}: ✅")
                else:
                    print(f"   📍 {monument_data.get('name', monument_id)}: ❌ Coordinate incomplete")
            else:
                print(f"   📍 {monument_data.get('name', monument_id)}: ❌ No coordinates")
        
        print(f"   📊 Monumenti con coordinate: {with_coordinates}/{total_monuments}")
        
        if with_coordinates == total_monuments:
            print("   ✅ Tutti i monumenti hanno coordinate GPS")
            return True
        else:
            print("   ⚠️  Alcuni monumenti mancano di coordinate")
            return False
        
    except Exception as e:
        print(f"   ❌ Errore lettura database: {e}")
        return False

def main():
    """Esegue tutti i test."""
    print("=" * 60)
    print("🧪 TEST FUNZIONALITÀ GPS E MAPPING")
    print("   Monument Recognizer v2.0")
    print("=" * 60)
    
    tests = [
        ("Database Coordinate", test_database_coordinates),
        ("GPS Manager", test_gps_manager),
        ("Visit Tracker", test_visit_tracker),
        ("Map Generator", test_map_generator),
        ("Integrazione GPS", test_monument_recognizer_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 Errore critico in {test_name}: {e}")
            results.append((test_name, False))
    
    # Riassunto
    print("\n" + "=" * 60)
    print("📊 RIASSUNTO TEST")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Test passati: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 TUTTI I TEST SONO PASSATI!")
        print("🚀 Le funzionalità GPS e mapping sono pronte!")
    else:
        print("⚠️  Alcuni test sono falliti. Controlla i messaggi sopra.")
    
    print("\n💡 Per testare manualmente:")
    print("   • Esegui: .\\avvia_app.bat")
    print("   • Riconosci un monumento")
    print("   • Controlla se la posizione GPS viene rilevata")
    print("   • Verifica la registrazione delle visite")

if __name__ == "__main__":
    main()
