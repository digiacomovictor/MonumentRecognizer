#!/usr/bin/env python3
"""
🧪 Test di integrazione del sistema autenticazione
Verifica che tutte le componenti funzionino insieme
"""

import os
import sys
from pathlib import Path

# Importazioni globali per i test
try:
    from user_system import UserSystem
    from visit_tracker import VisitTracker
    from monument_recognizer import MonumentRecognizer
    from auth_ui import AuthManager
    from gps_manager import GPSManager
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Errore import globale: {e}")
    IMPORTS_OK = False

def test_imports():
    """Test che tutte le importazioni funzionino."""
    if IMPORTS_OK:
        print("✅ Tutte le importazioni riuscite")
        return True
    else:
        print("❌ Importazioni fallite")
        return False

def test_user_system():
    """Test del sistema utenti."""
    try:
        # Crea sistema utenti
        user_system = UserSystem("test_users.db")
        
        # Test registrazione
        success, message, user = user_system.register_user(
            username="test_user",
            email="test@example.com", 
            full_name="Test User",
            password="TestPassword123!"
        )
        
        if success:
            print(f"✅ Registrazione test utente: {user.full_name}")
        else:
            print(f"⚠️  Registrazione: {message}")
        
        # Test login
        success, message, user = user_system.login_user("test_user", "TestPassword123!")
        if success:
            print(f"✅ Login test utente: {user.full_name}")
        else:
            print(f"❌ Login fallito: {message}")
            return False
            
        # Test logout
        user_system.logout_user()
        print("✅ Logout completato")
        
        # Cleanup
        if os.path.exists("test_users.db"):
            os.remove("test_users.db")
        
        return True
    except Exception as e:
        print(f"❌ Errore test user system: {e}")
        return False

def test_visit_tracker():
    """Test del visit tracker."""
    try:
        # Test con utente
        tracker_user = VisitTracker(user_id=1)
        
        # Aggiungi visita test
        visit = tracker_user.add_visit(
            monument_id="test_monument",
            monument_name="Test Monument",
            user_notes="Test visit",
            recognition_method="test"
        )
        
        print(f"✅ Visita utente aggiunta: {visit.monument_name}")
        
        # Test con ospite
        tracker_guest = VisitTracker()
        visit_guest = tracker_guest.add_visit(
            monument_id="test_monument_guest",
            monument_name="Test Monument Guest",
            user_notes="Guest visit"
        )
        
        print(f"✅ Visita ospite aggiunta: {visit_guest.monument_name}")
        
        # Cleanup
        for file in ["monument_visits_user_1.json", "monument_visits_guest.json"]:
            if os.path.exists(file):
                os.remove(file)
        
        for dir in ["visit_photos_user_1", "visit_photos_guest"]:
            if os.path.exists(dir):
                os.rmdir(dir)
        
        return True
    except Exception as e:
        print(f"❌ Errore test visit tracker: {e}")
        return False

def test_monument_recognizer():
    """Test del monument recognizer."""
    try:
        # Test senza utente
        recognizer_guest = MonumentRecognizer()
        print("✅ Recognizer ospite creato")
        
        # Test con user system
        user_system = UserSystem("test_users_rec.db")
        user_system.register_user("test_rec", "test_rec@example.com", "Test Recognizer", "TestPassword123!")
        user_system.login_user("test_rec", "TestPassword123!")
        
        recognizer_user = MonumentRecognizer(user_system)
        print("✅ Recognizer utente creato")
        
        # Test aggiornamento contesto
        recognizer_guest.update_user_context(user_system)
        print("✅ Contesto utente aggiornato")
        
        # Cleanup
        if os.path.exists("test_users_rec.db"):
            os.remove("test_users_rec.db")
        
        return True
    except Exception as e:
        print(f"❌ Errore test monument recognizer: {e}")
        return False

def test_gps_manager():
    """Test del GPS manager."""
    try:
        gps = GPSManager()
        print("✅ GPS Manager creato")
        
        # Test posizione IP
        position = gps.get_location_via_ip()
        if position:
            print(f"✅ Posizione IP ottenuta: {position.latitude:.4f}, {position.longitude:.4f}")
        else:
            print("⚠️  Posizione IP non disponibile")
        
        # Cleanup cache
        if os.path.exists("user_position_cache.json"):
            os.remove("user_position_cache.json")
            
        return True
    except Exception as e:
        print(f"❌ Errore test GPS: {e}")
        return False

def main():
    """Esegue tutti i test."""
    print("🧪 TESTING INTEGRAZIONE SISTEMA AUTENTICAZIONE")
    print("=" * 50)
    
    tests = [
        ("Importazioni", test_imports),
        ("Sistema Utenti", test_user_system), 
        ("Visit Tracker", test_visit_tracker),
        ("Monument Recognizer", test_monument_recognizer),
        ("GPS Manager", test_gps_manager)
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
        print(f"{name:<20} {status}")
        if result:
            success_count += 1
    
    print(f"\n🎯 Test riusciti: {success_count}/{len(tests)}")
    
    if success_count == len(tests):
        print("🎉 TUTTI I TEST SONO RIUSCITI!")
        print("🚀 L'integrazione del sistema autenticazione è completa!")
    else:
        print("⚠️  Alcuni test sono falliti. Controlla i log sopra.")
    
    return success_count == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
