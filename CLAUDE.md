# Calendiorama Atlas Temporis — Claude Code Instructions

## Project Summary

Interactive historical world map web application built entirely in Python (backend) + Leaflet.js (frontend). For any date selected on a chronological timeline, the map shows:
- **Historical borders** of that era
- **Local calendar dates** per region (Gregorian, Hijri, Hebrew, Persian, Japanese Imperial, Julian, Coptic, Ethiopian)

## Developer Profile

- Python: advanced
- Docker: experienced
- Flask, GeoPandas, Leaflet.js: **learning** — explain concepts before coding, do not write full files without being asked

## Collaboration Rules

**IMPORTANT: This is a learning project.** The developer wants to understand each technology by building it.
- Explain the *why* behind every technical decision before showing code
- Show short illustrative examples, then let the developer implement
- Do NOT write complete files ready to copy-paste unless explicitly asked
- When the developer is stuck, guide with hints before giving the solution
- Keep explanations in **French** (developer's language), code and comments in **English**

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask (Application Factory pattern) |
| Geographic data | GeoPandas + Shapely + rtree |
| Map rendering | Leaflet.js (direct, NOT Folium for live updates) |
| Calendar conversion | convertdate, hijri-converter, jdatetime, pyluach |
| Partial UI updates | HTMX (sidebars only, not the map) |
| Caching | flask-caching (SimpleCache dev / Redis prod) |
| Production server | Gunicorn + Nginx |
| Containerization | Docker multi-stage + docker-compose |
| Package manager | Poetry |

## Project Structure (target)

```
├── app.py              # create_app() factory
├── config.py           # Dev/Prod/Test configs
├── calendars/          # Calendar conversion engine
├── maps/               # Geographic data engine
├── api/                # Flask Blueprints (REST API)
├── data/               # GeoJSON files + calendar data
├── static/             # CSS, JS, vendor assets
├── templates/          # Jinja2 HTML templates
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Current Development Phase

See full plan at: `~/.claude/plans/tender-cooking-crayon.md`

Phases:
- [x] **Phase 0** — Fix existing bugs, learn Flask Application Factory pattern
- [x] **Phase 1** — Contemporary map via REST API, learn GeoPandas + Leaflet.js
  - [x] Dependencies: flask-caching, flask-compress, orjson
  - [x] Data: `ne_110m_admin_0_countries.geojson` in `data/geojson/raw/`
  - [x] `maps/loader.py`: `load_geojson()` working
  - [x] `api/borders.py`: Blueprint `borders_bp` + `GET /api/borders` → GeoJSON 200 OK
  - [x] `app.py`: Blueprint registered under `/api`
  - [x] `create_app()`: init `flask-caching` + `flask-compress`
  - [x] `static/js/map.js`: Leaflet init + fetch `/api/borders`
  - [x] `templates/index.html`: extract inline JS
- [ ] Phase 2 — Calendar conversion engine, learn ABC pattern + calendar libraries
- [ ] Phase 3 — Timeline slider + dynamic historical borders
- [ ] Phase 4 — Calendar labels overlay on map, learn HTMX
- [ ] Phase 5 — CShapes day-level precision data (1886+)
- [ ] Phase 6 — Docker production deployment

## Historical Data Sources

- **CShapes 2.0**: 1886–2019, day-level precision (CC BY 4.0) — icr.ethz.ch/data/cshapes/
- **aourednik/historical-basemaps**: –3000 to 2000 CE, snapshots (CC BY-SA 4.0)
- **Natural Earth**: contemporary base map (public domain) — naturalearthdata.com
- **AWMC**: Greco-Roman antiquity (CC BY)

## Key Technical Decisions

1. **Leaflet.js directly, not Folium** — Folium regenerates full HTML on every call; Leaflet updates layers in-place
2. **Application Factory pattern** — Allows dev/test/prod configs and Blueprint registration
3. **GeoJSON geometry simplification** — Mandatory: raw files are 20–50 MB; simplify server-side by zoom level
4. **Integer year for BCE** — JS `Date` is unreliable before 100 CE; slider uses a plain integer
5. **Hijri fallback** — `hijri-converter` (Umm al-Qura) covers only 1937–2077; use `convertdate.islamic` for older dates

## Running the Project

```bash
# Development
poetry install
flask run --debug

# Tests
pytest

# Production
docker-compose up
```

