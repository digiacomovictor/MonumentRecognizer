#!/usr/bin/env python3
"""
📊 Dashboard Manager per Monument Recognizer
Sistema completo per statistiche avanzate, grafici e achievement
"""

import os
import json
import math
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter, defaultdict
from dataclasses import dataclass
import webbrowser

# Import per grafici (opzionali)
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    import pandas as pd
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
    
    # Configurazione matplotlib per evitare popup
    plt.switch_backend('Agg')
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 10
    
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("📊 Matplotlib non disponibile. Dashboard funzionerà in modalità base.")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from visit_tracker import VisitTracker, MonumentVisit, UserStats
from user_system import UserSystem


@dataclass
class DashboardStats:
    """Statistiche complete per la dashboard."""
    # Statistiche base
    total_visits: int = 0
    unique_monuments: int = 0
    countries_visited: int = 0
    cities_visited: int = 0
    total_photos: int = 0
    
    # Statistiche temporali
    first_visit_date: Optional[date] = None
    last_visit_date: Optional[date] = None
    most_active_month: Optional[str] = None
    most_active_day: Optional[str] = None
    
    # Statistiche geografiche
    continent_distribution: Dict[str, int] = None
    country_distribution: Dict[str, int] = None
    most_visited_country: Optional[str] = None
    
    # Statistiche architettoniche
    style_distribution: Dict[str, int] = None
    era_distribution: Dict[str, int] = None
    most_visited_style: Optional[str] = None
    
    # Statistiche performance
    recognition_methods: Dict[str, int] = None
    average_confidence: float = 0.0
    success_rate: float = 0.0
    
    # Progressi e achievement
    current_streak: int = 0
    longest_streak: int = 0
    achievement_progress: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.continent_distribution is None:
            self.continent_distribution = {}
        if self.country_distribution is None:
            self.country_distribution = {}
        if self.style_distribution is None:
            self.style_distribution = {}
        if self.era_distribution is None:
            self.era_distribution = {}
        if self.recognition_methods is None:
            self.recognition_methods = {}
        if self.achievement_progress is None:
            self.achievement_progress = {}


class DashboardManager:
    """Manager per dashboard e statistiche avanzate."""
    
    def __init__(self, visit_tracker: VisitTracker, monuments_db: Dict, user_system: UserSystem = None):
        self.visit_tracker = visit_tracker
        self.monuments_db = monuments_db
        self.user_system = user_system
        self.charts_dir = "dashboard_charts"
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # Mappa continenti per paesi
        self.country_to_continent = {
            'Italy': 'Europe', 'France': 'Europe', 'Spain': 'Europe', 'Germany': 'Europe',
            'United Kingdom': 'Europe', 'Greece': 'Europe', 'Russia': 'Europe',
            'USA': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
            'Brazil': 'South America', 'Argentina': 'South America', 'Peru': 'South America',
            'China': 'Asia', 'Japan': 'Asia', 'India': 'Asia', 'Thailand': 'Asia',
            'Egypt': 'Africa', 'Morocco': 'Africa', 'South Africa': 'Africa',
            'Australia': 'Oceania', 'New Zealand': 'Oceania'
        }
        
        # Mapping ere storiche
        self.era_mapping = {
            range(0, 500): "Antichità Classica",
            range(500, 1000): "Medioevo Iniziale", 
            range(1000, 1300): "Medioevo Maturo",
            range(1300, 1500): "Rinascimento",
            range(1500, 1700): "Barocco",
            range(1700, 1800): "Neoclassicismo",
            range(1800, 1900): "XIX Secolo",
            range(1900, 1950): "Modernismo",
            range(1950, 2000): "Contemporaneo",
            range(2000, 2100): "XXI Secolo"
        }
    
    def calculate_comprehensive_stats(self) -> DashboardStats:
        """Calcola statistiche complete per la dashboard."""
        stats = DashboardStats()
        visits = self.visit_tracker.visits
        
        if not visits:
            return stats
        
        # Statistiche base
        stats.total_visits = len(visits)
        stats.unique_monuments = len(set(visit.monument_id for visit in visits))
        stats.total_photos = len([v for v in visits if v.photo_path])
        
        # Date
        visit_dates = [visit.visit_date.date() for visit in visits]
        stats.first_visit_date = min(visit_dates)
        stats.last_visit_date = max(visit_dates)
        
        # Distribuzione geografica
        countries = []
        continents = []
        cities = []
        
        for visit in visits:
            monument_data = self.monuments_db.get(visit.monument_id, {})
            location = monument_data.get('location', '')
            
            # Estrai paese (ultima parte dopo la virgola)
            if ',' in location:
                country = location.split(',')[-1].strip()
                countries.append(country)
                
                # Mappa continente
                continent = self.country_to_continent.get(country, 'Unknown')
                continents.append(continent)
                
                # Estrai città (prima parte)
                city = location.split(',')[0].strip()
                cities.append(city)
        
        stats.country_distribution = dict(Counter(countries))
        stats.continent_distribution = dict(Counter(continents))
        stats.countries_visited = len(set(countries))
        stats.cities_visited = len(set(cities))
        
        if countries:
            stats.most_visited_country = Counter(countries).most_common(1)[0][0]
        
        # Distribuzione stili architettonici
        styles = []
        eras = []
        
        for visit in visits:
            monument_data = self.monuments_db.get(visit.monument_id, {})
            
            # Stile architettonico
            style = monument_data.get('style', 'Unknown')
            styles.append(style)
            
            # Era storica basata su anno di costruzione
            year_built = monument_data.get('year_built', '')
            if year_built and year_built.isdigit():
                year = int(year_built)
                era = self._get_era_from_year(year)
                eras.append(era)
        
        stats.style_distribution = dict(Counter(styles))
        stats.era_distribution = dict(Counter(eras))
        
        if styles:
            stats.most_visited_style = Counter(styles).most_common(1)[0][0]
        
        # Statistiche temporali
        months = [visit.visit_date.strftime('%B') for visit in visits]
        days = [visit.visit_date.strftime('%A') for visit in visits]
        
        if months:
            stats.most_active_month = Counter(months).most_common(1)[0][0]
        if days:
            stats.most_active_day = Counter(days).most_common(1)[0][0]
        
        # Statistiche riconoscimento
        methods = [visit.recognition_method for visit in visits if visit.recognition_method]
        stats.recognition_methods = dict(Counter(methods))
        
        # Confidenza media
        confidences = [visit.confidence_score for visit in visits if visit.confidence_score]
        if confidences:
            stats.average_confidence = sum(confidences) / len(confidences)
        
        # Calcola streak (visite consecutive)
        stats.current_streak, stats.longest_streak = self._calculate_streaks(visits)
        
        # Achievement progress
        stats.achievement_progress = self._calculate_achievements(stats)
        
        return stats
    
    def _get_era_from_year(self, year: int) -> str:
        """Determina l'era storica da un anno."""
        for year_range, era in self.era_mapping.items():
            if year in year_range:
                return era
        return "Era Sconosciuta"
    
    def _calculate_streaks(self, visits: List[MonumentVisit]) -> Tuple[int, int]:
        """Calcola streak corrente e più lungo."""
        if not visits:
            return 0, 0
        
        # Ordina per data
        sorted_visits = sorted(visits, key=lambda x: x.visit_date.date())
        
        current_streak = 0
        longest_streak = 0
        temp_streak = 1
        
        for i in range(1, len(sorted_visits)):
            prev_date = sorted_visits[i-1].visit_date.date()
            curr_date = sorted_visits[i].visit_date.date()
            
            # Se visite in giorni consecutivi o stesso giorno
            if (curr_date - prev_date).days <= 1:
                temp_streak += 1
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
        
        longest_streak = max(longest_streak, temp_streak)
        
        # Streak corrente (se ultima visita è recente)
        if sorted_visits:
            last_visit = sorted_visits[-1].visit_date.date()
            days_since = (date.today() - last_visit).days
            if days_since <= 7:  # Considera attivo se ultima visita entro una settimana
                current_streak = temp_streak
        
        return current_streak, longest_streak
    
    def _calculate_achievements(self, stats: DashboardStats) -> Dict[str, Dict]:
        """Calcola progressi achievement."""
        achievements = {
            'first_steps': {
                'name': '🎯 Primi Passi',
                'description': 'Visita il tuo primo monumento',
                'progress': min(stats.total_visits, 1),
                'target': 1,
                'completed': stats.total_visits >= 1,
                'reward': '10 punti esperienza'
            },
            'explorer': {
                'name': '🗺️ Esploratore',
                'description': 'Visita 5 monumenti diversi',
                'progress': min(stats.unique_monuments, 5),
                'target': 5,
                'completed': stats.unique_monuments >= 5,
                'reward': 'Badge Esploratore'
            },
            'adventurer': {
                'name': '🎒 Avventuriero',
                'description': 'Visita 10 monumenti diversi',
                'progress': min(stats.unique_monuments, 10),
                'target': 10,
                'completed': stats.unique_monuments >= 10,
                'reward': 'Badge Avventuriero'
            },
            'historian': {
                'name': '📚 Storico',
                'description': 'Visita 25 monumenti diversi',
                'progress': min(stats.unique_monuments, 25),
                'target': 25,
                'completed': stats.unique_monuments >= 25,
                'reward': 'Badge Storico'
            },
            'world_traveler': {
                'name': '🌍 Viaggiatore del Mondo',
                'description': 'Visita monumenti in 5 paesi diversi',
                'progress': min(stats.countries_visited, 5),
                'target': 5,
                'completed': stats.countries_visited >= 5,
                'reward': 'Badge Viaggiatore Mondiale'
            },
            'photographer': {
                'name': '📸 Fotografo',
                'description': 'Scatta 10 foto ai monumenti',
                'progress': min(stats.total_photos, 10),
                'target': 10,
                'completed': stats.total_photos >= 10,
                'reward': 'Badge Fotografo'
            },
            'dedicated': {
                'name': '🔥 Dedicato',
                'description': 'Mantieni uno streak di 7 giorni',
                'progress': min(stats.longest_streak, 7),
                'target': 7,
                'completed': stats.longest_streak >= 7,
                'reward': 'Badge Dedizione'
            },
            'architecture_lover': {
                'name': '🏛️ Amante Architettura',
                'description': 'Visita monumenti di 5 stili diversi',
                'progress': min(len(stats.style_distribution), 5),
                'target': 5,
                'completed': len(stats.style_distribution) >= 5,
                'reward': 'Badge Architettura'
            }
        }
        
        return achievements
    
    def generate_matplotlib_charts(self, stats: DashboardStats) -> Dict[str, str]:
        """Genera grafici usando matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            return {}
        
        chart_files = {}
        
        try:
            # 1. Timeline visite nel tempo
            if self.visit_tracker.visits:
                chart_files['timeline'] = self._create_timeline_chart(stats)
            
            # 2. Distribuzione geografica
            if stats.country_distribution:
                chart_files['countries'] = self._create_countries_chart(stats)
            
            # 3. Distribuzione stili architettonici
            if stats.style_distribution:
                chart_files['styles'] = self._create_styles_chart(stats)
            
            # 4. Distribuzione per epoca
            if stats.era_distribution:
                chart_files['eras'] = self._create_eras_chart(stats)
            
            # 5. Metodi di riconoscimento
            if stats.recognition_methods:
                chart_files['methods'] = self._create_methods_chart(stats)
            
        except Exception as e:
            print(f"⚠️ Errore generazione grafici matplotlib: {e}")
        
        return chart_files
    
    def _create_timeline_chart(self, stats: DashboardStats) -> str:
        """Crea grafico timeline visite."""
        visits = self.visit_tracker.visits
        dates = [visit.visit_date.date() for visit in visits]
        
        # Conta visite per giorno
        date_counts = Counter(dates)
        sorted_dates = sorted(date_counts.keys())
        counts = [date_counts[d] for d in sorted_dates]
        
        plt.figure(figsize=(12, 6))
        plt.plot(sorted_dates, counts, marker='o', linewidth=2, markersize=6)
        plt.title('🕐 Timeline delle Tue Visite ai Monumenti', fontsize=16, fontweight='bold')
        plt.xlabel('Data')
        plt.ylabel('Numero di Visite')
        plt.grid(True, alpha=0.3)
        
        # Formatta asse x
        if len(sorted_dates) > 30:
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        else:
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filename = os.path.join(self.charts_dir, 'timeline_chart.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_countries_chart(self, stats: DashboardStats) -> str:
        """Crea grafico paesi visitati."""
        # Prendi top 8 paesi
        top_countries = dict(Counter(stats.country_distribution).most_common(8))
        
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(top_countries)))
        
        plt.pie(top_countries.values(), 
               labels=top_countries.keys(),
               autopct='%1.1f%%',
               startangle=90,
               colors=colors)
        
        plt.title('🌍 Distribuzione Geografica delle Tue Visite', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        filename = os.path.join(self.charts_dir, 'countries_chart.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_styles_chart(self, stats: DashboardStats) -> str:
        """Crea grafico stili architettonici."""
        styles = dict(Counter(stats.style_distribution).most_common(6))
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(styles.keys(), styles.values(), 
                      color=plt.cm.viridis(np.linspace(0, 1, len(styles))))
        
        plt.title('🏛️ Stili Architettonici Preferiti', fontsize=16, fontweight='bold')
        plt.xlabel('Stile Architettonico')
        plt.ylabel('Numero di Monumenti Visitati')
        plt.xticks(rotation=45, ha='right')
        
        # Aggiungi valori sopra le barre
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.charts_dir, 'styles_chart.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_eras_chart(self, stats: DashboardStats) -> str:
        """Crea grafico ere storiche."""
        eras = stats.era_distribution
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(eras.keys(), eras.values(),
                      color=plt.cm.plasma(np.linspace(0, 1, len(eras))))
        
        plt.title('⏳ Ere Storiche dei Monumenti Visitati', fontsize=16, fontweight='bold')
        plt.xlabel('Era Storica')
        plt.ylabel('Numero di Monumenti')
        plt.xticks(rotation=45, ha='right')
        
        # Aggiungi valori
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        filename = os.path.join(self.charts_dir, 'eras_chart.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_methods_chart(self, stats: DashboardStats) -> str:
        """Crea grafico metodi di riconoscimento."""
        methods = stats.recognition_methods
        
        plt.figure(figsize=(8, 8))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        plt.pie(methods.values(),
               labels=methods.keys(),
               autopct='%1.1f%%',
               startangle=90,
               colors=colors[:len(methods)])
        
        plt.title('🔍 Metodi di Riconoscimento Utilizzati', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        filename = os.path.join(self.charts_dir, 'methods_chart.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def generate_plotly_interactive_dashboard(self, stats: DashboardStats) -> str:
        """Genera dashboard interattiva con Plotly."""
        if not PLOTLY_AVAILABLE:
            return ""
        
        try:
            # Crea subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    '📊 Timeline Visite', '🌍 Distribuzione Paesi',
                    '🏛️ Stili Architettonici', '⏳ Ere Storiche',
                    '🔍 Metodi Riconoscimento', '🏆 Progressi Achievement'
                ),
                specs=[[{"type": "scatter"}, {"type": "pie"}],
                      [{"type": "bar"}, {"type": "bar"}], 
                      [{"type": "pie"}, {"type": "bar"}]]
            )
            
            # 1. Timeline
            if self.visit_tracker.visits:
                dates = [visit.visit_date.date() for visit in self.visit_tracker.visits]
                date_counts = Counter(dates)
                sorted_dates = sorted(date_counts.keys())
                counts = [date_counts[d] for d in sorted_dates]
                
                fig.add_trace(
                    go.Scatter(x=sorted_dates, y=counts, mode='lines+markers',
                             name='Visite', line=dict(color='#1f77b4')),
                    row=1, col=1
                )
            
            # 2. Paesi (pie chart)
            if stats.country_distribution:
                countries = list(stats.country_distribution.keys())[:6]
                counts = list(stats.country_distribution.values())[:6]
                
                fig.add_trace(
                    go.Pie(labels=countries, values=counts, name="Paesi"),
                    row=1, col=2
                )
            
            # 3. Stili (bar chart)
            if stats.style_distribution:
                styles = list(stats.style_distribution.keys())[:6]
                counts = list(stats.style_distribution.values())[:6]
                
                fig.add_trace(
                    go.Bar(x=styles, y=counts, name="Stili",
                          marker_color='#2ca02c'),
                    row=2, col=1
                )
            
            # 4. Ere (bar chart)
            if stats.era_distribution:
                eras = list(stats.era_distribution.keys())
                counts = list(stats.era_distribution.values())
                
                fig.add_trace(
                    go.Bar(x=eras, y=counts, name="Ere",
                          marker_color='#ff7f0e'),
                    row=2, col=2
                )
            
            # 5. Metodi (pie chart)
            if stats.recognition_methods:
                methods = list(stats.recognition_methods.keys())
                counts = list(stats.recognition_methods.values())
                
                fig.add_trace(
                    go.Pie(labels=methods, values=counts, name="Metodi"),
                    row=3, col=1
                )
            
            # 6. Achievement progress
            if stats.achievement_progress:
                achievements = list(stats.achievement_progress.keys())[:5]
                progress = [stats.achievement_progress[a]['progress'] 
                           for a in achievements]
                
                fig.add_trace(
                    go.Bar(x=achievements, y=progress, name="Achievement",
                          marker_color='#d62728'),
                    row=3, col=2
                )
            
            # Layout
            fig.update_layout(
                height=900,
                title_text="📊 Dashboard Monument Recognizer",
                title_x=0.5,
                showlegend=False
            )
            
            # Salva dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.charts_dir, f"interactive_dashboard_{timestamp}.html")
            
            pyo.plot(fig, filename=filename, auto_open=False)
            return filename
            
        except Exception as e:
            print(f"⚠️ Errore generazione dashboard Plotly: {e}")
            return ""
    
    def generate_html_report(self, stats: DashboardStats, chart_files: Dict[str, str] = None) -> str:
        """Genera report HTML completo."""
        if chart_files is None:
            chart_files = {}
        
        # Header HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Dashboard Monument Recognizer</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .section {{
            margin: 40px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }}
        .achievement-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .achievement-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #28a745;
        }}
        .achievement-card.completed {{
            border-left-color: #28a745;
            background: #d4edda;
        }}
        .achievement-card.in-progress {{
            border-left-color: #ffc107;
            background: #fff3cd;
        }}
        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 10px;
            margin: 10px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #28a745, #20c997);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 La Tua Dashboard Monument Recognizer</h1>
            <p>Report generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats.total_visits}</div>
                <div class="stat-label">Visite Totali</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.unique_monuments}</div>
                <div class="stat-label">Monumenti Unici</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.countries_visited}</div>
                <div class="stat-label">Paesi Esplorati</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.cities_visited}</div>
                <div class="stat-label">Città Visitate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.total_photos}</div>
                <div class="stat-label">Foto Scattate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.current_streak}</div>
                <div class="stat-label">Streak Attuale</div>
            </div>
        </div>
        """
        
        # Sezione grafici
        if chart_files:
            html_content += '<div class="section"><h2>📈 Grafici e Analisi</h2>'
            
            for chart_type, chart_path in chart_files.items():
                if os.path.exists(chart_path):
                    # Converti path assoluto in relativo
                    rel_path = os.path.relpath(chart_path)
                    html_content += f'''
                    <div class="chart-container">
                        <img src="{rel_path}" alt="Grafico {chart_type}">
                    </div>
                    '''
            
            html_content += '</div>'
        
        # Sezione achievement
        html_content += f'''
        <div class="section">
            <h2>🏆 I Tuoi Achievement</h2>
            <div class="achievement-grid">
        '''
        
        for achievement_id, achievement in stats.achievement_progress.items():
            progress_percent = (achievement['progress'] / achievement['target']) * 100
            status_class = 'completed' if achievement['completed'] else 'in-progress'
            status_emoji = '✅' if achievement['completed'] else '🔄'
            
            html_content += f'''
                <div class="achievement-card {status_class}">
                    <h3>{status_emoji} {achievement['name']}</h3>
                    <p>{achievement['description']}</p>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress_percent}%;"></div>
                    </div>
                    <p><strong>{achievement['progress']}</strong> / {achievement['target']}</p>
                    <small>🎁 {achievement['reward']}</small>
                </div>
            '''
        
        html_content += '''
            </div>
        </div>
        '''
        
        # Informazioni aggiuntive
        html_content += f'''
        <div class="section">
            <h2>ℹ️ Informazioni Dettagliate</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats.first_visit_date.strftime('%d/%m/%Y') if stats.first_visit_date else 'N/A'}</div>
                    <div class="stat-label">Prima Visita</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.last_visit_date.strftime('%d/%m/%Y') if stats.last_visit_date else 'N/A'}</div>
                    <div class="stat-label">Ultima Visita</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.most_visited_country or 'N/A'}</div>
                    <div class="stat-label">Paese Preferito</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.most_visited_style or 'N/A'}</div>
                    <div class="stat-label">Stile Preferito</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.most_active_month or 'N/A'}</div>
                    <div class="stat-label">Mese Più Attivo</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats.longest_streak}</div>
                    <div class="stat-label">Streak Più Lungo</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🏛️ Generato da Monument Recognizer v2.0 | Continua a esplorare il mondo!</p>
        </div>
    </div>
</body>
</html>
        '''
        
        # Salva file HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.charts_dir, f"dashboard_report_{timestamp}.html")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def open_dashboard_in_browser(self, html_file: str) -> bool:
        """Apre la dashboard nel browser."""
        try:
            abs_path = os.path.abspath(html_file)
            webbrowser.open(f'file://{abs_path}')
            return True
        except Exception as e:
            print(f"❌ Errore apertura dashboard: {e}")
            return False
    
    def get_user_ranking(self) -> Dict[str, Any]:
        """Calcola ranking utente (se sistema multi-utente)."""
        # Placeholder per future implementazioni multi-utente
        stats = self.calculate_comprehensive_stats()
        
        # Calcola punteggio basato su vari fattori
        score = 0
        score += stats.unique_monuments * 10  # 10 punti per monumento unico
        score += stats.countries_visited * 50  # 50 punti per paese
        score += stats.total_photos * 5  # 5 punti per foto
        score += stats.longest_streak * 20  # 20 punti per streak
        
        # Bonus achievement
        completed_achievements = sum(1 for a in stats.achievement_progress.values() if a['completed'])
        score += completed_achievements * 100
        
        return {
            'score': score,
            'rank': 1,  # Placeholder
            'level': min(score // 1000 + 1, 50),  # Livello basato su punteggio
            'next_level_points': ((score // 1000) + 1) * 1000 - score
        }
