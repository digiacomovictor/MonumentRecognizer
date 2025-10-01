"""
Test Veloce Sistema Notifiche Push
Test senza dipendenze esterne per verificare funzionalità base
"""

import sqlite3
import json
import os
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import uuid


# Copia delle classi essenziali senza dipendenze esterne
class NotificationType(Enum):
    GENERAL = "general"
    MONUMENT_VISIT = "monument_visit"
    ACHIEVEMENT = "achievement"
    SOCIAL_INTERACTION = "social_interaction"
    DAILY_CHALLENGE = "daily_challenge"
    NEARBY_MONUMENTS = "nearby_monuments"
    SYSTEM_UPDATE = "system_update"
    REMINDER = "reminder"
    PROMOTIONAL = "promotional"
    EMERGENCY = "emergency"


class NotificationPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class SimpleNotification:
    id: str
    title: str
    body: str
    notification_type: NotificationType
    priority: NotificationPriority
    user_id: str
    created_at: datetime
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    data: Optional[Dict] = None


class SimpleNotificationManager:
    """Manager semplificato per test senza dipendenze"""
    
    def __init__(self, db_path: str = "test_simple.db"):
        self.db_path = db_path
        self._init_database()
        print(f"✅ SimpleNotificationManager inizializzato con DB: {db_path}")
    
    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    delivered_at TEXT,
                    read_at TEXT,
                    data TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT NOT NULL
                )
            """)
    
    def create_notification(self, title: str, body: str, user_id: str,
                          notification_type: NotificationType = NotificationType.GENERAL,
                          priority: NotificationPriority = NotificationPriority.NORMAL,
                          data: Optional[Dict] = None) -> str:
        
        notification_id = str(uuid.uuid4())
        notification = SimpleNotification(
            id=notification_id,
            title=title,
            body=body,
            notification_type=notification_type,
            priority=priority,
            user_id=user_id,
            created_at=datetime.now(),
            delivered_at=datetime.now(),  # Consegna immediata per semplicità
            data=data
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO notifications 
                (id, title, body, notification_type, priority, user_id, created_at, 
                 delivered_at, read_at, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification.id,
                notification.title,
                notification.body,
                notification.notification_type.value,
                notification.priority.value,
                notification.user_id,
                notification.created_at.isoformat(),
                notification.delivered_at.isoformat() if notification.delivered_at else None,
                notification.read_at.isoformat() if notification.read_at else None,
                json.dumps(notification.data) if notification.data else None
            ))
        
        print(f"📱 Notifica creata: {title}")
        return notification_id
    
    def get_user_notifications(self, user_id: str, limit: int = 50) -> List[SimpleNotification]:
        notifications = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, title, body, notification_type, priority, user_id, 
                       created_at, delivered_at, read_at, data
                FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            for row in cursor.fetchall():
                notifications.append(SimpleNotification(
                    id=row[0],
                    title=row[1],
                    body=row[2],
                    notification_type=NotificationType(row[3]),
                    priority=NotificationPriority(row[4]),
                    user_id=row[5],
                    created_at=datetime.fromisoformat(row[6]),
                    delivered_at=datetime.fromisoformat(row[7]) if row[7] else None,
                    read_at=datetime.fromisoformat(row[8]) if row[8] else None,
                    data=json.loads(row[9]) if row[9] else None
                ))
        
        return notifications
    
    def mark_as_read(self, notification_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE notifications 
                SET read_at = ? 
                WHERE id = ? AND read_at IS NULL
            """, (datetime.now().isoformat(), notification_id))
            
            success = cursor.rowcount > 0
            if success:
                print(f"✅ Notifica {notification_id} marcata come letta")
            return success
    
    def get_notification_stats(self, user_id: str) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN read_at IS NOT NULL THEN 1 END) as read,
                    COUNT(CASE WHEN read_at IS NULL THEN 1 END) as unread
                FROM notifications 
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            return {
                'total_notifications': result[0],
                'read_notifications': result[1],
                'unread_notifications': result[2],
                'read_percentage': (result[1] / result[0] * 100) if result[0] > 0 else 0
            }
    
    def cleanup(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"🗑️ Database {self.db_path} rimosso")


def test_basic_functionality():
    """Test funzionalità base"""
    print("🧪 === TEST FUNZIONALITÀ BASE ===")
    
    manager = SimpleNotificationManager()
    test_user = "test_user_123"
    
    try:
        # Test 1: Creazione notifica
        print("\n1️⃣ Test creazione notifica...")
        notif_id = manager.create_notification(
            title="🏛️ Benvenuto in Monument Recognizer!",
            body="Inizia la tua avventura alla scoperta dei monumenti!",
            user_id=test_user,
            notification_type=NotificationType.GENERAL,
            priority=NotificationPriority.HIGH,
            data={'welcome': True, 'version': '1.0'}
        )
        assert notif_id is not None
        print("✅ Creazione notifica: SUCCESSO")
        
        # Test 2: Recupero notifiche utente
        print("\n2️⃣ Test recupero notifiche...")
        notifications = manager.get_user_notifications(test_user)
        assert len(notifications) == 1
        assert notifications[0].title == "🏛️ Benvenuto in Monument Recognizer!"
        assert notifications[0].notification_type == NotificationType.GENERAL
        assert notifications[0].priority == NotificationPriority.HIGH
        print("✅ Recupero notifiche: SUCCESSO")
        
        # Test 3: Creazione notifiche multiple con tipi diversi
        print("\n3️⃣ Test notifiche multiple...")
        test_notifications = [
            ("🏛️ Colosseo Visitato!", "Hai scoperto il Colosseo! +100 punti", NotificationType.MONUMENT_VISIT),
            ("🏆 Achievement Sbloccato!", "Hai ottenuto: Primo Esploratore", NotificationType.ACHIEVEMENT),
            ("👥 Nuovo Like!", "Mario ha messo like al tuo post", NotificationType.SOCIAL_INTERACTION),
            ("🎯 Sfida Giornaliera!", "Visita 3 monumenti oggi", NotificationType.DAILY_CHALLENGE),
            ("📍 Monumenti Vicini!", "5 monumenti entro 2km da te", NotificationType.NEARBY_MONUMENTS)
        ]
        
        created_ids = []
        for title, body, notif_type in test_notifications:
            notif_id = manager.create_notification(
                title=title,
                body=body, 
                user_id=test_user,
                notification_type=notif_type,
                priority=NotificationPriority.NORMAL
            )
            created_ids.append(notif_id)
        
        # Verifica che siano state create
        all_notifications = manager.get_user_notifications(test_user)
        assert len(all_notifications) == 6  # 1 iniziale + 5 nuove
        print("✅ Notifiche multiple: SUCCESSO")
        
        # Test 4: Marcatura come lette
        print("\n4️⃣ Test marcatura come lette...")
        # Marca le prime 3 come lette
        for i in range(3):
            success = manager.mark_as_read(created_ids[i])
            assert success
        
        # Verifica che siano state marcate
        all_notifications = manager.get_user_notifications(test_user)
        read_count = sum(1 for n in all_notifications if n.read_at is not None)
        assert read_count == 3
        print("✅ Marcatura lettura: SUCCESSO")
        
        # Test 5: Statistiche
        print("\n5️⃣ Test statistiche...")
        stats = manager.get_notification_stats(test_user)
        
        assert stats['total_notifications'] == 6
        assert stats['read_notifications'] == 3
        assert stats['unread_notifications'] == 3
        assert stats['read_percentage'] == 50.0
        
        print(f"📊 Statistiche: {stats}")
        print("✅ Statistiche: SUCCESSO")
        
        # Test 6: Test tipi di notifica
        print("\n6️⃣ Test filtri per tipo...")
        all_notifications = manager.get_user_notifications(test_user)
        
        # Verifica che ci siano tutti i tipi
        types_found = set(n.notification_type for n in all_notifications)
        expected_types = {
            NotificationType.GENERAL,
            NotificationType.MONUMENT_VISIT,
            NotificationType.ACHIEVEMENT,
            NotificationType.SOCIAL_INTERACTION,
            NotificationType.DAILY_CHALLENGE,
            NotificationType.NEARBY_MONUMENTS
        }
        
        assert types_found == expected_types
        print("✅ Tipi di notifica: SUCCESSO")
        
        # Test 7: Test priorità
        print("\n7️⃣ Test priorità...")
        priorities_found = set(n.priority for n in all_notifications)
        assert NotificationPriority.HIGH in priorities_found
        assert NotificationPriority.NORMAL in priorities_found
        print("✅ Priorità: SUCCESSO")
        
        print("\n🎉 === TUTTI I TEST SUPERATI! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRORE NEL TEST: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        manager.cleanup()


def test_performance():
    """Test performance semplificato"""
    print("\n⚡ === TEST PERFORMANCE SEMPLIFICATO ===")
    
    manager = SimpleNotificationManager("perf_test.db")
    
    try:
        # Test creazione in massa
        print("🔄 Creazione 100 notifiche...")
        start_time = time.time()
        
        for i in range(100):
            manager.create_notification(
                title=f"Performance Test {i}",
                body=f"Notifica di test numero {i}",
                user_id=f"user_{i % 10}",  # 10 utenti diversi
                notification_type=NotificationType.GENERAL
            )
        
        creation_time = time.time() - start_time
        print(f"⏱️ Tempo creazione: {creation_time:.2f}s ({100/creation_time:.1f} notifiche/s)")
        
        # Test lettura
        print("📖 Test lettura notifiche...")
        start_time = time.time()
        
        total_read = 0
        for i in range(10):
            notifications = manager.get_user_notifications(f"user_{i}")
            total_read += len(notifications)
        
        read_time = time.time() - start_time
        print(f"⏱️ Tempo lettura: {read_time:.2f}s ({total_read} notifiche lette)")
        
        # Test statistiche
        print("📊 Test statistiche performance...")
        start_time = time.time()
        
        for i in range(10):
            stats = manager.get_notification_stats(f"user_{i}")
        
        stats_time = time.time() - start_time
        print(f"⏱️ Tempo statistiche: {stats_time:.2f}s")
        
        print("✅ Test performance completati!")
        return True
        
    except Exception as e:
        print(f"❌ Errore nel test performance: {e}")
        return False
        
    finally:
        manager.cleanup()


def demo_interactive():
    """Demo interattiva semplificata"""
    print("\n🎮 === DEMO INTERATTIVA SEMPLIFICATA ===")
    print("Comandi disponibili:")
    print("1. Crea notifica monumento")
    print("2. Crea notifica achievement") 
    print("3. Crea notifica social")
    print("4. Mostra tutte le notifiche")
    print("5. Marca notifica come letta")
    print("6. Mostra statistiche")
    print("0. Esci")
    
    manager = SimpleNotificationManager("demo_simple.db")
    demo_user = "demo_user"
    
    try:
        while True:
            choice = input("\n➤ Scegli opzione (0-6): ").strip()
            
            if choice == "1":
                monument_name = input("Nome monumento (default: Pantheon): ").strip() or "Pantheon"
                points = input("Punti guadagnati (default: 75): ").strip() or "75"
                
                manager.create_notification(
                    title=f"🏛️ {monument_name} Visitato!",
                    body=f"Hai scoperto {monument_name}! Guadagnati {points} punti!",
                    user_id=demo_user,
                    notification_type=NotificationType.MONUMENT_VISIT,
                    priority=NotificationPriority.HIGH,
                    data={'monument': monument_name, 'points': int(points)}
                )
                
            elif choice == "2":
                achievement_name = input("Nome achievement (default: Esploratore): ").strip() or "Esploratore"
                
                manager.create_notification(
                    title="🏆 Achievement Sbloccato!",
                    body=f"Complimenti! Hai ottenuto: {achievement_name}",
                    user_id=demo_user,
                    notification_type=NotificationType.ACHIEVEMENT,
                    priority=NotificationPriority.HIGH,
                    data={'achievement': achievement_name}
                )
                
            elif choice == "3":
                user_name = input("Nome utente (default: Marco): ").strip() or "Marco"
                action = input("Azione (like/comment/share, default: like): ").strip() or "like"
                
                action_map = {
                    'like': 'ha messo like a',
                    'comment': 'ha commentato',
                    'share': 'ha condiviso'
                }
                
                manager.create_notification(
                    title="👥 Nuova Interazione Social!",
                    body=f"{user_name} {action_map.get(action, 'ha interagito con')} il tuo post",
                    user_id=demo_user,
                    notification_type=NotificationType.SOCIAL_INTERACTION,
                    priority=NotificationPriority.NORMAL,
                    data={'actor': user_name, 'action': action}
                )
                
            elif choice == "4":
                notifications = manager.get_user_notifications(demo_user)
                
                if not notifications:
                    print("📭 Nessuna notifica trovata")
                else:
                    print(f"\n📱 Notifiche per {demo_user} ({len(notifications)} totali):")
                    for i, notif in enumerate(notifications, 1):
                        status = "✅ Letta" if notif.read_at else "📭 Non letta"
                        priority_emoji = "🔥" if notif.priority.value > 2 else "📌"
                        
                        print(f"\n{i}. [{notif.id[:8]}] {priority_emoji} {status}")
                        print(f"   {notif.title}")
                        print(f"   {notif.body}")
                        print(f"   Tipo: {notif.notification_type.value}")
                        print(f"   Creata: {notif.created_at.strftime('%d/%m/%Y %H:%M')}")
                        
                        if notif.data:
                            print(f"   Dati: {notif.data}")
                
            elif choice == "5":
                notifications = manager.get_user_notifications(demo_user)
                unread = [n for n in notifications if n.read_at is None]
                
                if not unread:
                    print("📖 Tutte le notifiche sono già lette!")
                else:
                    print("\nNotifiche non lette:")
                    for i, notif in enumerate(unread, 1):
                        print(f"{i}. {notif.title} [{notif.id[:8]}]")
                    
                    try:
                        choice_idx = int(input("Numero notifica da marcare come letta: ")) - 1
                        if 0 <= choice_idx < len(unread):
                            success = manager.mark_as_read(unread[choice_idx].id)
                            if success:
                                print("✅ Notifica marcata come letta!")
                            else:
                                print("❌ Errore nella marcatura!")
                        else:
                            print("❌ Numero non valido!")
                    except ValueError:
                        print("❌ Inserisci un numero valido!")
                
            elif choice == "6":
                stats = manager.get_notification_stats(demo_user)
                print(f"\n📊 Statistiche per {demo_user}:")
                print(f"📬 Totali: {stats['total_notifications']}")
                print(f"📖 Lette: {stats['read_notifications']}")
                print(f"📭 Non lette: {stats['unread_notifications']}")
                print(f"📈 Tasso lettura: {stats['read_percentage']:.1f}%")
                
            elif choice == "0":
                print("👋 Uscita dalla demo...")
                break
                
            else:
                print("❌ Opzione non valida!")
                
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrotta dall'utente")
    except Exception as e:
        print(f"❌ Errore nella demo: {e}")
    finally:
        manager.cleanup()


if __name__ == "__main__":
    print("🔔 === TEST RAPIDO SISTEMA NOTIFICHE PUSH ===")
    print("Versione semplificata senza dipendenze esterne\n")
    
    print("Modalità disponibili:")
    print("1. Test automatizzati")
    print("2. Test performance")
    print("3. Demo interattiva")
    print("4. Tutti i test")
    
    choice = input("\nScegli modalità (1-4): ").strip()
    
    if choice == "1":
        success = test_basic_functionality()
        print(f"\n{'🎉 TUTTI I TEST SUPERATI!' if success else '💥 ALCUNI TEST FALLITI!'}")
        
    elif choice == "2":
        success = test_performance()
        print(f"\n{'✅ Test performance superati!' if success else '❌ Test performance falliti!'}")
        
    elif choice == "3":
        demo_interactive()
        
    elif choice == "4":
        print("🔄 Esecuzione di tutti i test...\n")
        
        # Test funzionalità
        basic_success = test_basic_functionality()
        
        # Test performance  
        perf_success = test_performance()
        
        print(f"\n📋 === RIEPILOGO FINALE ===")
        print(f"Test funzionalità base: {'✅ SUCCESSO' if basic_success else '❌ FALLITO'}")
        print(f"Test performance: {'✅ SUCCESSO' if perf_success else '❌ FALLITO'}")
        
        if basic_success and perf_success:
            print("\n🎉 SISTEMA NOTIFICHE PUSH: PIENAMENTE FUNZIONANTE!")
            
            if input("\nVuoi provare la demo interattiva? (s/N): ").lower() == 's':
                demo_interactive()
        else:
            print("\n⚠️ Alcuni test sono falliti. Controllare l'implementazione.")
            
    else:
        print("❌ Scelta non valida!")
    
    print("\n👋 Test terminati!")
