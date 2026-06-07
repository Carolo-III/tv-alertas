"""
fetch_sources.py
Recolecta titulares de RSS y scraping de fuentes TV especializadas.
Fuentes: Barlovento, Fórmula TV, Vertele, DOS30, GECA (vía Fórmula TV/Vertele)
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import json
import time

# Umbral: solo noticias de las últimas 26 horas
HORAS_UMBRAL = 26

RSS_SOURCES = [
    {
        "nombre": "Barlovento Comunicación",
        "url": "https://barloventocomunicacion.es/feed",
        "tipo": "rss"
    },
    {
        "nombre": "Fórmula TV",
        "url": "https://www.formulatv.com/rss/noticias.xml",
        "tipo": "rss"
    },
    {
        "nombre": "Vertele",
        "url": "https://vertele.eldiario.es/feed/",
        "tipo": "rss"
    },
]

SCRAPE_SOURCES = [
    {
        "nombre": "DOS30",
        "url": "https://www.dos30.com/actualidad/",
        "tipo": "scrape"
    },
]

def es_reciente(entry):
    """Comprueba si una entrada es de las últimas HORAS_UMBRAL horas."""
    ahora = datetime.now(timezone.utc)
    umbral = ahora - timedelta(hours=HORAS_UMBRAL)
    
    fecha = None
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        fecha = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        fecha = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    
    if fecha is None:
        return True  # Sin fecha: incluir por precaución
    
    return fecha >= umbral

def fetch_rss(fuente):
    """Lee un feed RSS y devuelve titulares recientes."""
    try:
        feed = feedparser.parse(fuente["url"])
        items = []
        for entry in feed.entries:
            if not es_reciente(entry):
                continue
            titulo = entry.get("title", "").strip()
            resumen = entry.get("summary", "")[:300].strip()
            link = entry.get("link", "")
            items.append(f"- {titulo}. {resumen} [{link}]")
        return items
    except Exception as e:
        print(f"Error RSS {fuente['nombre']}: {e}")
        return []

def fetch_dos30():
    """Scraping básico de dos30.com/actualidad."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; tv-alertas-bot/1.0)"}
        r = requests.get("https://www.dos30.com/actualidad/", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        # DOS30 usa estructura WordPress estándar
        for article in soup.select("article")[:15]:
            titulo_el = article.select_one("h2, h3")
            if titulo_el:
                titulo = titulo_el.get_text(strip=True)
                link_el = article.select_one("a")
                link = link_el["href"] if link_el else ""
                items.append(f"- {titulo} [{link}]")
        return items
    except Exception as e:
        print(f"Error scraping DOS30: {e}")
        return []

def recoger_todo():
    """Recolecta todas las fuentes y devuelve un dict estructurado."""
    resultado = {}
    
    for fuente in RSS_SOURCES:
        print(f"  Leyendo RSS: {fuente['nombre']}...")
        items = fetch_rss(fuente)
        resultado[fuente["nombre"]] = items
        time.sleep(1)
    
    print("  Scrapeando DOS30...")
    resultado["DOS30"] = fetch_dos30()
    
    return resultado

if __name__ == "__main__":
    print("Recolectando fuentes...")
    datos = recoger_todo()
    
    total = sum(len(v) for v in datos.values())
    print(f"\nTotal titulares recogidos: {total}")
    for fuente, items in datos.items():
        print(f"  {fuente}: {len(items)} items")
    
    # Guardar para siguiente etapa
    with open("/tmp/raw_items.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    print("\nGuardado en /tmp/raw_items.json")
