"""
Gamification UI Components for Monument Recognizer
Interfacce Kivy per visualizzare progressi, achievement, sfide e classifiche
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.core.window import Window
from datetime import datetime
from typing import Dict, List, Optional
import threading
from gamification import GamificationManager, UserProgress, Achievement


class ProgressWidget(BoxLayout):
    """Widget per mostrare il progresso dell'utente"""
    
    def __init__(self, progress: UserProgress, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), **kwargs)
        self.progress = progress
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia del progresso"""
        # Header con livello e punti
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80))
        
        # Livello
        level_layout = BoxLayout(orientation='vertical', size_hint_x=0.3)
        level_icon = Label(
            text=self.get_level_icon(self.progress.level),
            font_size='32sp',
            size_hint_y=None,
            height=dp(50)
        )
        level_label = Label(
            text=f"Livello {self.progress.level}",
            font_size='14sp',
            size_hint_y=None,
            height=dp(30)
        )
        level_layout.add_widget(level_icon)
        level_layout.add_widget(level_label)
        
        # Punti totali
        points_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        points_label = Label(
            text=f"💎 {self.progress.total_points:,} Punti",
            font_size='24sp',
            bold=True,
            color=(1, 0.8, 0, 1),
            size_hint_y=None,
            height=dp(40)
        )
        
        # Barra esperienza
        exp_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        exp_info_label = Label(
            text=f"XP: {self.progress.experience} / {self.progress.experience + self.progress.experience_to_next_level}",
            font_size='12sp',
            size_hint_y=None,
            height=dp(20)
        )
        
        exp_progress = ProgressBar(
            max=self.progress.experience + self.progress.experience_to_next_level,
            value=self.progress.experience,
            size_hint_y=None,
            height=dp(20)
        )
        
        exp_layout.add_widget(exp_info_label)
        exp_layout.add_widget(exp_progress)
        
        points_layout.add_widget(points_label)
        points_layout.add_widget(exp_layout)
        
        header_layout.add_widget(level_layout)
        header_layout.add_widget(points_layout)
        
        self.add_widget(header_layout)
        
        # Statistiche aggiuntive
        stats_layout = GridLayout(cols=3, spacing=dp(10), size_hint_y=None, height=dp(60))
        
        # Streak
        streak_widget = self.create_stat_widget(
            "🔥", f"{self.progress.visits_streak}", "Streak"
        )
        
        # Achievement
        achievement_widget = self.create_stat_widget(
            "🏆", f"{len(self.progress.achievements_unlocked)}", "Achievement"
        )
        
        # Badge
        badge_widget = self.create_stat_widget(
            "🎖️", f"{len(self.progress.badges_earned)}", "Badge"
        )
        
        stats_layout.add_widget(streak_widget)
        stats_layout.add_widget(achievement_widget)
        stats_layout.add_widget(badge_widget)
        
        self.add_widget(stats_layout)
    
    def get_level_icon(self, level: int) -> str:
        """Ottiene l'icona appropriata per il livello"""
        if level < 5:
            return "🌱"  # Novizio
        elif level < 10:
            return "🌿"  # Principiante
        elif level < 20:
            return "🌳"  # Esperto
        elif level < 35:
            return "🏔️"  # Veterano
        elif level < 50:
            return "⭐"  # Maestro
        else:
            return "👑"  # Leggenda
    
    def create_stat_widget(self, icon: str, value: str, label: str) -> Widget:
        """Crea un widget per una statistica"""
        layout = BoxLayout(orientation='vertical')
        
        icon_label = Label(
            text=icon,
            font_size='24sp',
            size_hint_y=None,
            height=dp(30)
        )
        
        value_label = Label(
            text=value,
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(20)
        )
        
        desc_label = Label(
            text=label,
            font_size='10sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(10)
        )
        
        layout.add_widget(icon_label)
        layout.add_widget(value_label)
        layout.add_widget(desc_label)
        
        return layout


class AchievementCard(BoxLayout):
    """Card per mostrare un singolo achievement"""
    
    def __init__(self, achievement: Achievement, unlocked: bool = False, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(80), **kwargs)
        self.achievement = achievement
        self.unlocked = unlocked
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia della card"""
        # Background
        with self.canvas.before:
            if self.unlocked:
                Color(0.2, 0.7, 0.3, 0.3)  # Verde per sbloccati
            else:
                Color(0.5, 0.5, 0.5, 0.2)  # Grigio per bloccati
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Icona achievement
        icon_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(60))
        
        icon_label = Label(
            text=self.achievement.icon,
            font_size='32sp' if self.unlocked else '24sp',
            opacity=1.0 if self.unlocked else 0.5
        )
        
        rarity_colors = {
            'common': (0.8, 0.5, 0.2, 1),    # Bronze
            'rare': (0.7, 0.7, 0.7, 1),     # Silver  
            'epic': (1, 0.8, 0, 1),         # Gold
            'legendary': (0.8, 0.2, 0.8, 1) # Purple
        }
        
        rarity_label = Label(
            text=self.get_rarity_icon(self.achievement.rarity.value),
            font_size='12sp',
            color=rarity_colors.get(self.achievement.rarity.value, (1, 1, 1, 1))
        )
        
        icon_layout.add_widget(icon_label)
        icon_layout.add_widget(rarity_label)
        
        # Info achievement
        info_layout = BoxLayout(orientation='vertical')
        
        name_label = Label(
            text=self.achievement.name,
            font_size='16sp',
            bold=True,
            text_size=(None, None),
            halign='left',
            opacity=1.0 if self.unlocked else 0.7
        )
        
        desc_label = Label(
            text=self.achievement.description,
            font_size='12sp',
            text_size=(None, None),
            halign='left',
            color=(0.8, 0.8, 0.8, 1),
            opacity=1.0 if self.unlocked else 0.5
        )
        
        points_label = Label(
            text=f"💎 {self.achievement.points} punti",
            font_size='10sp',
            text_size=(None, None),
            halign='left',
            color=(1, 0.8, 0, 1)
        )
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(desc_label)
        info_layout.add_widget(points_label)
        
        # Status
        status_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(80))
        
        if self.unlocked:
            status_label = Label(
                text="✅\nSbloccato",
                font_size='12sp',
                halign='center',
                color=(0.2, 0.8, 0.2, 1)
            )
        else:
            status_label = Label(
                text="🔒\nBloccato",
                font_size='12sp',
                halign='center',
                color=(0.6, 0.6, 0.6, 1)
            )
        
        status_layout.add_widget(status_label)
        
        self.add_widget(icon_layout)
        self.add_widget(info_layout)
        self.add_widget(status_layout)
    
    def get_rarity_icon(self, rarity: str) -> str:
        """Ottiene l'icona per la rarità"""
        icons = {
            'common': '🥉',
            'rare': '🥈', 
            'epic': '🥇',
            'legendary': '💎'
        }
        return icons.get(rarity, '⭐')
    
    def update_rect(self, instance, value):
        """Aggiorna il rettangolo di background"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size


class ChallengeCard(BoxLayout):
    """Card per mostrare una sfida"""
    
    def __init__(self, challenge_data: Dict, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(100), **kwargs)
        self.challenge_data = challenge_data
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia della sfida"""
        # Background
        with self.canvas.before:
            if self.challenge_data['completed']:
                Color(0.2, 0.7, 0.2, 0.3)  # Verde per completate
            else:
                Color(0.2, 0.5, 0.8, 0.3)  # Blu per attive
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Icona sfida
        icon_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(60))
        
        icon_label = Label(
            text=self.challenge_data['icon'],
            font_size='36sp'
        )
        
        points_label = Label(
            text=f"+{self.challenge_data['points']}",
            font_size='12sp',
            color=(1, 0.8, 0, 1)
        )
        
        icon_layout.add_widget(icon_label)
        icon_layout.add_widget(points_label)
        
        # Info sfida
        info_layout = BoxLayout(orientation='vertical')
        
        name_label = Label(
            text=self.challenge_data['name'],
            font_size='16sp',
            bold=True,
            text_size=(None, None),
            halign='left'
        )
        
        desc_label = Label(
            text=self.challenge_data['description'],
            font_size='12sp',
            text_size=(None, None),
            halign='left',
            color=(0.8, 0.8, 0.8, 1)
        )
        
        # Barra progresso
        progress_layout = BoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=None, height=dp(25))
        
        progress_bar = ProgressBar(
            max=self.challenge_data['target'],
            value=self.challenge_data['progress'],
            size_hint_x=0.7
        )
        
        progress_text = Label(
            text=f"{self.challenge_data['progress']}/{self.challenge_data['target']}",
            font_size='12sp',
            size_hint_x=0.3
        )
        
        progress_layout.add_widget(progress_bar)
        progress_layout.add_widget(progress_text)
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(desc_label)
        info_layout.add_widget(progress_layout)
        
        # Status
        status_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(80))
        
        if self.challenge_data['completed']:
            status_label = Label(
                text="✅\nCompletata",
                font_size='12sp',
                halign='center',
                color=(0.2, 0.8, 0.2, 1)
            )
        else:
            progress_percent = (self.challenge_data['progress'] / self.challenge_data['target']) * 100
            status_label = Label(
                text=f"⏳\n{progress_percent:.0f}%",
                font_size='12sp',
                halign='center',
                color=(0.2, 0.5, 0.8, 1)
            )
        
        status_layout.add_widget(status_label)
        
        self.add_widget(icon_layout)
        self.add_widget(info_layout)
        self.add_widget(status_layout)
    
    def update_rect(self, instance, value):
        """Aggiorna il rettangolo di background"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size


class LeaderboardCard(BoxLayout):
    """Card per la classifica"""
    
    def __init__(self, entry: Dict, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(60), **kwargs)
        self.entry = entry
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia della classifica"""
        # Background
        with self.canvas.before:
            if self.entry['rank'] <= 3:
                Color(1, 0.8, 0, 0.2)  # Oro per top 3
            else:
                Color(0.9, 0.9, 0.9, 0.5)  # Grigio chiaro
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(5)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Ranking
        rank_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(60))
        
        rank_icon = self.get_rank_icon(self.entry['rank'])
        rank_label = Label(
            text=rank_icon,
            font_size='24sp' if self.entry['rank'] <= 3 else '18sp'
        )
        
        rank_number = Label(
            text=f"#{self.entry['rank']}",
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1)
        )
        
        rank_layout.add_widget(rank_label)
        rank_layout.add_widget(rank_number)
        
        # Info utente
        user_layout = BoxLayout(orientation='vertical')
        
        user_label = Label(
            text=f"👤 {self.entry['user_id']}",
            font_size='16sp',
            bold=True,
            text_size=(None, None),
            halign='left'
        )
        
        level_label = Label(
            text=f"Livello {self.entry['level']} • {self.entry['achievements']} Achievement",
            font_size='12sp',
            text_size=(None, None),
            halign='left',
            color=(0.7, 0.7, 0.7, 1)
        )
        
        user_layout.add_widget(user_label)
        user_layout.add_widget(level_label)
        
        # Punti
        points_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(100))
        
        points_label = Label(
            text=f"💎 {self.entry['points']:,}",
            font_size='16sp',
            bold=True,
            color=(1, 0.8, 0, 1),
            halign='center'
        )
        
        points_desc = Label(
            text="Punti",
            font_size='10sp',
            color=(0.6, 0.6, 0.6, 1),
            halign='center'
        )
        
        points_layout.add_widget(points_label)
        points_layout.add_widget(points_desc)
        
        self.add_widget(rank_layout)
        self.add_widget(user_layout)
        self.add_widget(points_layout)
    
    def get_rank_icon(self, rank: int) -> str:
        """Ottiene l'icona per la posizione in classifica"""
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        else:
            return "🏅"
    
    def update_rect(self, instance, value):
        """Aggiorna il rettangolo di background"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size


class GamificationDashboard(Screen):
    """Dashboard principale della gamification"""
    
    def __init__(self, gamification_manager: GamificationManager, user_id: str, **kwargs):
        super().__init__(**kwargs)
        self.gamification_manager = gamification_manager
        self.user_id = user_id
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configura l'interfaccia della dashboard"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Header
        header = Label(
            text="🎮 Dashboard Gamification",
            size_hint_y=None,
            height=dp(40),
            font_size='20sp',
            bold=True
        )
        main_layout.add_widget(header)
        
        # Pannelli tab
        self.tab_panel = TabbedPanel(
            do_default_tab=False,
            tab_pos='top_left',
            tab_height=dp(40)
        )
        
        # Tab Progresso
        progress_tab = TabbedPanelItem(text='📊 Progresso')
        self.progress_content = ScrollView()
        progress_tab.add_widget(self.progress_content)
        self.tab_panel.add_widget(progress_tab)
        
        # Tab Achievement
        achievements_tab = TabbedPanelItem(text='🏆 Achievement')
        self.achievements_content = ScrollView()
        achievements_tab.add_widget(self.achievements_content)
        self.tab_panel.add_widget(achievements_tab)
        
        # Tab Sfide
        challenges_tab = TabbedPanelItem(text='🎯 Sfide')
        self.challenges_content = ScrollView()
        challenges_tab.add_widget(self.challenges_content)
        self.tab_panel.add_widget(challenges_tab)
        
        # Tab Classifica
        leaderboard_tab = TabbedPanelItem(text='🏅 Classifica')
        self.leaderboard_content = ScrollView()
        leaderboard_tab.add_widget(self.leaderboard_content)
        self.tab_panel.add_widget(leaderboard_tab)
        
        # Imposta tab predefinita
        self.tab_panel.default_tab = progress_tab
        
        main_layout.add_widget(self.tab_panel)
        
        # Pulsanti controlli
        controls_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        refresh_btn = Button(
            text="🔄 Aggiorna",
            size_hint_x=0.5
        )
        refresh_btn.bind(on_press=lambda x: self.load_data())
        
        close_btn = Button(
            text="✖️ Chiudi",
            size_hint_x=0.5
        )
        close_btn.bind(on_press=self.close_dashboard)
        
        controls_layout.add_widget(refresh_btn)
        controls_layout.add_widget(close_btn)
        main_layout.add_widget(controls_layout)
        
        self.add_widget(main_layout)
    
    def load_data(self):
        """Carica tutti i dati della gamification"""
        def load_worker():
            """Worker per caricare dati in background"""
            try:
                # Carica progresso utente
                progress = self.gamification_manager.get_user_progress(self.user_id)
                
                # Carica achievement (sbloccati e non)
                all_achievements = self.gamification_manager.achievements
                
                # Carica sfide giornaliere
                challenges = self.gamification_manager.get_daily_challenges(self.user_id)
                
                # Carica classifica
                leaderboard = self.gamification_manager.get_leaderboard("points", 20)
                user_rank = self.gamification_manager.get_user_rank(self.user_id, "points")
                
                # Aggiorna UI nel thread principale
                Clock.schedule_once(
                    lambda dt: self.update_ui(progress, all_achievements, challenges, leaderboard, user_rank), 0
                )
                
            except Exception as e:
                print(f"❌ Errore caricamento dati gamification: {e}")
        
        # Avvia in thread separato
        threading.Thread(target=load_worker, daemon=True).start()
    
    def update_ui(self, progress: UserProgress, all_achievements: Dict, 
                 challenges: List[Dict], leaderboard: List[Dict], user_rank: Dict):
        """Aggiorna l'interfaccia con i dati caricati"""
        
        # Aggiorna tab progresso
        self.update_progress_tab(progress)
        
        # Aggiorna tab achievement
        self.update_achievements_tab(all_achievements, progress.achievements_unlocked)
        
        # Aggiorna tab sfide
        self.update_challenges_tab(challenges)
        
        # Aggiorna tab classifica
        self.update_leaderboard_tab(leaderboard, user_rank)
    
    def update_progress_tab(self, progress: UserProgress):
        """Aggiorna il tab del progresso"""
        # Crea layout contenuto
        content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Widget progresso principale
        progress_widget = ProgressWidget(progress)
        content_layout.add_widget(progress_widget)
        
        # Sezione titoli sbloccati (se ci sono)
        if hasattr(progress, 'titles') and progress.titles:
            titles_label = Label(
                text="🎖️ Titoli Sbloccati:",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=dp(30),
                halign='left'
            )
            content_layout.add_widget(titles_label)
            
            for title in progress.titles[:5]:  # Mostra max 5 titoli
                title_widget = Label(
                    text=f"• {title}",
                    font_size='14sp',
                    size_hint_y=None,
                    height=dp(25),
                    halign='left',
                    color=(0.2, 0.7, 0.9, 1)
                )
                content_layout.add_widget(title_widget)
        
        # Aggiorna scrollview
        self.progress_content.clear_widgets()
        self.progress_content.add_widget(content_layout)
    
    def update_achievements_tab(self, all_achievements: Dict, unlocked: List[str]):
        """Aggiorna il tab degli achievement"""
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Statistiche achievement
        stats_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        total_label = Label(
            text=f"Totali: {len(all_achievements)}",
            font_size='14sp'
        )
        
        unlocked_label = Label(
            text=f"Sbloccati: {len(unlocked)}",
            font_size='14sp',
            color=(0.2, 0.8, 0.2, 1)
        )
        
        percent = (len(unlocked) / len(all_achievements)) * 100 if all_achievements else 0
        progress_label = Label(
            text=f"Progresso: {percent:.1f}%",
            font_size='14sp',
            color=(1, 0.8, 0, 1)
        )
        
        stats_layout.add_widget(total_label)
        stats_layout.add_widget(unlocked_label)
        stats_layout.add_widget(progress_label)
        content_layout.add_widget(stats_layout)
        
        # Separatore
        separator = Label(
            text="═" * 40,
            size_hint_y=None,
            height=dp(20),
            font_size='10sp'
        )
        content_layout.add_widget(separator)
        
        # Achievement sbloccati prima
        unlocked_achievements = [ach for ach_id, ach in all_achievements.items() if ach_id in unlocked]
        locked_achievements = [ach for ach_id, ach in all_achievements.items() if ach_id not in unlocked]
        
        if unlocked_achievements:
            unlocked_header = Label(
                text="🏆 Achievement Sbloccati",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=dp(30),
                color=(0.2, 0.8, 0.2, 1)
            )
            content_layout.add_widget(unlocked_header)
            
            for achievement in unlocked_achievements:
                card = AchievementCard(achievement, unlocked=True)
                content_layout.add_widget(card)
        
        if locked_achievements:
            locked_header = Label(
                text="🔒 Achievement Da Sbloccare",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=dp(30),
                color=(0.6, 0.6, 0.6, 1)
            )
            content_layout.add_widget(locked_header)
            
            for achievement in locked_achievements:
                card = AchievementCard(achievement, unlocked=False)
                content_layout.add_widget(card)
        
        self.achievements_content.clear_widgets()
        self.achievements_content.add_widget(content_layout)
    
    def update_challenges_tab(self, challenges: List[Dict]):
        """Aggiorna il tab delle sfide"""
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Header sfide
        header = Label(
            text="🎯 Sfide Giornaliere",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content_layout.add_widget(header)
        
        if not challenges:
            no_challenges = Label(
                text="Nessuna sfida attiva.\nTorna domani per nuove sfide!",
                font_size='14sp',
                size_hint_y=None,
                height=dp(60),
                halign='center',
                color=(0.6, 0.6, 0.6, 1)
            )
            content_layout.add_widget(no_challenges)
        else:
            # Sfide completate prima
            completed = [c for c in challenges if c['completed']]
            active = [c for c in challenges if not c['completed']]
            
            if active:
                active_header = Label(
                    text="⏳ Sfide Attive",
                    font_size='16sp',
                    bold=True,
                    size_hint_y=None,
                    height=dp(30),
                    color=(0.2, 0.5, 0.8, 1)
                )
                content_layout.add_widget(active_header)
                
                for challenge in active:
                    card = ChallengeCard(challenge)
                    content_layout.add_widget(card)
            
            if completed:
                completed_header = Label(
                    text="✅ Sfide Completate",
                    font_size='16sp',
                    bold=True,
                    size_hint_y=None,
                    height=dp(30),
                    color=(0.2, 0.8, 0.2, 1)
                )
                content_layout.add_widget(completed_header)
                
                for challenge in completed:
                    card = ChallengeCard(challenge)
                    content_layout.add_widget(card)
        
        self.challenges_content.clear_widgets()
        self.challenges_content.add_widget(content_layout)
    
    def update_leaderboard_tab(self, leaderboard: List[Dict], user_rank: Dict):
        """Aggiorna il tab della classifica"""
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=dp(10))
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Header
        header = Label(
            text="🏅 Classifica Globale",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        content_layout.add_widget(header)
        
        # Posizione utente (se non in top 10)
        if user_rank and user_rank.get('rank', 0) > 10:
            your_rank_header = Label(
                text="📍 La Tua Posizione",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=dp(30),
                color=(0.9, 0.5, 0.1, 1)
            )
            content_layout.add_widget(your_rank_header)
            
            user_card = LeaderboardCard(user_rank)
            content_layout.add_widget(user_card)
            
            separator = Label(
                text="═" * 40,
                size_hint_y=None,
                height=dp(20),
                font_size='10sp'
            )
            content_layout.add_widget(separator)
        
        # Top players
        if leaderboard:
            top_header = Label(
                text="👑 Top Players",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=dp(30),
                color=(1, 0.8, 0, 1)
            )
            content_layout.add_widget(top_header)
            
            for entry in leaderboard:
                card = LeaderboardCard(entry)
                content_layout.add_widget(card)
        else:
            no_data = Label(
                text="Nessun dato di classifica disponibile.",
                font_size='14sp',
                size_hint_y=None,
                height=dp(60),
                halign='center',
                color=(0.6, 0.6, 0.6, 1)
            )
            content_layout.add_widget(no_data)
        
        self.leaderboard_content.clear_widgets()
        self.leaderboard_content.add_widget(content_layout)
    
    def close_dashboard(self, instance):
        """Chiude la dashboard"""
        if self.parent:
            self.parent.remove_widget(self)


class AchievementUnlockedPopup(Popup):
    """Popup celebrativo per achievement sbloccato"""
    
    def __init__(self, achievement: Achievement, **kwargs):
        self.achievement = achievement
        
        super().__init__(
            title="🎉 Achievement Sbloccato!",
            size_hint=(0.8, 0.6),
            auto_dismiss=True,
            **kwargs
        )
        
        self.setup_ui()
        self.start_celebration()
    
    def setup_ui(self):
        """Configura l'interfaccia del popup"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        # Icona grande
        icon_label = Label(
            text=self.achievement.icon,
            font_size='64sp',
            size_hint_y=None,
            height=dp(80)
        )
        main_layout.add_widget(icon_label)
        
        # Nome achievement
        name_label = Label(
            text=self.achievement.name,
            font_size='24sp',
            bold=True,
            size_hint_y=None,
            height=dp(40),
            color=(1, 0.8, 0, 1)
        )
        main_layout.add_widget(name_label)
        
        # Descrizione
        desc_label = Label(
            text=self.achievement.description,
            font_size='16sp',
            size_hint_y=None,
            height=dp(60),
            text_size=(Window.width * 0.6, None),
            halign='center'
        )
        main_layout.add_widget(desc_label)
        
        # Punti ottenuti
        points_label = Label(
            text=f"💎 +{self.achievement.points} Punti!",
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=dp(40),
            color=(0.2, 0.8, 0.2, 1)
        )
        main_layout.add_widget(points_label)
        
        # Rarità
        rarity_colors = {
            'common': (0.8, 0.5, 0.2, 1),
            'rare': (0.7, 0.7, 0.7, 1),
            'epic': (1, 0.8, 0, 1),
            'legendary': (0.8, 0.2, 0.8, 1)
        }
        
        rarity_text = {
            'common': '🥉 Comune',
            'rare': '🥈 Raro',
            'epic': '🥇 Epico', 
            'legendary': '💎 Leggendario'
        }
        
        rarity_label = Label(
            text=rarity_text.get(self.achievement.rarity.value, '⭐ Speciale'),
            font_size='14sp',
            size_hint_y=None,
            height=dp(30),
            color=rarity_colors.get(self.achievement.rarity.value, (1, 1, 1, 1))
        )
        main_layout.add_widget(rarity_label)
        
        # Pulsante OK
        ok_btn = Button(
            text="🎉 Fantastico!",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        ok_btn.bind(on_press=self.dismiss)
        main_layout.add_widget(ok_btn)
        
        self.content = main_layout
    
    def start_celebration(self):
        """Avvia animazioni celebrative"""
        # Animazione bounce per l'icona
        icon_label = self.content.children[4]  # Icona è il 5° widget
        
        # Sequenza di animazioni
        anim1 = Animation(font_size='72sp', duration=0.3)
        anim2 = Animation(font_size='64sp', duration=0.3)
        anim3 = Animation(font_size='68sp', duration=0.2)
        anim4 = Animation(font_size='64sp', duration=0.2)
        
        anim1.bind(on_complete=lambda *args: anim2.start(icon_label))
        anim2.bind(on_complete=lambda *args: anim3.start(icon_label))
        anim3.bind(on_complete=lambda *args: anim4.start(icon_label))
        
        anim1.start(icon_label)


class LevelUpPopup(Popup):
    """Popup per level up"""
    
    def __init__(self, old_level: int, new_level: int, **kwargs):
        self.old_level = old_level
        self.new_level = new_level
        
        super().__init__(
            title="⬆️ Level Up!",
            size_hint=(0.7, 0.5),
            auto_dismiss=True,
            **kwargs
        )
        
        self.setup_ui()
        self.start_animation()
    
    def setup_ui(self):
        """Configura l'interfaccia del popup"""
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # Messaggio level up
        level_label = Label(
            text=f"Livello {self.old_level} → {self.new_level}",
            font_size='32sp',
            bold=True,
            size_hint_y=None,
            height=dp(60),
            color=(1, 0.8, 0, 1)
        )
        main_layout.add_widget(level_label)
        
        # Icona livello
        icon = self.get_level_icon(self.new_level)
        icon_label = Label(
            text=icon,
            font_size='48sp',
            size_hint_y=None,
            height=dp(80)
        )
        main_layout.add_widget(icon_label)
        
        # Congratulazioni
        congrats_label = Label(
            text="Congratulazioni!\nHai raggiunto un nuovo livello!",
            font_size='16sp',
            size_hint_y=None,
            height=dp(60),
            halign='center'
        )
        main_layout.add_widget(congrats_label)
        
        # Pulsante continua
        continue_btn = Button(
            text="🚀 Continua",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        continue_btn.bind(on_press=self.dismiss)
        main_layout.add_widget(continue_btn)
        
        self.content = main_layout
    
    def get_level_icon(self, level: int) -> str:
        """Ottiene l'icona per il livello"""
        if level < 5:
            return "🌱"
        elif level < 10:
            return "🌿"
        elif level < 20:
            return "🌳"
        elif level < 35:
            return "🏔️"
        elif level < 50:
            return "⭐"
        else:
            return "👑"
    
    def start_animation(self):
        """Avvia animazione level up"""
        icon_label = self.content.children[2]  # Icona è il 3° widget
        
        # Animazione rotazione e scala
        anim = Animation(font_size='56sp', duration=0.5) + Animation(font_size='48sp', duration=0.5)
        anim.start(icon_label)


def test_gamification_ui():
    """Test delle interfacce gamification"""
    from kivy.app import App
    from gamification import GamificationManager
    
    class TestApp(App):
        def build(self):
            # Crea manager
            gm = GamificationManager("test_gamification_ui.db")
            
            # Simula alcuni dati
            gm.process_monument_visit("test_user", {
                "monument_name": "Torre Eiffel",
                "location": "Parigi, Francia"
            })
            
            # Crea dashboard
            dashboard = GamificationDashboard(gm, "test_user")
            return dashboard
    
    TestApp().run()


if __name__ == "__main__":
    test_gamification_ui()
