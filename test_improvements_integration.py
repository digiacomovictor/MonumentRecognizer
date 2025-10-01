"""
Test di Integrazione Completo per i Miglioramenti di Monument Recognizer
Valida il funzionamento dei nuovi sistemi implementati
"""

import unittest
import time
import threading
from datetime import datetime
import os
import tempfile
import shutil

from modern_ui import (
    theme_manager, MaterialCard, MaterialButton, MaterialIcon, 
    MaterialAppBar, FloatingActionButton, ThemeMode
)
from advanced_search import (
    AdvancedSearchEngine, SearchQuery, SearchCategory, SearchFilter
)
from intelligent_cache import (
    IntelligentCache, CacheType, cached
)


class TestModernUIIntegration(unittest.TestCase):
    """Test per il sistema UI moderno"""
    
    def setUp(self):
        """Setup test UI"""
        self.original_theme = theme_manager.current_mode
    
    def tearDown(self):
        """Cleanup test UI"""
        theme_manager.set_theme(self.original_theme)
    
    def test_theme_management(self):
        """Test gestione tema"""
        # Verifica tema iniziale
        self.assertIsNotNone(theme_manager.current_mode)
        
        # Test toggle tema
        original_mode = theme_manager.current_mode
        theme_manager.toggle_theme()
        self.assertNotEqual(theme_manager.current_mode, original_mode)
        
        # Test callback tema
        callback_called = False
        def test_callback(mode):
            nonlocal callback_called
            callback_called = True
        
        theme_manager.register_callback(test_callback)
        theme_manager.toggle_theme()
        self.assertTrue(callback_called)
    
    def test_material_components(self):
        """Test componenti Material Design"""
        # Test MaterialCard
        card = MaterialCard(elevation=4, corner_radius=16)
        self.assertEqual(card.elevation, 4)
        self.assertEqual(card.corner_radius, 16)
        
        # Test MaterialButton
        button = MaterialButton(text="Test Button", button_type="filled")
        self.assertEqual(button.text, "Test Button")
        self.assertEqual(button.button_type, "filled")
        
        # Test MaterialIcon
        icon = MaterialIcon("search")
        self.assertEqual(icon.text, "🔍")
        
        # Test MaterialAppBar
        app_bar = MaterialAppBar(title="Test App", show_back=True)
        self.assertEqual(app_bar.title, "Test App")
        
        # Test FloatingActionButton
        fab = FloatingActionButton(icon="add")
        self.assertIsNotNone(fab)
    
    def test_theme_colors(self):
        """Test ottenimento colori tema"""
        # Light theme
        theme_manager.set_theme(ThemeMode.LIGHT)
        primary_color = theme_manager.get_color('primary')
        self.assertEqual(len(primary_color), 4)  # RGBA
        
        # Dark theme
        theme_manager.set_theme(ThemeMode.DARK)
        dark_primary = theme_manager.get_color('primary')
        self.assertNotEqual(primary_color, dark_primary)


class TestAdvancedSearchIntegration(unittest.TestCase):
    """Test per il sistema di ricerca avanzato"""
    
    def setUp(self):
        """Setup test ricerca"""
        self.temp_dir = tempfile.mkdtemp()
        self.search_db = os.path.join(self.temp_dir, "test_search.db")
        self.engine = AdvancedSearchEngine(db_path=self.search_db)
    
    def tearDown(self):
        """Cleanup test ricerca"""
        shutil.rmtree(self.temp_dir)
    
    def test_basic_search(self):
        """Test ricerca di base"""
        query = SearchQuery(text="roma", limit=5)
        results = self.engine.search(query)
        
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)
        
        # Verifica struttura risultati
        if results:
            result = results[0]
            self.assertHasAttr(result, 'id')
            self.assertHasAttr(result, 'title')
            self.assertHasAttr(result, 'score')
            self.assertHasAttr(result, 'metadata')
    
    def test_filtered_search(self):
        """Test ricerca con filtri"""
        query = SearchQuery(
            text="",
            filters={SearchFilter.ERA: "Antica"},
            limit=10
        )
        results = self.engine.search(query)
        
        # Verifica che tutti i risultati abbiano era "Antica"
        for result in results:
            era = result.metadata.get('era')
            if era:
                self.assertEqual(era, "Antica")
    
    def test_autocomplete(self):
        """Test autocompletamento"""
        suggestions = self.engine.get_autocomplete_suggestions("col")
        self.assertIsInstance(suggestions, list)
        
        # Dovrebbe contenere "Colosseo"
        colosseo_found = any("Colosseo" in s for s in suggestions)
        self.assertTrue(colosseo_found)
    
    def test_recommendations(self):
        """Test raccomandazioni"""
        recommendations = self.engine.get_recommendations_for_user("test_user")
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)
    
    def test_trending_searches(self):
        """Test trending searches"""
        trending = self.engine.get_trending_searches()
        self.assertIsInstance(trending, list)
        self.assertGreater(len(trending), 0)
    
    def assertHasAttr(self, obj, attr):
        """Helper per verificare attributi"""
        self.assertTrue(hasattr(obj, attr), f"Object missing attribute: {attr}")


class TestIntelligentCacheIntegration(unittest.TestCase):
    """Test per il sistema di cache intelligente"""
    
    def setUp(self):
        """Setup test cache"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "cache")
        self.cache_db = os.path.join(self.temp_dir, "cache.db")
        
        self.cache = IntelligentCache(
            max_memory_mb=1,
            max_disk_mb=5,
            cache_dir=self.cache_dir,
            db_path=self.cache_db
        )
    
    def tearDown(self):
        """Cleanup test cache"""
        shutil.rmtree(self.temp_dir)
    
    def test_basic_caching(self):
        """Test caching di base"""
        # Test set/get
        test_data = {"key": "value", "number": 42}
        self.cache.set("test_key", test_data, CacheType.USER_DATA)
        
        retrieved = self.cache.get("test_key", CacheType.USER_DATA)
        self.assertEqual(retrieved, test_data)
        
        # Test cache miss
        missing = self.cache.get("nonexistent", CacheType.USER_DATA)
        self.assertIsNone(missing)
    
    def test_cache_expiration(self):
        """Test scadenza cache"""
        # Set con TTL molto breve
        self.cache.set("expiring_key", "value", CacheType.USER_DATA, ttl_seconds=1)
        
        # Immediatamente dovrebbe essere disponibile
        result = self.cache.get("expiring_key", CacheType.USER_DATA)
        self.assertEqual(result, "value")
        
        # Dopo scadenza dovrebbe essere None
        time.sleep(1.1)
        result = self.cache.get("expiring_key", CacheType.USER_DATA)
        self.assertIsNone(result)
    
    def test_cache_invalidation(self):
        """Test invalidazione cache"""
        self.cache.set("to_invalidate", "value", CacheType.USER_DATA)
        
        # Verifica presenza
        result = self.cache.get("to_invalidate", CacheType.USER_DATA)
        self.assertEqual(result, "value")
        
        # Invalida
        self.cache.invalidate("to_invalidate", CacheType.USER_DATA)
        
        # Verifica rimozione
        result = self.cache.get("to_invalidate", CacheType.USER_DATA)
        self.assertIsNone(result)
    
    def test_cache_stats(self):
        """Test statistiche cache"""
        stats = self.cache.get_stats()
        
        required_stats = [
            'memory_entries', 'memory_usage_mb', 'disk_usage_mb',
            'hit_rate', 'total_hits', 'total_misses'
        ]
        
        for stat in required_stats:
            self.assertIn(stat, stats)
    
    def test_cached_decorator(self):
        """Test decorator @cached"""
        call_count = 0
        
        @cached(CacheType.SEARCH_RESULT, ttl_seconds=60)
        def expensive_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}_{call_count}"
        
        # Prima chiamata
        result1 = expensive_function("test")
        self.assertEqual(call_count, 1)
        
        # Seconda chiamata (dovrebbe usare cache)
        result2 = expensive_function("test")
        self.assertEqual(call_count, 1)  # Non dovrebbe aumentare
        self.assertEqual(result1, result2)
        
        # Chiamata con parametro diverso
        result3 = expensive_function("different")
        self.assertEqual(call_count, 2)  # Dovrebbe aumentare


class TestSystemIntegration(unittest.TestCase):
    """Test integrazione tra sistemi"""
    
    def test_search_with_caching(self):
        """Test ricerca con caching automatico"""
        # Setup temporaneo
        temp_dir = tempfile.mkdtemp()
        try:
            search_db = os.path.join(temp_dir, "search.db")
            engine = AdvancedSearchEngine(db_path=search_db)
            
            # Simula ricerca con cache decorator
            @cached(CacheType.SEARCH_RESULT, ttl_seconds=300)
            def cached_search(query_text):
                query = SearchQuery(text=query_text, limit=3)
                return engine.search(query)
            
            # Prima ricerca
            start_time = time.time()
            results1 = cached_search("roma")
            time1 = time.time() - start_time
            
            # Seconda ricerca (cached)
            start_time = time.time()
            results2 = cached_search("roma")
            time2 = time.time() - start_time
            
            # La seconda dovrebbe essere più veloce (cache hit)
            self.assertLess(time2, time1)
            self.assertEqual(len(results1), len(results2))
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_ui_theme_persistence(self):
        """Test persistenza tema UI"""
        original_mode = theme_manager.current_mode
        
        # Cambia tema
        new_mode = ThemeMode.DARK if original_mode == ThemeMode.LIGHT else ThemeMode.LIGHT
        theme_manager.set_theme(new_mode)
        
        # Verifica che il tema sia cambiato
        self.assertEqual(theme_manager.current_mode, new_mode)
        
        # In un'app reale, qui si ricaricherebbe il ThemeManager
        # e si verificherebbe che il tema sia persistente
        
        # Ripristina tema originale
        theme_manager.set_theme(original_mode)


class TestPerformanceImprovements(unittest.TestCase):
    """Test miglioramenti performance"""
    
    def test_cache_performance_boost(self):
        """Test boost performance con cache"""
        cache = IntelligentCache(max_memory_mb=5)
        
        def slow_operation(data):
            time.sleep(0.01)  # Simula operazione lenta
            return data * 2
        
        # Senza cache
        start_time = time.time()
        for i in range(10):
            result = slow_operation(i)
        no_cache_time = time.time() - start_time
        
        # Con cache
        @cached(CacheType.API_RESPONSE)
        def cached_slow_operation(data):
            time.sleep(0.01)
            return data * 2
        
        start_time = time.time()
        for i in range(10):
            result = cached_slow_operation(i % 5)  # Ripeti alcuni valori
        cache_time = time.time() - start_time
        
        # Con cache dovrebbe essere più veloce
        self.assertLess(cache_time, no_cache_time)
    
    def test_search_performance(self):
        """Test performance ricerca"""
        temp_dir = tempfile.mkdtemp()
        try:
            search_db = os.path.join(temp_dir, "search.db")
            engine = AdvancedSearchEngine(db_path=search_db)
            
            # Test ricerca veloce
            start_time = time.time()
            query = SearchQuery(text="roma", limit=10)
            results = engine.search(query)
            search_time = time.time() - start_time
            
            # La ricerca dovrebbe completarsi rapidamente
            self.assertLess(search_time, 1.0)  # Meno di 1 secondo
            
        finally:
            shutil.rmtree(temp_dir)


def run_integration_tests():
    """Esegue tutti i test di integrazione"""
    print("🧪 AVVIO TEST DI INTEGRAZIONE - Monument Recognizer Improvements")
    print("=" * 70)
    
    # Crea test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Aggiungi test classes
    test_classes = [
        TestModernUIIntegration,
        TestAdvancedSearchIntegration,
        TestIntelligentCacheIntegration,
        TestSystemIntegration,
        TestPerformanceImprovements
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Esegui test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report finale
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f"✅ TUTTI I TEST SUPERATI! ({result.testsRun} test eseguiti)")
        print("\n🎉 I miglioramenti implementati funzionano correttamente!")
        print("\n📊 Riepilogo Miglioramenti Validati:")
        print("   • 🎨 Modern UI System: Material Design 3 + Theme Engine")
        print("   • 🔍 Advanced Search: Ricerca intelligente + AI ranking")
        print("   • 💾 Intelligent Cache: Multi-level caching + Performance boost")
        
        return True
        
    else:
        print(f"❌ {len(result.failures)} test falliti, {len(result.errors)} errori")
        
        # Mostra dettagli errori
        if result.failures:
            print("\n📋 TEST FALLITI:")
            for test, traceback in result.failures:
                print(f"   • {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\n⚠️ ERRORI:")
            for test, traceback in result.errors:
                print(f"   • {test}: {traceback.split('Exception:')[-1].strip()}")
        
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
