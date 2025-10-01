#!/usr/bin/env python3
"""
Script di monitoraggio avanzato per GitHub Actions - Android Build
Monitora i workflow e fornisce analisi dettagliate sui progressi della build
"""

import requests
import time
import json
import sys
from datetime import datetime, timedelta
import argparse

class GitHubWorkflowMonitor:
    def __init__(self, owner="OWNER", repo="REPO", token=None):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Android-Build-Monitor/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_workflows(self):
        """Ottieni lista dei workflow"""
        try:
            response = requests.get(f"{self.base_url}/actions/workflows", headers=self.headers)
            if response.status_code == 200:
                return response.json()["workflows"]
            else:
                print(f"❌ Errore nel recupero workflows: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Errore connessione API: {e}")
            return []

    def get_workflow_runs(self, workflow_id, limit=10):
        """Ottieni le esecuzioni recenti di un workflow"""
        try:
            params = {"per_page": limit, "page": 1}
            response = requests.get(
                f"{self.base_url}/actions/workflows/{workflow_id}/runs",
                headers=self.headers,
                params=params
            )
            if response.status_code == 200:
                return response.json()["workflow_runs"]
            else:
                print(f"❌ Errore nel recupero runs: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Errore connessione API: {e}")
            return []

    def get_run_details(self, run_id):
        """Ottieni dettagli di una specifica esecuzione"""
        try:
            response = requests.get(
                f"{self.base_url}/actions/runs/{run_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Errore nel recupero dettagli run: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Errore connessione API: {e}")
            return None

    def get_run_jobs(self, run_id):
        """Ottieni i job di una specifica esecuzione"""
        try:
            response = requests.get(
                f"{self.base_url}/actions/runs/{run_id}/jobs",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()["jobs"]
            else:
                print(f"❌ Errore nel recupero jobs: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Errore connessione API: {e}")
            return []

    def format_duration(self, seconds):
        """Formatta durata in formato leggibile"""
        if seconds is None:
            return "N/A"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def get_status_emoji(self, status, conclusion=None):
        """Ottieni emoji per status"""
        if status == "in_progress":
            return "🔄"
        elif status == "queued":
            return "⏳"
        elif status == "completed":
            if conclusion == "success":
                return "✅"
            elif conclusion == "failure":
                return "❌"
            elif conclusion == "cancelled":
                return "🚫"
            else:
                return "⚠️"
        else:
            return "❓"

    def monitor_android_builds(self, watch_mode=False, refresh_interval=30):
        """Monitora le build Android"""
        print("🔍 Ricerca workflow Android Build...")
        
        workflows = self.get_workflows()
        android_workflows = [w for w in workflows if "android" in w["name"].lower()]
        
        if not android_workflows:
            print("❌ Nessun workflow Android trovato!")
            return
        
        print(f"📋 Trovati {len(android_workflows)} workflow Android:")
        for i, wf in enumerate(android_workflows):
            print(f"  {i+1}. {wf['name']} (ID: {wf['id']})")
        
        # Monitora tutti i workflow Android o seleziona uno specifico
        target_workflows = android_workflows
        
        while True:
            print(f"\n{'='*80}")
            print(f"📊 MONITORAGGIO ANDROID BUILD - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            
            for workflow in target_workflows:
                print(f"\n🏗️  **{workflow['name']}**")
                print(f"   ID: {workflow['id']}")
                
                runs = self.get_workflow_runs(workflow['id'], limit=5)
                
                if not runs:
                    print("   📭 Nessuna esecuzione trovata")
                    continue
                
                for i, run in enumerate(runs):
                    status_emoji = self.get_status_emoji(run['status'], run.get('conclusion'))
                    
                    # Calcola durata
                    created_at = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                    if run['status'] == 'completed':
                        updated_at = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                        duration = int((updated_at - created_at).total_seconds())
                    else:
                        duration = int((datetime.now(created_at.tzinfo) - created_at).total_seconds())
                    
                    print(f"   {i+1}. {status_emoji} Run #{run['run_number']}")
                    print(f"      📅 {created_at.strftime('%Y-%m-%d %H:%M')} ({self.format_duration(duration)})")
                    print(f"      🌿 {run['head_branch']} - {run['head_commit']['message'][:50]}...")
                    print(f"      🔗 {run['html_url']}")
                    
                    # Dettagli jobs per run in corso
                    if run['status'] == 'in_progress':
                        jobs = self.get_run_jobs(run['id'])
                        if jobs:
                            print(f"      📋 Jobs in corso:")
                            for job in jobs:
                                job_emoji = self.get_status_emoji(job['status'], job.get('conclusion'))
                                print(f"         {job_emoji} {job['name']}")
                                
                                if job['status'] == 'in_progress' and 'steps' in job:
                                    current_step = None
                                    for step in job['steps']:
                                        if step['status'] == 'in_progress':
                                            current_step = step
                                            break
                                    
                                    if current_step:
                                        print(f"            🔄 Step corrente: {current_step['name']}")
            
            if not watch_mode:
                break
            
            print(f"\n⏳ Prossimo aggiornamento in {refresh_interval} secondi... (Ctrl+C per uscire)")
            try:
                time.sleep(refresh_interval)
            except KeyboardInterrupt:
                print("\n👋 Monitoraggio interrotto dall'utente")
                break

    def analyze_build_trends(self):
        """Analizza i trend delle build Android"""
        print("📈 ANALISI TREND BUILD ANDROID")
        print("="*50)
        
        workflows = self.get_workflows()
        android_workflows = [w for w in workflows if "android" in w["name"].lower()]
        
        for workflow in android_workflows:
            print(f"\n🏗️  {workflow['name']}")
            runs = self.get_workflow_runs(workflow['id'], limit=20)
            
            if not runs:
                continue
            
            # Statistiche
            total_runs = len(runs)
            successful = len([r for r in runs if r.get('conclusion') == 'success'])
            failed = len([r for r in runs if r.get('conclusion') == 'failure'])
            cancelled = len([r for r in runs if r.get('conclusion') == 'cancelled'])
            in_progress = len([r for r in runs if r['status'] == 'in_progress'])
            
            print(f"   📊 Statistiche recenti ({total_runs} runs):")
            print(f"      ✅ Successo: {successful} ({successful/total_runs*100:.1f}%)")
            print(f"      ❌ Fallite: {failed} ({failed/total_runs*100:.1f}%)")
            print(f"      🚫 Cancellate: {cancelled} ({cancelled/total_runs*100:.1f}%)")
            print(f"      🔄 In corso: {in_progress}")
            
            # Durate medie
            completed_runs = [r for r in runs if r['status'] == 'completed']
            if completed_runs:
                durations = []
                for run in completed_runs:
                    created = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                    updated = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                    duration = (updated - created).total_seconds()
                    durations.append(duration)
                
                avg_duration = sum(durations) / len(durations)
                print(f"   ⏱️  Durata media: {self.format_duration(int(avg_duration))}")
                
                # Trend recente
                recent_runs = completed_runs[:5]
                recent_success = len([r for r in recent_runs if r.get('conclusion') == 'success'])
                print(f"   📈 Trend recente: {recent_success}/{len(recent_runs)} successi")


def main():
    parser = argparse.ArgumentParser(description="Monitora le build Android su GitHub Actions")
    parser.add_argument("--owner", default="OWNER", help="Owner del repository GitHub")
    parser.add_argument("--repo", default="MonumentRecognizer", help="Nome del repository")
    parser.add_argument("--token", help="Token GitHub per API rate limiting")
    parser.add_argument("--watch", "-w", action="store_true", help="Modalità monitoraggio continuo")
    parser.add_argument("--interval", "-i", type=int, default=30, help="Intervallo refresh in secondi (default: 30)")
    parser.add_argument("--analyze", "-a", action="store_true", help="Analizza trend delle build")
    
    args = parser.parse_args()
    
    monitor = GitHubWorkflowMonitor(args.owner, args.repo, args.token)
    
    if args.analyze:
        monitor.analyze_build_trends()
    else:
        monitor.monitor_android_builds(args.watch, args.interval)

if __name__ == "__main__":
    main()
