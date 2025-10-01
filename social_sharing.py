"""
Social Sharing System for Monument Recognizer
Gestisce la condivisione delle visite sui social media e all'interno dell'app
"""

import json
import sqlite3
import urllib.parse
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import io
import base64


class SocialSharingManager:
    """Gestisce la condivisione social delle visite ai monumenti"""
    
    def __init__(self, db_path: str = "visits.db"):
        self.db_path = db_path
        self.init_social_database()
        
        # Template per i post sui social media
        self.post_templates = {
            'discovery': "🏛️ Ho appena scoperto {monument_name}! {description} 📍 {location} #MonumentRecognizer #Heritage #Travel",
            'achievement': "🎉 Ho raggiunto {achievement}! {stats} monumenti visitati con MonumentRecognizer! #Achievement #Heritage",
            'collection': "📸 La mia collezione di monumenti cresce! Ultimo aggiunto: {monument_name} 🏛️ #MonumentCollection #Heritage",
            'location': "📍 Esplorando {location} - {monument_name}: {description} #Travel #Monument #Heritage"
        }
        
        # URL per condivisione diretta sui social media
        self.social_urls = {
            'twitter': 'https://twitter.com/intent/tweet?text={text}&hashtags={hashtags}',
            'facebook': 'https://www.facebook.com/sharer/sharer.php?u={url}&quote={text}',
            'instagram': None,  # Instagram non supporta condivisione diretta via URL
            'whatsapp': 'https://wa.me/?text={text}',
            'telegram': 'https://t.me/share/url?url={url}&text={text}',
            'linkedin': 'https://www.linkedin.com/sharing/share-offsite/?url={url}'
        }
    
    def init_social_database(self):
        """Inizializza le tabelle del database per le funzionalità social"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabella per le condivisioni
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shared_visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visit_id INTEGER,
                    user_id TEXT,
                    platform TEXT,
                    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    post_text TEXT,
                    FOREIGN KEY (visit_id) REFERENCES visits (id)
                )
            ''')
            
            # Tabella per il feed interno delle visite condivise
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS social_feed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    monument_name TEXT,
                    post_text TEXT,
                    image_path TEXT,
                    location TEXT,
                    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    likes_count INTEGER DEFAULT 0,
                    comments_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tabella per i like sui post del feed
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS social_likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    user_id TEXT,
                    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES social_feed (id)
                )
            ''')
            
            # Tabella per i commenti sui post del feed
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS social_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    user_id TEXT,
                    comment_text TEXT,
                    commented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES social_feed (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database social inizializzato correttamente")
            
        except Exception as e:
            print(f"Errore nell'inizializzazione del database social: {e}")
    
    def generate_post_content(self, visit_data: Dict, template_type: str = 'discovery', 
                            include_stats: bool = False) -> Dict[str, str]:
        """Genera il contenuto per un post sui social media"""
        try:
            monument_name = visit_data.get('monument_name', 'Monumento sconosciuto')
            location = visit_data.get('location', 'Posizione non disponibile')
            description = visit_data.get('description', '')
            
            # Tronca la descrizione se troppo lunga
            if len(description) > 100:
                description = description[:97] + "..."
            
            # Genera statistiche se richieste
            stats_text = ""
            if include_stats:
                user_id = visit_data.get('user_id', 'guest')
                total_visits = self.get_user_visit_count(user_id)
                stats_text = f"({total_visits} monumenti visitati finora)"
            
            # Seleziona il template appropriato
            template = self.post_templates.get(template_type, self.post_templates['discovery'])
            
            # Sostituisce i placeholder nel template
            post_text = template.format(
                monument_name=monument_name,
                description=description,
                location=location,
                stats=stats_text,
                achievement=f"{monument_name} aggiunto alla collezione!"
            )
            
            # Genera hashtag
            hashtags = self.generate_hashtags(visit_data)
            
            # Genera URL condivisibile se disponibile
            share_url = self.generate_share_url(visit_data)
            
            return {
                'text': post_text,
                'hashtags': hashtags,
                'url': share_url,
                'monument_name': monument_name,
                'location': location,
                'image_path': visit_data.get('image_path', '')
            }
            
        except Exception as e:
            print(f"Errore nella generazione del contenuto del post: {e}")
            return {
                'text': f"Ho visitato {monument_name} con MonumentRecognizer! #Heritage",
                'hashtags': 'MonumentRecognizer,Heritage,Travel',
                'url': '',
                'monument_name': monument_name,
                'location': location,
                'image_path': ''
            }
    
    def generate_hashtags(self, visit_data: Dict) -> str:
        """Genera hashtag appropriati basati sui dati della visita"""
        hashtags = ['MonumentRecognizer', 'Heritage', 'Travel']
        
        monument_name = visit_data.get('monument_name', '')
        location = visit_data.get('location', '')
        
        # Aggiungi hashtag basati sul nome del monumento
        if monument_name:
            # Rimuovi spazi e caratteri speciali per gli hashtag
            clean_name = ''.join(c for c in monument_name if c.isalnum())
            if len(clean_name) > 3:
                hashtags.append(clean_name)
        
        # Aggiungi hashtag basati sulla posizione
        if location:
            location_parts = location.replace(',', ' ').split()
            for part in location_parts:
                clean_part = ''.join(c for c in part if c.isalnum())
                if len(clean_part) > 3:
                    hashtags.append(clean_part)
                    break  # Solo il primo elemento significativo
        
        # Aggiungi hashtag stagionali o temporali
        current_month = datetime.now().month
        if current_month in [12, 1, 2]:
            hashtags.append('WinterTravel')
        elif current_month in [3, 4, 5]:
            hashtags.append('SpringTravel')
        elif current_month in [6, 7, 8]:
            hashtags.append('SummerTravel')
        else:
            hashtags.append('AutumnTravel')
        
        return ','.join(hashtags[:6])  # Limita a 6 hashtag
    
    def generate_share_url(self, visit_data: Dict) -> str:
        """Genera un URL condivisibile per la visita (placeholder per futura implementazione web)"""
        # In futuro, questo potrebbe generare un link a una pagina web dell'app
        monument_name = visit_data.get('monument_name', '').replace(' ', '-')
        visit_id = visit_data.get('id', '')
        return f"https://monumentrecognizer.app/visit/{visit_id}/{monument_name}"
    
    def share_to_platform(self, visit_data: Dict, platform: str, template_type: str = 'discovery') -> bool:
        """Condivide una visita su una piattaforma social specifica"""
        try:
            if platform not in self.social_urls:
                print(f"Piattaforma {platform} non supportata")
                return False
            
            content = self.generate_post_content(visit_data, template_type, include_stats=True)
            
            if platform == 'instagram':
                # Instagram non supporta condivisione diretta, apri l'app o mostra istruzioni
                self.open_instagram_sharing(content)
                return True
            
            url_template = self.social_urls[platform]
            if not url_template:
                return False
            
            # Codifica il contenuto per l'URL
            encoded_text = urllib.parse.quote(content['text'])
            encoded_hashtags = urllib.parse.quote(content['hashtags'])
            encoded_url = urllib.parse.quote(content['url'])
            
            # Costruisci l'URL finale
            if platform == 'twitter':
                final_url = url_template.format(text=encoded_text, hashtags=encoded_hashtags)
            elif platform in ['facebook', 'linkedin']:
                final_url = url_template.format(url=encoded_url, text=encoded_text)
            else:  # whatsapp, telegram
                full_text = f"{content['text']} {content['url']}"
                encoded_full_text = urllib.parse.quote(full_text)
                final_url = url_template.format(text=encoded_full_text, url=encoded_url)
            
            # Apri il browser con l'URL di condivisione
            webbrowser.open(final_url)
            
            # Registra la condivisione nel database
            self.log_share(visit_data.get('id'), visit_data.get('user_id'), platform, content['text'])
            
            return True
            
        except Exception as e:
            print(f"Errore nella condivisione su {platform}: {e}")
            return False
    
    def open_instagram_sharing(self, content: Dict):
        """Gestisce la condivisione su Instagram (che non supporta URL diretti)"""
        try:
            # Crea un'immagine condivisibile se disponibile
            if content.get('image_path') and os.path.exists(content['image_path']):
                self.create_instagram_story_template(content)
            
            # Mostra le istruzioni all'utente
            instructions = f"""
📱 CONDIVISIONE SU INSTAGRAM:

📋 Copia questo testo:
{content['text']}

📸 Se hai un'immagine del monumento, puoi:
1. Aprire Instagram
2. Creare una nuova Storia o Post
3. Aggiungere la tua foto del monumento
4. Incollare il testo copiato
5. Pubblicare!

💡 Suggerimento: Usa gli sticker di posizione di Instagram per taggare il luogo!
            """
            print(instructions)
            return instructions
            
        except Exception as e:
            print(f"Errore nella preparazione per Instagram: {e}")
            return None
    
    def create_instagram_story_template(self, content: Dict):
        """Crea un template per Instagram Story con l'immagine e il testo"""
        try:
            if not content.get('image_path') or not os.path.exists(content['image_path']):
                return None
            
            # Carica l'immagine originale
            img = Image.open(content['image_path'])
            
            # Ridimensiona per Instagram Story (1080x1920)
            story_width, story_height = 1080, 1920
            img_ratio = img.width / img.height
            story_ratio = story_width / story_height
            
            if img_ratio > story_ratio:
                # Immagine più larga, adatta l'altezza
                new_height = story_height
                new_width = int(story_height * img_ratio)
            else:
                # Immagine più alta, adatta la larghezza
                new_width = story_width
                new_height = int(story_width / img_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crea canvas per story
            story_img = Image.new('RGB', (story_width, story_height), (0, 0, 0))
            
            # Centra l'immagine
            paste_x = (story_width - new_width) // 2
            paste_y = (story_height - new_height) // 2
            story_img.paste(img, (paste_x, paste_y))
            
            # Aggiungi overlay con testo
            overlay = Image.new('RGBA', (story_width, story_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Prova a caricare un font, altrimenti usa quello di default
            try:
                font_large = ImageFont.truetype("arial.ttf", 48)
                font_small = ImageFont.truetype("arial.ttf", 32)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Aggiungi titolo
            title = content.get('monument_name', 'Monumento')
            title_bbox = draw.textbbox((0, 0), title, font=font_large)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (story_width - title_width) // 2
            
            # Background per il testo
            draw.rectangle([(title_x - 20, 50), (title_x + title_width + 20, 120)], 
                          fill=(0, 0, 0, 180))
            draw.text((title_x, 60), title, fill=(255, 255, 255), font=font_large)
            
            # Aggiungi hashtag in basso
            hashtags = f"#{content.get('hashtags', '').replace(',', ' #')}"
            hashtags_bbox = draw.textbbox((0, 0), hashtags, font=font_small)
            hashtags_width = hashtags_bbox[2] - hashtags_bbox[0]
            hashtags_x = (story_width - hashtags_width) // 2
            
            draw.rectangle([(hashtags_x - 20, story_height - 100), 
                           (hashtags_x + hashtags_width + 20, story_height - 50)], 
                          fill=(0, 0, 0, 180))
            draw.text((hashtags_x, story_height - 90), hashtags, 
                     fill=(255, 255, 255), font=font_small)
            
            # Combina l'immagine con l'overlay
            story_img = Image.alpha_composite(story_img.convert('RGBA'), overlay)
            
            # Salva nel temp
            temp_path = os.path.join(tempfile.gettempdir(), f"instagram_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            story_img.convert('RGB').save(temp_path, quality=95)
            
            print(f"Template Instagram Story salvato in: {temp_path}")
            return temp_path
            
        except Exception as e:
            print(f"Errore nella creazione del template Instagram: {e}")
            return None
    
    def share_to_app_feed(self, visit_data: Dict, custom_message: str = "") -> bool:
        """Condivide una visita nel feed interno dell'app"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Genera il contenuto del post
            content = self.generate_post_content(visit_data, 'discovery')
            
            # Usa messaggio personalizzato se fornito
            post_text = custom_message if custom_message else content['text']
            
            # Inserisci nel feed social
            cursor.execute('''
                INSERT INTO social_feed (user_id, monument_name, post_text, image_path, location)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                visit_data.get('user_id', 'guest'),
                visit_data.get('monument_name', ''),
                post_text,
                visit_data.get('image_path', ''),
                visit_data.get('location', '')
            ))
            
            post_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"Visita condivisa nel feed interno con ID: {post_id}")
            return True
            
        except Exception as e:
            print(f"Errore nella condivisione nel feed interno: {e}")
            return False
    
    def log_share(self, visit_id: int, user_id: str, platform: str, post_text: str):
        """Registra una condivisione nel database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO shared_visits (visit_id, user_id, platform, post_text)
                VALUES (?, ?, ?, ?)
            ''', (visit_id, user_id, platform, post_text))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Errore nel logging della condivisione: {e}")
    
    def get_user_visit_count(self, user_id: str) -> int:
        """Ottiene il numero totale di visite di un utente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM visits WHERE user_id = ?', (user_id,))
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            print(f"Errore nel conteggio delle visite: {e}")
            return 0
    
    def get_social_feed(self, limit: int = 50) -> List[Dict]:
        """Ottiene i post dal feed social interno"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, monument_name, post_text, image_path, location, 
                       shared_at, likes_count, comments_count
                FROM social_feed
                ORDER BY shared_at DESC
                LIMIT ?
            ''', (limit,))
            
            posts = []
            for row in cursor.fetchall():
                posts.append({
                    'id': row[0],
                    'user_id': row[1],
                    'monument_name': row[2],
                    'post_text': row[3],
                    'image_path': row[4],
                    'location': row[5],
                    'shared_at': row[6],
                    'likes_count': row[7],
                    'comments_count': row[8]
                })
            
            conn.close()
            return posts
            
        except Exception as e:
            print(f"Errore nel recupero del feed social: {e}")
            return []
    
    def like_post(self, post_id: int, user_id: str) -> bool:
        """Mette like a un post del feed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verifica se l'utente ha già messo like
            cursor.execute('SELECT id FROM social_likes WHERE post_id = ? AND user_id = ?', 
                          (post_id, user_id))
            if cursor.fetchone():
                conn.close()
                return False  # Like già presente
            
            # Aggiungi like
            cursor.execute('INSERT INTO social_likes (post_id, user_id) VALUES (?, ?)', 
                          (post_id, user_id))
            
            # Aggiorna il contatore
            cursor.execute('UPDATE social_feed SET likes_count = likes_count + 1 WHERE id = ?', 
                          (post_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Errore nel mettere like: {e}")
            return False
    
    def add_comment(self, post_id: int, user_id: str, comment_text: str) -> bool:
        """Aggiunge un commento a un post del feed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Aggiungi commento
            cursor.execute('''
                INSERT INTO social_comments (post_id, user_id, comment_text)
                VALUES (?, ?, ?)
            ''', (post_id, user_id, comment_text))
            
            # Aggiorna il contatore
            cursor.execute('UPDATE social_feed SET comments_count = comments_count + 1 WHERE id = ?', 
                          (post_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Errore nell'aggiungere commento: {e}")
            return False
    
    def get_post_comments(self, post_id: int) -> List[Dict]:
        """Ottiene i commenti di un post"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, comment_text, commented_at
                FROM social_comments
                WHERE post_id = ?
                ORDER BY commented_at DESC
            ''', (post_id,))
            
            comments = []
            for row in cursor.fetchall():
                comments.append({
                    'user_id': row[0],
                    'comment_text': row[1],
                    'commented_at': row[2]
                })
            
            conn.close()
            return comments
            
        except Exception as e:
            print(f"Errore nel recupero dei commenti: {e}")
            return []
    
    def get_share_stats(self, user_id: str) -> Dict:
        """Ottiene le statistiche di condivisione di un utente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Condivisioni per piattaforma
            cursor.execute('''
                SELECT platform, COUNT(*) as count
                FROM shared_visits
                WHERE user_id = ?
                GROUP BY platform
            ''', (user_id,))
            platform_stats = dict(cursor.fetchall())
            
            # Totale condivisioni
            cursor.execute('SELECT COUNT(*) FROM shared_visits WHERE user_id = ?', (user_id,))
            total_shares = cursor.fetchone()[0]
            
            # Post nel feed interno
            cursor.execute('SELECT COUNT(*) FROM social_feed WHERE user_id = ?', (user_id,))
            internal_posts = cursor.fetchone()[0]
            
            # Like ricevuti
            cursor.execute('''
                SELECT SUM(likes_count) 
                FROM social_feed 
                WHERE user_id = ?
            ''', (user_id,))
            total_likes = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_shares': total_shares,
                'platform_stats': platform_stats,
                'internal_posts': internal_posts,
                'total_likes_received': total_likes
            }
            
        except Exception as e:
            print(f"Errore nel recupero delle statistiche: {e}")
            return {}


def test_social_sharing():
    """Test delle funzionalità di condivisione social"""
    print("🧪 Test del sistema di condivisione social...")
    
    # Crea istanza del manager
    social = SocialSharingManager("test_social.db")
    
    # Dati di esempio per una visita
    visit_data = {
        'id': 1,
        'user_id': 'test_user',
        'monument_name': 'Colosseo',
        'description': 'Anfiteatro romano costruito nel I secolo d.C.',
        'location': 'Roma, Italia',
        'image_path': 'images/colosseo.jpg',
        'timestamp': datetime.now().isoformat()
    }
    
    # Test generazione contenuto
    print("\n📝 Test generazione contenuto...")
    content = social.generate_post_content(visit_data, 'discovery', True)
    print(f"Testo generato: {content['text']}")
    print(f"Hashtags: {content['hashtags']}")
    
    # Test condivisione nel feed interno
    print("\n📱 Test condivisione nel feed interno...")
    success = social.share_to_app_feed(visit_data, "Che spettacolo il Colosseo! 🏛️")
    print(f"Condivisione nel feed: {'✅' if success else '❌'}")
    
    # Test recupero feed
    print("\n📰 Test recupero feed...")
    feed = social.get_social_feed(10)
    print(f"Post nel feed: {len(feed)}")
    
    if feed:
        post = feed[0]
        print(f"Ultimo post: {post['post_text']}")
        
        # Test like
        print("\n👍 Test like...")
        like_success = social.like_post(post['id'], 'test_user_2')
        print(f"Like aggiunto: {'✅' if like_success else '❌'}")
        
        # Test commento
        print("\n💬 Test commento...")
        comment_success = social.add_comment(post['id'], 'test_user_2', "Bellissimo monumento!")
        print(f"Commento aggiunto: {'✅' if comment_success else '❌'}")
    
    # Test statistiche
    print("\n📊 Test statistiche...")
    stats = social.get_share_stats('test_user')
    print(f"Statistiche: {stats}")
    
    print("\n✅ Test completato!")


if __name__ == "__main__":
    test_social_sharing()
