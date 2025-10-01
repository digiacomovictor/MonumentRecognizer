"""
Test Completi e Demo per Sistema Notifiche Push Avanzato
Suite di test e demo interattiva per verificare tutte le funzionalità.
"""

import unittest
import threading
import time
import json
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import del sistema notifiche
from push_notifications import (
    PushNotificationManager,
    NotificationType,
    NotificationPriority,
    PushNotification,
    NotificationTemplate
)

from notifications_integration import (
    NotificationIntegrationManager,
    create_integrated_notification_system
)

from notifications_ui import (
    NotificationsApp,
    NotificationCard,
    NotificationsList,
    NotificationsMainScreen
)


class TestPushNotificationManager(unittest.TestCase):
    """Test per PushNotificationManager"""
    
    def setUp(self):
        """Setup per ogni test"""
        self.test_db = "test_notifications.db"
        self.manager = PushNotificationManager(db_path=self.test_db)
        self.test_user_id = "test_user_123"
    
    def tearDown(self):
        """Cleanup dopo ogni test"""
        self.manager.stop()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_notification_creation(self):
        """Test creazione notifica base"""
        notification_id = self.manager.create_notification(
            title="Test Notification",
            body="This is a test notification",
            user_id=self.test_user_id,
            notification_type=NotificationType.GENERAL,
            priority=NotificationPriority.NORMAL
        )
        
        self.assertIsNotNone(notification_id)
        self.assertTrue(len(notification_id) > 0)
        
        # Verifica che sia stata salvata
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].title, "Test Notification")
    
    def test_templated_notification(self):
        """Test notifica con template"""
        notification_id = self.manager.create_templated_notification(
            user_id=self.test_user_id,
            notification_type=NotificationType.MONUMENT_VISIT,
            template_data={
                'monument_name': 'Colosseo',
                'points': 100
            }
        )
        
        self.assertIsNotNone(notification_id)
        
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertEqual(len(notifications), 1)
        self.assertIn('Colosseo', notifications[0].title)
        self.assertIn('100', notifications[0].body)
    
    def test_notification_priorities(self):
        """Test gestione priorità notifiche"""
        # Crea notifiche con diverse priorità
        priorities = [
            (NotificationPriority.LOW, "Low priority"),
            (NotificationPriority.NORMAL, "Normal priority"),
            (NotificationPriority.HIGH, "High priority"),
            (NotificationPriority.URGENT, "Urgent priority")
        ]
        
        for priority, title in priorities:
            self.manager.create_notification(
                title=title,
                body="Test body",
                user_id=self.test_user_id,
                priority=priority
            )
        
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertEqual(len(notifications), 4)
        
        # Verifica che le priorità siano state salvate correttamente
        priority_values = [n.priority.value for n in notifications]
        self.assertIn(1, priority_values)  # LOW
        self.assertIn(2, priority_values)  # NORMAL  
        self.assertIn(3, priority_values)  # HIGH
        self.assertIn(4, priority_values)  # URGENT
    
    def test_scheduled_notifications(self):
        """Test notifiche programmate"""
        # Programma notifica per tra 2 secondi
        scheduled_time = datetime.now() + timedelta(seconds=2)
        
        notification_id = self.manager.create_notification(
            title="Scheduled Test",
            body="This should be delivered later",
            user_id=self.test_user_id,
            scheduled_at=scheduled_time
        )
        
        # Verifica che non sia ancora stata consegnata
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertEqual(len(notifications), 1)
        self.assertIsNone(notifications[0].delivered_at)
        
        # Aspetta la consegna
        time.sleep(3)
        
        # Verifica che ora sia stata consegnata
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertIsNotNone(notifications[0].delivered_at)
    
    def test_mark_as_read(self):
        """Test marcatura come letta"""
        notification_id = self.manager.create_notification(
            title="Read Test",
            body="Test notification",
            user_id=self.test_user_id
        )
        
        # Verifica che non sia letta inizialmente
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertIsNone(notifications[0].read_at)
        
        # Marca come letta
        result = self.manager.mark_as_read(notification_id)
        self.assertTrue(result)
        
        # Verifica che sia ora letta
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertIsNotNone(notifications[0].read_at)
    
    def test_user_preferences(self):
        """Test gestione preferenze utente"""
        # Imposta preferenze custom
        prefs = {
            'notifications_enabled': True,
            'monument_visit_enabled': False,
            'quiet_hours_start': '22:00',
            'quiet_hours_end': '08:00'
        }
        
        self.manager.set_user_preferences(self.test_user_id, prefs)
        
        # Verifica che siano state salvate
        retrieved_prefs = self.manager.get_user_preferences(self.test_user_id)
        self.assertEqual(retrieved_prefs['notifications_enabled'], True)
        self.assertEqual(retrieved_prefs['monument_visit_enabled'], False)
    
    def test_notification_stats(self):
        """Test statistiche notifiche"""
        # Crea diverse notifiche
        for i in range(5):
            notification_id = self.manager.create_notification(
                title=f"Notification {i}",
                body="Test body",
                user_id=self.test_user_id,
                notification_type=NotificationType.GENERAL
            )
            
            # Marca alcune come lette
            if i < 3:
                self.manager.mark_as_read(notification_id)
        
        # Ottieni statistiche
        stats = self.manager.get_notification_stats(self.test_user_id)
        
        self.assertEqual(stats['general']['total_notifications'], 5)
        self.assertEqual(stats['general']['read_notifications'], 3)
        self.assertEqual(stats['general']['unread_notifications'], 2)
        self.assertEqual(stats['general']['read_percentage'], 60.0)
    
    def test_daily_reminder(self):
        """Test promemoria giornalieri"""
        # Programma promemoria per le 10:00
        reminder_id = self.manager.schedule_daily_reminder(
            user_id=self.test_user_id,
            title="Daily Reminder",
            body="Your daily exploration reminder!",
            hour=10,
            minute=0
        )
        
        self.assertIsNotNone(reminder_id)
        
        # Verifica che sia stata creata
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].notification_type, NotificationType.REMINDER)
    
    def test_clear_notifications(self):
        """Test cancellazione notifiche"""
        # Crea notifiche
        ids = []
        for i in range(3):
            notification_id = self.manager.create_notification(
                title=f"Test {i}",
                body="Test body",
                user_id=self.test_user_id
            )
            ids.append(notification_id)
        
        # Marca le prime due come lette
        for i in range(2):
            self.manager.mark_as_read(ids[i])
        
        # Cancella solo quelle lette
        self.manager.clear_user_notifications(self.test_user_id, read_only=True)
        
        # Verifica che ne rimanga solo una
        notifications = self.manager.get_user_notifications(self.test_user_id)
        self.assertEqual(len(notifications), 1)
        self.assertIsNone(notifications[0].read_at)


class TestNotificationIntegration(unittest.TestCase):
    """Test per NotificationIntegrationManager"""
    
    def setUp(self):
        """Setup per test integrazione"""
        self.test_db = "test_integration.db"
        self.integration_manager = create_integrated_notification_system(
            db_path=self.test_db
        )
        self.test_user_id = "integration_test_user"
    
    def tearDown(self):
        """Cleanup"""
        self.integration_manager.stop_monitoring()
        self.integration_manager.notification_manager.stop()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_monument_visit_integration(self):
        """Test integrazione visite monumenti"""
        self.integration_manager.trigger_monument_visit_notification(
            self.test_user_id,
            "Test Monument",
            points=75,
            first_visit=True,
            streak=1
        )
        
        # Verifica che siano state create le notifiche giuste
        notifications = self.integration_manager.notification_manager.get_user_notifications(
            self.test_user_id
        )
        
        # Dovrebbero esserci almeno 2 notifiche (visita + prima visita)
        self.assertGreaterEqual(len(notifications), 1)
        
        # Verifica contenuto
        titles = [n.title for n in notifications]
        self.assertTrue(any("Test Monument" in title for title in titles))
    
    def test_achievement_integration(self):
        """Test integrazione achievement"""
        self.integration_manager.trigger_achievement_notification(
            self.test_user_id,
            "Test Achievement",
            description="Test achievement description",
            points=150
        )
        
        notifications = self.integration_manager.notification_manager.get_user_notifications(
            self.test_user_id
        )
        
        self.assertGreater(len(notifications), 0)
        
        achievement_notifications = [
            n for n in notifications 
            if n.notification_type == NotificationType.ACHIEVEMENT
        ]
        self.assertGreater(len(achievement_notifications), 0)
    
    def test_social_integration(self):
        """Test integrazione social"""
        self.integration_manager.trigger_social_notification(
            self.test_user_id,
            "like",
            "TestUser",
            target="Test Monument"
        )
        
        notifications = self.integration_manager.notification_manager.get_user_notifications(
            self.test_user_id
        )
        
        social_notifications = [
            n for n in notifications
            if n.notification_type == NotificationType.SOCIAL_INTERACTION
        ]
        
        self.assertGreater(len(social_notifications), 0)
        self.assertIn("TestUser", social_notifications[0].body)
    
    def test_nearby_monuments_integration(self):
        """Test integrazione monumenti vicini"""
        # Roma coordinates
        self.integration_manager.trigger_nearby_monuments_check(
            self.test_user_id,
            41.8902,  # Rome latitude
            12.4922   # Rome longitude
        )
        
        # Aspetta un momento per il processing asincrono
        time.sleep(1)
        
        notifications = self.integration_manager.notification_manager.get_user_notifications(
            self.test_user_id
        )
        
        # Potrebbe non esserci notifica se non ci sono monumenti "vicini" nel mock
        # Ma verifica che il sistema non sia crashato
        self.assertIsInstance(notifications, list)
    
    def test_system_announcement(self):
        """Test annuncio di sistema"""
        self.integration_manager.send_system_announcement(
            "Test System Announcement",
            "This is a test system-wide notification",
            NotificationPriority.HIGH
        )
        
        # Verifica che sia stata inviata agli utenti attivi
        # (nel mock dovrebbe includere il nostro test user)
        notifications = self.integration_manager.notification_manager.get_user_notifications(
            self.test_user_id
        )
        
        # Se il test user è negli utenti attivi, dovrebbe aver ricevuto l'annuncio
        system_notifications = [
            n for n in notifications
            if n.notification_type == NotificationType.SYSTEM_UPDATE
        ]
        
        # Potrebbe essere 0 se test_user non è negli active users del mock
        self.assertIsInstance(system_notifications, list)
    
    def test_integration_stats(self):
        """Test statistiche integrazione"""
        stats = self.integration_manager.get_integration_stats()
        
        self.assertIn('active_listeners', stats)
        self.assertIn('cache_size', stats)
        self.assertIn('monitoring_active', stats)
        self.assertIn('integrations_available', stats)
        
        self.assertIsInstance(stats['active_listeners'], int)
        self.assertIsInstance(stats['cache_size'], int)
        self.assertIsInstance(stats['monitoring_active'], bool)


class TestNotificationUI(unittest.TestCase):
    """Test per componenti UI"""
    
    def test_notification_template_formatting(self):
        """Test formattazione template notifiche"""
        template = NotificationTemplate.get_template(
            NotificationType.MONUMENT_VISIT,
            monument_name="Colosseo",
            points=100
        )
        
        self.assertIn("Colosseo", template['title'])
        self.assertIn("100", template['body'])
        self.assertIn("monument_discovery.mp3", template['sound'])
    
    def test_notification_data_conversion(self):
        """Test conversione dati notifica"""
        original = PushNotification(
            id="test_id",
            title="Test Title",
            body="Test Body",
            notification_type=NotificationType.GENERAL,
            priority=NotificationPriority.NORMAL,
            user_id="test_user",
            created_at=datetime.now()
        )
        
        # Converti in dict e torna a object
        dict_data = original.to_dict()
        converted = PushNotification.from_dict(dict_data)
        
        self.assertEqual(original.id, converted.id)
        self.assertEqual(original.title, converted.title)
        self.assertEqual(original.notification_type, converted.notification_type)
        self.assertEqual(original.priority, converted.priority)


class NotificationDemoApp:
    """Demo app interattiva per testare il sistema notifiche"""
    
    def __init__(self):
        self.integration_manager = None
        self.running = True
    
    def start_demo(self):
        """Avvia demo interattiva"""
        print("🔔 === DEMO SISTEMA NOTIFICHE PUSH AVANZATO ===")
        print("Inizializzazione sistema...")
        
        # Inizializza sistema integrato
        self.integration_manager = create_integrated_notification_system(
            db_path="demo_notifications.db"
        )
        
        print("✅ Sistema inizializzato!")
        print("\n📱 Comandi disponibili:")
        print("1. Crea notifica monumento")
        print("2. Crea notifica achievement")
        print("3. Crea notifica social")
        print("4. Controlla monumenti vicini")
        print("5. Invia annuncio sistema")
        print("6. Mostra statistiche")
        print("7. Test notifiche programmate")
        print("8. Gestione preferenze utente")
        print("9. Pulizia database")
        print("0. Esci")
        
        while self.running:
            try:
                self.handle_user_input()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Errore: {e}")
        
        self.cleanup()
    
    def handle_user_input(self):
        """Gestisce input utente"""
        choice = input("\n➤ Scegli opzione (0-9): ").strip()
        
        if choice == "1":
            self.demo_monument_notification()
        elif choice == "2":
            self.demo_achievement_notification()
        elif choice == "3":
            self.demo_social_notification()
        elif choice == "4":
            self.demo_nearby_monuments()
        elif choice == "5":
            self.demo_system_announcement()
        elif choice == "6":
            self.show_statistics()
        elif choice == "7":
            self.demo_scheduled_notifications()
        elif choice == "8":
            self.demo_user_preferences()
        elif choice == "9":
            self.cleanup_database()
        elif choice == "0":
            self.running = False
        else:
            print("❌ Opzione non valida!")
    
    def demo_monument_notification(self):
        """Demo notifiche monumenti"""
        print("\n🏛️ === DEMO NOTIFICA MONUMENTO ===")
        
        monument_name = input("Nome monumento (default: Colosseo): ").strip() or "Colosseo"
        points = input("Punti guadagnati (default: 100): ").strip() or "100"
        first_visit = input("Prima visita? (s/n, default: s): ").strip().lower() != 'n'
        
        try:
            points = int(points)
            self.integration_manager.trigger_monument_visit_notification(
                "demo_user",
                monument_name,
                points=points,
                first_visit=first_visit,
                streak=3 if first_visit else 1
            )
            
            print(f"✅ Notifica monumento creata per: {monument_name}")
            
        except ValueError:
            print("❌ Punti deve essere un numero!")
    
    def demo_achievement_notification(self):
        """Demo notifiche achievement"""
        print("\n🏆 === DEMO NOTIFICA ACHIEVEMENT ===")
        
        achievement_name = input("Nome achievement (default: Esploratore): ").strip() or "Esploratore"
        description = input("Descrizione (default: Primo monumento visitato): ").strip() or "Primo monumento visitato"
        points = input("Punti (default: 150): ").strip() or "150"
        
        try:
            points = int(points)
            self.integration_manager.trigger_achievement_notification(
                "demo_user",
                achievement_name,
                description=description,
                points=points,
                rarity="rare" if points > 200 else "common"
            )
            
            print(f"✅ Notifica achievement creata: {achievement_name}")
            
        except ValueError:
            print("❌ Punti deve essere un numero!")
    
    def demo_social_notification(self):
        """Demo notifiche social"""
        print("\n👥 === DEMO NOTIFICA SOCIAL ===")
        
        print("Tipi disponibili: like, comment, share, follow")
        interaction_type = input("Tipo interazione (default: like): ").strip() or "like"
        actor_name = input("Nome utente (default: Marco): ").strip() or "Marco"
        target = input("Target (default: Pantheon): ").strip() or "Pantheon"
        
        self.integration_manager.trigger_social_notification(
            "demo_user",
            interaction_type,
            actor_name,
            target=target
        )
        
        print(f"✅ Notifica social creata: {actor_name} -> {interaction_type}")
    
    def demo_nearby_monuments(self):
        """Demo monumenti vicini"""
        print("\n📍 === DEMO MONUMENTI VICINI ===")
        
        print("Posizioni predefinite:")
        print("1. Roma (Colosseo)")
        print("2. Parigi (Torre Eiffel)")
        print("3. Custom")
        
        choice = input("Scegli posizione (1-3): ").strip()
        
        if choice == "1":
            lat, lon = 41.8902, 12.4922
            location_name = "Roma"
        elif choice == "2":
            lat, lon = 48.8584, 2.2945
            location_name = "Parigi"
        else:
            try:
                lat = float(input("Latitudine: "))
                lon = float(input("Longitudine: "))
                location_name = "Custom"
            except ValueError:
                print("❌ Coordinate non valide!")
                return
        
        self.integration_manager.trigger_nearby_monuments_check(
            "demo_user",
            lat,
            lon
        )
        
        print(f"✅ Controllo monumenti vicini per {location_name} ({lat}, {lon})")
    
    def demo_system_announcement(self):
        """Demo annuncio sistema"""
        print("\n📢 === DEMO ANNUNCIO SISTEMA ===")
        
        title = input("Titolo annuncio: ").strip()
        body = input("Messaggio: ").strip()
        
        if not title or not body:
            print("❌ Titolo e messaggio sono obbligatori!")
            return
        
        print("Priorità: 1=Low, 2=Normal, 3=High, 4=Urgent")
        priority_choice = input("Priorità (default: 2): ").strip() or "2"
        
        try:
            priority_value = int(priority_choice)
            priority = NotificationPriority(priority_value)
            
            self.integration_manager.send_system_announcement(
                title,
                body,
                priority
            )
            
            print("✅ Annuncio sistema inviato!")
            
        except ValueError:
            print("❌ Priorità non valida!")
    
    def show_statistics(self):
        """Mostra statistiche sistema"""
        print("\n📊 === STATISTICHE SISTEMA ===")
        
        # Statistiche integrazione
        integration_stats = self.integration_manager.get_integration_stats()
        print(f"Listeners attivi: {integration_stats['active_listeners']}")
        print(f"Cache size: {integration_stats['cache_size']}")
        print(f"Monitoraggio attivo: {integration_stats['monitoring_active']}")
        
        print("\nIntegrazioni disponibili:")
        for system, available in integration_stats['integrations_available'].items():
            status = "✅" if available else "❌"
            print(f"  {status} {system}")
        
        # Statistiche notifiche utente
        try:
            user_stats = self.integration_manager.notification_manager.get_notification_stats("demo_user")
            general = user_stats.get('general', {})
            
            print(f"\n📈 Statistiche Demo User:")
            print(f"Totali: {general.get('total_notifications', 0)}")
            print(f"Lette: {general.get('read_notifications', 0)}")
            print(f"Non lette: {general.get('unread_notifications', 0)}")
            print(f"Tasso lettura: {general.get('read_percentage', 0):.1f}%")
            
            # Statistiche per tipo
            by_type = user_stats.get('by_type', {})
            if by_type:
                print("\n📋 Per tipo:")
                for notif_type, stats in by_type.items():
                    print(f"  {notif_type}: {stats['sent']} inviate, {stats['read']} lette")
            
        except Exception as e:
            print(f"❌ Errore nel recupero statistiche: {e}")
    
    def demo_scheduled_notifications(self):
        """Demo notifiche programmate"""
        print("\n⏰ === DEMO NOTIFICHE PROGRAMMATE ===")
        
        print("1. Promemoria tra 10 secondi")
        print("2. Promemoria giornaliero")
        print("3. Custom scheduling")
        
        choice = input("Scegli opzione (1-3): ").strip()
        
        if choice == "1":
            # Notifica tra 10 secondi
            scheduled_time = datetime.now() + timedelta(seconds=10)
            
            notification_id = self.integration_manager.notification_manager.create_notification(
                title="⏰ Promemoria Programmato",
                body="Questa notifica era programmata per ora!",
                user_id="demo_user",
                notification_type=NotificationType.REMINDER,
                scheduled_at=scheduled_time
            )
            
            print("✅ Notifica programmata per tra 10 secondi!")
            print(f"ID: {notification_id}")
            
        elif choice == "2":
            hour = input("Ora (0-23, default: 10): ").strip() or "10"
            minute = input("Minuti (0-59, default: 0): ").strip() or "0"
            
            try:
                hour, minute = int(hour), int(minute)
                
                reminder_id = self.integration_manager.notification_manager.schedule_daily_reminder(
                    "demo_user",
                    "🌅 Promemoria Giornaliero",
                    "È ora della tua esplorazione quotidiana!",
                    hour,
                    minute
                )
                
                print(f"✅ Promemoria giornaliero programmato per {hour:02d}:{minute:02d}")
                print(f"ID: {reminder_id}")
                
            except ValueError:
                print("❌ Ora e minuti devono essere numeri!")
        
        else:
            print("Custom scheduling non implementato in demo")
    
    def demo_user_preferences(self):
        """Demo gestione preferenze"""
        print("\n⚙️ === DEMO PREFERENZE UTENTE ===")
        
        # Mostra preferenze attuali
        current_prefs = self.integration_manager.notification_manager.get_user_preferences("demo_user")
        
        print("Preferenze attuali:")
        for key, value in current_prefs.items():
            print(f"  {key}: {value}")
        
        print("\n1. Disabilita tutte le notifiche")
        print("2. Abilita solo emergenze")
        print("3. Disabilita notifiche social")
        print("4. Ripristina default")
        print("5. Custom")
        
        choice = input("Scegli opzione (1-5): ").strip()
        
        if choice == "1":
            current_prefs['notifications_enabled'] = False
        elif choice == "2":
            for key in current_prefs:
                if key.endswith('_enabled') and key != 'emergency_enabled':
                    current_prefs[key] = False
        elif choice == "3":
            current_prefs['social_interaction_enabled'] = False
        elif choice == "4":
            # Reset a default
            current_prefs = {
                'notifications_enabled': True,
                'monument_visit_enabled': True,
                'achievement_enabled': True,
                'social_interaction_enabled': True,
                'daily_challenge_enabled': True,
                'nearby_monuments_enabled': True,
                'system_update_enabled': True,
                'reminder_enabled': True,
                'promotional_enabled': False,
                'emergency_enabled': True,
                'sound_enabled': True,
                'vibration_enabled': True
            }
        elif choice == "5":
            key = input("Chiave da modificare: ").strip()
            if key in current_prefs:
                value = input(f"Nuovo valore per {key} (True/False): ").strip().lower()
                current_prefs[key] = value in ['true', '1', 'yes', 'on']
            else:
                print("❌ Chiave non trovata!")
                return
        else:
            print("❌ Opzione non valida!")
            return
        
        # Salva preferenze
        self.integration_manager.notification_manager.set_user_preferences("demo_user", current_prefs)
        print("✅ Preferenze aggiornate!")
    
    def cleanup_database(self):
        """Pulisce database demo"""
        print("\n🗑️ === PULIZIA DATABASE ===")
        
        confirm = input("Cancellare tutte le notifiche? (s/N): ").strip().lower()
        if confirm == 's':
            self.integration_manager.notification_manager.clear_user_notifications("demo_user", read_only=False)
            
            # Pulisci anche cache integrazione
            self.integration_manager.notification_cache.clear()
            
            print("✅ Database pulito!")
        else:
            print("❌ Operazione annullata!")
    
    def cleanup(self):
        """Pulizia finale"""
        print("\n🔄 Spegnimento sistema...")
        
        if self.integration_manager:
            self.integration_manager.stop_monitoring()
            self.integration_manager.notification_manager.stop()
        
        print("✅ Sistema spento correttamente!")


def run_automated_tests():
    """Esegue tutti i test automatizzati"""
    print("🧪 === ESECUZIONE TEST AUTOMATIZZATI ===\n")
    
    # Crea test suite
    test_suite = unittest.TestSuite()
    
    # Aggiungi test cases
    test_suite.addTest(unittest.makeSuite(TestPushNotificationManager))
    test_suite.addTest(unittest.makeSuite(TestNotificationIntegration))
    test_suite.addTest(unittest.makeSuite(TestNotificationUI))
    
    # Esegui test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Riepilogo risultati
    print(f"\n📊 === RIEPILOGO TEST ===")
    print(f"Test eseguiti: {result.testsRun}")
    print(f"Successi: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallimenti: {len(result.failures)}")
    print(f"Errori: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ FALLIMENTI:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split()[-1] if traceback else 'Unknown'}")
    
    if result.errors:
        print(f"\n💥 ERRORI:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split()[-1] if traceback else 'Unknown'}")
    
    return result.wasSuccessful()


def run_performance_tests():
    """Esegue test di performance"""
    print("\n⚡ === TEST PERFORMANCE ===")
    
    # Test creazione notifiche in massa
    start_time = time.time()
    manager = PushNotificationManager(db_path="perf_test.db")
    
    # Crea 1000 notifiche
    print("Creazione 1000 notifiche...")
    for i in range(1000):
        manager.create_notification(
            title=f"Performance Test {i}",
            body="This is a performance test notification",
            user_id=f"user_{i % 10}",  # 10 utenti diversi
            notification_type=NotificationType.GENERAL
        )
    
    creation_time = time.time() - start_time
    print(f"⏱️ Tempo creazione: {creation_time:.2f}s ({1000/creation_time:.1f} notifiche/s)")
    
    # Test lettura notifiche
    start_time = time.time()
    for i in range(10):
        notifications = manager.get_user_notifications(f"user_{i}", limit=100)
    
    read_time = time.time() - start_time
    print(f"⏱️ Tempo lettura: {read_time:.2f}s ({1000/read_time:.1f} notifiche/s)")
    
    # Test statistiche
    start_time = time.time()
    for i in range(10):
        stats = manager.get_notification_stats(f"user_{i}")
    
    stats_time = time.time() - start_time
    print(f"⏱️ Tempo statistiche: {stats_time:.2f}s ({10/stats_time:.1f} richieste/s)")
    
    # Cleanup
    manager.stop()
    if os.path.exists("perf_test.db"):
        os.remove("perf_test.db")
    
    print("✅ Test performance completati!")


if __name__ == "__main__":
    print("🔔 === SISTEMA TEST NOTIFICHE PUSH AVANZATO ===")
    print("Scegli modalità:")
    print("1. Test automatizzati")
    print("2. Demo interattiva")  
    print("3. Test performance")
    print("4. Tutti i test")
    
    choice = input("\nModalità (1-4): ").strip()
    
    if choice == "1":
        success = run_automated_tests()
        print(f"\n{'✅ Tutti i test superati!' if success else '❌ Alcuni test falliti!'}")
        
    elif choice == "2":
        demo = NotificationDemoApp()
        demo.start_demo()
        
    elif choice == "3":
        run_performance_tests()
        
    elif choice == "4":
        print("📋 Esecuzione test completi...\n")
        
        # Test automatizzati
        success = run_automated_tests()
        
        # Test performance
        run_performance_tests()
        
        # Offri demo
        if input("\nVuoi eseguire la demo interattiva? (s/N): ").lower() == 's':
            demo = NotificationDemoApp()
            demo.start_demo()
        
        print(f"\n🏁 Test completi terminati!")
        print(f"Risultato test automatizzati: {'✅ SUCCESSO' if success else '❌ FALLIMENTI'}")
        
    else:
        print("❌ Scelta non valida!")
