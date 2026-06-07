# 📺 TV Alertas

Monitor automático de eventos relevantes en la televisión española. Detecta estrenos, retransmisiones deportivas, especiales, entrevistas, cambios de parrilla y récords de audiencia en las cadenas nacionales generalistas y autonómicas.

## Cadenas monitorizadas
La 1 · Antena 3 · Telecinco · Cuatro · laSexta · Autonómicas (FORTA)

## Fuentes
- **Barlovento Comunicación** — audiencias diarias y récords
- **Fórmula TV** — estrenos, parrillas y noticias TV
- **Vertele** — programación y análisis
- **DOS30** — análisis de audiencias

## Cómo funciona
GitHub Actions ejecuta el análisis cada día a las 09:00 (hora española):
1. Recolecta titulares de RSS y scraping
2. Claude API filtra y clasifica los eventos relevantes
3. Genera un HTML estático publicado en GitHub Pages

## Ver el dashboard
👉 `https://carolo-iii.github.io/tv-alertas`

## Configuración

### Secreto necesario en GitHub
`ANTHROPIC_API_KEY` → Settings → Secrets and variables → Actions → New repository secret

### Activar GitHub Pages
Settings → Pages → Source: `Deploy from a branch` → Branch: `main` → Folder: `/docs`

## Ejecución manual
Desde GitHub → Actions → "TV Alertas" → Run workflow
