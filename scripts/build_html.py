"""
build_html.py
Genera la página HTML del día y actualiza el índice histórico.
Visual: dark theme coherente con carolo-iii.github.io
"""

import json
import os
from datetime import datetime
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"
DIAS_DIR = DOCS_DIR / "dias"

CATEGORIAS_META = {
    "estrenos":    {"label": "Estrenos",          "icon": "🎬", "color": "#e8c547"},
    "deportes":    {"label": "Deportes",           "icon": "⚽", "color": "#47c5e8"},
    "especiales":  {"label": "Especiales / Galas", "icon": "⭐", "color": "#e847a3"},
    "entrevistas": {"label": "Entrevistas",        "icon": "🎙️", "color": "#a347e8"},
    "parrilla":    {"label": "Cambios de parrilla","icon": "📋", "color": "#e87347"},
    "records":     {"label": "Récords",            "icon": "📊", "color": "#47e87e"},
}

CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0a0a0b;
  --bg2: #111113;
  --bg3: #1a1a1d;
  --border: #2a2a2e;
  --text: #e8e8ec;
  --text-muted: #6b6b78;
  --accent: #e8c547;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  line-height: 1.6;
  min-height: 100vh;
}

.site-header {
  border-bottom: 1px solid var(--border);
  padding: 20px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  background: rgba(10,10,11,0.95);
  backdrop-filter: blur(8px);
  z-index: 100;
}

.site-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 24px;
  letter-spacing: 2px;
  color: var(--accent);
}

.site-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.nav-link {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 13px;
  letter-spacing: 0.5px;
  transition: color 0.2s;
}
.nav-link:hover { color: var(--accent); }

main { max-width: 900px; margin: 0 auto; padding: 40px 24px; }

.fecha-display {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 48px;
  letter-spacing: 3px;
  color: var(--text);
  margin-bottom: 4px;
}

.resumen-ejecutivo {
  font-size: 16px;
  color: var(--text-muted);
  margin-bottom: 40px;
  padding-left: 16px;
  border-left: 3px solid var(--accent);
}

.sin-alertas {
  text-align: center;
  padding: 80px 24px;
  color: var(--text-muted);
}

.sin-alertas .icon { font-size: 48px; margin-bottom: 16px; }
.sin-alertas h2 { font-family: 'Bebas Neue', sans-serif; font-size: 28px; letter-spacing: 2px; margin-bottom: 8px; color: var(--text); }

.categoria-bloque { margin-bottom: 40px; }

.categoria-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.categoria-icon { font-size: 20px; }

.categoria-label {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 20px;
  letter-spacing: 2px;
}

.categoria-count {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: var(--bg3);
  color: var(--text-muted);
  font-weight: 500;
}

.alerta-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 10px;
  border-left: 3px solid transparent;
  transition: border-color 0.2s, background 0.2s;
}

.alerta-card:hover { background: var(--bg3); }

.alerta-titular {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
  color: var(--text);
}

.alerta-detalle {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.alerta-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
}

.badge-cadena {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 7px;
  color: var(--text-muted);
}

.badge-fuente {
  color: var(--text-muted);
  font-style: italic;
}

/* Histórico */
.historico-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 24px;
}

.dia-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  text-decoration: none;
  display: block;
  transition: border-color 0.2s, background 0.2s;
}

.dia-card:hover { background: var(--bg3); border-color: var(--accent); }

.dia-fecha {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 18px;
  letter-spacing: 1px;
  color: var(--text);
  margin-bottom: 4px;
}

.dia-alertas {
  font-size: 12px;
  color: var(--text-muted);
}

.dia-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
  margin-right: 6px;
  vertical-align: middle;
}

.dia-sin-alertas .dia-dot { background: var(--border); }

footer {
  border-top: 1px solid var(--border);
  padding: 20px 32px;
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}
"""

def fecha_legible(fecha_str):
    """Convierte '2026-06-07' a 'Sábado 7 de junio de 2026'."""
    meses = ["enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    dias_semana = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    d = datetime.strptime(fecha_str, "%Y-%m-%d")
    return f"{dias_semana[d.weekday()].capitalize()} {d.day} de {meses[d.month-1]} de {d.year}"

def render_dia(alertas_json):
    """Genera el HTML de la página de un día concreto."""
    fecha = alertas_json["fecha"]
    fecha_display = fecha_legible(fecha)
    resumen = alertas_json.get("resumen_ejecutivo", "Sin eventos destacados.")
    hay_alertas = alertas_json.get("hay_alertas", False)
    alertas = alertas_json.get("alertas", {})
    
    categorias_con_datos = {k: v for k, v in alertas.items() if v}
    
    # Construir tarjetas de alertas
    bloques_html = ""
    for cat_key, items in categorias_con_datos.items():
        meta = CATEGORIAS_META.get(cat_key, {"label": cat_key, "icon": "•", "color": "#fff"})
        color = meta["color"]
        
        tarjetas = ""
        for item in items:
            titular = item.get("titular", "")
            detalle = item.get("detalle", "")
            cadena = item.get("cadena", "")
            fuente = item.get("fuente", "")
            tarjetas += f"""
            <div class="alerta-card" style="border-left-color:{color}">
              <div class="alerta-titular">{titular}</div>
              {"<div class='alerta-detalle'>" + detalle + "</div>" if detalle else ""}
              <div class="alerta-meta">
                {"<span class='badge-cadena'>" + cadena + "</span>" if cadena else ""}
                {"<span class='badge-fuente'>" + fuente + "</span>" if fuente else ""}
              </div>
            </div>"""
        
        bloques_html += f"""
        <div class="categoria-bloque">
          <div class="categoria-header">
            <span class="categoria-icon">{meta['icon']}</span>
            <span class="categoria-label" style="color:{color}">{meta['label']}</span>
            <span class="categoria-count">{len(items)}</span>
          </div>
          {tarjetas}
        </div>"""
    
    contenido_principal = bloques_html if hay_alertas and categorias_con_datos else """
    <div class="sin-alertas">
      <div class="icon">📺</div>
      <h2>Sin alertas hoy</h2>
      <p>No se han detectado eventos especiales en las cadenas monitorizadas.</p>
    </div>"""
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TV Alertas — {fecha_display}</title>

  <style>{CSS_BASE}</style>
</head>
<body>
  <header class="site-header">
    <div>
      <div class="site-title">TV ALERTAS</div>
      <div class="site-subtitle">Monitor de televisión española</div>
    </div>
    <a href="../index.html" class="nav-link">← Histórico</a>
  </header>
  <main>
    <div class="fecha-display">{fecha_display.upper()}</div>
    <div class="resumen-ejecutivo">{resumen}</div>
    {contenido_principal}
  </main>
  <footer>Generado automáticamente · Fuentes: Barlovento, Fórmula TV, Vertele, DOS30</footer>
</body>
</html>"""

def cargar_historico():
    """Lee todos los JSON de días anteriores para construir el índice."""
    historico = []
    if not DIAS_DIR.exists():
        return historico
    
    for archivo in sorted(DIAS_DIR.glob("*.json"), reverse=True):
        try:
            with open(archivo, encoding="utf-8") as f:
                datos = json.load(f)
            total = sum(len(v) for v in datos.get("alertas", {}).values())
            historico.append({
                "fecha": datos["fecha"],
                "fecha_legible": fecha_legible(datos["fecha"]),
                "total_alertas": total,
                "hay_alertas": datos.get("hay_alertas", False),
                "resumen": datos.get("resumen_ejecutivo", ""),
            })
        except Exception:
            pass
    
    return historico

def render_indice(historico):
    """Genera el index.html con el día actual y el archivo histórico."""
    hoy = historico[0] if historico else None
    
    # Tarjeta del día actual
    if hoy:
        dot_class = "" if hoy["hay_alertas"] else "dia-sin-alertas"
        hoy_html = f"""
        <a href="dias/{hoy['fecha']}.html" class="dia-card" style="border-color: var(--accent); grid-column: 1 / -1;">
          <div style="font-size:11px;color:var(--accent);letter-spacing:1px;text-transform:uppercase;margin-bottom:4px">Hoy</div>
          <div class="dia-fecha">{hoy['fecha_legible'].upper()}</div>
          <div class="dia-alertas">
            <span class="dia-dot {dot_class}"></span>
            {hoy['total_alertas']} alertas detectadas · {hoy['resumen'][:80]}{'...' if len(hoy['resumen']) > 80 else ''}
          </div>
        </a>"""
    else:
        hoy_html = ""
    
    # Días anteriores
    dias_anteriores = ""
    for dia in historico[1:]:
        dot_class = "" if dia["hay_alertas"] else "dia-sin-alertas"
        dias_anteriores += f"""
        <a href="dias/{dia['fecha']}.html" class="dia-card {dot_class}">
          <div class="dia-fecha">{dia['fecha_legible'].upper()}</div>
          <div class="dia-alertas">
            <span class="dia-dot"></span>
            {dia['total_alertas']} alertas
          </div>
        </a>"""
    
    historico_section = f"""
    <h2 style="font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:2px;color:var(--text-muted);margin-top:48px;margin-bottom:0">
      HISTÓRICO
    </h2>
    <div class="historico-grid">
      {hoy_html}
      {dias_anteriores}
    </div>""" if historico else ""
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TV Alertas — Monitor de televisión española</title>
  <style>{CSS_BASE}</style>
</head>
<body>
  <header class="site-header">
    <div>
      <div class="site-title">TV ALERTAS</div>
      <div class="site-subtitle">Monitor de televisión española</div>
    </div>
  </header>
  <main>
    {historico_section}
  </main>
  <footer>Actualizado diariamente a las 09:00 · Fuentes: Barlovento, Fórmula TV, Vertele, DOS30</footer>

def build(alertas_json):
    """Punto de entrada principal: genera HTML del día y actualiza índice."""
    DIAS_DIR.mkdir(parents=True, exist_ok=True)
    
    fecha = alertas_json["fecha"]
    
    # 1. Guardar JSON del día para el histórico
    json_path = DIAS_DIR / f"{fecha}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(alertas_json, f, ensure_ascii=False, indent=2)
    print(f"  JSON guardado: {json_path}")
    
    # 2. Generar HTML del día
    html_dia = render_dia(alertas_json)
    html_path = DIAS_DIR / f"{fecha}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_dia)
    print(f"  HTML del día generado: {html_path}")
    
    # 3. Cargar histórico completo y regenerar índice
    historico = cargar_historico()
    html_indice = render_indice(historico)
    indice_path = DOCS_DIR / "index.html"
    with open(indice_path, "w", encoding="utf-8") as f:
        f.write(html_indice)
    print(f"  Índice actualizado: {indice_path}")

if __name__ == "__main__":
    print("Cargando alertas analizadas...")
    with open("/tmp/alertas.json", "r", encoding="utf-8") as f:
        alertas_json = json.load(f)
    
    print("Generando HTML...")
    build(alertas_json)
    print("\nListo.")
