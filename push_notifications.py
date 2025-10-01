"""
Sistema Notifiche Push Avanzato per MonumentRecognizer
Supporta notifiche locali, remote, scheduling e categorizzazione intelligente.
"""

import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import requests
import schedule
from plyer import notification
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Tipi di notifiche supportate"""
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
    """Priorità delle notifiche"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class PushNotification:
    """Struttura dati per notifiche push"""
    id: str
    title: str
    body: str
    notification_type: NotificationType
    priority: NotificationPriority
    user_id: str
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    data: Optional[Dict] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    category: Optional[str] = None
    sound: Optional[str] = None
    badge_count: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Converte in dizionario per serializzazione"""
        data = asdict(self)
        # Converte enum in stringhe
        data['notification_type'] = self.notification_type.value
        data['priority'] = self.priority.value
        # Converte datetime in ISO string
        data['created_at'] = self.created_at.isoformat()
        if self.scheduled_at:
            data['scheduled_at'] = self.scheduled_at.isoformat()
        if self.delivered_at:
            data['delivered_at'] = self.delivered_at.isoformat()
        if self.read_at:
            data['read_at'] = self.read_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PushNotification':
        """Crea istanza da dizionario"""
        data['notification_type'] = NotificationType(data['notification_type'])
        data['priority'] = NotificationPriority(data['priority'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data['scheduled_at']:
            data['scheduled_at'] = datetime.fromisoformat(data['scheduled_at'])
        if data['delivered_at']:
            data['delivered_at'] = datetime.fromisoformat(data['delivered_at'])
        if data['read_at']:
            data['read_at'] = datetime.fromisoformat(data['read_at'])
        return cls(**data)


class NotificationTemplate:
    """Template per notifiche personalizzate"""
    
    TEMPLATES = {
        NotificationType.MONUMENT_VISIT: {
            "title": "🏛️ Nuovo Monumento Scoperto!",
            "body": "Hai visitato {monument_name}! Guadagnati {points} punti!",
            "sound": "monument_discovery.mp3"
        },
        NotificationType.ACHIEVEMENT: {
            "title": "🏆 Achievement Sbloccato!",
            "body": "Complimenti! Hai ottenuto: {achievement_name}",
            "sound": "achievement_unlock.mp3"
        },
        NotificationType.SOCIAL_INTERACTION: {
            "title": "👥 Nuova Interazione Social",
            "body": "{user_name} ha {action} il tuo post su {monument_name}",
            "sound": "social_ping.mp3"
        },
        NotificationType.DAILY_CHALLENGE: {
            "title": "🎯 Sfida Giornaliera",
            "body": "Nuova sfida disponibile: {challenge_name}. Ricompensa: {reward}",
            "sound": "challenge_notification.mp3"
        },
        NotificationType.NEARBY_MONUMENTS: {
            "title": "📍 Monumenti Vicini",
            "body": "Ci sono {count} monumenti entro {distance}km da te!",
            "sound": "proximity_alert.mp3"
        },
        NotificationType.REMINDER: {
            "title": "⏰ Promemoria",
            "body": "{reminder_text}",
            "sound": "gentle_reminder.mp3"
        }
    }
    
    @classmethod
    def get_template(cls, notification_type: NotificationType, **kwargs) -> Dict[str, str]:
        """Ottiene template personalizzato per tipo notifica"""
        template = cls.TEMPLATES.get(notification_type, {
            "title": "Monument Recognizer",
            "body": "Nuova notifica disponibile",
            "sound": "default.mp3"
        })
        
        # Sostituisce placeholder con valori reali
        formatted_template = {}
        for key, value in template.items():
            if isinstance(value, str):
                try:
                    formatted_template[key] = value.format(**kwargs)
                except KeyError:
                    formatted_template[key] = value
            else:
                formatted_template[key] = value
                
        return formatted_template


class PushNotificationManager:
    """Manager principale per sistema notifiche push"""
    
    def __init__(self, db_path: str = "notifications.db"):
        self.db_path = db_path
        self.listeners: Dict[str, List[Callable]] = {}
        self.firebase_config: Dict = {}
        self.user_preferences: Dict[str, Dict] = {}
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # Inizializza database
        self._init_database()
        
        # Avvia scheduler per notifiche programmate
        self._start_scheduler()
        
        logger.info("PushNotificationManager inizializzato")
    
    def _init_database(self):
        """Inizializza il database SQLite per notifiche"""
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
                    scheduled_at TEXT,
                    delivered_at TEXT,
                    read_at TEXT,
                    data TEXT,
                    image_url TEXT,
                    action_url TEXT,
                    category TEXT,
                    sound TEXT,
                    badge_count INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notification_stats (
                    user_id TEXT,
                    notification_type TEXT,
                    total_sent INTEGER DEFAULT 0,
                    total_read INTEGER DEFAULT 0,
                    last_sent TEXT,
                    PRIMARY KEY (user_id, notification_type)
                )
            """)
    
    def _start_scheduler(self):
        """Avvia il thread per gestire notifiche programmate"""
        if not self.scheduler_running:
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
    
    def _run_scheduler(self):
        """Esegue lo scheduler per notifiche programmate"""
        while self.scheduler_running:
            try:
                # Controlla notifiche da inviare
                self._process_scheduled_notifications()
                time.sleep(60)  # Controlla ogni minuto
            except Exception as e:
                logger.error(f"Errore nello scheduler: {e}")
                time.sleep(60)
    
    def _process_scheduled_notifications(self):
        """Processa notifiche programmate da inviare"""
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM notifications 
                WHERE scheduled_at <= ? AND delivered_at IS NULL
            """, (now.isoformat(),))
            
            for row in cursor.fetchall():
                try:
                    notification = self._row_to_notification(row)
                    self._deliver_notification(notification)
                    
                    # Aggiorna stato come consegnata
                    conn.execute("""
                        UPDATE notifications 
                        SET delivered_at = ? 
                        WHERE id = ?
                    """, (now.isoformat(), notification.id))
                    
                except Exception as e:
                    logger.error(f"Errore nella consegna notifica {row[0]}: {e}")
    
    def _row_to_notification(self, row) -> PushNotification:
        """Converte riga database in oggetto PushNotification"""
        return PushNotification(
            id=row[0],
            title=row[1],
            body=row[2],
            notification_type=NotificationType(row[3]),
            priority=NotificationPriority(row[4]),
            user_id=row[5],
            created_at=datetime.fromisoformat(row[6]),
            scheduled_at=datetime.fromisoformat(row[7]) if row[7] else None,
            delivered_at=datetime.fromisoformat(row[8]) if row[8] else None,
            read_at=datetime.fromisoformat(row[9]) if row[9] else None,
            data=json.loads(row[10]) if row[10] else None,
            image_url=row[11],
            action_url=row[12],
            category=row[13],
            sound=row[14],
            badge_count=row[15]
        )
    
    def create_notification(
        self,
        title: str,
        body: str,
        user_id: str,
        notification_type: NotificationType = NotificationType.GENERAL,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
        data: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """Crea una nuova notifica"""
        
        notification_id = str(uuid.uuid4())
        
        notification = PushNotification(
            id=notification_id,
            title=title,
            body=body,
            notification_type=notification_type,
            priority=priority,
            user_id=user_id,
            created_at=datetime.now(),
            scheduled_at=scheduled_at,
            data=data,
            **{k: v for k, v in kwargs.items() if k in [
                'image_url', 'action_url', 'category', 'sound', 'badge_count'
            ]}
        )
        
        # Salva nel database
        self._save_notification(notification)
        
        # Se non è programmata, consegnala subito
        if scheduled_at is None:
            self._deliver_notification(notification)
            notification.delivered_at = datetime.now()
            self._update_notification_delivery(notification_id, notification.delivered_at)
        
        logger.info(f"Notifica creata: {notification_id}")
        return notification_id
    
    def create_templated_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        template_data: Dict,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """Crea notifica usando template predefinito"""
        
        template = NotificationTemplate.get_template(notification_type, **template_data)
        
        return self.create_notification(
            title=template['title'],
            body=template['body'],
            user_id=user_id,
            notification_type=notification_type,
            priority=priority,
            scheduled_at=scheduled_at,
            sound=template.get('sound'),
            data=template_data
        )
    
    def _save_notification(self, notification: PushNotification):
        """Salva notifica nel database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO notifications 
                (id, title, body, notification_type, priority, user_id, created_at, 
                 scheduled_at, delivered_at, read_at, data, image_url, action_url, 
                 category, sound, badge_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification.id,
                notification.title,
                notification.body,
                notification.notification_type.value,
                notification.priority.value,
                notification.user_id,
                notification.created_at.isoformat(),
                notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                notification.delivered_at.isoformat() if notification.delivered_at else None,
                notification.read_at.isoformat() if notification.read_at else None,
                json.dumps(notification.data) if notification.data else None,
                notification.image_url,
                notification.action_url,
                notification.category,
                notification.sound,
                notification.badge_count
            ))
    
    def _update_notification_delivery(self, notification_id: str, delivered_at: datetime):
        """Aggiorna timestamp di consegna notifica"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE notifications 
                SET delivered_at = ? 
                WHERE id = ?
            """, (delivered_at.isoformat(), notification_id))
    
    def _deliver_notification(self, notification: PushNotification):
        """Consegna la notifica all'utente"""
        
        # Verifica preferenze utente
        if not self._should_deliver_notification(notification):
            logger.info(f"Notifica {notification.id} bloccata dalle preferenze utente")
            return
        
        try:
            # Notifica locale tramite plyer
            notification.notify(
                title=notification.title,
                message=notification.body,
                timeout=10,
                toast=True
            )
            
            # Chiama listeners registrati
            self._call_listeners(notification)
            
            # Aggiorna statistiche
            self._update_notification_stats(notification)
            
            logger.info(f"Notifica consegnata: {notification.id}")
            
        except Exception as e:
            logger.error(f"Errore nella consegna notifica {notification.id}: {e}")
    
    def _should_deliver_notification(self, notification: PushNotification) -> bool:
        """Verifica se la notifica deve essere consegnata in base alle preferenze utente"""
        prefs = self.get_user_preferences(notification.user_id)
        
        # Controllo globale notifiche
        if not prefs.get('notifications_enabled', True):
            return False
        
        # Controllo per tipo di notifica
        type_key = f"{notification.notification_type.value}_enabled"
        if not prefs.get(type_key, True):
            return False
        
        # Controllo orari non disturbare
        now = datetime.now().time()
        quiet_start = prefs.get('quiet_hours_start')
        quiet_end = prefs.get('quiet_hours_end')
        
        if quiet_start and quiet_end:
            if quiet_start <= now <= quiet_end:
                # Consegna solo notifiche urgenti durante quiet hours
                return notification.priority == NotificationPriority.URGENT
        
        return True
    
    def _call_listeners(self, notification: PushNotification):
        """Chiama i listener registrati per la notifica"""
        for listener_type in [notification.notification_type.value, 'all']:
            if listener_type in self.listeners:
                for callback in self.listeners[listener_type]:
                    try:
                        callback(notification)
                    except Exception as e:
                        logger.error(f"Errore nel listener {callback}: {e}")
    
    def _update_notification_stats(self, notification: PushNotification):
        """Aggiorna statistiche notifiche"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO notification_stats 
                (user_id, notification_type, total_sent, total_read, last_sent)
                VALUES (
                    ?, ?, 
                    COALESCE((SELECT total_sent FROM notification_stats 
                             WHERE user_id = ? AND notification_type = ?), 0) + 1,
                    COALESCE((SELECT total_read FROM notification_stats 
                             WHERE user_id = ? AND notification_type = ?), 0),
                    ?
                )
            """, (
                notification.user_id,
                notification.notification_type.value,
                notification.user_id,
                notification.notification_type.value,
                notification.user_id,
                notification.notification_type.value,
                datetime.now().isoformat()
            ))
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Marca notifica come letta"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE notifications 
                    SET read_at = ? 
                    WHERE id = ? AND read_at IS NULL
                """, (datetime.now().isoformat(), notification_id))
                
                if cursor.rowcount > 0:
                    # Aggiorna statistiche lettura
                    conn.execute("""
                        UPDATE notification_stats 
                        SET total_read = total_read + 1
                        WHERE user_id = (SELECT user_id FROM notifications WHERE id = ?)
                        AND notification_type = (SELECT notification_type FROM notifications WHERE id = ?)
                    """, (notification_id, notification_id))
                    
                    logger.info(f"Notifica {notification_id} marcata come letta")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Errore nel marcare notifica come letta: {e}")
            return False
    
    def get_user_notifications(
        self, 
        user_id: str, 
        limit: int = 50,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None
    ) -> List[PushNotification]:
        """Ottiene notifiche per un utente"""
        
        query = "SELECT * FROM notifications WHERE user_id = ?"
        params = [user_id]
        
        if unread_only:
            query += " AND read_at IS NULL"
            
        if notification_type:
            query += " AND notification_type = ?"
            params.append(notification_type.value)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        notifications = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor.fetchall():
                notifications.append(self._row_to_notification(row))
        
        return notifications
    
    def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """Ottiene statistiche notifiche per utente"""
        stats = {}
        
        with sqlite3.connect(self.db_path) as conn:
            # Statistiche generali
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN read_at IS NOT NULL THEN 1 END) as read,
                    COUNT(CASE WHEN read_at IS NULL THEN 1 END) as unread
                FROM notifications 
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            stats['general'] = {
                'total_notifications': result[0],
                'read_notifications': result[1],
                'unread_notifications': result[2],
                'read_percentage': (result[1] / result[0] * 100) if result[0] > 0 else 0
            }
            
            # Statistiche per tipo
            cursor = conn.execute("""
                SELECT notification_type, total_sent, total_read
                FROM notification_stats
                WHERE user_id = ?
            """, (user_id,))
            
            stats['by_type'] = {}
            for row in cursor.fetchall():
                stats['by_type'][row[0]] = {
                    'sent': row[1],
                    'read': row[2],
                    'read_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0
                }
        
        return stats
    
    def set_user_preferences(self, user_id: str, preferences: Dict):
        """Imposta preferenze notifiche per utente"""
        self.user_preferences[user_id] = preferences
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_preferences (user_id, preferences)
                VALUES (?, ?)
            """, (user_id, json.dumps(preferences)))
        
        logger.info(f"Preferenze aggiornate per utente {user_id}")
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Ottiene preferenze notifiche utente"""
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT preferences FROM user_preferences WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                prefs = json.loads(result[0])
                self.user_preferences[user_id] = prefs
                return prefs
        
        # Preferenze predefinite
        default_prefs = {
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
            'quiet_hours_start': None,
            'quiet_hours_end': None,
            'sound_enabled': True,
            'vibration_enabled': True
        }
        
        self.set_user_preferences(user_id, default_prefs)
        return default_prefs
    
    def add_listener(self, notification_type: str, callback: Callable):
        """Aggiunge listener per notifiche"""
        if notification_type not in self.listeners:
            self.listeners[notification_type] = []
        
        self.listeners[notification_type].append(callback)
        logger.info(f"Listener aggiunto per tipo: {notification_type}")
    
    def remove_listener(self, notification_type: str, callback: Callable):
        """Rimuove listener per notifiche"""
        if notification_type in self.listeners:
            try:
                self.listeners[notification_type].remove(callback)
                logger.info(f"Listener rimosso per tipo: {notification_type}")
            except ValueError:
                logger.warning(f"Listener non trovato per tipo: {notification_type}")
    
    def schedule_daily_reminder(
        self, 
        user_id: str, 
        title: str, 
        body: str, 
        hour: int, 
        minute: int = 0
    ) -> str:
        """Programma promemoria giornaliero"""
        
        # Calcola prossima occorrenza
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Se l'orario è già passato oggi, programma per domani
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)
        
        return self.create_notification(
            title=title,
            body=body,
            user_id=user_id,
            notification_type=NotificationType.REMINDER,
            scheduled_at=scheduled_time,
            data={'recurring': 'daily', 'hour': hour, 'minute': minute}
        )
    
    def cancel_notification(self, notification_id: str) -> bool:
        """Cancella notifica programmata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM notifications 
                    WHERE id = ? AND delivered_at IS NULL
                """, (notification_id,))
                
                if cursor.rowcount > 0:
                    logger.info(f"Notifica {notification_id} cancellata")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Errore nella cancellazione notifica: {e}")
            return False
    
    def clear_user_notifications(self, user_id: str, read_only: bool = True):
        """Pulisce notifiche utente"""
        try:
            query = "DELETE FROM notifications WHERE user_id = ?"
            params = [user_id]
            
            if read_only:
                query += " AND read_at IS NOT NULL"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                count = cursor.rowcount
                
            logger.info(f"Rimosse {count} notifiche per utente {user_id}")
            
        except Exception as e:
            logger.error(f"Errore nella pulizia notifiche: {e}")
    
    def get_unread_count(self, user_id: str) -> int:
        """Ottiene conteggio notifiche non lette"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM notifications 
                WHERE user_id = ? AND read_at IS NULL
            """, (user_id,))
            
            return cursor.fetchone()[0]
    
    def configure_firebase(self, config: Dict):
        """Configura Firebase Cloud Messaging"""
        self.firebase_config = config
        logger.info("Firebase Cloud Messaging configurato")
    
    def send_fcm_notification(
        self, 
        device_tokens: List[str], 
        notification: PushNotification
    ) -> bool:
        """Invia notifica tramite Firebase Cloud Messaging"""
        if not self.firebase_config:
            logger.error("Firebase non configurato")
            return False
        
        try:
            payload = {
                "registration_ids": device_tokens,
                "notification": {
                    "title": notification.title,
                    "body": notification.body,
                    "sound": notification.sound or "default",
                    "badge": notification.badge_count
                },
                "data": notification.data or {}
            }
            
            headers = {
                "Authorization": f"key={self.firebase_config.get('server_key')}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://fcm.googleapis.com/fcm/send",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Notifica FCM inviata con successo: {notification.id}")
                return True
            else:
                logger.error(f"Errore FCM: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Errore nell'invio FCM: {e}")
            return False
    
    def cleanup_old_notifications(self, days_old: int = 30):
        """Rimuove notifiche vecchie"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM notifications 
                WHERE created_at < ? AND read_at IS NOT NULL
            """, (cutoff_date.isoformat(),))
            
            count = cursor.rowcount
            logger.info(f"Rimosse {count} notifiche vecchie")
    
    def stop(self):
        """Ferma il manager notifiche"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("PushNotificationManager fermato")


# Utility functions per integrazione facile
def create_quick_notification(title: str, body: str, user_id: str) -> str:
    """Crea rapidamente una notifica semplice"""
    manager = PushNotificationManager()
    return manager.create_notification(title, body, user_id)


def notify_monument_visit(user_id: str, monument_name: str, points: int) -> str:
    """Notifica visita monumento"""
    manager = PushNotificationManager()
    return manager.create_templated_notification(
        user_id=user_id,
        notification_type=NotificationType.MONUMENT_VISIT,
        template_data={
            'monument_name': monument_name,
            'points': points
        }
    )


def notify_achievement_unlock(user_id: str, achievement_name: str) -> str:
    """Notifica achievement sbloccato"""
    manager = PushNotificationManager()
    return manager.create_templated_notification(
        user_id=user_id,
        notification_type=NotificationType.ACHIEVEMENT,
        template_data={
            'achievement_name': achievement_name
        },
        priority=NotificationPriority.HIGH
    )


if __name__ == "__main__":
    # Test del sistema notifiche
    manager = PushNotificationManager()
    
    # Crea notifica di test
    notification_id = manager.create_notification(
        title="🏛️ Benvenuto in Monument Recognizer!",
        body="Inizia la tua avventura alla scoperta dei monumenti!",
        user_id="test_user",
        notification_type=NotificationType.GENERAL,
        priority=NotificationPriority.HIGH
    )
    
    print(f"Notifica di test creata: {notification_id}")
    
    # Test template
    temple_notification = notify_monument_visit("test_user", "Colosseo", 100)
    print(f"Notifica tempio creata: {temple_notification}")
    
    # Mostra statistiche
    stats = manager.get_notification_stats("test_user")
    print(f"Statistiche: {json.dumps(stats, indent=2)}")
    
    # Ferma manager
    time.sleep(2)
    manager.stop()
