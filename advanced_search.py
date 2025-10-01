"""
Advanced Search System per Monument Recognizer
Sistema di ricerca intelligente con filtri, autocompletamento e raccomandazioni AI
"""

import sqlite3
import json
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import math
import re
from collections import defaultdict, Counter


class SearchCategory(Enum):
    """Categorie di ricerca disponibili"""
    ALL = "all"
    MONUMENTS = "monuments"
    CITIES = "cities"
    STYLES = "styles"
    EPOCHS = "epochs"
    USERS = "users"


class SearchFilter(Enum):
    """Tipi di filtri disponibili"""
    DISTANCE = "distance"
    ERA = "era"
    STYLE = "style"
    RATING = "rating"
    VISITED = "visited"
    POPULARITY = "popularity"
    RECENT = "recent"


@dataclass
class SearchResult:
    """Risultato di ricerca singolo"""
    id: str
    type: SearchCategory
    title: str
    subtitle: str
    description: str
    image_url: Optional[str]
    coordinates: Optional[Tuple[float, float]]
    score: float
    metadata: Dict


@dataclass
class SearchQuery:
    """Query di ricerca strutturata"""
    text: str
    category: SearchCategory = SearchCategory.ALL
    filters: Dict[SearchFilter, any] = None
    user_location: Optional[Tuple[float, float]] = None
    limit: int = 20
    offset: int = 0


class MonumentDatabase:
    """Database dei monumenti con info estese per la ricerca"""
    
    def __init__(self, db_path: str = "monuments_search.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_sample_data()
    
    def init_database(self):
        """Inizializza il database dei monumenti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella monumenti principale
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monuments (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT,
                country TEXT,
                latitude REAL,
                longitude REAL,
                style TEXT,
                era TEXT,
                built_year INTEGER,
                description TEXT,
                image_url TEXT,
                wikipedia_url TEXT,
                rating REAL DEFAULT 0,
                visit_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella tag per categorizzazione flessibile
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monument_tags (
                monument_id TEXT,
                tag TEXT,
                FOREIGN KEY (monument_id) REFERENCES monuments (id)
            )
        ''')
        
        # Tabella per full-text search
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS monuments_fts USING fts5(
                id, name, city, country, style, era, description, tags,
                content='monuments'
            )
        ''')
        
        # Indici per performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_monuments_location ON monuments (latitude, longitude)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_monuments_style ON monuments (style)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_monuments_era ON monuments (era)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_monuments_rating ON monuments (rating)')
        
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Popola database con dati di esempio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Controlla se già popolato
        cursor.execute('SELECT COUNT(*) FROM monuments')
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Monumenti italiani di esempio
        sample_monuments = [
            {
                'id': 'colosseo',
                'name': 'Colosseo',
                'city': 'Roma',
                'country': 'Italia',
                'latitude': 41.8902,
                'longitude': 12.4922,
                'style': 'Romano',
                'era': 'Antica',
                'built_year': 80,
                'description': 'Anfiteatro romano, simbolo di Roma e dell\'Impero Romano',
                'rating': 4.8,
                'visit_count': 150000,
                'tags': ['anfiteatro', 'gladiatori', 'unesco', 'iconico']
            },
            {
                'id': 'torre_pisa',
                'name': 'Torre di Pisa',
                'city': 'Pisa',
                'country': 'Italia', 
                'latitude': 43.7230,
                'longitude': 10.3966,
                'style': 'Romanico',
                'era': 'Medievale',
                'built_year': 1173,
                'description': 'Campanile pendente famoso in tutto il mondo',
                'rating': 4.5,
                'visit_count': 80000,
                'tags': ['torre', 'pendente', 'campanile', 'unesco']
            },
            {
                'id': 'duomo_milano',
                'name': 'Duomo di Milano',
                'city': 'Milano',
                'country': 'Italia',
                'latitude': 45.4642,
                'longitude': 9.1900,
                'style': 'Gotico',
                'era': 'Medievale',
                'built_year': 1386,
                'description': 'Cattedrale gotica con magnifiche guglie',
                'rating': 4.7,
                'visit_count': 120000,
                'tags': ['cattedrale', 'gotico', 'guglie', 'milano']
            },
            {
                'id': 'pantheon',
                'name': 'Pantheon',
                'city': 'Roma',
                'country': 'Italia',
                'latitude': 41.8986,
                'longitude': 12.4769,
                'style': 'Romano',
                'era': 'Antica',
                'built_year': 126,
                'description': 'Tempio romano perfettamente conservato',
                'rating': 4.6,
                'visit_count': 90000,
                'tags': ['tempio', 'cupola', 'romano', 'conservato']
            },
            {
                'id': 'ponte_vecchio',
                'name': 'Ponte Vecchio',
                'city': 'Firenze',
                'country': 'Italia',
                'latitude': 43.7683,
                'longitude': 11.2533,
                'style': 'Medievale',
                'era': 'Medievale',
                'built_year': 1345,
                'description': 'Ponte medievale con botteghe di orafi',
                'rating': 4.4,
                'visit_count': 70000,
                'tags': ['ponte', 'orafi', 'arno', 'medievale']
            },
            {
                'id': 'sagrada_familia',
                'name': 'Sagrada Familia',
                'city': 'Barcellona',
                'country': 'Spagna',
                'latitude': 41.4036,
                'longitude': 2.1744,
                'style': 'Art Nouveau',
                'era': 'Moderna',
                'built_year': 1882,
                'description': 'Basilica di Gaudí ancora in costruzione',
                'rating': 4.9,
                'visit_count': 200000,
                'tags': ['gaudi', 'basilica', 'art-nouveau', 'barcellona']
            }
        ]
        
        for monument in sample_monuments:
            # Inserisci monumento
            tags = monument.pop('tags', [])
            cursor.execute('''
                INSERT OR REPLACE INTO monuments 
                (id, name, city, country, latitude, longitude, style, era, built_year, 
                 description, rating, visit_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                monument['id'], monument['name'], monument['city'], monument['country'],
                monument['latitude'], monument['longitude'], monument['style'], 
                monument['era'], monument['built_year'], monument['description'],
                monument['rating'], monument['visit_count']
            ))
            
            # Inserisci tag
            for tag in tags:
                cursor.execute('INSERT INTO monument_tags (monument_id, tag) VALUES (?, ?)',
                             (monument['id'], tag))
            
            # Inserisci in FTS
            tags_str = ' '.join(tags)
            cursor.execute('''
                INSERT INTO monuments_fts (id, name, city, country, style, era, description, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                monument['id'], monument['name'], monument['city'], monument['country'],
                monument['style'], monument['era'], monument['description'], tags_str
            ))
        
        conn.commit()
        conn.close()


class AdvancedSearchEngine:
    """Motore di ricerca avanzato con AI e algoritmi intelligenti"""
    
    def __init__(self, db_path: str = "monuments_search.db", visits_db: str = "visits.db"):
        self.monument_db = MonumentDatabase(db_path)
        self.db_path = db_path
        self.visits_db = visits_db
        self.user_preferences = {}
        self.search_history = defaultdict(list)
    
    def search(self, query: SearchQuery, user_id: Optional[str] = None) -> List[SearchResult]:
        """Ricerca principale con ranking intelligente"""
        results = []
        
        # Full-text search
        fts_results = self._full_text_search(query)
        results.extend(fts_results)
        
        # Ricerca semantica (similarità)
        semantic_results = self._semantic_search(query)
        results.extend(semantic_results)
        
        # Applica filtri
        filtered_results = self._apply_filters(results, query)
        
        # Applica ranking personalizzato
        if user_id:
            filtered_results = self._personalized_ranking(filtered_results, user_id, query)
        
        # Rimuovi duplicati mantenendo il migliore score
        unique_results = self._deduplicate_results(filtered_results)
        
        # Ordina per score e limita risultati
        final_results = sorted(unique_results, key=lambda x: x.score, reverse=True)
        
        # Traccia ricerca per analytics
        if user_id:
            self._track_search(user_id, query, len(final_results))
        
        return final_results[query.offset:query.offset + query.limit]
    
    def _full_text_search(self, query: SearchQuery) -> List[SearchResult]:
        """Ricerca full-text nei monumenti"""
        if not query.text.strip():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query FTS con ranking
        search_text = query.text.replace("'", "''")  # Escape quotes
        
        try:
            cursor.execute('''
                SELECT m.* FROM monuments m
                JOIN monuments_fts fts ON m.id = fts.id
                WHERE monuments_fts MATCH ?
                LIMIT 50
            ''', (search_text,))
        except sqlite3.OperationalError:
            # Fallback a ricerca semplice se FTS fallisce
            cursor.execute('''
                SELECT * FROM monuments
                WHERE name LIKE ? OR city LIKE ? OR description LIKE ?
                LIMIT 50
            ''', (f"%{query.text}%", f"%{query.text}%", f"%{query.text}%"))
        
        results = []
        for row in cursor.fetchall():
            result = self._row_to_search_result(row, SearchCategory.MONUMENTS)
            # Score basato su FTS rank + popolarità
            result.score = self._calculate_fts_score(row, query.text)
            results.append(result)
        
        conn.close()
        return results
    
    def _semantic_search(self, query: SearchQuery) -> List[SearchResult]:
        """Ricerca semantica basata su similarità"""
        if not query.text.strip():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ricerca per similarità in descrizioni e nomi
        cursor.execute('SELECT * FROM monuments')
        all_monuments = cursor.fetchall()
        
        results = []
        query_lower = query.text.lower()
        
        for monument in all_monuments:
            similarity_score = self._calculate_semantic_similarity(monument, query_lower)
            if similarity_score > 0.1:  # Soglia minima
                result = self._row_to_search_result(monument, SearchCategory.MONUMENTS)
                result.score = similarity_score
                results.append(result)
        
        conn.close()
        return results
    
    def _calculate_semantic_similarity(self, monument_row: tuple, query: str) -> float:
        """Calcola similarità semantica tra query e monumento"""
        # Estrai campi testo dal monumento con gestione sicura dei tipi
        def safe_string(value):
            return str(value).lower() if value is not None else ""
        
        name = safe_string(monument_row[1])
        city = safe_string(monument_row[2]) 
        style = safe_string(monument_row[6])  # Corretto indice per style
        era = safe_string(monument_row[7])    # Corretto indice per era 
        description = safe_string(monument_row[9])  # Corretto indice per description
        
        # Testo completo del monumento
        monument_text = f"{name} {city} {style} {era} {description}"
        
        # Calcola similarità basata su parole comuni
        query_words = set(re.findall(r'\w+', query))
        monument_words = set(re.findall(r'\w+', monument_text))
        
        if not query_words:
            return 0.0
        
        # Jaccard similarity
        intersection = len(query_words.intersection(monument_words))
        union = len(query_words.union(monument_words))
        
        jaccard = intersection / union if union > 0 else 0
        
        # Boost per match esatti nel nome
        name_boost = 0.5 if any(word in name for word in query_words) else 0
        
        # Boost per popolarità
        visit_count = monument_row[13] if len(monument_row) > 13 and monument_row[13] else 0
        popularity_boost = min(float(visit_count) / 100000, 0.3) if visit_count else 0
        
        return jaccard + name_boost + popularity_boost
    
    def _calculate_fts_score(self, row: tuple, query: str) -> float:
        """Calcola score per risultato FTS"""
        # Score base da FTS (assumendo che rank sia nell'ultima colonna)
        base_score = 1.0  # FTS non fornisce score numerico diretto
        
        # Boost per popolarità (visit_count) - row[13] per visit_count
        visit_count = row[13] if len(row) > 13 and row[13] else 0
        popularity_score = min(float(visit_count) / 100000, 0.5) if visit_count else 0
        
        # Boost per rating - row[12] per rating
        rating = row[12] if len(row) > 12 and row[12] else 0
        rating_score = (float(rating) / 5.0) * 0.3 if rating else 0
        
        # Penalty per distanza (se location fornita)
        distance_penalty = 0  # TODO: Implementare quando location è disponibile
        
        return base_score + popularity_score + rating_score - distance_penalty
    
    def _apply_filters(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Applica filtri ai risultati"""
        if not query.filters:
            return results
        
        filtered = results.copy()
        
        for filter_type, filter_value in query.filters.items():
            if filter_type == SearchFilter.DISTANCE and query.user_location:
                max_distance = filter_value  # in km
                filtered = [r for r in filtered if self._calculate_distance(
                    query.user_location, r.coordinates) <= max_distance if r.coordinates]
            
            elif filter_type == SearchFilter.ERA:
                filtered = [r for r in filtered if r.metadata.get('era') == filter_value]
            
            elif filter_type == SearchFilter.STYLE:
                filtered = [r for r in filtered if r.metadata.get('style') == filter_value]
            
            elif filter_type == SearchFilter.RATING:
                min_rating = filter_value
                filtered = [r for r in filtered if r.metadata.get('rating', 0) >= min_rating]
            
            elif filter_type == SearchFilter.VISITED:
                # TODO: Filtra per monumenti visitati/non visitati
                pass
            
            elif filter_type == SearchFilter.POPULARITY:
                min_visits = filter_value
                filtered = [r for r in filtered if r.metadata.get('visit_count', 0) >= min_visits]
        
        return filtered
    
    def _personalized_ranking(self, results: List[SearchResult], user_id: str, query: SearchQuery) -> List[SearchResult]:
        """Applica ranking personalizzato basato su preferenze utente"""
        user_prefs = self.get_user_preferences(user_id)
        
        for result in results:
            personalization_boost = 0.0
            
            # Boost per stili preferiti
            if result.metadata.get('style') in user_prefs.get('preferred_styles', []):
                personalization_boost += 0.2
            
            # Boost per ere preferite
            if result.metadata.get('era') in user_prefs.get('preferred_eras', []):
                personalization_boost += 0.15
            
            # Boost per città già visitate
            if result.metadata.get('city') in user_prefs.get('visited_cities', []):
                personalization_boost += 0.1
            
            # Penalità per monumenti già visitati di recente
            if result.id in user_prefs.get('recently_visited', []):
                personalization_boost -= 0.3
            
            result.score += personalization_boost
        
        return results
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Ottiene preferenze utente da cronologia visite"""
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]
        
        prefs = {
            'preferred_styles': [],
            'preferred_eras': [],
            'visited_cities': [],
            'recently_visited': []
        }
        
        try:
            # Analizza cronologia visite
            conn = sqlite3.connect(self.visits_db)
            cursor = conn.cursor()
            
            # Stili più visitati
            cursor.execute('''
                SELECT m.style, COUNT(*) as count 
                FROM visits v 
                JOIN monuments m ON v.monument_name = m.name
                WHERE v.user_id = ? 
                GROUP BY m.style 
                ORDER BY count DESC 
                LIMIT 3
            ''', (user_id,))
            
            prefs['preferred_styles'] = [row[0] for row in cursor.fetchall()]
            
            # Ere più visitate
            cursor.execute('''
                SELECT m.era, COUNT(*) as count 
                FROM visits v 
                JOIN monuments m ON v.monument_name = m.name
                WHERE v.user_id = ? 
                GROUP BY m.era 
                ORDER BY count DESC 
                LIMIT 3
            ''', (user_id,))
            
            prefs['preferred_eras'] = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
        except Exception as e:
            print(f"Errore nel calcolo preferenze: {e}")
        
        self.user_preferences[user_id] = prefs
        return prefs
    
    def get_autocomplete_suggestions(self, partial_text: str, limit: int = 10) -> List[str]:
        """Fornisce suggerimenti di autocompletamento"""
        if len(partial_text) < 2:
            return []
        
        suggestions = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Suggerimenti da nomi monumenti
        cursor.execute('''
            SELECT DISTINCT name FROM monuments 
            WHERE name LIKE ? 
            ORDER BY visit_count DESC 
            LIMIT ?
        ''', (f"{partial_text}%", limit // 2))
        
        suggestions.extend([row[0] for row in cursor.fetchall()])
        
        # Suggerimenti da città
        cursor.execute('''
            SELECT DISTINCT city FROM monuments 
            WHERE city LIKE ? 
            ORDER BY visit_count DESC 
            LIMIT ?
        ''', (f"{partial_text}%", limit - len(suggestions)))
        
        suggestions.extend([row[0] for row in cursor.fetchall()])
        
        conn.close()
        return suggestions[:limit]
    
    def get_trending_searches(self, days: int = 7, limit: int = 10) -> List[str]:
        """Ottiene ricerche di tendenza"""
        # Simulazione - in produzione analizzare search_history
        return [
            "Colosseo Roma",
            "Duomo Milano", 
            "Torre Pisa",
            "Sagrada Familia",
            "Pantheon",
            "Ponte Vecchio",
            "Fontana Trevi",
            "Basilica San Pietro"
        ][:limit]
    
    def get_recommendations_for_user(self, user_id: str, limit: int = 5) -> List[SearchResult]:
        """Genera raccomandazioni personalizzate"""
        query = SearchQuery(
            text="",
            category=SearchCategory.MONUMENTS,
            limit=limit * 2  # Prendiamo più risultati per filtering
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Monumenti popolari non ancora visitati
        cursor.execute('''
            SELECT * FROM monuments 
            ORDER BY visit_count DESC, rating DESC 
            LIMIT ?
        ''', (limit * 2,))
        
        results = []
        for row in cursor.fetchall():
            result = self._row_to_search_result(row, SearchCategory.MONUMENTS)
            # Calcola score correttamente
            rating = float(row[12]) if len(row) > 12 and row[12] else 0
            visit_count = float(row[13]) if len(row) > 13 and row[13] else 0
            result.score = (rating * 0.6) + (min(visit_count / 100000, 1.0) * 0.4)  # rating + popularity
            results.append(result)
        
        conn.close()
        
        # Applica personalizzazione
        personalized = self._personalized_ranking(results, user_id, query)
        
        return sorted(personalized, key=lambda x: x.score, reverse=True)[:limit]
    
    def _row_to_search_result(self, row: tuple, category: SearchCategory) -> SearchResult:
        """Converte riga database in SearchResult"""
        def safe_str(value):
            return str(value) if value is not None else ""
        
        return SearchResult(
            id=safe_str(row[0]),
            type=category,
            title=safe_str(row[1]),
            subtitle=f"{safe_str(row[2])}, {safe_str(row[3])}" if row[2] and row[3] else (safe_str(row[2]) or safe_str(row[3]) or ""),
            description=safe_str(row[9]) if len(row) > 9 else "",  # description è all'indice 9
            image_url=safe_str(row[10]) if len(row) > 10 and row[10] else None,
            coordinates=(row[4], row[5]) if row[4] and row[5] else None,
            score=0.0,
            metadata={
                'style': safe_str(row[6]),
                'era': safe_str(row[7]),
                'built_year': row[8] if len(row) > 8 else None,
                'rating': float(row[12]) if len(row) > 12 and row[12] else 0,
                'visit_count': int(row[13]) if len(row) > 13 and row[13] else 0
            }
        )
    
    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calcola distanza tra due coordinate in km (formula di Haversine)"""
        lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
        lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371 * c  # Raggio Terra in km
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Rimuove duplicati mantenendo il risultato con score migliore"""
        seen = {}
        for result in results:
            if result.id not in seen or result.score > seen[result.id].score:
                seen[result.id] = result
        return list(seen.values())
    
    def _track_search(self, user_id: str, query: SearchQuery, results_count: int):
        """Traccia ricerca per analytics"""
        self.search_history[user_id].append({
            'query': query.text,
            'timestamp': datetime.now().isoformat(),
            'category': query.category.value,
            'results_count': results_count
        })


def demo_advanced_search():
    """Demo del sistema di ricerca avanzato"""
    print("🔍 DEMO ADVANCED SEARCH - Monument Recognizer")
    print("=" * 60)
    
    # Inizializza motore di ricerca
    search_engine = AdvancedSearchEngine()
    
    print("📊 Database populato con monumenti di esempio")
    
    # Test ricerca semplice
    print("\n🔍 Test Ricerca Semplice: 'roma'")
    query = SearchQuery(text="roma", limit=5)
    results = search_engine.search(query)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.title} - {result.subtitle}")
        print(f"   Score: {result.score:.3f} | {result.description[:80]}...")
    
    # Test filtri
    print("\n🏛️ Test con Filtri: Era 'Antica'")
    query = SearchQuery(
        text="",
        filters={SearchFilter.ERA: "Antica"},
        limit=5
    )
    results = search_engine.search(query)
    
    for i, result in enumerate(results, 1):
        era = result.metadata.get('era', 'N/A')
        print(f"{i}. {result.title} ({era}) - Score: {result.score:.3f}")
    
    # Test autocompletamento
    print("\n✨ Test Autocompletamento: 'duo'")
    suggestions = search_engine.get_autocomplete_suggestions("duo")
    print("Suggerimenti:", suggestions)
    
    # Test raccomandazioni
    print("\n🎯 Test Raccomandazioni per utente 'mario'")
    recommendations = search_engine.get_recommendations_for_user("mario")
    
    for i, rec in enumerate(recommendations, 1):
        rating = rec.metadata.get('rating', 0)
        visits = rec.metadata.get('visit_count', 0)
        print(f"{i}. {rec.title} - Rating: {rating} | Visite: {visits:,}")
    
    # Test trending
    print("\n📈 Trending Searches:")
    trending = search_engine.get_trending_searches()
    for i, trend in enumerate(trending[:5], 1):
        print(f"{i}. {trend}")
    
    print("\n✅ Demo completato! Sistema di ricerca avanzato funzionante.")


if __name__ == "__main__":
    demo_advanced_search()
