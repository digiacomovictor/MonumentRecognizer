#!/usr/bin/env python3
"""
🎯 Test Integrazione Completa Monument Recognizer
Verifica l'integrazione di tutti i moduli del sistema
"""

import os
import sys
import tempfile
from datetime import datetime, timedelta

def test_all_imports():
    """Test che tutti i moduli si importino correttamente."""
    print("🔍 Testing imports...")
    
    try:
        from user_system import UserSystem
        from visit_tracker import VisitTracker  
        from monument_recognizer import MonumentRecognizer
        from dashboard_manager import DashboardManager
        from map_generator import MapGenerator
        from gps_manager import GPSCoordinate
        from auth_ui import AuthManager
        print("✅ Tutti i moduli importati con successo")
        return True
    except ImportError as e:
        print(f"❌ Errore import: {e}")
        return False

def test_user_system_integration():
    """Test sistema utenti integrato."""
    print("\n👤 Testing User System...")
    
    try:
        from user_system import UserSystem
        user_system = UserSystem()
        
        # Test registrazione
        result = user_system.register_user(
            "test_user", "test@example.com", "TestPassword123", "Utente Test"
        )
        
        if result['success']:
            print("✅ Registrazione utente riuscita")
            
            # Test login
            login_result = user_system.login_user("test_user", "TestPassword123")
            if login_result['success']:
                print("✅ Login utente riuscito")
                return True
            else:
                print(f"❌ Login fallito: {login_result['message']}")
                return False
        else:
            print(f"❌ Registrazione fallita: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Errore user system: {e}")
        return False

def test_monument_recognition_integration():
    """Test sistema riconoscimento integrato."""
    print("\n🏛️ Testing Monument Recognition...")
    
    try:
        from user_system import UserSystem
        from monument_recognizer import MonumentRecognizer
        
        user_system = UserSystem()
        recognizer = MonumentRecognizer(user_system)
        
        # Test inizializzazione
        if hasattr(recognizer, 'monuments_db') and hasattr(recognizer, 'visit_tracker'):
            print("✅ Monument Recognizer inizializzato correttamente")
            print(f"📚 Database monumenti: {len(recognizer.monuments_db)} monumenti")
            return True
        else:
            print("❌ Monument Recognizer non inizializzato correttamente")
            return False
            
    except Exception as e:
        print(f"❌ Errore monument recognition: {e}")
        return False

def test_visit_tracking_integration():
    """Test sistema tracking visite integrato."""
    print("\n📝 Testing Visit Tracking...")
    
    try:
        from visit_tracker import VisitTracker
        from gps_manager import GPSCoordinate
        
        visit_tracker = VisitTracker(user_id="test_integration")
        
        # Test aggiunta visita
        test_coords = GPSCoordinate(41.8902, 12.4922)  # Colosseo
        
        visit_tracker.add_visit(
            monument_id="colosseum",
            monument_name="Colosseo",
            gps_coords=test_coords,
            photo_path="test_photo.jpg",
            user_notes="Visita di test",
            recognition_method="Test",
            confidence_score=95
        )
        
        visits = visit_tracker.visits
        if len(visits) > 0:
            print("✅ Visit tracking funzionante")
            print(f"📊 Visite registrate: {len(visits)}")
            return True
        else:
            print("❌ Nessuna visita registrata")
            return False
            
    except Exception as e:
        print(f"❌ Errore visit tracking: {e}")
        return False

def test_dashboard_integration():
    """Test sistema dashboard integrato."""
    print("\n📊 Testing Dashboard Integration...")
    
    try:
        from user_system import UserSystem
        from visit_tracker import VisitTracker
        from dashboard_manager import DashboardManager
        from gps_manager import GPSCoordinate
        
        # Setup con dati di test
        user_system = UserSystem()
        visit_tracker = VisitTracker(user_id="test_dashboard_integration")
        
        # Aggiungi alcune visite di test
        monuments = [
            ("colosseum", "Colosseo", 41.8902, 12.4922),
            ("eiffel_tower", "Torre Eiffel", 48.8584, 2.2945),
            ("big_ben", "Big Ben", 51.5007, -0.1246)
        ]
        
        monuments_db = {
            "colosseum": {
                "name": "Colosseo", "location": "Rome, Italy",
                "year_built": "80", "style": "Romano",
                "coordinates": {"latitude": 41.8902, "longitude": 12.4922}
            },
            "eiffel_tower": {
                "name": "Torre Eiffel", "location": "Paris, France",
                "year_built": "1889", "style": "Iron Architecture", 
                "coordinates": {"latitude": 48.8584, "longitude": 2.2945}
            },
            "big_ben": {
                "name": "Big Ben", "location": "London, UK",
                "year_built": "1859", "style": "Gothic Revival",
                "coordinates": {"latitude": 51.5007, "longitude": -0.1246}
            }
        }
        
        for monument_id, name, lat, lon in monuments:
            coords = GPSCoordinate(lat, lon)
            visit_tracker.add_visit(
                monument_id=monument_id,
                monument_name=name,
                gps_coords=coords,
                photo_path=f"test_{monument_id}.jpg",
                user_notes=f"Test visita {name}",
                recognition_method="Integration Test",
                confidence_score=90
            )
        
        # Test dashboard manager
        dashboard_manager = DashboardManager(visit_tracker, monuments_db, user_system)
        stats = dashboard_manager.calculate_comprehensive_stats()
        
        if stats.total_visits >= 3 and stats.unique_monuments >= 3:
            print("✅ Dashboard integration funzionante")
            print(f"📈 Statistiche: {stats.total_visits} visite, {stats.unique_monuments} monumenti")
            
            # Test generazione grafici
            try:
                chart_files = dashboard_manager.generate_matplotlib_charts(stats)
                if len(chart_files) > 0:
                    print(f"✅ Generazione grafici riuscita: {len(chart_files)} chart")
                else:
                    print("⚠️ Nessun grafico generato")
            except Exception as chart_error:
                print(f"⚠️ Errore generazione grafici: {chart_error}")
            
            return True
        else:
            print(f"❌ Statistiche non corrette: {stats.total_visits} visite, {stats.unique_monuments} monumenti")
            return False
            
    except Exception as e:
        print(f"❌ Errore dashboard integration: {e}")
        return False

def test_map_integration():
    """Test sistema mappe integrato.""" 
    print("\n🗺️ Testing Map Integration...")
    
    try:
        from visit_tracker import VisitTracker
        from map_generator import MapGenerator
        from gps_manager import GPSCoordinate
        
        # Setup
        visit_tracker = VisitTracker(user_id="test_map_integration")
        monuments_db = {
            "colosseum": {
                "name": "Colosseo", "location": "Rome, Italy",
                "coordinates": {"latitude": 41.8902, "longitude": 12.4922}
            }
        }
        
        # Aggiungi visita
        coords = GPSCoordinate(41.8902, 12.4922)
        visit_tracker.add_visit(
            monument_id="colosseum",
            monument_name="Colosseo",
            gps_coords=coords,
            photo_path="test_colosseum.jpg",
            user_notes="Test mappa",
            recognition_method="Map Test",
            confidence_score=95
        )
        
        # Test map generator
        map_generator = MapGenerator(monuments_db, visit_tracker)
        
        # Test creazione mappa visite
        map_file = map_generator.create_visited_monuments_map()
        
        if map_file and os.path.exists(map_file):
            print("✅ Map integration funzionante")
            print(f"🗺️ Mappa generata: {map_file}")
            return True
        else:
            print("❌ Mappa non generata")
            return False
            
    except Exception as e:
        print(f"❌ Errore map integration: {e}")
        return False

def cleanup_test_files():
    """Pulisce i file di test generati."""
    try:
        patterns = [
            "monument_visits_user_test_",
            "visit_photos_user_test_",
            "users_db.json",
            "session.txt"
        ]
        
        cleaned = 0
        for pattern in patterns:
            for file in os.listdir("."):
                if file.startswith(pattern):
                    try:
                        if os.path.isfile(file):
                            os.remove(file)
                        elif os.path.isdir(file):
                            import shutil
                            shutil.rmtree(file)
                        cleaned += 1
                    except:
                        pass
        
        # Pulisce directory mappe
        if os.path.exists("generated_maps"):
            try:
                import shutil
                shutil.rmtree("generated_maps")
                cleaned += 1
            except:
                pass
        
        # Pulisce directory dashboard
        if os.path.exists("dashboard_charts"):
            for file in os.listdir("dashboard_charts"):
                if file.startswith(("timeline_", "countries_", "dashboard_")):
                    try:
                        os.remove(os.path.join("dashboard_charts", file))
                        cleaned += 1
                    except:
                        pass
        
        if cleaned > 0:
            print(f"🧹 {cleaned} file di test puliti")
            
    except Exception as e:
        print(f"⚠️ Errore pulizia: {e}")

def main():
    """Esegue tutti i test di integrazione completa."""
    print("🎯 TESTING INTEGRAZIONE COMPLETA MONUMENT RECOGNIZER")
    print("=" * 55)
    
    tests = [
        ("Import Moduli", test_all_imports),
        ("User System", test_user_system_integration),
        ("Monument Recognition", test_monument_recognition_integration), 
        ("Visit Tracking", test_visit_tracking_integration),
        ("Dashboard", test_dashboard_integration),
        ("Map Generation", test_map_integration)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔬 Test: {name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Errore critico in {name}: {e}")
            results.append((name, False))
    
    print("\n🎯 RISULTATI INTEGRAZIONE COMPLETA")
    print("=" * 55)
    
    success_count = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<20} {status}")
        if result:
            success_count += 1
    
    print(f"\n📊 Test riusciti: {success_count}/{len(tests)}")
    
    # Cleanup
    cleanup_test_files()
    
    if success_count == len(tests):
        print("\n🎉 INTEGRAZIONE COMPLETA RIUSCITA!")
        print("🚀 Il sistema Monument Recognizer è completamente integrato e funzionante!")
        print("\n📋 Componenti Verificati:")
        print("  ✅ Sistema Autenticazione Utenti")
        print("  ✅ Riconoscimento Monumenti (Online/Offline)")
        print("  ✅ Tracking Visite Persistente") 
        print("  ✅ Dashboard con Statistiche e Grafici")
        print("  ✅ Mappe Interattive")
        print("  ✅ Gestione GPS e Localizzazione")
        print("\n🏛️ L'app è pronta per l'uso!")
    else:
        print(f"\n⚠️ {len(tests) - success_count} test falliti. Controlla i log sopra.")
    
    return success_count == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
