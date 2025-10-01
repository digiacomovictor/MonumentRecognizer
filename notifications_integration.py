"""
Integrazione Sistema Notifiche con Sistemi Esistenti
Collega il sistema notifiche push con gamification, social, visite monumenti, GPS e utenti.
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import logging

# Import dei sistemi esistenti
from push_notifications import (
    PushNotificationManager, 
    NotificationType, 
    NotificationPriority,
    notify_monument_visit,
    notify_achievement_unlock
)

# Simulazione import dei sistemi esistenti (sostituire con import reali)
try:
    from gamification import GamificationManager
    from social_sharing import SocialManager
    from user_system import UserSystem
    from gps_manager import GPSManager
    from visit_tracker import VisitTracker
    from monument_recognizer import MonumentRecognizer
    SYSTEMS_AVAILABLE = True
except ImportError:
    SYSTEMS_AVAILABLE = False
    print("Alcuni sistemi non sono disponibili per l'integrazione completa")

logger = logging.getLogger(__name__)


class NotificationIntegrationManager:
    """Manager per integrare notifiche con tutti i sistemi esistenti"""
    
    def __init__(self, 
                 notification_manager: PushNotificationManager,
                 gamification_manager=None,
                 social_manager=None,
                 user_system=None,
                 gps_manager=None,
                 visit_tracker=None,
                 monument_recognizer=None):
        
        self.notification_manager = notification_manager
        self.gamification_manager = gamification_manager
        self.social_manager = social_manager
        self.user_system = user_system
        self.gps_manager = gps_manager
        self.visit_tracker = visit_tracker
        self.monument_recognizer = monument_recognizer
        
        # Listeners attivi
        self.active_listeners = []
        
        # Cache per evitare notifiche duplicate
        self.notification_cache = {}
        
        # Thread per monitoraggio continuo
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Inizializza integrazioni
        self.setup_integrations()
        
        logger.info("NotificationIntegrationManager inizializzato")
    
    def setup_integrations(self):
        """Configura tutte le integrazioni disponibili"""
        
        # Integrazione Gamification
        if self.gamification_manager:
            self.setup_gamification_integration()
        
        # Integrazione Social
        if self.social_manager:
            self.setup_social_integration()
        
        # Integrazione GPS e Monumenti Vicini
        if self.gps_manager:
            self.setup_gps_integration()
        
        # Integrazione Visite Monumenti
        if self.visit_tracker and self.monument_recognizer:
            self.setup_monument_visits_integration()
        
        # Integrazione Sistema Utenti
        if self.user_system:
            self.setup_user_system_integration()
        
        # Avvia monitoraggio continuo
        self.start_monitoring()
    
    def setup_gamification_integration(self):
        """Integra notifiche con sistema gamification"""
        
        def on_achievement_unlock(user_id: str, achievement_data: Dict):
            """Notifica achievement sbloccato"""
            try:
                self.notification_manager.create_templated_notification(
                    user_id=user_id,
                    notification_type=NotificationType.ACHIEVEMENT,
                    template_data={
                        'achievement_name': achievement_data.get('name', 'Achievement'),
                        'achievement_description': achievement_data.get('description', ''),
                        'points_earned': achievement_data.get('points', 0)
                    },
                    priority=NotificationPriority.HIGH,
                    data=achievement_data
                )
                
                logger.info(f"Notifica achievement inviata per {user_id}")
                
            except Exception as e:
                logger.error(f"Errore notifica achievement: {e}")
        
        def on_level_up(user_id: str, level_data: Dict):
            """Notifica level up"""
            try:
                self.notification_manager.create_notification(
                    title=f"🎉 Livello {level_data.get('new_level', '?')} Raggiunto!",
                    body=f"Complimenti! Hai raggiunto il livello {level_data.get('new_level', '?')}!",
                    user_id=user_id,
                    notification_type=NotificationType.ACHIEVEMENT,
                    priority=NotificationPriority.HIGH,
                    data=level_data
                )
                
                logger.info(f"Notifica level up inviata per {user_id}")
                
            except Exception as e:
                logger.error(f"Errore notifica level up: {e}")
        
        def on_points_earned(user_id: str, points_data: Dict):
            """Notifica punti guadagnati (solo per grandi quantità)"""
            points = points_data.get('points', 0)
            
            # Solo per punti significativi (>= 50)
            if points >= 50:
                try:
                    self.notification_manager.create_notification(
                        title=f"💎 {points} Punti Guadagnati!",
                        body=f"Hai guadagnato {points} punti da: {points_data.get('source', 'attività')}",
                        user_id=user_id,
                        notification_type=NotificationType.ACHIEVEMENT,
                        priority=NotificationPriority.NORMAL,
                        data=points_data
                    )
                    
                    logger.info(f"Notifica punti inviata per {user_id}: {points}")
                    
                except Exception as e:
                    logger.error(f"Errore notifica punti: {e}")
        
        def check_daily_challenges(user_id: str):
            """Controlla e notifica sfide giornaliere"""
            try:
                challenges = self.gamification_manager.get_daily_challenges(user_id)
                
                for challenge in challenges:
                    if challenge.get('status') == 'new':
                        self.notification_manager.create_templated_notification(
                            user_id=user_id,
                            notification_type=NotificationType.DAILY_CHALLENGE,
                            template_data={
                                'challenge_name': challenge.get('name', 'Sfida'),
                                'reward': f"{challenge.get('points', 0)} punti"
                            },
                            priority=NotificationPriority.NORMAL,
                            data=challenge
                        )
                
                logger.info(f"Controllo sfide giornaliere per {user_id}")
                
            except Exception as e:
                logger.error(f"Errore controllo sfide: {e}")
        
        # Registra listeners per gamification (simulato)
        self.active_listeners.extend([
            ('achievement_unlock', on_achievement_unlock),
            ('level_up', on_level_up), 
            ('points_earned', on_points_earned),
            ('daily_challenges', check_daily_challenges)
        ])
        
        logger.info("Integrazione gamification configurata")
    
    def setup_social_integration(self):
        """Integra notifiche con sistema social"""
        
        def on_social_interaction(user_id: str, interaction_data: Dict):
            """Notifica interazione social"""
            try:
                interaction_type = interaction_data.get('type', 'interaction')
                actor = interaction_data.get('actor_name', 'Qualcuno')
                target = interaction_data.get('target', 'il tuo post')
                
                action_map = {
                    'like': 'ha messo like a',
                    'comment': 'ha commentato',
                    'share': 'ha condiviso',
                    'follow': 'ti sta seguendo'
                }
                
                action_text = action_map.get(interaction_type, 'ha interagito con')
                
                self.notification_manager.create_templated_notification(
                    user_id=user_id,
                    notification_type=NotificationType.SOCIAL_INTERACTION,
                    template_data={
                        'user_name': actor,
                        'action': action_text,
                        'monument_name': target
                    },
                    priority=NotificationPriority.NORMAL,
                    data=interaction_data
                )
                
                logger.info(f"Notifica social inviata per {user_id}: {interaction_type}")
                
            except Exception as e:
                logger.error(f"Errore notifica social: {e}")
        
        def on_milestone_reached(user_id: str, milestone_data: Dict):
            """Notifica milestone social raggiunti"""
            try:
                milestone_type = milestone_data.get('type', 'milestone')
                count = milestone_data.get('count', 0)
                
                milestone_messages = {
                    'followers': f"🎉 Hai raggiunto {count} follower!",
                    'likes': f"❤️ I tuoi post hanno ricevuto {count} like!",
                    'posts': f"📸 Hai condiviso {count} monumenti!"
                }
                
                message = milestone_messages.get(milestone_type, f"Milestone raggiunto: {count}")
                
                self.notification_manager.create_notification(
                    title="🏆 Milestone Social Raggiunto!",
                    body=message,
                    user_id=user_id,
                    notification_type=NotificationType.SOCIAL_INTERACTION,
                    priority=NotificationPriority.HIGH,
                    data=milestone_data
                )
                
                logger.info(f"Notifica milestone social per {user_id}: {milestone_type}")
                
            except Exception as e:
                logger.error(f"Errore notifica milestone social: {e}")
        
        # Registra listeners social
        self.active_listeners.extend([
            ('social_interaction', on_social_interaction),
            ('social_milestone', on_milestone_reached)
        ])
        
        logger.info("Integrazione social configurata")
    
    def setup_gps_integration(self):
        """Integra notifiche con GPS per monumenti vicini"""
        
        def check_nearby_monuments(user_id: str, location_data: Dict):
            """Controlla monumenti nelle vicinanze"""
            try:
                # Simula ricerca monumenti vicini
                lat = location_data.get('latitude', 0)
                lon = location_data.get('longitude', 0)
                
                # Cache key per evitare troppe notifiche
                cache_key = f"nearby_{user_id}_{lat:.2f}_{lon:.2f}"
                
                # Controlla cache (evita notifiche multiple nello stesso posto)
                if cache_key in self.notification_cache:
                    last_time = self.notification_cache[cache_key]
                    if datetime.now() - last_time < timedelta(hours=2):
                        return
                
                # Simula monumenti trovati (in caso reale, usa GPS manager)
                nearby_monuments = self.find_nearby_monuments(lat, lon)
                
                if nearby_monuments and len(nearby_monuments) > 0:
                    distance = location_data.get('accuracy', 1.0)
                    
                    self.notification_manager.create_templated_notification(
                        user_id=user_id,
                        notification_type=NotificationType.NEARBY_MONUMENTS,
                        template_data={
                            'count': len(nearby_monuments),
                            'distance': f"{distance:.1f}"
                        },
                        priority=NotificationPriority.LOW,
                        data={
                            'monuments': nearby_monuments,
                            'location': location_data
                        }
                    )
                    
                    # Aggiorna cache
                    self.notification_cache[cache_key] = datetime.now()
                    
                    logger.info(f"Notifica monumenti vicini per {user_id}: {len(nearby_monuments)} monumenti")
                
            except Exception as e:
                logger.error(f"Errore controllo monumenti vicini: {e}")
        
        def on_location_update(user_id: str, location_data: Dict):
            """Gestisce aggiornamenti posizione"""
            # Pianifica controllo monumenti vicini
            threading.Thread(
                target=check_nearby_monuments,
                args=(user_id, location_data),
                daemon=True
            ).start()
        
        # Registra listener GPS
        self.active_listeners.append(('location_update', on_location_update))
        
        logger.info("Integrazione GPS configurata")
    
    def setup_monument_visits_integration(self):
        """Integra notifiche con visite ai monumenti"""
        
        def on_monument_visit(user_id: str, visit_data: Dict):
            """Notifica visita monumento"""
            try:
                monument_name = visit_data.get('monument_name', 'Monumento')
                points_earned = visit_data.get('points_earned', 0)
                
                # Notifica visita
                notify_monument_visit(user_id, monument_name, points_earned)
                
                # Controlla se è la prima visita
                if visit_data.get('first_visit', False):
                    self.notification_manager.create_notification(
                        title="🎯 Prima Visita!",
                        body=f"È la tua prima volta al {monument_name}! Bonus: {points_earned * 2} punti!",
                        user_id=user_id,
                        notification_type=NotificationType.ACHIEVEMENT,
                        priority=NotificationPriority.HIGH,
                        data=visit_data
                    )
                
                # Controlla streak di visite
                streak = visit_data.get('visit_streak', 0)
                if streak > 0 and streak % 5 == 0:  # Ogni 5 visite consecutive
                    self.notification_manager.create_notification(
                        title=f"🔥 Streak di {streak} Visite!",
                        body=f"Incredibile! Hai visitato {streak} monumenti di fila!",
                        user_id=user_id,
                        notification_type=NotificationType.ACHIEVEMENT,
                        priority=NotificationPriority.HIGH,
                        data={'streak': streak, 'bonus_points': streak * 10}
                    )
                
                logger.info(f"Notifiche visita monumento per {user_id}: {monument_name}")
                
            except Exception as e:
                logger.error(f"Errore notifica visita monumento: {e}")
        
        def on_monument_recognized(user_id: str, recognition_data: Dict):
            """Notifica riconoscimento monumento"""
            try:
                monument_name = recognition_data.get('monument_name', 'Monumento')
                confidence = recognition_data.get('confidence', 0)
                
                # Solo per riconoscimenti con alta confidenza
                if confidence >= 0.8:
                    self.notification_manager.create_notification(
                        title=f"📸 {monument_name} Riconosciuto!",
                        body=f"Riconoscimento: {confidence*100:.0f}% di certezza. Tocca per saperne di più!",
                        user_id=user_id,
                        notification_type=NotificationType.GENERAL,
                        priority=NotificationPriority.NORMAL,
                        data=recognition_data
                    )
                    
                    logger.info(f"Notifica riconoscimento per {user_id}: {monument_name}")
                
            except Exception as e:
                logger.error(f"Errore notifica riconoscimento: {e}")
        
        # Registra listeners visite
        self.active_listeners.extend([
            ('monument_visit', on_monument_visit),
            ('monument_recognized', on_monument_recognized)
        ])
        
        logger.info("Integrazione visite monumenti configurata")
    
    def setup_user_system_integration(self):
        """Integra notifiche con sistema utenti"""
        
        def on_user_login(user_id: str, login_data: Dict):
            """Notifica login utente (benvenuto giornaliero)"""
            try:
                # Controlla se è il primo login della giornata
                last_login = login_data.get('last_login')
                if last_login:
                    last_date = datetime.fromisoformat(last_login).date()
                    today = datetime.now().date()
                    
                    if last_date < today:
                        # Primo login del giorno
                        login_streak = login_data.get('login_streak', 1)
                        
                        self.notification_manager.create_notification(
                            title=f"🌅 Benvenuto Esploratore!",
                            body=f"Giorno {login_streak} della tua avventura! Cosa scoprirai oggi?",
                            user_id=user_id,
                            notification_type=NotificationType.GENERAL,
                            priority=NotificationPriority.NORMAL,
                            data={'login_streak': login_streak}
                        )
                        
                        # Notifica promemoria obiettivi giornalieri
                        self.schedule_daily_reminders(user_id)
                
                logger.info(f"Notifica login per {user_id}")
                
            except Exception as e:
                logger.error(f"Errore notifica login: {e}")
        
        def on_profile_milestone(user_id: str, milestone_data: Dict):
            """Notifica milestone profilo"""
            try:
                milestone_type = milestone_data.get('type', 'milestone')
                
                messages = {
                    'profile_complete': "✅ Profilo completato! Ora gli altri esploratori possono trovarti!",
                    'first_photo': "📸 Prima foto caricata! La tua avventura inizia!",
                    'preferences_set': "⚙️ Preferenze configurate! L'app è ora personalizzata per te!"
                }
                
                message = messages.get(milestone_type, "Milestone profilo raggiunto!")
                
                self.notification_manager.create_notification(
                    title="👤 Profilo Aggiornato",
                    body=message,
                    user_id=user_id,
                    notification_type=NotificationType.GENERAL,
                    priority=NotificationPriority.LOW,
                    data=milestone_data
                )
                
                logger.info(f"Notifica milestone profilo per {user_id}: {milestone_type}")
                
            except Exception as e:
                logger.error(f"Errore notifica milestone profilo: {e}")
        
        # Registra listeners sistema utenti
        self.active_listeners.extend([
            ('user_login', on_user_login),
            ('profile_milestone', on_profile_milestone)
        ])
        
        logger.info("Integrazione sistema utenti configurata")
    
    def schedule_daily_reminders(self, user_id: str):
        """Programma promemoria giornalieri per un utente"""
        try:
            # Promemoria esplorazioni (ore 10:00)
            self.notification_manager.schedule_daily_reminder(
                user_id=user_id,
                title="🗺️ Tempo di Esplorare!",
                body="Ci sono nuovi monumenti da scoprire nella tua zona!",
                hour=10,
                minute=0
            )
            
            # Promemoria sfide giornaliere (ore 18:00)
            self.notification_manager.schedule_daily_reminder(
                user_id=user_id,
                title="🎯 Sfide in Scadenza!",
                body="Non dimenticare di completare le sfide giornaliere!",
                hour=18,
                minute=0
            )
            
            logger.info(f"Promemoria giornalieri programmati per {user_id}")
            
        except Exception as e:
            logger.error(f"Errore programmazione promemoria: {e}")
    
    def start_monitoring(self):
        """Avvia monitoraggio continuo per notifiche automatiche"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("Monitoraggio notifiche avviato")
    
    def _monitoring_loop(self):
        """Loop di monitoraggio per controlli automatici"""
        while self.monitoring_active:
            try:
                # Controlla ogni 5 minuti
                time.sleep(300)
                
                # Controlli automatici
                self._check_user_inactivity()
                self._check_seasonal_events()
                self._cleanup_old_cache()
                
            except Exception as e:
                logger.error(f"Errore nel monitoraggio: {e}")
                time.sleep(60)
    
    def _check_user_inactivity(self):
        """Controlla utenti inattivi e invia promemoria"""
        try:
            # Simula controllo utenti inattivi
            inactive_users = self.get_inactive_users()
            
            for user_id in inactive_users:
                # Non inviare troppi promemoria
                cache_key = f"inactivity_{user_id}"
                if cache_key in self.notification_cache:
                    last_time = self.notification_cache[cache_key]
                    if datetime.now() - last_time < timedelta(days=3):
                        continue
                
                self.notification_manager.create_notification(
                    title="🏛️ Ci Manchi!",
                    body="Torna a esplorare! Ci sono nuovi monumenti che ti aspettano!",
                    user_id=user_id,
                    notification_type=NotificationType.REMINDER,
                    priority=NotificationPriority.LOW
                )
                
                self.notification_cache[cache_key] = datetime.now()
            
        except Exception as e:
            logger.error(f"Errore controllo inattività: {e}")
    
    def _check_seasonal_events(self):
        """Controlla eventi stagionali e invia notifiche"""
        try:
            current_month = datetime.now().month
            current_day = datetime.now().day
            
            seasonal_events = {
                (4, 21): {
                    'title': '🏛️ Giornata Mondiale dei Monumenti!',
                    'body': 'Oggi è la Giornata Mondiale dei Monumenti! Visita un monumento storico!'
                },
                (5, 18): {
                    'title': '🏛️ Notte Europea dei Musei!',
                    'body': 'Stasera è la Notte Europea dei Musei! Scopri eventi speciali!'
                },
                (9, 26): {
                    'title': '🏛️ Giornata Europea del Patrimonio!',
                    'body': 'Celebriamo il patrimonio culturale europeo! Esplora la storia locale!'
                }
            }
            
            event_key = (current_month, current_day)
            if event_key in seasonal_events:
                event = seasonal_events[event_key]
                
                # Controlla cache per non inviare lo stesso evento più volte
                cache_key = f"seasonal_{current_month}_{current_day}"
                if cache_key not in self.notification_cache:
                    
                    # Invia a tutti gli utenti attivi
                    active_users = self.get_active_users()
                    
                    for user_id in active_users:
                        self.notification_manager.create_notification(
                            title=event['title'],
                            body=event['body'],
                            user_id=user_id,
                            notification_type=NotificationType.SYSTEM_UPDATE,
                            priority=NotificationPriority.NORMAL,
                            data={'event_type': 'seasonal', 'date': f"{current_month}-{current_day}"}
                        )
                    
                    self.notification_cache[cache_key] = datetime.now()
            
        except Exception as e:
            logger.error(f"Errore controllo eventi stagionali: {e}")
    
    def _cleanup_old_cache(self):
        """Pulisce vecchi elementi dalla cache"""
        try:
            cutoff_time = datetime.now() - timedelta(days=7)
            
            keys_to_remove = []
            for key, timestamp in self.notification_cache.items():
                if timestamp < cutoff_time:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.notification_cache[key]
            
            if keys_to_remove:
                logger.info(f"Puliti {len(keys_to_remove)} elementi dalla cache notifiche")
            
        except Exception as e:
            logger.error(f"Errore pulizia cache: {e}")
    
    # Metodi helper (da implementare con dati reali)
    
    def find_nearby_monuments(self, lat: float, lon: float, radius_km: float = 2.0) -> List[Dict]:
        """Trova monumenti nelle vicinanze (simulato)"""
        # In implementazione reale, usa GPS manager e database monumenti
        return [
            {'name': 'Colosseo', 'distance': 1.2, 'lat': lat + 0.01, 'lon': lon + 0.01},
            {'name': 'Fori Romani', 'distance': 1.5, 'lat': lat + 0.015, 'lon': lon + 0.005}
        ]
    
    def get_inactive_users(self, days_threshold: int = 7) -> List[str]:
        """Ottiene lista utenti inattivi (simulato)"""
        # In implementazione reale, controlla ultimo accesso dal sistema utenti
        return ['user1', 'user2']
    
    def get_active_users(self) -> List[str]:
        """Ottiene lista utenti attivi (simulato)"""
        # In implementazione reale, ottiene dal sistema utenti
        return ['user1', 'user2', 'demo_user']
    
    # Metodi pubblici per triggering manuale
    
    def trigger_monument_visit_notification(self, user_id: str, monument_name: str, **kwargs):
        """Triggera manualmente notifica visita monumento"""
        visit_data = {
            'monument_name': monument_name,
            'points_earned': kwargs.get('points', 50),
            'first_visit': kwargs.get('first_visit', False),
            'visit_streak': kwargs.get('streak', 1)
        }
        
        # Trova listener e chiamalo
        for listener_type, callback in self.active_listeners:
            if listener_type == 'monument_visit':
                callback(user_id, visit_data)
                break
    
    def trigger_achievement_notification(self, user_id: str, achievement_name: str, **kwargs):
        """Triggera manualmente notifica achievement"""
        achievement_data = {
            'name': achievement_name,
            'description': kwargs.get('description', ''),
            'points': kwargs.get('points', 100),
            'rarity': kwargs.get('rarity', 'common')
        }
        
        for listener_type, callback in self.active_listeners:
            if listener_type == 'achievement_unlock':
                callback(user_id, achievement_data)
                break
    
    def trigger_social_notification(self, user_id: str, interaction_type: str, actor_name: str, **kwargs):
        """Triggera manualmente notifica social"""
        interaction_data = {
            'type': interaction_type,
            'actor_name': actor_name,
            'target': kwargs.get('target', 'il tuo post'),
            'timestamp': datetime.now().isoformat()
        }
        
        for listener_type, callback in self.active_listeners:
            if listener_type == 'social_interaction':
                callback(user_id, interaction_data)
                break
    
    def trigger_nearby_monuments_check(self, user_id: str, latitude: float, longitude: float):
        """Triggera controllo monumenti vicini"""
        location_data = {
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': 1.0,
            'timestamp': datetime.now().isoformat()
        }
        
        for listener_type, callback in self.active_listeners:
            if listener_type == 'location_update':
                callback(user_id, location_data)
                break
    
    def send_system_announcement(self, title: str, body: str, priority: NotificationPriority = NotificationPriority.NORMAL):
        """Invia annuncio di sistema a tutti gli utenti attivi"""
        active_users = self.get_active_users()
        
        for user_id in active_users:
            self.notification_manager.create_notification(
                title=title,
                body=body,
                user_id=user_id,
                notification_type=NotificationType.SYSTEM_UPDATE,
                priority=priority,
                data={'announcement': True, 'timestamp': datetime.now().isoformat()}
            )
        
        logger.info(f"Annuncio sistema inviato a {len(active_users)} utenti")
    
    def stop_monitoring(self):
        """Ferma il monitoraggio"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Monitoraggio notifiche fermato")
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Ottiene statistiche delle integrazioni"""
        return {
            'active_listeners': len(self.active_listeners),
            'cache_size': len(self.notification_cache),
            'monitoring_active': self.monitoring_active,
            'integrations_available': {
                'gamification': self.gamification_manager is not None,
                'social': self.social_manager is not None,
                'gps': self.gps_manager is not None,
                'visit_tracker': self.visit_tracker is not None,
                'user_system': self.user_system is not None,
                'monument_recognizer': self.monument_recognizer is not None
            }
        }


# Utility per inizializzazione rapida
def create_integrated_notification_system(
    gamification_manager=None,
    social_manager=None,
    user_system=None,
    gps_manager=None,
    visit_tracker=None,
    monument_recognizer=None,
    **notification_config
) -> NotificationIntegrationManager:
    """Crea sistema notifiche completamente integrato"""
    
    # Inizializza notification manager
    notification_manager = PushNotificationManager(**notification_config)
    
    # Crea integration manager
    integration_manager = NotificationIntegrationManager(
        notification_manager=notification_manager,
        gamification_manager=gamification_manager,
        social_manager=social_manager,
        user_system=user_system,
        gps_manager=gps_manager,
        visit_tracker=visit_tracker,
        monument_recognizer=monument_recognizer
    )
    
    return integration_manager


if __name__ == "__main__":
    # Test dell'integrazione
    print("🔔 Test Sistema Notifiche Integrato")
    
    # Crea sistema integrato
    integration_manager = create_integrated_notification_system()
    
    # Test delle notifiche
    print("\n📱 Test notifiche...")
    
    # Test visita monumento
    integration_manager.trigger_monument_visit_notification(
        "test_user", 
        "Colosseo", 
        points=100, 
        first_visit=True
    )
    
    # Test achievement
    integration_manager.trigger_achievement_notification(
        "test_user", 
        "Primo Esploratore", 
        description="Hai visitato il tuo primo monumento!"
    )
    
    # Test social
    integration_manager.trigger_social_notification(
        "test_user", 
        "like", 
        "Marco",
        target="Pantheon"
    )
    
    # Test monumenti vicini
    integration_manager.trigger_nearby_monuments_check(
        "test_user", 
        41.8902, 
        12.4922
    )
    
    # Annuncio sistema
    integration_manager.send_system_announcement(
        "🆕 Nuova Funzionalità!",
        "Ora puoi condividere le tue avventure sui social media!"
    )
    
    # Statistiche
    stats = integration_manager.get_integration_stats()
    print(f"\n📊 Statistiche Integrazione:")
    print(f"Listeners attivi: {stats['active_listeners']}")
    print(f"Cache size: {stats['cache_size']}")
    print(f"Monitoraggio attivo: {stats['monitoring_active']}")
    print(f"Integrazioni: {stats['integrations_available']}")
    
    # Pausa e cleanup
    time.sleep(3)
    integration_manager.stop_monitoring()
    integration_manager.notification_manager.stop()
    
    print("\n✅ Test completato!")
