"""
analyze.py
Manda los titulares recogidos a Claude API para filtrar eventos relevantes.
Devuelve un JSON estructurado por categorías.
"""

import anthropic
import json
import os
from datetime import datetime

PROMPT_SISTEMA = """Eres un analista experto en televisión española. Tu tarea es analizar titulares
de medios especializados y extraer los eventos relevantes para seguimiento de competencia televisiva.

CADENAS DE INTERÉS PRINCIPAL: La 1, Antena 3, Telecinco, Cuatro, laSexta y cadenas autonómicas (FORTA).

CATEGORÍAS A DETECTAR — sé generoso, incluye todo lo que pueda ser relevante:
1. estrenos: Nuevos programas, nuevas temporadas, debuts en parrilla, regresos tras pausa
2. deportes: Retransmisiones deportivas destacadas, grandes eventos (fútbol, tenis, motor, olimpiadas, etc.)
3. especiales: Programas especiales motivados por eventos de actualidad (visitas de Estado, catástrofes,
   elecciones, muerte de personajes relevantes, eventos religiosos como visita del Papa, etc.),
   galas, finales de realities, magacines de emergencia
4. entrevistas: Entrevistas a personajes relevantes (políticos, papas, reyes, famosos de primer nivel)
5. parrilla: Cambios de programación, cancelaciones, sustituciones, movimientos estratégicos,
   programas que se adelantan o retrasan por eventos de actualidad
6. records: Récords de audiencia, datos llamativos, mínimos o máximos históricos, programas
   que superan su media habitual de forma notable

IMPORTANTE: Si un evento de actualidad importante (visita del Papa, partido de selección, funeral de Estado,
catástrofe natural, etc.) ha provocado cambios en la parrilla o programas especiales, INCLÚYELO aunque
los titulares no mencionen explícitamente los datos de audiencia. El contexto del evento es suficiente.

NO incluyas: informativos diarios habituales sin contexto especial, programación completamente rutinaria.

Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
{
  "fecha": "YYYY-MM-DD",
  "hay_alertas": true/false,
  "resumen_ejecutivo": "Una frase concisa con lo más importante del día",
  "alertas": {
    "estrenos": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "...", "url": "..."}],
    "deportes": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "...", "url": "..."}],
    "especiales": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "...", "url": "..."}],
    "entrevistas": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "...", "url": "..."}],
    "parrilla": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "...", "url": "..."}],
    "records": [{"titular": "...", "cadena": "...", "detalle": "...", "fuente": "...", "url": "..."}]
  }
}

Si una categoría no tiene alertas, devuelve array vacío [].
El campo "cadena" puede ser "Varias" si aplica a múltiples, o dejarlo vacío si no se especifica.
El campo "detalle" es una frase corta con el contexto clave.
El campo "url" es la URL original de la noticia extraída del titular entre corchetes. Si no hay URL, deja cadena vacía.
"""

def construir_prompt_usuario(datos_raw, fecha):
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
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]
    texto = texto.strip()

    resultado = json.loads(texto)
    resultado["fecha"] = fecha
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
