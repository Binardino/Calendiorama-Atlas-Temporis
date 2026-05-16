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

### Coding Guidelines (Karpathy Principles)

**Think Before Coding** — Don't assume. Don't hide confusion. Surface tradeoffs.
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.

**Simplicity First** — Minimum code that solves the problem. Nothing speculative.
- No features beyond what was asked.
- No abstractions for single-use code.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

**Surgical Changes** — Touch only what you must. Clean up only your own mess.
- Don't "improve" adjacent code, comments, or formatting.
- Match existing style, even if you'd do it differently.
- Every changed line should trace directly to the user's request.

**Goal-Driven Execution** — Define success criteria. Loop until verified.
- Transform tasks into verifiable goals before starting.
- For multi-step tasks, state a brief plan with explicit verification steps.

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

See full plan at: `~/.claude/plans/structured-wondering-eclipse.md`

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
- [x] **Phase 2** — Calendar conversion engine, learn ABC pattern + calendar libraries
  - [x] Dependencies: convertdate, hijridate, jdatetime, pyluach
  - [x] `calendars/base.py`: `CalendarDate` dataclass + `CalendarConverter` ABC
  - [x] `calendars/gregorian.py`: GregorianCalendar converter + tests
  - [x] `calendars/julian.py`: JulianCalendar converter + tests
  - [x] `calendars/coptic.py`: CopticCalendar converter + tests
  - [x] `calendars/ethiopian.py`: EthiopianCalendar converter + tests (via convertdate.coptic + year offset +276)
  - [x] `calendars/hijri.py`: HijriCalendar converter + tests (Umm al-Qura + tabular fallback)
  - [x] `calendars/hebrew.py`: HebrewCalendar converter + tests (pyluach, Nisan-based month numbering)
  - [x] `calendars/persian.py`: PersianCalendar converter + tests
  - [x] `calendars/japanese.py`: JapaneseCalendar converter + tests (JSON era lookup, 248 eras)
  - [x] `calendars/dispatcher.py`: `get_calendars(iso_region, jdn)` with absolute path
  - [x] `data/calendars/japanese_eras.json` + `region_calendar_map.json`
  - [x] `api/calendars.py`: Blueprint + `GET /api/calendars?date=YYYY-MM-DD&region=ISO`
  - [x] `tests/calendars/`: unit tests for all 8 converters + dispatcher
- [x] **Phase 3** — Timeline slider + dynamic historical borders
  - [x] Data: `aourednik/historical-basemaps` GeoJSON in `data/geojson/historical/` (gitignored, GPL v3)
  - [x] `maps/loader.py`: `get_available_years()` + `find_nearest_year(year, available)`
  - [x] `api/borders.py`: `GET /api/borders?year=<int>` with `query_string=True` cache
  - [x] `templates/index.html`: `<input type="range">` slider + year label
  - [x] `static/js/map.js`: slider event listener + `updateBorders(year)` + 300ms debounce
- [x] **Phase 4** — Calendar overlay on map + HTMX panel on country click
  - [x] `calendars/dispatcher.py`: `_CALENDAR_PRIORITY` dict + `get_primary_calendar(region_id, jdn)` → `(key, CalendarDate)`
  - [x] `api/calendars.py`: `GET /api/calendars/panel` (HTML fragment via HTMX) + `GET /api/calendars/overlay?year=<int>`
  - [x] `templates/partials/calendar_panel.html`: Jinja2 fragment for HTMX injection
  - [x] `static/js/map.js`: `CALENDAR_COLORS`, `labelsLayer`, `rebuildLabels()`, `updateCalendarOverlay()`, zoom handler, CartoDB Positron basemap
  - [x] `templates/index.html`: calendar legend, `.calendar-label` CSS, `.cal-*` color classes, HTMX CDN
  - [x] Key fix: `get_primary_calendar()` returns internal key (`hijri`) not display name (`Islamic`) — avoids JS name mapping
  - [x] Labels hidden below zoom 4 to avoid overlap
  - [x] Overlay only active for year > 2010 (Natural Earth has ISO_A2; aourednik does not)
- [x] **Phase 5** — CShapes day-level precision data (1886+)
  - [x] `scripts/generate_gwcode_iso.py` + `data/calendars/gwcode_iso.json` (252 entries, spatial join + 33 manual overrides)
  - [x] `maps/loader.py`: `load_cshapes(target_date)` with date-range filter and gwcode→ISO mapping
  - [x] `api/borders.py`: three-source routing (aourednik / CShapes / Natural Earth), `month`+`day` params
  - [x] `api/calendars.py`: overlay accepts `month`+`day`, June 15 hardcode removed
  - [x] `templates/index.html` + `static/js/map.js`: `<input type="date">`, bidirectional slider↔date sync, BCE label
- [x] **Phase 6** — Docker production deployment
  - [x] `Dockerfile`: multi-stage (Poetry builder → Gunicorn runtime)
  - [x] `docker-compose.yml`: web + redis + nginx
  - [x] `nginx/nginx.conf`: reverse proxy + static files
  - [x] `.env.example`: SECRET_KEY, REDIS_URL, FLASK_ENV
  - [x] `.dockerignore`: excludes historical GeoJSON, CShapes, tests, .git from build context
- [x] **Phase 7** — UX improvements
  - [x] `templates/index.html` + `static/js/map.js`: wider timeline bar, century/millennium tick marks, year tooltip on slider thumb
  - [x] Calendar legend moved to top-left (below zoom controls)
  - [x] Dark/light mode toggle — `#theme-toggle` button (top-left next to zoom), CSS variables (`--bg-panel`, `--accent`, `--tick-color`…), CartoDB dark tile swap on toggle
  - [x] CSS extracted from inline `<style>` to `static/css/style.css`
- [ ] **Phase 8** — URL state persistence (deep linking)
  - [ ] `static/js/map.js`: on page load, read `URLSearchParams` — restore year, month, day, lat, lng, zoom if present
  - [ ] `static/js/map.js`: `pushUrlState(year, month, day)` helper — calls `history.replaceState()` after each `updateBorders()` call
  - [ ] `static/js/map.js`: include `map.getCenter()` + `map.getZoom()` in URL on `moveend` event
  - [ ] No backend changes — pure JS URL manipulation
  - Goal: `?year=814&month=6&day=15&lat=33.3&lng=44.4&zoom=5` opens map at exact state, shareable

- [x] **Phase 9** — Historical state labels on map
  - [x] `maps/loader.py`: normalize `label` field in all three sources (aourednik `NAME`, CShapes `cntry_name`, Natural Earth `NAME`)
  - [x] `static/js/map.js`: `stateLabelsLayer` + `buildStateLabels()` — font size scales with zoom, polygon pixel-size filter (threshold 50px), hidden below zoom 3, suppressed for year > 2000, `Aa` toggle button
  - [x] `static/css/style.css`: `.state-label` class + `#state-labels-toggle` button
  - [x] `templates/index.html`: `Aa` toggle button

- [x] **Phase 10** — Calendar graceful degradation for BCE dates
  - [x] `calendars/base.py`: add `out_of_range: bool = False` to `CalendarDate`
  - [x] Each converter: `out_of_range=True` guard — gregorian (JDN 1704987), japanese (1947154), hijri (1948439), persian (2122292), hebrew (1721426), coptic (1825030), ethiopian (1724221); julian has no guard (arithmetic native)
  - [x] `calendars/README.md`: document JDN concept, all converters, and out_of_range thresholds
  - [x] `api/calendars.py` overlay: exclude `out_of_range` entries from JSON; panel: display "— (before calendar epoch)"
  - [x] `tests/calendars/`: add BCE tests for all 8 converters

- [ ] **Phase 11** — Peters (Gall-Peters) projection toggle
  - [ ] `proj4` + `proj4leaflet` CDN in `templates/index.html`
  - [ ] `PETERS_CRS` defined in `static/js/map.js`; `initMap(crs)` factory refactor
  - [ ] `#projection-toggle` button; toggle handler destroys + recreates map with new CRS
  - [ ] `static/css/style.css`: `#map { background: #c9e8f0; }` for ocean color without tiles

- [ ] **Phase 12** — Collecte des données de calendrier (données, deux datasets)
  - [x] `scripts/list_aourednik_names.py`: scan 52 fichiers aourednik → `data/calendars/aourednik_names_raw.txt` (3027 NAMEs uniques)
  - **Dataset A** — `data/calendars/gregorian_adoption_dates.json` : pour les pays CShapes/NaturalEarth (ISO codes) qui étaient encore sur le calendrier Julien en 1886, la date exacte de bascule vers le Grégorien. Format : `{"RU": {"gregorian_from": "1918-02-14", "note": "..."}, ...}`. Périmètre : pays de tradition orthodoxe/byzantine + Chine, Turquie, Égypte. Collecté via Gemini + vérification humaine.
  - **Dataset B** — `data/calendars/aourednik_calendar_map.json` : pour les ~200–400 entités historiquement pertinentes dans les 3027 NAMEs aourednik (empires, royaumes, califats — exclure cultures archéologiques et groupes autochtones sans calendrier documenté). Format : `{"Roman Empire": "julian", "Ottoman Empire": "hijri", ...}`. Collecté via Gemini sur la base de `aourednik_names_raw.txt`.

- [ ] **Phase 13** — Extension de l'overlay calendrier (dépend de Phase 12)
  - [ ] **Étape A** — `calendars/dispatcher.py` : chargement de `gregorian_adoption_dates.json` au niveau module ; fonction `_apply_transitions(names, region_id, jdn)` qui remplace `"gregorian"` par `"julian"` si `jdn < adoption_jdn` ; appel dans `get_calendars()` et `get_primary_calendar()`
  - [ ] **Étape B** — `calendars/dispatcher.py` : chargement de `aourednik_calendar_map.json` au niveau module ; nouvelle fonction `get_primary_calendar_by_name(entity_name, jdn)` — lookup par NAME, fallback `"gregorian"`; même signature de retour que `get_primary_calendar()`
  - [ ] **Étape C** — `api/calendars.py` overlay : pour `year >= 1886`, logique existante (ISO codes) avec dispatcher JDN-aware ; pour `year < 1886`, itérer sur `_aourednik_map` et retourner JSON keyed par `entity_name`
  - [ ] **Étape D** — `static/js/map.js` : lever la garde `year > 2010` → `year > 1886` ; pour `year <= 1886`, appeler `updateCalendarOverlayByName()` qui matche sur `props.label` (NAME) au lieu de `props.ISO_A2`
  - Vérification : Russie 1900-01-01 → julien ; Russie 1920-01-01 → grégorien ; "Roman Empire" an 300 → julien ; "Ottoman Empire" 1500 → hijri

- [ ] **Phase 14** — Global Search & Geocoding
  - [ ] Add search bar (Leaflet.Control.Search or custom) to find countries/cities.
  - [ ] Integration with a geocoding API (Nominatim) or local index of historical names.
  - [ ] Update map state and calendar panel on search result selection.

- [ ] **Phase 15** — Time-Lapse & Animations
  - [ ] Add "Play" button to automatically increment year.
  - [ ] Client-side interpolation (if possible) or smooth transitions between border snapshots.
  - [ ] Exportable GIFs/Videos of border changes over a selected period.


## Historical Data Sources

- **CShapes 2.0**: 1886–2019, day-level precision (CC BY 4.0) — icr.ethz.ch/data/cshapes/
- **aourednik/historical-basemaps**: −123000 to 2010 CE, 51 snapshots (GPL v3) — github.com/aourednik/historical-basemaps
- **Natural Earth**: contemporary base map (public domain) — naturalearthdata.com
- **AWMC**: Greco-Roman antiquity (CC BY)

## Key Technical Decisions

1. **Leaflet.js directly, not Folium** — Folium regenerates full HTML on every call; Leaflet updates layers in-place
2. **Application Factory pattern** — Allows dev/test/prod configs and Blueprint registration
3. **GeoJSON geometry simplification** — Mandatory: raw files are 20–50 MB; simplify server-side by zoom level
4. **Integer year for BCE** — JS `Date` is unreliable before 100 CE; slider uses a plain integer
5. **Hijri fallback** — `hijri-converter` (Umm al-Qura) covers only 1937–2077; use `convertdate.islamic` for older dates
6. **Three-source pipeline** — aourednik (< 1886) / CShapes 1886–2019 / Natural Earth (> 2019). Future snapshots before 1886: aourednik format. Do not collapse sources.

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