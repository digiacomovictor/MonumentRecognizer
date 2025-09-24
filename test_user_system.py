#!/usr/bin/env python3
"""
🧪 Test Sistema Autenticazione Utenti
Testa tutte le funzionalità del sistema di login e gestione utenti
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

def test_user_system():
    """Testa il sistema di gestione utenti."""
    print("🔍 Test UserSystem...")
    
    try:
        from user_system import UserSystem, User
        
        # Usa un database di test
        test_db = "test_users.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        user_system = UserSystem(test_db)
        
        print("   ✅ UserSystem inizializzato")
        
        # Test registrazione utente
        success, message, user = user_system.register_user(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="Password123!"
        )
        
        if success:
            print(f"   ✅ Registrazione riuscita: {user.username}")
        else:
            print(f"   ❌ Registrazione fallita: {message}")
            return False
        
        # Test login
        success, message, logged_user = user_system.login_user("testuser", "Password123!")
        
        if success:
            print(f"   ✅ Login riuscito: {logged_user.full_name}")
        else:
            print(f"   ❌ Login fallito: {message}")
            return False
        
        # Test sessione
        if user_system.is_logged_in():
            print("   ✅ Utente loggato correttamente")
        else:
            print("   ❌ Stato login non corretto")
            return False
        
        # Test statistiche utente
        stats = user_system.get_user_stats()
        if stats and 'username' in stats:
            print(f"   ✅ Statistiche utente: {stats['username']}")
        else:
            print("   ❌ Errore nelle statistiche")
            return False
        
        # Test logout
        user_system.logout_user()
        if not user_system.is_logged_in():
            print("   ✅ Logout riuscito")
        else:
            print("   ❌ Logout fallito")
            return False
        
        # Test login con credenziali sbagliate
        success, message, _ = user_system.login_user("testuser", "password_sbagliata")
        if not success:
            print("   ✅ Credenziali sbagliate respinte correttamente")
        else:
            print("   ❌ Credenziali sbagliate accettate erroneamente")
            return False
        
        # Pulisci database di test
        user_system = None  # Assicura che la connessione sia chiusa
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except PermissionError:
                print(f"   ⚠️ Impossibile rimuovere {test_db} (in uso)")
        
        print("   ✅ UserSystem funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore UserSystem: {e}")
        return False

def test_auth_ui_imports():
    """Testa che le interfacce UI si importino correttamente."""
    print("\n🔍 Test Auth UI Imports...")
    
    try:
        from auth_ui import LoginScreen, RegisterScreen, ProfileScreen, AuthManager
        from user_system import UserSystem
        
        # Crea un sistema utenti di test
        test_db = "test_ui_users.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        user_system = UserSystem(test_db)
        
        # Test creazione AuthManager
        auth_manager = AuthManager(user_system)
        
        if auth_manager.screen_manager:
            print("   ✅ AuthManager creato con ScreenManager")
        else:
            print("   ❌ AuthManager senza ScreenManager")
            return False
        
        # Test che le schermate siano state create
        screen_names = [screen.name for screen in auth_manager.screen_manager.screens]
        expected_screens = ['login', 'register', 'profile']
        
        for screen_name in expected_screens:
            if screen_name in screen_names:
                print(f"   ✅ Schermata '{screen_name}' creata")
            else:
                print(f"   ❌ Schermata '{screen_name}' mancante")
                return False
        
        # Pulisci
        auth_manager = None  # Assicura che la connessione sia chiusa
        user_system = None
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except PermissionError:
                print(f"   ⚠️ Impossibile rimuovere {test_db} (in uso)")
        
        print("   ✅ Auth UI si importa correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore Auth UI: {e}")
        return False

def test_database_structure():
    """Testa la struttura del database."""
    print("\n🔍 Test Database Structure...")
    
    try:
        from user_system import UserSystem
        
        test_db = "test_db_structure.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        user_system = UserSystem(test_db)
        
        # Controlla le tabelle create
        with sqlite3.connect(test_db) as conn:
            cursor = conn.cursor()
            
            # Lista tabelle
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['users', 'user_sessions', 'login_attempts', 'password_resets']
            
            for table in expected_tables:
                if table in tables:
                    print(f"   ✅ Tabella '{table}' creata")
                else:
                    print(f"   ❌ Tabella '{table}' mancante")
                    return False
            
            # Controlla struttura tabella users
            cursor.execute("PRAGMA table_info(users);")
            columns = [row[1] for row in cursor.fetchall()]
            
            expected_columns = ['user_id', 'username', 'email', 'full_name', 'password_hash', 'salt']
            
            for column in expected_columns:
                if column in columns:
                    print(f"   ✅ Colonna users.{column} presente")
                else:
                    print(f"   ❌ Colonna users.{column} mancante")
                    return False
        
        # Pulisci
        user_system = None  # Assicura che la connessione sia chiusa
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except PermissionError:
                print(f"   ⚠️ Impossibile rimuovere {test_db} (in uso)")
        
        print("   ✅ Struttura database corretta")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore struttura database: {e}")
        return False

def test_password_security():
    """Testa la sicurezza delle password."""
    print("\n🔍 Test Password Security...")
    
    try:
        from user_system import UserSystem
        
        test_db = "test_password_security.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        user_system = UserSystem(test_db)
        
        # Test password deboli
        weak_passwords = [
            "123",          # Troppo corta
            "password",     # Senza maiuscole, numeri, simboli
            "Password",     # Senza numeri, simboli
            "Password123",  # Senza simboli
            "PASSW0RD123!"  # Senza minuscole
        ]
        
        for weak_pwd in weak_passwords:
            success, message, _ = user_system.register_user(
                f"test_{weak_pwd[:3]}", 
                f"test_{weak_pwd[:3]}@example.com", 
                "Test User", 
                weak_pwd
            )
            
            if not success:
                print(f"   ✅ Password debole respinta: {weak_pwd[:8]}...")
            else:
                print(f"   ❌ Password debole accettata: {weak_pwd[:8]}...")
                return False
        
        # Test password forte
        strong_password = "StrongPass123!@#"
        success, message, user = user_system.register_user(
            "stronguser", 
            "strong@example.com", 
            "Strong User", 
            strong_password
        )
        
        if success:
            print("   ✅ Password forte accettata")
        else:
            print(f"   ❌ Password forte respinta: {message}")
            return False
        
        # Test che la password sia hashata nel database
        with sqlite3.connect(test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", ("stronguser",))
            result = cursor.fetchone()
            
            if result and result[0] != strong_password and result[1]:
                print("   ✅ Password hashata correttamente con salt")
            else:
                print("   ❌ Password non hashata correttamente")
                return False
        
        # Pulisci
        user_system = None  # Assicura che la connessione sia chiusa
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except PermissionError:
                print(f"   ⚠️ Impossibile rimuovere {test_db} (in uso)")
        
        print("   ✅ Sicurezza password funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore sicurezza password: {e}")
        return False

def test_session_management():
    """Testa la gestione delle sessioni."""
    print("\n🔍 Test Session Management...")
    
    try:
        from user_system import UserSystem
        
        test_db = "test_sessions.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        user_system = UserSystem(test_db)
        
        # Registra e logga utente
        user_system.register_user("sessionuser", "session@example.com", "Session User", "SessionPass123!")
        success, message, user = user_system.login_user("sessionuser", "SessionPass123!")
        
        if not success:
            print("   ❌ Login fallito per test sessioni")
            return False
        
        # Verifica che sia stata creata una sessione
        if user_system.session_token:
            print("   ✅ Token di sessione creato")
            
            # Test validazione sessione
            is_valid = user_system.validate_session(user_system.session_token)
            if is_valid:
                print("   ✅ Sessione valida")
            else:
                print("   ❌ Sessione non valida")
                return False
            
            # Test che la sessione rimanga valida
            old_token = user_system.session_token
            
            # Crea una nuova istanza del sistema per testare il ripristino
            from user_system import UserSystem as NewUserSystem
            new_user_system = NewUserSystem(test_db)
            
            if new_user_system.restore_session(old_token):
                print("   ✅ Sessione ripristinata")
            else:
                print("   ❌ Ripristino sessione fallito")
                return False
        else:
            print("   ❌ Token di sessione non creato")
            return False
        
        # Pulisci
        user_system = None  # Assicura che la connessione sia chiusa
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except PermissionError:
                print(f"   ⚠️ Impossibile rimuovere {test_db} (in uso)")
        
        print("   ✅ Gestione sessioni funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Errore gestione sessioni: {e}")
        return False

def main():
    """Esegue tutti i test del sistema utenti."""
    print("=" * 60)
    print("🧪 TEST SISTEMA AUTENTICAZIONE UTENTI")
    print("   Monument Recognizer v2.0")
    print("=" * 60)
    
    tests = [
        ("Sistema Utenti Base", test_user_system),
        ("Interfacce UI", test_auth_ui_imports),
        ("Struttura Database", test_database_structure),
        ("Sicurezza Password", test_password_security),
        ("Gestione Sessioni", test_session_management),
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
    print("📊 RIASSUNTO TEST AUTENTICAZIONE")
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
        print("🚀 Il sistema di autenticazione è pronto!")
        print("\n💡 Prossimi passi:")
        print("   • Integrare con l'app principale")
        print("   • Collegare con il sistema visite")
        print("   • Implementare sincronizzazione cloud")
    else:
        print("⚠️  Alcuni test sono falliti. Controlla i messaggi sopra.")
    
    print("\n🔧 Per testare manualmente le UI:")
    print("   • Crea un'app Kivy che usa AuthManager")
    print("   • Testa login/registrazione/profilo")
    print("   • Verifica persistenza sessioni")

if __name__ == "__main__":
    main()
