"""
analyze.py
Manda los titulares recogidos a Claude API para filtrar eventos relevantes.
Devuelve un JSON estructurado por categorías.
"""

import anthropic
import json
import os
from datetime import datetime

CATEGORIAS = [
    "estrenos",
    "deportes", 
    "especiales",
    "entrevistas",
    "parrilla",
    "records"
]

PROMPT_SISTEMA = """Eres un analista experto en audiencias de televisión española.
Tu tarea es analizar titulares de medios especializados y extraer SOLO los eventos relevantes
para un analista de competencia de una cadena autonómica española.

CADENAS DE INTERÉS: La 1, Antena 3, Telecinco, Cuatro, laSexta y cadenas autonómicas (FORTA).

CATEGORÍAS A DETECTAR:
1. estrenos: Nuevos programas, nuevas temporadas, debuts en parrilla
2. deportes: Retransmisiones deportivas destacadas, grandes eventos (fútbol, tenis, motor, etc.)
3. especiales: Galas, eventos únicos, programas especiales, finales de realities
4. entrevistas: Entrevistas a personajes relevantes (políticos, famosos de primer nivel, etc.)
5. parrilla: Cambios de programación, cancelaciones, sustituciones, movimientos estratégicos
6. records: Récords de audiencia, datos llamativos, mínimos o máximos históricos

NO incluyas: programación rutinaria, informativos habituales, resultados de audiencia del día sin contexto especial.

Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
{
  "fecha": "YYYY-MM-DD",
  "hay_alertas": true/false,
  "resumen_ejecutivo": "Una frase concisa con lo más importante del día",
  "alertas": {
    "estrenos": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "..."}],
    "deportes": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "..."}],
    "especiales": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "..."}],
    "entrevistas": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "..."}],
    "parrilla": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "..."}],
    "records": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "..."}]
  }
}

Si una categoría no tiene alertas, devuelve array vacío [].
El campo "cadena" puede ser "Varias" si aplica a múltiples.
El campo "detalle" es una frase corta con el contexto clave.
"""

def construir_prompt_usuario(datos_raw, fecha):
    """Construye el mensaje con todos los titulares recogidos."""
    lineas = [f"Fecha de análisis: {fecha}\n", "TITULARES RECOGIDOS POR FUENTE:\n"]
    
    for fuente, items in datos_raw.items():
        if items:
            lineas.append(f"\n## {fuente} ({len(items)} items)")
            for item in items:
                lineas.append(item)
    
    total = sum(len(v) for v in datos_raw.values())
    lineas.append(f"\n\nTotal titulares analizados: {total}")
    
    return "\n".join(lineas)

def analizar(datos_raw):
    """Llama a Claude API y devuelve el JSON de alertas."""
    cliente = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    prompt_usuario = construir_prompt_usuario(datos_raw, fecha)
    
    print("  Llamando a Claude API...")
    respuesta = cliente.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system=PROMPT_SISTEMA,
        messages=[{"role": "user", "content": prompt_usuario}]
    )
    
    texto = respuesta.content[0].text.strip()
    
    # Limpiar posibles backticks
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]
    texto = texto.strip()
    
    resultado = json.loads(texto)
    resultado["fecha"] = fecha  # Asegurar fecha correcta
    
    return resultado

if __name__ == "__main__":
    print("Cargando titulares...")
    with open("/tmp/raw_items.json", "r", encoding="utf-8") as f:
        datos_raw = json.load(f)
    
    print("Analizando con Claude...")
    resultado = analizar(datos_raw)
    
    total_alertas = sum(len(v) for v in resultado["alertas"].values())
    print(f"\nResultado: {total_alertas} alertas detectadas")
    print(f"Hay alertas: {resultado['hay_alertas']}")
    print(f"Resumen: {resultado['resumen_ejecutivo']}")
    
    with open("/tmp/alertas.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print("\nGuardado en /tmp/alertas.json")
