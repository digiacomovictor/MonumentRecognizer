"""
Gamification System for Monument Recognizer
Sistema completo di gamification con punti, livelli, achievement, badge e sfide
"""

import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random
import math


class AchievementCategory(Enum):
    """Categorie degli achievement"""
    EXPLORER = "explorer"          # Esplorazione e scoperta
    SOCIAL = "social"             # Condivisione e interazioni
    GEOGRAPHIC = "geographic"     # Esplorazione geografica  
    TIME_BASED = "time_based"     # Attività temporali
    COLLECTION = "collection"     # Collezione e completamento
    SPECIAL = "special"          # Eventi speciali


class BadgeRarity(Enum):
    """Rarità dei badge"""
    COMMON = "common"       # 🥉 Bronze
    RARE = "rare"          # 🥈 Silver  
    EPIC = "epic"          # 🥇 Gold
    LEGENDARY = "legendary" # 💎 Diamond


@dataclass
class Achievement:
    """Definizione di un achievement"""
    id: str
    name: str
    description: str
    category: AchievementCategory
    rarity: BadgeRarity
    points: int
    icon: str
    criteria: Dict[str, Any]
    rewards: Dict[str, Any]


@dataclass
class UserProgress:
    """Progresso utente nel sistema gamification"""
    user_id: str
    total_points: int
    level: int
    experience: int
    experience_to_next_level: int
    visits_streak: int
    last_visit_date: str
    achievements_unlocked: List[str]
    badges_earned: List[str]
    challenges_completed: List[str]


class GamificationManager:
    """Manager principale del sistema di gamification"""
    
    def __init__(self, db_path: str = "visits.db"):
        self.db_path = db_path
        self.achievements = {}
        self.challenges = {}
        
        # Inizializza database e definizioni
        self.init_gamification_database()
        self.define_achievements()
        self.define_challenges()
    
    def init_gamification_database(self):
        """Inizializza le tabelle del database per la gamification"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabella progressi utente
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id TEXT PRIMARY KEY,
                    total_points INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    visits_streak INTEGER DEFAULT 0,
                    last_visit_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabella achievement sbloccati
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    achievement_id TEXT,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_progress (user_id)
                )
            ''')
            
            # Tabella badge ottenuti
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    badge_id TEXT,
                    badge_name TEXT,
                    badge_icon TEXT,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_progress (user_id)
                )
            ''')
            
            # Tabella sfide utente
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    challenge_id TEXT,
                    challenge_type TEXT,
                    target_value INTEGER,
                    current_progress INTEGER DEFAULT 0,
                    completed BOOLEAN DEFAULT FALSE,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_progress (user_id)
                )
            ''')
            
            # Tabella statistiche globali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS global_stats (
                    stat_name TEXT PRIMARY KEY,
                    stat_value INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabella eventi speciali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS special_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_name TEXT,
                    event_type TEXT,
                    description TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    rewards TEXT,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.commit()
            conn.close()
            print("📊 Database gamification inizializzato correttamente")
            
        except Exception as e:
            print(f"❌ Errore inizializzazione database gamification: {e}")
    
    def define_achievements(self):
        """Definisce tutti gli achievement del sistema"""
        
        # EXPLORER ACHIEVEMENTS - Esplorazione e scoperta
        self.achievements.update({
            "first_monument": Achievement(
                id="first_monument",
                name="Primo Esploratore",
                description="Riconosci il tuo primo monumento",
                category=AchievementCategory.EXPLORER,
                rarity=BadgeRarity.COMMON,
                points=50,
                icon="🏛️",
                criteria={"visits": 1},
                rewards={"title": "Novizio Esploratore"}
            ),
            
            "explorer_bronze": Achievement(
                id="explorer_bronze",
                name="Esploratore di Bronzo",
                description="Visita 10 monumenti diversi",
                category=AchievementCategory.EXPLORER,
                rarity=BadgeRarity.COMMON,
                points=200,
                icon="🥉",
                criteria={"unique_monuments": 10},
                rewards={"title": "Esploratore di Bronzo", "points_bonus": 100}
            ),
            
            "explorer_silver": Achievement(
                id="explorer_silver", 
                name="Esploratore d'Argento",
                description="Visita 25 monumenti diversi",
                category=AchievementCategory.EXPLORER,
                rarity=BadgeRarity.RARE,
                points=500,
                icon="🥈",
                criteria={"unique_monuments": 25},
                rewards={"title": "Esploratore d'Argento", "points_bonus": 250}
            ),
            
            "explorer_gold": Achievement(
                id="explorer_gold",
                name="Esploratore d'Oro", 
                description="Visita 50 monumenti diversi",
                category=AchievementCategory.EXPLORER,
                rarity=BadgeRarity.EPIC,
                points=1000,
                icon="🥇",
                criteria={"unique_monuments": 50},
                rewards={"title": "Esploratore d'Oro", "points_bonus": 500}
            ),
            
            "monument_master": Achievement(
                id="monument_master",
                name="Maestro dei Monumenti",
                description="Visita 100 monumenti diversi",
                category=AchievementCategory.EXPLORER,
                rarity=BadgeRarity.LEGENDARY,
                points=2500,
                icon="💎",
                criteria={"unique_monuments": 100},
                rewards={"title": "Maestro dei Monumenti", "points_bonus": 1000}
            )
        })
        
        # SOCIAL ACHIEVEMENTS - Condivisione e interazioni
        self.achievements.update({
            "social_butterfly": Achievement(
                id="social_butterfly",
                name="Farfalla Social",
                description="Condividi la tua prima visita sui social",
                category=AchievementCategory.SOCIAL,
                rarity=BadgeRarity.COMMON,
                points=75,
                icon="🦋",
                criteria={"social_shares": 1},
                rewards={"title": "Condivisore"}
            ),
            
            "viral_explorer": Achievement(
                id="viral_explorer",
                name="Esploratore Virale",
                description="Ottieni 50 like sui tuoi post nel feed",
                category=AchievementCategory.SOCIAL,
                rarity=BadgeRarity.RARE,
                points=300,
                icon="🔥",
                criteria={"likes_received": 50},
                rewards={"title": "Influencer", "points_bonus": 150}
            ),
            
            "community_leader": Achievement(
                id="community_leader",
                name="Leader della Community",
                description="Ricevi 100 like e fai 50 commenti",
                category=AchievementCategory.SOCIAL,
                rarity=BadgeRarity.EPIC,
                points=750,
                icon="👑",
                criteria={"likes_received": 100, "comments_made": 50},
                rewards={"title": "Leader Community", "points_bonus": 400}
            )
        })
        
        # GEOGRAPHIC ACHIEVEMENTS - Esplorazione geografica
        self.achievements.update({
            "city_explorer": Achievement(
                id="city_explorer",
                name="Esploratore Urbano",
                description="Visita monumenti in 5 città diverse",
                category=AchievementCategory.GEOGRAPHIC,
                rarity=BadgeRarity.COMMON,
                points=150,
                icon="🏙️",
                criteria={"unique_cities": 5},
                rewards={"title": "Viaggiatore Urbano"}
            ),
            
            "country_hopper": Achievement(
                id="country_hopper",
                name="Saltatore di Paesi",
                description="Visita monumenti in 10 paesi diversi",
                category=AchievementCategory.GEOGRAPHIC,
                rarity=BadgeRarity.RARE,
                points=600,
                icon="🌍",
                criteria={"unique_countries": 10},
                rewards={"title": "Globetrotter", "points_bonus": 300}
            ),
            
            "continental_master": Achievement(
                id="continental_master",
                name="Maestro Continentale",
                description="Visita monumenti in tutti i continenti",
                category=AchievementCategory.GEOGRAPHIC,
                rarity=BadgeRarity.LEGENDARY,
                points=2000,
                icon="🗺️",
                criteria={"unique_continents": 6},
                rewards={"title": "Conquistatore del Mondo", "points_bonus": 1000}
            )
        })
        
        # TIME-BASED ACHIEVEMENTS - Attività temporali  
        self.achievements.update({
            "streak_starter": Achievement(
                id="streak_starter",
                name="Inizio Striscia",
                description="Visita monumenti per 3 giorni consecutivi",
                category=AchievementCategory.TIME_BASED,
                rarity=BadgeRarity.COMMON,
                points=100,
                icon="🔥",
                criteria={"visit_streak": 3},
                rewards={"title": "Costante"}
            ),
            
            "week_warrior": Achievement(
                id="week_warrior",
                name="Guerriero Settimanale", 
                description="Visita monumenti per 7 giorni consecutivi",
                category=AchievementCategory.TIME_BASED,
                rarity=BadgeRarity.RARE,
                points=350,
                icon="⚔️",
                criteria={"visit_streak": 7},
                rewards={"title": "Dedicato", "points_bonus": 200}
            ),
            
            "marathon_explorer": Achievement(
                id="marathon_explorer",
                name="Esploratore Maratoneta",
                description="Visita monumenti per 30 giorni consecutivi", 
                category=AchievementCategory.TIME_BASED,
                rarity=BadgeRarity.LEGENDARY,
                points=1500,
                icon="🏃",
                criteria={"visit_streak": 30},
                rewards={"title": "Maratoneta", "points_bonus": 750}
            ),
            
            "early_bird": Achievement(
                id="early_bird",
                name="Mattiniero",
                description="Visita 10 monumenti prima delle 9:00",
                category=AchievementCategory.TIME_BASED,
                rarity=BadgeRarity.RARE,
                points=250,
                icon="🌅",
                criteria={"early_visits": 10},
                rewards={"title": "Mattiniero"}
            )
        })
        
        # COLLECTION ACHIEVEMENTS - Collezione e completamento
        self.achievements.update({
            "style_collector": Achievement(
                id="style_collector",
                name="Collezionista di Stili",
                description="Visita monumenti di 10 stili architettonici diversi",
                category=AchievementCategory.COLLECTION,
                rarity=BadgeRarity.RARE,
                points=400,
                icon="🏛️",
                criteria={"architectural_styles": 10},
                rewards={"title": "Conoscitore Architettura"}
            ),
            
            "era_master": Achievement(
                id="era_master", 
                name="Maestro delle Ere",
                description="Visita monumenti di ogni era storica",
                category=AchievementCategory.COLLECTION,
                rarity=BadgeRarity.EPIC,
                points=800,
                icon="⏳",
                criteria={"historical_eras": 8}, # Antico, Classico, Medievale, Rinascimento, Barocco, Moderno, Contemporaneo
                rewards={"title": "Storico", "points_bonus": 400}
            ),
            
            "completionist": Achievement(
                id="completionist",
                name="Completista",
                description="Sblocca il 90% di tutti gli achievement",
                category=AchievementCategory.COLLECTION,
                rarity=BadgeRarity.LEGENDARY,
                points=3000,
                icon="💯",
                criteria={"achievement_completion": 90},
                rewards={"title": "Perfezionista", "points_bonus": 2000}
            )
        })
        
        # SPECIAL ACHIEVEMENTS - Eventi speciali
        self.achievements.update({
            "christmas_explorer": Achievement(
                id="christmas_explorer",
                name="Esploratore di Natale",
                description="Visita 5 monumenti durante il periodo natalizio",
                category=AchievementCategory.SPECIAL,
                rarity=BadgeRarity.EPIC,
                points=500,
                icon="🎄",
                criteria={"christmas_visits": 5},
                rewards={"title": "Spirito Natalizio", "limited_badge": True}
            ),
            
            "new_year_starter": Achievement(
                id="new_year_starter",
                name="Inizio Anno Nuovo",
                description="Visita un monumento il primo gennaio",
                category=AchievementCategory.SPECIAL,
                rarity=BadgeRarity.RARE,
                points=200,
                icon="🎊",
                criteria={"new_year_visit": True},
                rewards={"title": "Nuovo Inizio", "limited_badge": True}
            )
        })
    
    def define_challenges(self):
        """Definisce le sfide del sistema"""
        
        # Sfide giornaliere
        daily_challenges = [
            {
                "id": "daily_explorer",
                "name": "Esploratore Quotidiano", 
                "description": "Visita 2 monumenti oggi",
                "type": "daily",
                "target": 2,
                "metric": "visits_today",
                "points": 50,
                "icon": "🎯"
            },
            {
                "id": "daily_social",
                "name": "Social Quotidiano",
                "description": "Condividi 1 visita sui social oggi", 
                "type": "daily",
                "target": 1,
                "metric": "shares_today", 
                "points": 30,
                "icon": "📤"
            },
            {
                "id": "daily_engagement",
                "name": "Engagement Quotidiano",
                "description": "Metti 3 like nel feed oggi",
                "type": "daily", 
                "target": 3,
                "metric": "likes_given_today",
                "points": 25,
                "icon": "👍"
            }
        ]
        
        # Sfide settimanali
        weekly_challenges = [
            {
                "id": "weekly_marathon",
                "name": "Maratona Settimanale",
                "description": "Visita 10 monumenti questa settimana",
                "type": "weekly",
                "target": 10, 
                "metric": "visits_week",
                "points": 200,
                "icon": "🏃"
            },
            {
                "id": "weekly_diversity",
                "name": "Diversità Settimanale", 
                "description": "Visita monumenti in 3 paesi diversi",
                "type": "weekly",
                "target": 3,
                "metric": "countries_week",
                "points": 150,
                "icon": "🌍"
            },
            {
                "id": "weekly_social",
                "name": "Social Week",
                "description": "Ottieni 20 like sui tuoi post questa settimana",
                "type": "weekly",
                "target": 20,
                "metric": "likes_received_week", 
                "points": 100,
                "icon": "💖"
            }
        ]
        
        self.challenges = {
            "daily": daily_challenges,
            "weekly": weekly_challenges
        }
    
    def get_user_progress(self, user_id: str) -> UserProgress:
        """Ottiene il progresso di un utente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ottieni dati base progresso
            cursor.execute('''
                SELECT total_points, level, experience, visits_streak, last_visit_date
                FROM user_progress WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if not result:
                # Crea nuovo progresso utente
                cursor.execute('''
                    INSERT INTO user_progress (user_id) VALUES (?)
                ''', (user_id,))
                conn.commit()
                result = (0, 1, 0, 0, None)
            
            total_points, level, experience, visits_streak, last_visit_date = result
            
            # Calcola XP necessario per il prossimo livello
            exp_to_next = self.calculate_experience_for_level(level + 1) - experience
            
            # Ottieni achievement sbloccati
            cursor.execute('''
                SELECT achievement_id FROM user_achievements WHERE user_id = ?
            ''', (user_id,))
            achievements = [row[0] for row in cursor.fetchall()]
            
            # Ottieni badge ottenuti
            cursor.execute('''
                SELECT badge_id FROM user_badges WHERE user_id = ?
            ''', (user_id,))
            badges = [row[0] for row in cursor.fetchall()]
            
            # Ottieni sfide completate
            cursor.execute('''
                SELECT challenge_id FROM user_challenges 
                WHERE user_id = ? AND completed = TRUE
            ''', (user_id,))
            challenges = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            return UserProgress(
                user_id=user_id,
                total_points=total_points,
                level=level,
                experience=experience,
                experience_to_next_level=exp_to_next,
                visits_streak=visits_streak,
                last_visit_date=last_visit_date or "",
                achievements_unlocked=achievements,
                badges_earned=badges,
                challenges_completed=challenges
            )
            
        except Exception as e:
            print(f"❌ Errore nel recupero progresso utente: {e}")
            return UserProgress(
                user_id=user_id, total_points=0, level=1, experience=0,
                experience_to_next_level=100, visits_streak=0, last_visit_date="",
                achievements_unlocked=[], badges_earned=[], challenges_completed=[]
            )
    
    def calculate_experience_for_level(self, level: int) -> int:
        """Calcola l'esperienza totale necessaria per un livello"""
        # Formula: XP = 100 * level^1.5
        return int(100 * (level ** 1.5))
    
    def calculate_level_from_experience(self, experience: int) -> int:
        """Calcola il livello basato sull'esperienza totale"""
        level = 1
        while self.calculate_experience_for_level(level + 1) <= experience:
            level += 1
        return level
    
    def award_points(self, user_id: str, points: int, source: str = "general") -> Dict[str, Any]:
        """Assegna punti a un utente e verifica levelup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ottieni stato attuale
            progress = self.get_user_progress(user_id)
            
            # Calcola nuovi valori
            new_total_points = progress.total_points + points
            new_experience = progress.experience + points
            new_level = self.calculate_level_from_experience(new_experience)
            
            # Verifica levelup
            level_up = new_level > progress.level
            
            # Aggiorna database
            cursor.execute('''
                UPDATE user_progress 
                SET total_points = ?, experience = ?, level = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_total_points, new_experience, new_level, user_id))
            
            if cursor.rowcount == 0:
                # Crea nuovo record se non esiste
                cursor.execute('''
                    INSERT INTO user_progress (user_id, total_points, experience, level)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, new_total_points, new_experience, new_level))
            
            conn.commit()
            conn.close()
            
            return {
                "points_awarded": points,
                "total_points": new_total_points,
                "level_up": level_up,
                "new_level": new_level if level_up else progress.level,
                "source": source
            }
            
        except Exception as e:
            print(f"❌ Errore nell'assegnazione punti: {e}")
            return {"points_awarded": 0, "total_points": 0, "level_up": False}
    
    def process_monument_visit(self, user_id: str, visit_data: Dict) -> Dict[str, Any]:
        """Processa una visita a un monumento per gamification"""
        try:
            results = {
                "points_awarded": 0,
                "achievements_unlocked": [],
                "badges_earned": [],
                "level_up": False,
                "streak_updated": False,
                "challenges_completed": []
            }
            
            # Punti base per visita
            base_points = 25
            bonus_points = 0
            
            # Bonus per primo riconoscimento del giorno
            if self.is_first_visit_today(user_id):
                bonus_points += 10
                
            # Bonus per streak
            streak = self.update_visit_streak(user_id)
            if streak > 1:
                bonus_points += min(streak * 2, 50)  # Max 50 bonus points
                results["streak_updated"] = True
            
            # Assegna punti
            total_points = base_points + bonus_points
            point_result = self.award_points(user_id, total_points, "monument_visit")
            results.update(point_result)
            
            # Verifica achievement
            new_achievements = self.check_achievements(user_id, "monument_visit", visit_data)
            results["achievements_unlocked"] = new_achievements
            
            # Aggiorna sfide
            challenge_results = self.update_challenges(user_id, "monument_visit", visit_data)
            results["challenges_completed"] = challenge_results
            
            return results
            
        except Exception as e:
            print(f"❌ Errore elaborazione visita monumento: {e}")
            return {"points_awarded": 0, "achievements_unlocked": [], "level_up": False}
    
    def process_social_share(self, user_id: str, share_data: Dict) -> Dict[str, Any]:
        """Processa una condivisione social per gamification"""
        try:
            results = {
                "points_awarded": 0,
                "achievements_unlocked": [],
                "badges_earned": [],
                "challenges_completed": []
            }
            
            # Punti per condivisione
            share_points = 15
            platform = share_data.get('platform', '')
            
            # Bonus per diverse piattaforme
            if platform in ['instagram', 'linkedin']:
                share_points += 5
            
            # Assegna punti
            point_result = self.award_points(user_id, share_points, "social_share")
            results.update(point_result)
            
            # Verifica achievement social
            new_achievements = self.check_achievements(user_id, "social_share", share_data)
            results["achievements_unlocked"] = new_achievements
            
            # Aggiorna sfide social
            challenge_results = self.update_challenges(user_id, "social_share", share_data)
            results["challenges_completed"] = challenge_results
            
            return results
            
        except Exception as e:
            print(f"❌ Errore elaborazione condivisione social: {e}")
            return {"points_awarded": 0, "achievements_unlocked": []}
    
    def is_first_visit_today(self, user_id: str) -> bool:
        """Verifica se è la prima visita della giornata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date()
            cursor.execute('''
                SELECT COUNT(*) FROM visits 
                WHERE user_id = ? AND DATE(timestamp) = ?
            ''', (user_id, today))
            
            visit_count = cursor.fetchone()[0]
            conn.close()
            
            return visit_count == 1  # Se è la prima (conta = 1)
            
        except Exception as e:
            print(f"❌ Errore verifica prima visita: {e}")
            return False
    
    def update_visit_streak(self, user_id: str) -> int:
        """Aggiorna la striscia di visite consecutive"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            progress = self.get_user_progress(user_id)
            today = datetime.now().date()
            
            # Verifica ultima visita
            if progress.last_visit_date:
                last_date = datetime.fromisoformat(progress.last_visit_date).date()
                days_diff = (today - last_date).days
                
                if days_diff == 0:
                    # Stessa giornata, mantieni streak
                    new_streak = progress.visits_streak
                elif days_diff == 1:
                    # Giorno consecutivo, incrementa streak
                    new_streak = progress.visits_streak + 1
                else:
                    # Streak interrotta, ricomincia
                    new_streak = 1
            else:
                # Prima visita in assoluto
                new_streak = 1
            
            # Aggiorna database
            cursor.execute('''
                UPDATE user_progress 
                SET visits_streak = ?, last_visit_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_streak, today.isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            return new_streak
            
        except Exception as e:
            print(f"❌ Errore aggiornamento streak: {e}")
            return 1
    
    def check_achievements(self, user_id: str, action_type: str, action_data: Dict) -> List[str]:
        """Verifica se l'utente ha sbloccato nuovi achievement"""
        try:
            new_achievements = []
            progress = self.get_user_progress(user_id)
            
            for achievement_id, achievement in self.achievements.items():
                # Skip se già sbloccato
                if achievement_id in progress.achievements_unlocked:
                    continue
                
                # Verifica criteri
                if self.check_achievement_criteria(user_id, achievement, action_type, action_data):
                    self.unlock_achievement(user_id, achievement_id)
                    new_achievements.append(achievement_id)
            
            return new_achievements
            
        except Exception as e:
            print(f"❌ Errore verifica achievement: {e}")
            return []
    
    def check_achievement_criteria(self, user_id: str, achievement: Achievement, 
                                 action_type: str, action_data: Dict) -> bool:
        """Verifica se i criteri per un achievement sono soddisfatti"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            criteria = achievement.criteria
            
            # Verifica conteggio visite
            if "visits" in criteria:
                cursor.execute('SELECT COUNT(*) FROM visits WHERE user_id = ?', (user_id,))
                visit_count = cursor.fetchone()[0]
                if visit_count < criteria["visits"]:
                    return False
            
            # Verifica monumenti unici
            if "unique_monuments" in criteria:
                cursor.execute('''
                    SELECT COUNT(DISTINCT monument_name) FROM visits WHERE user_id = ?
                ''', (user_id,))
                unique_count = cursor.fetchone()[0]
                if unique_count < criteria["unique_monuments"]:
                    return False
            
            # Verifica streak visite
            if "visit_streak" in criteria:
                progress = self.get_user_progress(user_id)
                if progress.visits_streak < criteria["visit_streak"]:
                    return False
            
            # Verifica condivisioni social
            if "social_shares" in criteria:
                cursor.execute('SELECT COUNT(*) FROM shared_visits WHERE user_id = ?', (user_id,))
                shares_count = cursor.fetchone()[0]
                if shares_count < criteria["social_shares"]:
                    return False
            
            # Verifica like ricevuti
            if "likes_received" in criteria:
                cursor.execute('''
                    SELECT SUM(likes_count) FROM social_feed WHERE user_id = ?
                ''', (user_id,))
                result = cursor.fetchone()[0]
                likes_count = result if result else 0
                if likes_count < criteria["likes_received"]:
                    return False
            
            # Verifica città uniche
            if "unique_cities" in criteria:
                cursor.execute('''
                    SELECT COUNT(DISTINCT 
                        CASE 
                            WHEN location LIKE '%,%' THEN TRIM(SUBSTR(location, 1, INSTR(location, ',') - 1))
                            ELSE location 
                        END
                    ) FROM visits WHERE user_id = ?
                ''', (user_id,))
                cities_count = cursor.fetchone()[0]
                if cities_count < criteria["unique_cities"]:
                    return False
            
            # Verifica paesi unici
            if "unique_countries" in criteria:
                cursor.execute('''
                    SELECT COUNT(DISTINCT 
                        CASE 
                            WHEN location LIKE '%,%' THEN TRIM(SUBSTR(location, INSTR(location, ',') + 1))
                            ELSE location 
                        END
                    ) FROM visits WHERE user_id = ?
                ''', (user_id,))
                countries_count = cursor.fetchone()[0]
                if countries_count < criteria["unique_countries"]:
                    return False
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Errore verifica criteri achievement: {e}")
            return False
    
    def unlock_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Sblocca un achievement per l'utente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            achievement = self.achievements[achievement_id]
            
            # Inserisci achievement sbloccato
            cursor.execute('''
                INSERT INTO user_achievements (user_id, achievement_id)
                VALUES (?, ?)
            ''', (user_id, achievement_id))
            
            # Aggiungi badge se previsto
            cursor.execute('''
                INSERT INTO user_badges (user_id, badge_id, badge_name, badge_icon)
                VALUES (?, ?, ?, ?)
            ''', (user_id, achievement_id, achievement.name, achievement.icon))
            
            # Assegna punti bonus se previsti
            if "points_bonus" in achievement.rewards:
                bonus_points = achievement.rewards["points_bonus"]
                self.award_points(user_id, bonus_points, f"achievement_{achievement_id}")
            
            conn.commit()
            conn.close()
            
            print(f"🏆 Achievement '{achievement.name}' sbloccato per {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Errore sblocco achievement: {e}")
            return False
    
    def get_daily_challenges(self, user_id: str) -> List[Dict]:
        """Ottiene le sfide giornaliere dell'utente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date()
            
            # Verifica se ci sono sfide attive per oggi
            cursor.execute('''
                SELECT challenge_id, target_value, current_progress, completed
                FROM user_challenges
                WHERE user_id = ? AND challenge_type = 'daily' 
                AND DATE(started_at) = ?
            ''', (user_id, today))
            
            active_challenges = cursor.fetchall()
            
            # Se non ci sono sfide per oggi, genera nuove sfide
            if not active_challenges:
                self.generate_daily_challenges(user_id)
                # Ricarica sfide
                cursor.execute('''
                    SELECT challenge_id, target_value, current_progress, completed
                    FROM user_challenges
                    WHERE user_id = ? AND challenge_type = 'daily' 
                    AND DATE(started_at) = ?
                ''', (user_id, today))
                active_challenges = cursor.fetchall()
            
            # Formatta risultati
            challenges = []
            for challenge_data in active_challenges:
                challenge_id, target, progress, completed = challenge_data
                
                # Trova definizione sfida
                challenge_def = next((c for c in self.challenges["daily"] if c["id"] == challenge_id), None)
                if challenge_def:
                    challenges.append({
                        "id": challenge_id,
                        "name": challenge_def["name"],
                        "description": challenge_def["description"],
                        "target": target,
                        "progress": progress,
                        "completed": bool(completed),
                        "points": challenge_def["points"],
                        "icon": challenge_def["icon"]
                    })
            
            conn.close()
            return challenges
            
        except Exception as e:
            print(f"❌ Errore recupero sfide giornaliere: {e}")
            return []
    
    def generate_daily_challenges(self, user_id: str):
        """Genera nuove sfide giornaliere casuali"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Seleziona 2-3 sfide casuali
            selected_challenges = random.sample(self.challenges["daily"], min(3, len(self.challenges["daily"])))
            
            for challenge in selected_challenges:
                cursor.execute('''
                    INSERT INTO user_challenges 
                    (user_id, challenge_id, challenge_type, target_value, expires_at)
                    VALUES (?, ?, 'daily', ?, ?)
                ''', (
                    user_id, 
                    challenge["id"], 
                    challenge["target"],
                    datetime.now() + timedelta(days=1)  # Scade domani
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Errore generazione sfide giornaliere: {e}")
    
    def update_challenges(self, user_id: str, action_type: str, action_data: Dict) -> List[str]:
        """Aggiorna il progresso delle sfide attive"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            completed_challenges = []
            today = datetime.now().date()
            
            # Ottieni sfide attive non completate
            cursor.execute('''
                SELECT id, challenge_id, target_value, current_progress
                FROM user_challenges
                WHERE user_id = ? AND completed = FALSE
                AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            ''', (user_id,))
            
            active_challenges = cursor.fetchall()
            
            for challenge_record in active_challenges:
                record_id, challenge_id, target, current_progress = challenge_record
                
                # Determina incremento basato su azione
                increment = 0
                
                if challenge_id == "daily_explorer" and action_type == "monument_visit":
                    # Verifica se è una nuova visita oggi
                    cursor.execute('''
                        SELECT COUNT(*) FROM visits 
                        WHERE user_id = ? AND DATE(timestamp) = ?
                    ''', (user_id, today))
                    visits_today = cursor.fetchone()[0]
                    increment = min(1, visits_today - current_progress)
                
                elif challenge_id == "daily_social" and action_type == "social_share":
                    increment = 1
                
                elif challenge_id == "daily_engagement" and action_type == "like_given":
                    increment = 1
                
                # Altri tipi di sfide...
                
                if increment > 0:
                    new_progress = current_progress + increment
                    completed = new_progress >= target
                    
                    # Aggiorna progresso
                    cursor.execute('''
                        UPDATE user_challenges 
                        SET current_progress = ?, completed = ?, 
                            completed_at = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END
                        WHERE id = ?
                    ''', (new_progress, completed, completed, record_id))
                    
                    if completed:
                        completed_challenges.append(challenge_id)
                        
                        # Assegna punti per completamento sfida
                        challenge_def = next((c for c in self.challenges["daily"] if c["id"] == challenge_id), None)
                        if challenge_def:
                            self.award_points(user_id, challenge_def["points"], f"challenge_{challenge_id}")
            
            conn.commit()
            conn.close()
            
            return completed_challenges
            
        except Exception as e:
            print(f"❌ Errore aggiornamento sfide: {e}")
            return []
    
    def get_leaderboard(self, category: str = "points", limit: int = 10) -> List[Dict]:
        """Ottiene la classifica degli utenti"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if category == "points":
                cursor.execute('''
                    SELECT up.user_id, up.total_points, up.level,
                           COUNT(ua.achievement_id) as achievements_count
                    FROM user_progress up
                    LEFT JOIN user_achievements ua ON up.user_id = ua.user_id
                    GROUP BY up.user_id
                    ORDER BY up.total_points DESC
                    LIMIT ?
                ''', (limit,))
            
            elif category == "level":
                cursor.execute('''
                    SELECT up.user_id, up.total_points, up.level,
                           COUNT(ua.achievement_id) as achievements_count
                    FROM user_progress up
                    LEFT JOIN user_achievements ua ON up.user_id = ua.user_id
                    GROUP BY up.user_id
                    ORDER BY up.level DESC, up.experience DESC
                    LIMIT ?
                ''', (limit,))
            
            elif category == "achievements":
                cursor.execute('''
                    SELECT up.user_id, up.total_points, up.level,
                           COUNT(ua.achievement_id) as achievements_count
                    FROM user_progress up
                    LEFT JOIN user_achievements ua ON up.user_id = ua.user_id
                    GROUP BY up.user_id
                    ORDER BY achievements_count DESC, up.total_points DESC
                    LIMIT ?
                ''', (limit,))
            
            results = []
            for i, row in enumerate(cursor.fetchall(), 1):
                user_id, points, level, achievement_count = row
                results.append({
                    "rank": i,
                    "user_id": user_id,
                    "points": points,
                    "level": level,
                    "achievements": achievement_count
                })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"❌ Errore recupero classifica: {e}")
            return []
    
    def get_user_rank(self, user_id: str, category: str = "points") -> Dict:
        """Ottiene il ranking di un utente specifico"""
        try:
            leaderboard = self.get_leaderboard(category, 1000)  # Top 1000
            
            for entry in leaderboard:
                if entry["user_id"] == user_id:
                    return entry
            
            # Se non in top 1000, calcola posizione approssimativa
            return {"rank": "1000+", "user_id": user_id}
            
        except Exception as e:
            print(f"❌ Errore recupero rank utente: {e}")
            return {"rank": "N/A", "user_id": user_id}


def test_gamification_system():
    """Test del sistema di gamification"""
    print("🧪 Test sistema gamification...")
    
    # Crea manager
    gm = GamificationManager("test_gamification.db")
    
    # Test progresso utente
    print("\n📊 Test progresso utente...")
    progress = gm.get_user_progress("test_user")
    print(f"Progresso iniziale: Livello {progress.level}, {progress.total_points} punti")
    
    # Test assegnazione punti
    print("\n🎯 Test assegnazione punti...")
    result = gm.award_points("test_user", 150, "test")
    print(f"Punti assegnati: {result}")
    
    # Test visita monumento
    print("\n🏛️ Test visita monumento...")
    visit_data = {
        "monument_name": "Torre Eiffel",
        "location": "Parigi, Francia",
        "timestamp": datetime.now().isoformat()
    }
    
    visit_result = gm.process_monument_visit("test_user", visit_data)
    print(f"Risultato visita: {visit_result}")
    
    # Test sfide giornaliere
    print("\n🎯 Test sfide giornaliere...")
    challenges = gm.get_daily_challenges("test_user")
    print(f"Sfide attive: {len(challenges)}")
    for challenge in challenges:
        print(f"- {challenge['name']}: {challenge['progress']}/{challenge['target']}")
    
    # Test classifica
    print("\n🏆 Test classifica...")
    leaderboard = gm.get_leaderboard("points", 5)
    print("Top 5 per punti:")
    for entry in leaderboard:
        print(f"{entry['rank']}. {entry['user_id']}: {entry['points']} punti")
    
    print("\n✅ Test gamification completato!")


if __name__ == "__main__":
    test_gamification_system()
