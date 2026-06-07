"""
run.py
Orquestador principal: fetch → analyze → build.
Ejecutado por GitHub Actions cada día a las 09:00.
"""

import sys
import json
from fetch_sources import recoger_todo
from analyze import analizar
from build_html import build

def main():
    print("=" * 50)
    print("TV ALERTAS — Ejecución diaria")
    print("=" * 50)
    
    # Paso 1: Recoger fuentes
    print("\n[1/3] Recolectando fuentes...")
    try:
        datos_raw = recoger_todo()
        total = sum(len(v) for v in datos_raw.values())
        print(f"  {total} titulares recogidos")
    except Exception as e:
        print(f"  ERROR en recolección: {e}")
        sys.exit(1)
    
    if total == 0:
        print("  Sin titulares. Abortando.")
        sys.exit(1)
    
    # Paso 2: Analizar con Claude
    print("\n[2/3] Analizando con Claude API...")
    try:
        alertas_json = analizar(datos_raw)
        total_alertas = sum(len(v) for v in alertas_json["alertas"].values())
        print(f"  {total_alertas} alertas detectadas")
        print(f"  Resumen: {alertas_json['resumen_ejecutivo']}")
    except Exception as e:
        print(f"  ERROR en análisis: {e}")
        sys.exit(1)
    
    # Paso 3: Generar HTML
    print("\n[3/3] Generando HTML...")
    try:
        build(alertas_json)
    except Exception as e:
        print(f"  ERROR en generación HTML: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Ejecución completada con éxito.")
    print("=" * 50)

if __name__ == "__main__":
    main()
