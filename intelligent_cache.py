"""
Intelligent Cache System per Monument Recognizer
Sistema di caching avanzato per ottimizzare performance e UX
"""

import sqlite3
import json
import hashlib
import threading
import time
import os
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, OrderedDict
import pickle
import gzip


class CacheType(Enum):
    """Tipi di cache disponibili"""
    RECOGNITION_RESULT = "recognition"     # Risultati riconoscimento AI
    IMAGE_PROCESSED = "image_processed"    # Immagini elaborate/compresse
    SEARCH_RESULT = "search"               # Risultati di ricerca
    MAP_DATA = "map_data"                  # Dati mappe e coordinate
    USER_DATA = "user_data"                # Dati utente frequenti
    API_RESPONSE = "api_response"          # Risposte API esterne
    THUMBNAIL = "thumbnail"                # Thumbnail immagini
    GEOLOCATION = "geolocation"           # Dati geolocalizzazione


class CacheStrategy(Enum):
    """Strategie di caching"""
    LRU = "lru"                    # Least Recently Used
    LFU = "lfu"                    # Least Frequently Used
    TTL = "ttl"                    # Time To Live
    ADAPTIVE = "adaptive"          # Adattiva basata su pattern di uso


@dataclass
class CacheEntry:
    """Entry singola nella cache"""
    key: str
    data: Any
    cache_type: CacheType
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def is_expired(self) -> bool:
        """Verifica se l'entry è scaduta"""
        if self.ttl_seconds is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl_seconds)
    
    def update_access(self):
        """Aggiorna statistiche di accesso"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class IntelligentCache:
    """Sistema di cache intelligente multi-level"""
    
    def __init__(self, 
                 max_memory_mb: int = 100,
                 max_disk_mb: int = 500,
                 cache_dir: str = "cache",
                 db_path: str = "cache_meta.db"):
        
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_disk_bytes = max_disk_mb * 1024 * 1024
        self.cache_dir = cache_dir
        self.db_path = db_path
        
        # Cache in memoria (veloce, limitata)
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.memory_usage = 0
        
        # Cache su disco (lenta, capacità maggiore)
        self.disk_usage = 0
        
        # Lock per thread safety
        self.lock = threading.RLock()
        
        # Statistiche
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'disk_writes': 0,
            'disk_reads': 0
        }
        
        # Configurazioni per tipo di cache
        self.cache_configs = {
            CacheType.RECOGNITION_RESULT: {
                'ttl_seconds': 7 * 24 * 3600,  # 1 settimana
                'strategy': CacheStrategy.LRU,
                'priority': 10,
                'compress': True
            },
            CacheType.IMAGE_PROCESSED: {
                'ttl_seconds': 30 * 24 * 3600,  # 1 mese
                'strategy': CacheStrategy.LFU,
                'priority': 5,
                'compress': True
            },
            CacheType.SEARCH_RESULT: {
                'ttl_seconds': 24 * 3600,  # 1 giorno
                'strategy': CacheStrategy.TTL,
                'priority': 7,
                'compress': False
            },
            CacheType.THUMBNAIL: {
                'ttl_seconds': 90 * 24 * 3600,  # 3 mesi
                'strategy': CacheStrategy.LFU,
                'priority': 3,
                'compress': True
            },
            CacheType.USER_DATA: {
                'ttl_seconds': 6 * 3600,  # 6 ore
                'strategy': CacheStrategy.LRU,
                'priority': 8,
                'compress': False
            }
        }
        
        # Inizializza sistema
        self.init_cache_system()
        
        # Avvia thread di manutenzione
        self.maintenance_thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self.maintenance_thread.start()
    
    def init_cache_system(self):
        """Inizializza il sistema di cache"""
        # Crea directory cache
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Inizializza database metadata
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                cache_type TEXT,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER,
                size_bytes INTEGER,
                ttl_seconds INTEGER,
                file_path TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_stats (
                date TEXT PRIMARY KEY,
                hits INTEGER,
                misses INTEGER,
                evictions INTEGER,
                total_size INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Carica cache esistente
        self._load_cache_metadata()
    
    def get(self, key: str, cache_type: CacheType) -> Optional[Any]:
        """Recupera item dalla cache"""
        with self.lock:
            full_key = self._make_key(key, cache_type)
            
            # Cerca in memoria prima
            if full_key in self.memory_cache:
                entry = self.memory_cache[full_key]
                
                if entry.is_expired():
                    self._evict_entry(full_key, from_memory=True)
                    self.stats['misses'] += 1
                    return None
                
                # Sposta in fondo (LRU)
                self.memory_cache.move_to_end(full_key)
                entry.update_access()
                self.stats['hits'] += 1
                return entry.data
            
            # Cerca su disco
            entry = self._load_from_disk(full_key)
            if entry and not entry.is_expired():
                # Promuovi in memoria se spazio disponibile
                self._promote_to_memory(entry)
                self.stats['hits'] += 1
                self.stats['disk_reads'] += 1
                return entry.data
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, data: Any, cache_type: CacheType, 
            ttl_seconds: Optional[int] = None, metadata: Dict = None):
        """Inserisce item nella cache"""
        with self.lock:
            full_key = self._make_key(key, cache_type)
            config = self.cache_configs.get(cache_type, {})
            
            # Calcola dimensioni
            data_size = self._calculate_size(data)
            
            # Crea entry
            entry = CacheEntry(
                key=full_key,
                data=data,
                cache_type=cache_type,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=data_size,
                ttl_seconds=ttl_seconds or config.get('ttl_seconds'),
                metadata=metadata or {}
            )
            
            # Decide dove salvare
            if self._should_store_in_memory(entry):
                self._store_in_memory(entry)
            else:
                self._store_on_disk(entry)
    
    def invalidate(self, key: str, cache_type: CacheType):
        """Invalida specifica entry"""
        with self.lock:
            full_key = self._make_key(key, cache_type)
            self._evict_entry(full_key, from_memory=True, from_disk=True)
    
    def invalidate_by_pattern(self, pattern: str, cache_type: Optional[CacheType] = None):
        """Invalida entries che matchano un pattern"""
        with self.lock:
            to_remove = []
            
            # Cerca in memoria
            for full_key in self.memory_cache:
                if self._key_matches_pattern(full_key, pattern, cache_type):
                    to_remove.append(full_key)
            
            for key in to_remove:
                self._evict_entry(key, from_memory=True, from_disk=True)
    
    def clear_all(self, cache_type: Optional[CacheType] = None):
        """Pulisce tutta la cache o un tipo specifico"""
        with self.lock:
            if cache_type is None:
                # Pulisce tutto
                self.memory_cache.clear()
                self.memory_usage = 0
                
                # Pulisce disco
                for file in os.listdir(self.cache_dir):
                    if file.endswith('.cache'):
                        os.remove(os.path.join(self.cache_dir, file))
                
                self.disk_usage = 0
            else:
                # Pulisce tipo specifico
                to_remove = [k for k, v in self.memory_cache.items() 
                           if v.cache_type == cache_type]
                
                for key in to_remove:
                    self._evict_entry(key, from_memory=True, from_disk=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Ottiene statistiche della cache"""
        with self.lock:
            hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) \
                      if (self.stats['hits'] + self.stats['misses']) > 0 else 0
            
            return {
                'memory_entries': len(self.memory_cache),
                'memory_usage_mb': self.memory_usage / (1024 * 1024),
                'memory_usage_percent': (self.memory_usage / self.max_memory_bytes) * 100,
                'disk_usage_mb': self.disk_usage / (1024 * 1024),
                'disk_usage_percent': (self.disk_usage / self.max_disk_bytes) * 100,
                'hit_rate': hit_rate,
                'total_hits': self.stats['hits'],
                'total_misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'disk_operations': self.stats['disk_reads'] + self.stats['disk_writes']
            }
    
    def _make_key(self, key: str, cache_type: CacheType) -> str:
        """Crea chiave unica per cache"""
        return f"{cache_type.value}:{hashlib.md5(key.encode()).hexdigest()}"
    
    def _calculate_size(self, data: Any) -> int:
        """Calcola dimensione approssimativa dei dati"""
        try:
            return len(pickle.dumps(data))
        except:
            return len(str(data).encode('utf-8'))
    
    def _should_store_in_memory(self, entry: CacheEntry) -> bool:
        """Decide se salvare entry in memoria o disco"""
        config = self.cache_configs.get(entry.cache_type, {})
        priority = config.get('priority', 5)
        
        # Piccoli file ad alta priorità vanno in memoria
        if entry.size_bytes < 1024 * 100 and priority >= 7:  # < 100KB, alta priorità
            return True
        
        # Se c'è spazio in memoria
        if self.memory_usage + entry.size_bytes <= self.max_memory_bytes:
            return True
        
        return False
    
    def _store_in_memory(self, entry: CacheEntry):
        """Salva entry in memoria"""
        # Libera spazio se necessario
        while (self.memory_usage + entry.size_bytes > self.max_memory_bytes 
               and self.memory_cache):
            self._evict_lru_from_memory()
        
        self.memory_cache[entry.key] = entry
        self.memory_usage += entry.size_bytes
    
    def _store_on_disk(self, entry: CacheEntry):
        """Salva entry su disco"""
        config = self.cache_configs.get(entry.cache_type, {})
        compress = config.get('compress', False)
        
        # Libera spazio su disco se necessario
        while self.disk_usage + entry.size_bytes > self.max_disk_bytes:
            self._evict_lru_from_disk()
        
        # Nome file
        file_name = f"{entry.key}.cache"
        file_path = os.path.join(self.cache_dir, file_name)
        
        try:
            # Serializza dati
            data_bytes = pickle.dumps(entry.data)
            
            if compress:
                data_bytes = gzip.compress(data_bytes)
            
            # Scrivi su disco
            with open(file_path, 'wb') as f:
                f.write(data_bytes)
            
            # Salva metadata nel database
            self._save_entry_metadata(entry, file_path, compress)
            
            self.disk_usage += entry.size_bytes
            self.stats['disk_writes'] += 1
            
        except Exception as e:
            print(f"Errore scrittura cache su disco: {e}")
    
    def _load_from_disk(self, full_key: str) -> Optional[CacheEntry]:
        """Carica entry dal disco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cache_type, created_at, last_accessed, access_count, 
                       size_bytes, ttl_seconds, file_path, metadata
                FROM cache_entries WHERE key = ?
            ''', (full_key,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            file_path = row[6]
            if not os.path.exists(file_path):
                return None
            
            # Leggi dati
            with open(file_path, 'rb') as f:
                data_bytes = f.read()
            
            # Decomprimi se necessario
            config = self.cache_configs.get(CacheType(row[0]), {})
            if config.get('compress', False):
                data_bytes = gzip.decompress(data_bytes)
            
            data = pickle.loads(data_bytes)
            
            # Ricostruisci entry
            entry = CacheEntry(
                key=full_key,
                data=data,
                cache_type=CacheType(row[0]),
                created_at=datetime.fromisoformat(row[1]),
                last_accessed=datetime.fromisoformat(row[2]),
                access_count=row[3],
                size_bytes=row[4],
                ttl_seconds=row[5],
                metadata=json.loads(row[7]) if row[7] else {}
            )
            
            entry.update_access()
            return entry
            
        except Exception as e:
            print(f"Errore lettura cache da disco: {e}")
            return None
    
    def _promote_to_memory(self, entry: CacheEntry):
        """Promuove entry da disco a memoria"""
        if self._should_store_in_memory(entry):
            self._store_in_memory(entry)
    
    def _evict_lru_from_memory(self):
        """Rimuove item meno recente dalla memoria"""
        if self.memory_cache:
            oldest_key, oldest_entry = self.memory_cache.popitem(last=False)
            self.memory_usage -= oldest_entry.size_bytes
            self.stats['evictions'] += 1
    
    def _evict_lru_from_disk(self):
        """Rimuove item meno recente dal disco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT key, file_path, size_bytes 
                FROM cache_entries 
                ORDER BY last_accessed ASC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                key, file_path, size_bytes = row
                
                # Rimuovi file
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Rimuovi metadata
                cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                conn.commit()
                
                self.disk_usage -= size_bytes
                self.stats['evictions'] += 1
            
            conn.close()
            
        except Exception as e:
            print(f"Errore eviction da disco: {e}")
    
    def _evict_entry(self, full_key: str, from_memory: bool = True, from_disk: bool = False):
        """Rimuove entry specifica"""
        if from_memory and full_key in self.memory_cache:
            entry = self.memory_cache.pop(full_key)
            self.memory_usage -= entry.size_bytes
        
        if from_disk:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT file_path, size_bytes FROM cache_entries WHERE key = ?', 
                             (full_key,))
                row = cursor.fetchone()
                
                if row:
                    file_path, size_bytes = row
                    
                    # Rimuovi file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # Rimuovi metadata
                    cursor.execute('DELETE FROM cache_entries WHERE key = ?', (full_key,))
                    conn.commit()
                    
                    self.disk_usage -= size_bytes
                
                conn.close()
                
            except Exception as e:
                print(f"Errore rimozione da disco: {e}")
    
    def _key_matches_pattern(self, full_key: str, pattern: str, 
                           cache_type: Optional[CacheType] = None) -> bool:
        """Verifica se chiave matcha pattern"""
        if cache_type and not full_key.startswith(cache_type.value + ":"):
            return False
        
        return pattern in full_key
    
    def _save_entry_metadata(self, entry: CacheEntry, file_path: str, compressed: bool):
        """Salva metadata entry nel database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache_entries
                (key, cache_type, created_at, last_accessed, access_count, 
                 size_bytes, ttl_seconds, file_path, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.key,
                entry.cache_type.value,
                entry.created_at.isoformat(),
                entry.last_accessed.isoformat(),
                entry.access_count,
                entry.size_bytes,
                entry.ttl_seconds,
                file_path,
                json.dumps(entry.metadata) if entry.metadata else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Errore salvataggio metadata: {e}")
    
    def _load_cache_metadata(self):
        """Carica metadata cache esistente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT SUM(size_bytes) FROM cache_entries')
            result = cursor.fetchone()
            
            if result and result[0]:
                self.disk_usage = result[0]
            
            conn.close()
            
        except Exception as e:
            print(f"Errore caricamento metadata: {e}")
    
    def _maintenance_loop(self):
        """Loop di manutenzione cache"""
        while True:
            try:
                time.sleep(300)  # Ogni 5 minuti
                self._cleanup_expired()
                self._save_stats()
                
            except Exception as e:
                print(f"Errore manutenzione cache: {e}")
    
    def _cleanup_expired(self):
        """Rimuove entries scadute"""
        with self.lock:
            # Cleanup memoria
            expired_keys = [k for k, v in self.memory_cache.items() if v.is_expired()]
            for key in expired_keys:
                self._evict_entry(key, from_memory=True)
            
            # Cleanup disco
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Trova entries scadute
                cursor.execute('''
                    SELECT key, file_path, size_bytes 
                    FROM cache_entries 
                    WHERE ttl_seconds IS NOT NULL 
                    AND datetime(created_at, '+' || ttl_seconds || ' seconds') < datetime('now')
                ''')
                
                expired = cursor.fetchall()
                
                for key, file_path, size_bytes in expired:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                    self.disk_usage -= size_bytes
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                print(f"Errore cleanup disco: {e}")
    
    def _save_stats(self):
        """Salva statistiche giornaliere"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache_stats
                (date, hits, misses, evictions, total_size)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                today,
                self.stats['hits'],
                self.stats['misses'],
                self.stats['evictions'],
                self.memory_usage + self.disk_usage
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Errore salvataggio statistiche: {e}")


# Cache globale per l'applicazione
app_cache = IntelligentCache()


def cached(cache_type: CacheType, ttl_seconds: Optional[int] = None, 
          key_func: Optional[Callable] = None):
    """Decorator per caching automatico delle funzioni"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Genera chiave cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Cerca in cache
            result = app_cache.get(cache_key, cache_type)
            if result is not None:
                return result
            
            # Esegui funzione e salva risultato
            result = func(*args, **kwargs)
            app_cache.set(cache_key, result, cache_type, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


def demo_cache_system():
    """Demo del sistema di caching intelligente"""
    print("💾 DEMO INTELLIGENT CACHE SYSTEM - Monument Recognizer")
    print("=" * 60)
    
    cache = IntelligentCache(max_memory_mb=10, max_disk_mb=50)
    
    # Test caching di base
    print("\n📦 Test Cache di Base")
    
    # Salva alcuni dati
    cache.set("colosseo_recognition", {"name": "Colosseo", "confidence": 0.95}, 
              CacheType.RECOGNITION_RESULT)
    cache.set("user_123_profile", {"name": "Mario", "visits": 42}, 
              CacheType.USER_DATA, ttl_seconds=3600)
    cache.set("roma_search", [{"id": "colosseo"}, {"id": "pantheon"}], 
              CacheType.SEARCH_RESULT)
    
    print("✅ Dati salvati in cache")
    
    # Recupera dati
    result = cache.get("colosseo_recognition", CacheType.RECOGNITION_RESULT)
    print(f"🔍 Cache hit: {result}")
    
    result = cache.get("inesistente", CacheType.SEARCH_RESULT)
    print(f"❌ Cache miss: {result}")
    
    # Test decorator
    print("\n🎭 Test Decorator Caching")
    
    @cached(CacheType.SEARCH_RESULT, ttl_seconds=300)
    def expensive_search(query: str):
        print(f"   Eseguendo ricerca costosa per: {query}")
        time.sleep(0.1)  # Simula operazione lenta
        return {"results": [f"result1_{query}", f"result2_{query}"]}
    
    print("Prima chiamata (miss):")
    result1 = expensive_search("roma")
    print(f"   Risultato: {result1}")
    
    print("Seconda chiamata (hit):")
    result2 = expensive_search("roma")  
    print(f"   Risultato: {result2}")
    
    # Test statistiche
    print("\n📊 Statistiche Cache")
    stats = cache.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Test invalidazione
    print("\n🗑️ Test Invalidazione")
    cache.set("temp_data_1", "data1", CacheType.USER_DATA)
    cache.set("temp_data_2", "data2", CacheType.USER_DATA) 
    
    print(f"Prima invalidazione: {cache.get('temp_data_1', CacheType.USER_DATA)}")
    
    cache.invalidate_by_pattern("temp_data", CacheType.USER_DATA)
    print(f"Dopo invalidazione: {cache.get('temp_data_1', CacheType.USER_DATA)}")
    
    print("\n✅ Demo cache system completato!")


if __name__ == "__main__":
    demo_cache_system()
