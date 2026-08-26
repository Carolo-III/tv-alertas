"""
fetch_sources.py
Recolecta titulares de RSS y scraping de fuentes TV especializadas.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import json
import time

HORAS_UMBRAL = 36

RSS_SOURCES = [
    {
        "nombre": "Barlovento Comunicación",
        "url": "https://barloventocomunicacion.es/feed",
    },
    {
        "nombre": "Fórmula TV — Noticias",
        "url": "https://www.formulatv.com/rss/noticias.xml",
    },
    {
        "nombre": "Fórmula TV — Programación",
        "url": "https://www.formulatv.com/rss/programacion.xml",
    },
    {
        "nombre": "Vertele",
        "url": "https://vertele.eldiario.es/feed/",
    },
    {
        "nombre": "RTVE Noticias TV",
        "url": "https://www.rtve.es/api/programas/television.rss",
    },
    {
        "nombre": "El Mundo TV",
        "url": "https://e00-elmundo.uecdn.es/television/rss2.xml",
    },
    {
        "nombre": "20minutos TV",
        "url": "https://www.20minutos.es/rss/television/",
    },
]

SCRAPE_SOURCES = [
    {
        "nombre": "DOS30",
        "url": "https://www.dos30.com/actualidad/",
    },
    {
        "nombre": "Vertele",
        "url": "https://www.eldiario.es/vertele/audiencias-tv/",
    },
    {
        "nombre": "Fórmula TV — Portada",
        "url": "https://www.formulatv.com/",
    },
]

def es_reciente(entry):
    ahora = datetime.now(timezone.utc)
    umbral = ahora - timedelta(hours=HORAS_UMBRAL)
    fecha = None
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        fecha = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        fecha = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    if fecha is None:
        return True
    return fecha >= umbral

def fetch_rss(fuente):
    try:
        feed = feedparser.parse(fuente["url"])
        items = []
        for entry in feed.entries:
            if not es_reciente(entry):
                continue
            titulo = entry.get("title", "").strip()
            resumen = entry.get("summary", "")[:300].strip()
            link = entry.get("link", "")
            if titulo:
                items.append(f"- {titulo}. {resumen} [{link}]")
        return items
    except Exception as e:
        print(f"  Error RSS {fuente['nombre']}: {e}")
        return []

def fetch_scrape(fuente):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; tv-alertas-bot/1.0)"}
        r = requests.get(fuente["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        for el in soup.select("h2, h3")[:20]:
            titulo = el.get_text(strip=True)
            if len(titulo) > 20:
                link_el = el.find("a") or el.find_parent("a")
                link = link_el["href"] if link_el and link_el.get("href") else ""
                items.append(f"- {titulo} [{link}]")
        return items
    except Exception as e:
        print(f"  Error scraping {fuente['nombre']}: {e}")
        return []

def recoger_todo():
    resultado = {}
    for fuente in RSS_SOURCES:
        print(f"  Leyendo RSS: {fuente['nombre']}...")
        items = fetch_rss(fuente)
        if items:
            resultado[fuente["nombre"]] = items
        time.sleep(1)
    for fuente in SCRAPE_SOURCES:
        print(f"  Scrapeando: {fuente['nombre']}...")
        items = fetch_scrape(fuente)
        if items:
            resultado[fuente["nombre"]] = items
        time.sleep(1)
    return resultado

if __name__ == "__main__":
    print("Recolectando fuentes...")
    datos = recoger_todo()
    total = sum(len(v) for v in datos.values())
    print(f"\nTotal titulares recogidos: {total}")
    for fuente, items in datos.items():
        print(f"  {fuente}: {len(items)} items")
        for item in items[:3]:
            print(f"    {item[:100]}")
    with open("/tmp/raw_items.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print("\nGuardado en /tmp/raw_items.json")
