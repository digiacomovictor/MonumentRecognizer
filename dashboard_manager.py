"""
Dashboard Manager Android-Compatible
Rimuove dipendenze matplotlib, plotly, pandas
"""
import json
from typing import Dict, List
from datetime import datetime

class DashboardManager:
    def __init__(self):
        self.stats = {}
    
    def generate_charts_data(self, visit_data: List[Dict]) -> Dict:
        """Genera dati per chart Android-compatibili"""
        if not visit_data:
            return {"message": "Nessuna visita registrata"}
        
        # Conta visite per paese
        countries = {}
        cities = {}
        monthly_visits = {}
        
        for visit in visit_data:
            country = visit.get('country', 'Sconosciuto')
            city = visit.get('city', 'Sconosciuta')
            date = visit.get('date', datetime.now().isoformat())
            
            countries[country] = countries.get(country, 0) + 1
            cities[city] = cities.get(city, 0) + 1
            
            month_key = date[:7]  # YYYY-MM
            monthly_visits[month_key] = monthly_visits.get(month_key, 0) + 1
        
        return {
            'countries_count': countries,
            'cities_count': cities,
            'monthly_visits': monthly_visits,
            'total_visits': len(visit_data),
            'android_mode': True
        }
    
    def create_text_summary(self, data: Dict) -> str:
        """Crea riassunto testuale delle statistiche"""
        summary = "📊 STATISTICHE VISITE\n\n"
        
        if data.get('total_visits', 0) > 0:
            summary += f"🏛️ Visite totali: {data['total_visits']}\n"
            
            if 'countries_count' in data:
                top_country = max(data['countries_count'].items(), key=lambda x: x[1])
                summary += f"🌍 Paese più visitato: {top_country[0]} ({top_country[1]} visite)\n"
            
            if 'cities_count' in data:
                top_city = max(data['cities_count'].items(), key=lambda x: x[1])
                summary += f"🏙️ Città più visitata: {top_city[0]} ({top_city[1]} visite)\n"
        else:
            summary += "Nessuna visita registrata ancora.\n"
        
        summary += "\n📱 Modalità Android - Grafici non disponibili"
        return summary
