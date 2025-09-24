"""
👤 Sistema di Autenticazione e Gestione Utenti
Sistema completo per login, registrazione e gestione profili utente
"""

import os
import sqlite3
import hashlib
import secrets
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class User:
    """Rappresenta un utente del sistema."""
    user_id: int
    username: str
    email: str
    full_name: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    profile_settings: Dict = None
    
    def __post_init__(self):
        if self.profile_settings is None:
            self.profile_settings = {}
    
    def to_dict(self) -> Dict:
        """Converte l'utente in dizionario."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'profile_settings': self.profile_settings
        }

class UserSystem:
    """Sistema di gestione utenti e autenticazione."""
    
    def __init__(self, db_path: str = "monument_users.db"):
        self.db_path = db_path
        self.current_user: Optional[User] = None
        self.session_token: Optional[str] = None
        self.init_database()
    
    def init_database(self):
        """Inizializza il database SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabella utenti
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        full_name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        profile_settings TEXT DEFAULT '{}'
                    )
                """)
                
                # Tabella sessioni
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                # Tabella tentativi di login
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS login_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        ip_address TEXT,
                        attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN
                    )
                """)
                
                # Tabella reset password
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS password_resets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        reset_token TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        used BOOLEAN DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                """)
                
                conn.commit()
                print("📊 Database utenti inizializzato")
                
        except Exception as e:
            print(f"❌ Errore nell'inizializzazione database: {e}")
    
    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """
        Crea hash sicuro della password con salt.
        
        Args:
            password: Password in chiaro
            salt: Salt esistente (opzionale)
            
        Returns:
            Tupla (password_hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Usa PBKDF2 con SHA-256 per hash sicuro
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterazioni
        ).hex()
        
        return password_hash, salt
    
    def _validate_email(self, email: str) -> bool:
        """Valida formato email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_username(self, username: str) -> bool:
        """Valida formato username."""
        # Username: 3-20 caratteri, solo lettere, numeri, underscore
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None
    
    def _validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """
        Valida la sicurezza della password.
        
        Returns:
            Tupla (is_valid, errori)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Password deve avere almeno 8 caratteri")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password deve contenere almeno una maiuscola")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password deve contenere almeno una minuscola")
        
        if not re.search(r'[0-9]', password):
            errors.append("Password deve contenere almeno un numero")
        
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            errors.append("Password deve contenere almeno un simbolo")
        
        return len(errors) == 0, errors
    
    def register_user(self, username: str, email: str, full_name: str, 
                     password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Registra un nuovo utente.
        
        Returns:
            Tupla (success, message, user)
        """
        try:
            # Validazioni
            if not self._validate_username(username):
                return False, "Username non valido (3-20 caratteri, solo lettere, numeri, _)", None
            
            if not self._validate_email(email):
                return False, "Email non valida", None
            
            if not full_name.strip():
                return False, "Nome completo richiesto", None
            
            password_valid, password_errors = self._validate_password(password)
            if not password_valid:
                return False, "; ".join(password_errors), None
            
            # Controlla duplicati
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT username FROM users WHERE username = ? OR email = ?", 
                             (username, email))
                if cursor.fetchone():
                    return False, "Username o email già esistenti", None
                
                # Crea hash password
                password_hash, salt = self._hash_password(password)
                
                # Inserisci utente
                cursor.execute("""
                    INSERT INTO users (username, email, full_name, password_hash, salt, profile_settings)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, email, full_name, password_hash, salt, '{}'))
                
                user_id = cursor.lastrowid
                
                # Crea oggetto utente
                user = User(
                    user_id=user_id,
                    username=username,
                    email=email,
                    full_name=full_name,
                    created_at=datetime.now(),
                    profile_settings={}
                )
                
                conn.commit()
                print(f"✅ Utente registrato: {username}")
                
                return True, "Registrazione completata con successo", user
                
        except Exception as e:
            print(f"❌ Errore nella registrazione: {e}")
            return False, f"Errore interno: {str(e)}", None
    
    def login_user(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Autentica un utente.
        
        Returns:
            Tupla (success, message, user)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Cerca utente per username o email
                cursor.execute("""
                    SELECT user_id, username, email, full_name, password_hash, salt, 
                           created_at, last_login, is_active, profile_settings
                    FROM users 
                    WHERE (username = ? OR email = ?) AND is_active = 1
                """, (username_or_email, username_or_email))
                
                user_data = cursor.fetchone()
                if not user_data:
                    # Log tentativo fallito
                    cursor.execute("""
                        INSERT INTO login_attempts (username, attempt_time, success)
                        VALUES (?, CURRENT_TIMESTAMP, 0)
                    """, (username_or_email,))
                    conn.commit()
                    
                    return False, "Credenziali non valide", None
                
                # Verifica password
                stored_hash = user_data[4]
                salt = user_data[5]
                password_hash, _ = self._hash_password(password, salt)
                
                if password_hash != stored_hash:
                    # Log tentativo fallito
                    cursor.execute("""
                        INSERT INTO login_attempts (username, attempt_time, success)
                        VALUES (?, CURRENT_TIMESTAMP, 0)
                    """, (username_or_email,))
                    conn.commit()
                    
                    return False, "Credenziali non valide", None
                
                # Login riuscito
                user = User(
                    user_id=user_data[0],
                    username=user_data[1],
                    email=user_data[2],
                    full_name=user_data[3],
                    created_at=datetime.fromisoformat(user_data[6]) if user_data[6] else datetime.now(),
                    last_login=datetime.fromisoformat(user_data[7]) if user_data[7] else None,
                    is_active=bool(user_data[8]),
                    profile_settings=json.loads(user_data[9]) if user_data[9] else {}
                )
                
                # Aggiorna ultimo login
                cursor.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?
                """, (user.user_id,))
                
                # Log tentativo riuscito
                cursor.execute("""
                    INSERT INTO login_attempts (username, attempt_time, success)
                    VALUES (?, CURRENT_TIMESTAMP, 1)
                """, (username_or_email,))
                
                # Crea sessione
                session_token = secrets.token_urlsafe(32)
                expires_at = datetime.now() + timedelta(days=30)  # Sessione 30 giorni
                
                cursor.execute("""
                    INSERT INTO user_sessions (session_id, user_id, expires_at)
                    VALUES (?, ?, ?)
                """, (session_token, user.user_id, expires_at))
                
                conn.commit()
                
                # Imposta utente corrente
                self.current_user = user
                self.session_token = session_token
                
                print(f"✅ Login riuscito: {user.username}")
                return True, "Login effettuato con successo", user
                
        except Exception as e:
            print(f"❌ Errore nel login: {e}")
            return False, f"Errore interno: {str(e)}", None
    
    def logout_user(self):
        """Effettua logout dell'utente corrente."""
        if self.session_token:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE user_sessions SET is_active = 0 WHERE session_id = ?
                    """, (self.session_token,))
                    conn.commit()
            except Exception as e:
                print(f"⚠️ Errore nel logout: {e}")
        
        self.current_user = None
        self.session_token = None
        print("👋 Logout effettuato")
    
    def is_logged_in(self) -> bool:
        """Verifica se c'è un utente loggato."""
        return self.current_user is not None
    
    def validate_session(self, session_token: str) -> bool:
        """Valida un token di sessione."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, expires_at FROM user_sessions 
                    WHERE session_id = ? AND is_active = 1
                """, (session_token,))
                
                session_data = cursor.fetchone()
                if not session_data:
                    return False
                
                expires_at = datetime.fromisoformat(session_data[1])
                if expires_at < datetime.now():
                    # Sessione scaduta
                    cursor.execute("""
                        UPDATE user_sessions SET is_active = 0 WHERE session_id = ?
                    """, (session_token,))
                    conn.commit()
                    return False
                
                return True
                
        except Exception as e:
            print(f"❌ Errore validazione sessione: {e}")
            return False
    
    def restore_session(self, session_token: str) -> bool:
        """Ripristina una sessione valida."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.user_id, u.username, u.email, u.full_name, 
                           u.created_at, u.last_login, u.is_active, u.profile_settings
                    FROM users u
                    JOIN user_sessions s ON u.user_id = s.user_id
                    WHERE s.session_id = ? AND s.is_active = 1 AND s.expires_at > CURRENT_TIMESTAMP
                """, (session_token,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    return False
                
                # Ripristina utente
                self.current_user = User(
                    user_id=user_data[0],
                    username=user_data[1],
                    email=user_data[2],
                    full_name=user_data[3],
                    created_at=datetime.fromisoformat(user_data[4]) if user_data[4] else datetime.now(),
                    last_login=datetime.fromisoformat(user_data[5]) if user_data[5] else None,
                    is_active=bool(user_data[6]),
                    profile_settings=json.loads(user_data[7]) if user_data[7] else {}
                )
                
                self.session_token = session_token
                print(f"🔄 Sessione ripristinata: {self.current_user.username}")
                return True
                
        except Exception as e:
            print(f"❌ Errore ripristino sessione: {e}")
            return False
    
    def update_user_profile(self, **kwargs) -> bool:
        """Aggiorna il profilo dell'utente corrente."""
        if not self.current_user:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Campi aggiornabili
                updatable_fields = ['full_name', 'email']
                updates = []
                values = []
                
                for field, value in kwargs.items():
                    if field in updatable_fields and value is not None:
                        updates.append(f"{field} = ?")
                        values.append(value)
                
                if updates:
                    query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
                    values.append(self.current_user.user_id)
                    
                    cursor.execute(query, values)
                    conn.commit()
                    
                    # Aggiorna oggetto utente
                    for field, value in kwargs.items():
                        if field in updatable_fields and hasattr(self.current_user, field):
                            setattr(self.current_user, field, value)
                
                return True
                
        except Exception as e:
            print(f"❌ Errore aggiornamento profilo: {e}")
            return False
    
    def update_profile_settings(self, settings: Dict) -> bool:
        """Aggiorna le impostazioni del profilo."""
        if not self.current_user:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Merge con impostazioni esistenti
                current_settings = self.current_user.profile_settings.copy()
                current_settings.update(settings)
                
                cursor.execute("""
                    UPDATE users SET profile_settings = ? WHERE user_id = ?
                """, (json.dumps(current_settings), self.current_user.user_id))
                
                conn.commit()
                self.current_user.profile_settings = current_settings
                
                return True
                
        except Exception as e:
            print(f"❌ Errore aggiornamento impostazioni: {e}")
            return False
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Cambia la password dell'utente corrente."""
        if not self.current_user:
            return False, "Nessun utente loggato"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verifica password attuale
                cursor.execute("""
                    SELECT password_hash, salt FROM users WHERE user_id = ?
                """, (self.current_user.user_id,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    return False, "Utente non trovato"
                
                old_hash, salt = self._hash_password(old_password, user_data[1])
                if old_hash != user_data[0]:
                    return False, "Password attuale non corretta"
                
                # Valida nuova password
                password_valid, password_errors = self._validate_password(new_password)
                if not password_valid:
                    return False, "; ".join(password_errors)
                
                # Aggiorna password
                new_hash, new_salt = self._hash_password(new_password)
                cursor.execute("""
                    UPDATE users SET password_hash = ?, salt = ? WHERE user_id = ?
                """, (new_hash, new_salt, self.current_user.user_id))
                
                conn.commit()
                return True, "Password aggiornata con successo"
                
        except Exception as e:
            print(f"❌ Errore cambio password: {e}")
            return False, f"Errore interno: {str(e)}"
    
    def get_user_stats(self) -> Dict:
        """Ottiene statistiche dell'utente corrente."""
        if not self.current_user:
            return {}
        
        stats = {
            'user_id': self.current_user.user_id,
            'username': self.current_user.username,
            'full_name': self.current_user.full_name,
            'member_since': self.current_user.created_at.strftime('%d/%m/%Y'),
            'last_login': self.current_user.last_login.strftime('%d/%m/%Y %H:%M') if self.current_user.last_login else 'Mai',
            'profile_settings': self.current_user.profile_settings
        }
        
        return stats
    
    def cleanup_expired_sessions(self):
        """Pulisce le sessioni scadute."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP
                """)
                deleted = cursor.rowcount
                conn.commit()
                
                if deleted > 0:
                    print(f"🧹 Pulite {deleted} sessioni scadute")
                    
        except Exception as e:
            print(f"❌ Errore pulizia sessioni: {e}")
    
    def get_all_users(self) -> List[Dict]:
        """Ottiene lista di tutti gli utenti (per admin)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, username, email, full_name, created_at, last_login, is_active
                    FROM users ORDER BY created_at DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'user_id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'full_name': row[3],
                        'created_at': row[4],
                        'last_login': row[5],
                        'is_active': bool(row[6])
                    })
                
                return users
                
        except Exception as e:
            print(f"❌ Errore caricamento utenti: {e}")
            return []
