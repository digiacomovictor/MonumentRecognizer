"""
Test Suite per le funzionalità social di Monument Recognizer
Test per condivisione, feed interno, UI e integrazione
"""

import os
import sys
import sqlite3
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Aggiungi il percorso del progetto al path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from social_sharing import SocialSharingManager
from visit_tracker import VisitTracker
from user_system import UserSystem


class TestSocialSharing:
    """Test per il sistema di condivisione social"""
    
    def __init__(self):
        # Crea database temporanei per i test
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.temp_dir, "test_social.db")
        
        # Inizializza i manager per i test
        self.social_manager = SocialSharingManager(self.test_db)
        self.visit_tracker = VisitTracker(self.test_db)
        self.user_system = UserSystem(os.path.join(self.temp_dir, "test_users.db"))
        
        print(f"🧪 Test environment creato in: {self.temp_dir}")
    
    def cleanup(self):
        """Pulizia dei file temporanei"""
        try:
            shutil.rmtree(self.temp_dir)
            print("🧹 Cleanup completato")
        except Exception as e:
            print(f"⚠️ Errore cleanup: {e}")
    
    def create_test_data(self):
        """Crea dati di test"""
        # Crea utente di test
        test_user = self.user_system.register_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            full_name="Test User"
        )
        
        if test_user:
            self.user_system.login("testuser", "testpass123")
            print("✅ Utente di test creato e loggato")
        
        # Crea visita di test
        visit_data = {
            'user_id': 'testuser',
            'monument_name': 'Colosseo',
            'description': 'Anfiteatro romano del I secolo d.C., simbolo di Roma',
            'location': 'Roma, Italia',
            'image_path': '',
            'latitude': 41.8902,
            'longitude': 12.4922,
            'timestamp': datetime.now().isoformat()
        }
        
        return visit_data
    
    def test_social_database_init(self):
        """Test inizializzazione database social"""
        print("\n🧪 Test inizializzazione database social...")
        
        try:
            # Verifica che le tabelle siano state create
            conn = sqlite3.connect(self.test_db)
            cursor = conn.cursor()
            
            # Lista delle tabelle che dovrebbero esistere
            expected_tables = ['shared_visits', 'social_feed', 'social_likes', 'social_comments']
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in expected_tables:
                if table in existing_tables:
                    print(f"✅ Tabella {table} creata correttamente")
                else:
                    print(f"❌ Tabella {table} mancante")
                    return False
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Errore test database: {e}")
            return False
    
    def test_post_content_generation(self):
        """Test generazione contenuto post"""
        print("\n🧪 Test generazione contenuto post...")
        
        try:
            visit_data = self.create_test_data()
            
            # Test template discovery
            content = self.social_manager.generate_post_content(visit_data, 'discovery', True)
            
            if content and content['text'] and content['hashtags']:
                print(f"✅ Contenuto discovery generato: {content['text'][:50]}...")
                print(f"✅ Hashtags generati: {content['hashtags']}")
            else:
                print("❌ Errore nella generazione contenuto discovery")
                return False
            
            # Test template achievement
            content_achievement = self.social_manager.generate_post_content(visit_data, 'achievement', True)
            
            if content_achievement and content_achievement['text']:
                print(f"✅ Contenuto achievement generato: {content_achievement['text'][:50]}...")
            else:
                print("❌ Errore nella generazione contenuto achievement")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Errore test generazione contenuto: {e}")
            return False
    
    def test_hashtag_generation(self):
        """Test generazione hashtag"""
        print("\n🧪 Test generazione hashtag...")
        
        try:
            visit_data = self.create_test_data()
            
            hashtags = self.social_manager.generate_hashtags(visit_data)
            
            if hashtags:
                hashtag_list = hashtags.split(',')
                print(f"✅ Hashtags generati: {hashtags}")
                print(f"✅ Numero hashtags: {len(hashtag_list)}")
                
                # Verifica hashtag obbligatori
                required_hashtags = ['MonumentRecognizer', 'Heritage', 'Travel']
                for req_tag in required_hashtags:
                    if req_tag in hashtags:
                        print(f"✅ Hashtag obbligatorio '{req_tag}' presente")
                    else:
                        print(f"❌ Hashtag obbligatorio '{req_tag}' mancante")
                        return False
                
                return True
            else:
                print("❌ Nessun hashtag generato")
                return False
                
        except Exception as e:
            print(f"❌ Errore test hashtag: {e}")
            return False
    
    def test_internal_feed_sharing(self):
        """Test condivisione nel feed interno"""
        print("\n🧪 Test condivisione feed interno...")
        
        try:
            visit_data = self.create_test_data()
            
            # Test condivisione nel feed
            success = self.social_manager.share_to_app_feed(
                visit_data, 
                "Test post nel feed interno! 🏛️"
            )
            
            if success:
                print("✅ Condivisione nel feed interno riuscita")
            else:
                print("❌ Errore condivisione nel feed interno")
                return False
            
            # Test recupero feed
            feed_posts = self.social_manager.get_social_feed(10)
            
            if feed_posts and len(feed_posts) > 0:
                print(f"✅ Feed recuperato con {len(feed_posts)} post")
                
                # Verifica dati del primo post
                first_post = feed_posts[0]
                if first_post['monument_name'] == visit_data['monument_name']:
                    print("✅ Dati post corretti")
                else:
                    print("❌ Dati post incorretti")
                    return False
                
                return True
            else:
                print("❌ Feed vuoto o errore recupero")
                return False
                
        except Exception as e:
            print(f"❌ Errore test feed interno: {e}")
            return False
    
    def test_likes_and_comments(self):
        """Test like e commenti sui post"""
        print("\n🧪 Test like e commenti...")
        
        try:
            visit_data = self.create_test_data()
            
            # Condividi un post per test
            self.social_manager.share_to_app_feed(visit_data, "Post di test per like e commenti")
            
            # Ottieni il post
            feed_posts = self.social_manager.get_social_feed(1)
            if not feed_posts:
                print("❌ Nessun post per test like/commenti")
                return False
            
            post = feed_posts[0]
            post_id = post['id']
            
            # Test like
            like_success = self.social_manager.like_post(post_id, 'test_user_2')
            if like_success:
                print("✅ Like aggiunto con successo")
                
                # Test like duplicato (dovrebbe fallire)
                duplicate_like = self.social_manager.like_post(post_id, 'test_user_2')
                if not duplicate_like:
                    print("✅ Like duplicato correttamente rifiutato")
                else:
                    print("❌ Like duplicato non dovrebbe essere permesso")
                    return False
            else:
                print("❌ Errore aggiunta like")
                return False
            
            # Test commento
            comment_success = self.social_manager.add_comment(
                post_id, 
                'test_user_2', 
                "Bellissimo monumento! 🏛️"
            )
            
            if comment_success:
                print("✅ Commento aggiunto con successo")
                
                # Test recupero commenti
                comments = self.social_manager.get_post_comments(post_id)
                if comments and len(comments) > 0:
                    print(f"✅ Commenti recuperati: {len(comments)}")
                    if comments[0]['comment_text'] == "Bellissimo monumento! 🏛️":
                        print("✅ Testo commento corretto")
                    else:
                        print("❌ Testo commento incorretto")
                        return False
                else:
                    print("❌ Errore recupero commenti")
                    return False
            else:
                print("❌ Errore aggiunta commento")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Errore test like/commenti: {e}")
            return False
    
    def test_share_stats(self):
        """Test statistiche condivisioni"""
        print("\n🧪 Test statistiche condivisioni...")
        
        try:
            visit_data = self.create_test_data()
            
            # Aggiungi alcune condivisioni simulate
            for platform in ['twitter', 'facebook', 'instagram']:
                self.social_manager.log_share(1, 'testuser', platform, f"Test post {platform}")
            
            # Test statistiche
            stats = self.social_manager.get_share_stats('testuser')
            
            if stats:
                print(f"✅ Statistiche recuperate: {stats}")
                
                if stats.get('total_shares', 0) >= 3:
                    print("✅ Conteggio condivisioni corretto")
                else:
                    print("❌ Conteggio condivisioni incorretto")
                    return False
                
                if 'platform_stats' in stats and len(stats['platform_stats']) > 0:
                    print("✅ Statistiche per piattaforma disponibili")
                else:
                    print("❌ Statistiche per piattaforma mancanti")
                    return False
                
                return True
            else:
                print("❌ Errore recupero statistiche")
                return False
                
        except Exception as e:
            print(f"❌ Errore test statistiche: {e}")
            return False
    
    def test_share_url_generation(self):
        """Test generazione URL condivisibili"""
        print("\n🧪 Test generazione URL condivisibili...")
        
        try:
            visit_data = self.create_test_data()
            
            share_url = self.social_manager.generate_share_url(visit_data)
            
            if share_url and 'monumentrecognizer.app' in share_url:
                print(f"✅ URL condivisibile generato: {share_url}")
                
                # Verifica formato URL
                if visit_data['monument_name'].replace(' ', '-') in share_url:
                    print("✅ Nome monumento nell'URL corretto")
                else:
                    print("❌ Nome monumento nell'URL incorretto")
                    return False
                
                return True
            else:
                print("❌ URL condivisibile non generato correttamente")
                return False
                
        except Exception as e:
            print(f"❌ Errore test URL generation: {e}")
            return False
    
    def test_platform_sharing_simulation(self):
        """Test simulazione condivisione piattaforme (senza aprire browser)"""
        print("\n🧪 Test simulazione condivisione piattaforme...")
        
        try:
            visit_data = self.create_test_data()
            
            # Test per ogni piattaforma (modalità test - non apre browser)
            platforms = ['twitter', 'facebook', 'whatsapp', 'telegram', 'linkedin']
            
            for platform in platforms:
                # Genera contenuto per la piattaforma
                content = self.social_manager.generate_post_content(visit_data, 'discovery')
                
                if content:
                    print(f"✅ Contenuto per {platform} generato")
                    
                    # Simula log della condivisione
                    self.social_manager.log_share(1, 'testuser', platform, content['text'])
                    print(f"✅ Condivisione su {platform} simulata e loggata")
                else:
                    print(f"❌ Errore generazione contenuto per {platform}")
                    return False
            
            # Verifica che tutte le condivisioni siano state loggate
            stats = self.social_manager.get_share_stats('testuser')
            if stats and stats.get('total_shares', 0) >= len(platforms):
                print(f"✅ Tutte le condivisioni loggate correttamente: {stats['total_shares']}")
                return True
            else:
                print("❌ Condivisioni non loggate correttamente")
                return False
                
        except Exception as e:
            print(f"❌ Errore test condivisione piattaforme: {e}")
            return False
    
    def test_visit_count_integration(self):
        """Test integrazione con conteggio visite utente"""
        print("\n🧪 Test integrazione conteggio visite...")
        
        try:
            # Aggiungi alcune visite simulate al database
            conn = sqlite3.connect(self.test_db)
            cursor = conn.cursor()
            
            # Crea tabella visits se non esiste
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    monument_name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Aggiungi visite di test
            for i in range(5):
                cursor.execute(
                    'INSERT INTO visits (user_id, monument_name) VALUES (?, ?)',
                    ('testuser', f'Monumento Test {i+1}')
                )
            
            conn.commit()
            conn.close()
            
            # Test conteggio visite
            visit_count = self.social_manager.get_user_visit_count('testuser')
            
            if visit_count == 5:
                print(f"✅ Conteggio visite corretto: {visit_count}")
            else:
                print(f"❌ Conteggio visite incorretto: {visit_count} (atteso: 5)")
                return False
            
            # Test generazione contenuto con statistiche
            visit_data = self.create_test_data()
            content = self.social_manager.generate_post_content(visit_data, 'discovery', True)
            
            if '5' in content['text'] or 'monumenti' in content['text']:
                print("✅ Statistiche integrate nel contenuto")
                return True
            else:
                print("❌ Statistiche non integrate nel contenuto")
                return False
                
        except Exception as e:
            print(f"❌ Errore test integrazione visite: {e}")
            return False
    
    def run_all_tests(self):
        """Esegue tutti i test"""
        print("🚀 Avvio test suite per funzionalità social...")
        print("=" * 60)
        
        tests = [
            ('Database Initialization', self.test_social_database_init),
            ('Post Content Generation', self.test_post_content_generation),
            ('Hashtag Generation', self.test_hashtag_generation),
            ('Internal Feed Sharing', self.test_internal_feed_sharing),
            ('Likes and Comments', self.test_likes_and_comments),
            ('Share Statistics', self.test_share_stats),
            ('Share URL Generation', self.test_share_url_generation),
            ('Platform Sharing Simulation', self.test_platform_sharing_simulation),
            ('Visit Count Integration', self.test_visit_count_integration)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ Errore durante {test_name}: {e}")
                results[test_name] = False
        
        # Riassunto risultati
        print("\n" + "=" * 60)
        print("📊 RIASSUNTO RISULTATI TEST")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Risultato finale: {passed}/{total} test passati")
        
        if passed == total:
            print("🎉 Tutti i test sono passati! Sistema social funzionante.")
        else:
            print(f"⚠️ {total - passed} test falliti. Controlla i risultati sopra.")
        
        return passed == total


def test_ui_components():
    """Test per i componenti UI (test basic senza Kivy)"""
    print("\n🧪 Test componenti UI social...")
    
    try:
        # Test import
        from social_ui import SocialSharePopup, SocialFeedScreen, QuickShareButton
        print("✅ Import componenti UI riuscito")
        
        # Test che le classi esistano
        if all([SocialSharePopup, SocialFeedScreen, QuickShareButton]):
            print("✅ Tutte le classi UI disponibili")
            return True
        else:
            print("❌ Classi UI mancanti")
            return False
            
    except ImportError as e:
        print(f"❌ Errore import UI: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore test UI: {e}")
        return False


def main():
    """Funzione principale per eseguire tutti i test"""
    print("🧪 MONUMENT RECOGNIZER - TEST SUITE SOCIAL")
    print("=" * 60)
    
    # Test sistema social
    social_tester = TestSocialSharing()
    
    try:
        social_results = social_tester.run_all_tests()
        
        # Test UI components
        ui_results = test_ui_components()
        
        print("\n" + "=" * 60)
        print("🏁 RISULTATI FINALI")
        print("=" * 60)
        
        print(f"🔧 Test Sistema Social: {'✅ PASS' if social_results else '❌ FAIL'}")
        print(f"🎨 Test Componenti UI: {'✅ PASS' if ui_results else '❌ FAIL'}")
        
        overall_success = social_results and ui_results
        
        if overall_success:
            print("\n🎉 TUTTI I TEST PASSATI!")
            print("✅ Il sistema di condivisione social è pronto all'uso!")
        else:
            print("\n⚠️ ALCUNI TEST FALLITI!")
            print("❌ Controlla i risultati per i dettagli.")
        
        return overall_success
        
    finally:
        # Cleanup
        social_tester.cleanup()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
