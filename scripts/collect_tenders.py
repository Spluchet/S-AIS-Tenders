import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# 🔍 Liste de mots-clés à rechercher
KEYWORDS = [
    "S-AIS",
    "Satellite AIS",
    "Maritime tracking data",
    "Vessel positioning service",
    "AIS satellite data"
]

# 🌍 Liste de portails à explorer (on peut en ajouter d'autres)
PORTALS = [
    "https://ted.europa.eu/TED/main/HomePage.do",  # Europe
    "https://sam.gov/content/home",                # USA
    "https://www.gov.br/compras/pt-br"             # Brésil
]

OUTPUT_FILE = "sais_tenders_2025.json"

def fetch_page(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"⚠️ Erreur en accédant à {url}: {e}")
        return None

def extract_tenders_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        link = a["href"]
        if any(keyword.lower() in text.lower() for keyword in KEYWORDS):
            tenders.append({
                "title": text,
                "url": link if link.startswith("http") else f"{base_url}/{link}",
                "source": base_url,
                "date_collected": datetime.utcnow().strftime("%Y-%m-%d")
            })
    return tenders

def load_existing_data():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("🚀 Recherche d'appels d'offres S-AIS en cours...")
    all_tenders = load_existing_data()

    for portal in PORTALS:
        html = fetch_page(portal)
        if html:
            new_tenders = extract_tenders_from_html(html, portal)
            for tender in new_tenders:
                if tender not in all_tenders:
                    all_tenders.append(tender)
                    print(f"➕ Nouveau : {tender['title']} ({tender['source']})")

    save_data(all_tenders)
    print(f"✅ Mise à jour terminée ({len(all_tenders)} appels d’offres enregistrés).")

if __name__ == "__main__":
    main()
