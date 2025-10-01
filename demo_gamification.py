"""
Demo del Sistema di Gamification per Monument Recognizer
Mostra tutte le funzionalità principali del sistema
"""

from gamification import GamificationManager
from datetime import datetime
import os


def print_separator(title=""):
    """Stampa un separatore con titolo opzionale"""
    print("\n" + "="*60)
    if title:
        print(f"🎯 {title}")
        print("="*60)


def print_user_progress(gm, user_id):
    """Mostra il progresso di un utente"""
    progress = gm.get_user_progress(user_id)
    print(f"\n📊 Progresso di {user_id}:")
    print(f"   • Punti totali: {progress.total_points}")
    print(f"   • Livello: {progress.level}")
    print(f"   • Esperienza: {progress.experience}")
    print(f"   • Streak visite: {progress.visits_streak}")
    print(f"   • Achievement sbloccati: {len(progress.achievements_unlocked)}")
    print(f"   • Badge ottenuti: {len(progress.badges_earned)}")
    print(f"   • Sfide completate: {len(progress.challenges_completed)}")


def demo_gamification():
    """Demo completo del sistema di gamification"""
    
    print("🎮 DEMO SISTEMA GAMIFICATION - MONUMENT RECOGNIZER")
    print("=" * 60)
    
    # Inizializza il sistema
    demo_db = "demo_gamification.db"
    if os.path.exists(demo_db):
        os.remove(demo_db)
    
    gm = GamificationManager(db_path=demo_db)
    
    print_separator("CREAZIONE UTENTI")
    
    # Crea alcuni utenti demo
    users = ["Marco", "Sofia", "Luca", "Giulia"]
    for user in users:
        progress = gm.get_user_progress(user)  # Crea automaticamente l'utente
        print(f"✅ Utente '{user}' creato (Livello {progress.level}, {progress.total_points} punti)")
    
    print_separator("SIMULAZIONE VISITE AI MONUMENTI")
    
    # Simula visite per Marco
    monuments_marco = [
        {"monument_name": "Colosseo", "coordinates": (41.8902, 12.4922), "category": "Anfiteatro"},
        {"monument_name": "Pantheon", "coordinates": (41.8986, 12.4769), "category": "Tempio"},
        {"monument_name": "Torre di Pisa", "coordinates": (43.7230, 10.3966), "category": "Torre"},
        {"monument_name": "Duomo di Milano", "coordinates": (45.4642, 9.1900), "category": "Cattedrale"},
    ]
    
    for monument in monuments_marco:
        result = gm.process_monument_visit("Marco", monument)
        print(f"🏛️ Marco visita {monument['monument_name']}")
        print(f"   → Punti ottenuti: {result['points_awarded']}")
        if result['achievements_unlocked']:
            for achievement in result['achievements_unlocked']:
                print(f"   🏆 Achievement sbloccato: {achievement}")
        if result['level_up']:
            print(f"   📈 LEVEL UP! Nuovo livello: {result['new_level']}")
    
    print_user_progress(gm, "Marco")
    
    print_separator("SIMULAZIONE CONDIVISIONI SOCIAL")
    
    # Simula condivisioni social per Sofia
    shares = [
        {"monument_name": "Fontana di Trevi", "platform": "instagram"},
        {"monument_name": "Ponte Vecchio", "platform": "facebook"},
        {"monument_name": "Sagrada Familia", "platform": "twitter"},
    ]
    
    for share in shares:
        result = gm.process_social_share("Sofia", share)
        print(f"📱 Sofia condivide {share['monument_name']} su {share['platform']}")
        print(f"   → Punti ottenuti: {result['points_awarded']}")
        if result['achievements_unlocked']:
            for achievement in result['achievements_unlocked']:
                print(f"   🏆 Achievement sbloccato: {achievement}")
    
    print_user_progress(gm, "Sofia")
    
    print_separator("ASSEGNAZIONE PUNTI DIRETTA")
    
    # Assegna punti bonus a Luca
    point_awards = [
        (100, "Primo login del giorno"),
        (50, "Completamento profilo"),
        (75, "Feedback positivo"),
        (200, "Partecipazione evento speciale")
    ]
    
    for points, reason in point_awards:
        result = gm.award_points("Luca", points, reason)
        print(f"🎯 Luca riceve {points} punti per: {reason}")
        if result['level_up']:
            print(f"   📈 LEVEL UP! Nuovo livello: {result['new_level']}")
    
    print_user_progress(gm, "Luca")
    
    print_separator("SFIDE GIORNALIERE")
    
    # Mostra sfide giornaliere per Giulia
    challenges = gm.get_daily_challenges("Giulia")
    print(f"🎯 Sfide giornaliere per Giulia ({len(challenges)} attive):")
    
    for challenge in challenges:
        status = "✅ COMPLETATA" if challenge['completed'] else f"📊 {challenge['progress']}/{challenge['target']}"
        print(f"   • {challenge['name']}: {challenge['description']}")
        print(f"     {status} - Ricompensa: {challenge['points']} punti {challenge['icon']}")
    
    print_separator("LEADERBOARD GLOBALE")
    
    # Aggiungi più punti per creare una classifica interessante
    gm.award_points("Marco", 200, "Bonus esploratore")
    gm.award_points("Sofia", 150, "Bonus social")
    gm.award_points("Luca", 300, "Bonus completamento")
    gm.award_points("Giulia", 250, "Bonus sfide")
    
    # Mostra leaderboard
    leaderboard = gm.get_leaderboard("points", 10)
    print("🏆 TOP UTENTI PER PUNTI:")
    
    for entry in leaderboard:
        medal = "🥇" if entry['rank'] == 1 else "🥈" if entry['rank'] == 2 else "🥉" if entry['rank'] == 3 else "📍"
        print(f"   {medal} #{entry['rank']} - {entry['user_id']}: {entry['points']} punti (Lv.{entry['level']}, {entry['achievements']} achievement)")
    
    print_separator("STATISTICHE FINALI")
    
    print("📊 RIASSUNTO DEMO:")
    total_users = len(users)
    total_points_awarded = sum(gm.get_user_progress(user).total_points for user in users)
    
    print(f"   • Utenti creati: {total_users}")
    print(f"   • Punti totali distribuiti: {total_points_awarded}")
    print(f"   • Achievement disponibili: {len(gm.achievements)}")
    print(f"   • Sfide giornaliere: {len(gm.challenges['daily'])}")
    print(f"   • Sfide settimanali: {len(gm.challenges['weekly'])}")
    
    # Mostra statistiche per ogni utente
    print(f"\n📈 PROGRESSI INDIVIDUALI:")
    for user in users:
        progress = gm.get_user_progress(user)
        level_progress = f"Lv.{progress.level}"
        if progress.experience_to_next_level > 0:
            next_level_xp = gm.calculate_experience_for_level(progress.level + 1)
            current_xp = progress.experience
            level_progress += f" ({current_xp}/{next_level_xp} XP)"
        
        print(f"   • {user}: {progress.total_points} punti, {level_progress}, {len(progress.achievements_unlocked)} achievement")
    
    print_separator()
    print("✅ Demo completato! Il sistema di gamification è perfettamente funzionante.")
    print("🎮 Il sistema include:")
    print("   • Sistema di punti e livelli dinamico")
    print("   • Achievement con criteri complessi") 
    print("   • Sfide giornaliere e settimanali")
    print("   • Leaderboard competitiva")
    print("   • Integrazione con visite e condivisioni social")
    print("   • Tracking completo delle statistiche utente")
    
    # Cleanup
    if os.path.exists(demo_db):
        os.remove(demo_db)


if __name__ == "__main__":
    demo_gamification()
