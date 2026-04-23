# Changelog

All notable changes to Calendiorama Atlas Temporis are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — Phase 9: Historical State Labels

### Added
- `static/js/map.js`: `stateLabelsLayer` + `buildStateLabels()` — displays entity name (empire/kingdom/state) centered on each polygon
  - Font size scales with zoom level (`zoom * 2 + 2`, min 8px)
  - Polygon pixel-size filter via `latLngToContainerPoint` (threshold 50px largest dimension) — fewer labels at world scale, more as user zooms in
  - Centering via `iconSize/iconAnchor: [0,0]` + inner div `transform: translate(-50%, -50%)`
  - Hidden below zoom 3; suppressed for year > 2000 (basemap already labels contemporary states)
  - `Aa` toggle button (`#state-labels-toggle`) to show/hide labels, persists across year changes
- `static/css/style.css`: `.state-label` class (white 4-direction halo, `var(--text-color)` for dark/light mode); `#state-labels-toggle` button positioned below theme toggle; `.toggle-off` opacity dimming
- `templates/index.html`: `Aa` toggle button

### Changed
- `maps/loader.py`: normalized `label` field in all three sources (aourednik `NAME`, CShapes `cntry_name`, Natural Earth `NAME`); `label` added to `load_cshapes()` return columns

---

## [0.7.0] — Phase 7: UX Improvements

### Added
- `static/css/style.css`: all CSS extracted from inline `<style>` in `index.html` → external file served by Nginx cache
- Dark/light mode toggle: `#theme-toggle` button (top-left, next to zoom controls); CSS custom properties (`--bg-panel`, `--text-color`, `--accent`, `--slider-track`, `--tick-color`); CartoDB `dark_all` tile layer swapped on toggle

### Changed
- `templates/index.html`: timeline restructured — `#timeline-wrapper` (flex column), `#ticks` (JS-generated markers), `#year-tooltip` (follows slider thumb); calendar legend moved to top-left below zoom controls
- `static/js/map.js`: `buildTicks()` generates BCE millennium + CE century markers; `updateTooltip()` positions year badge above slider thumb with thumb-width correction; `yearLabel` → `yearTooltip`; tile layer swap on dark mode toggle

---

## [0.6.0] — Phase 6: Docker Production Deployment

### Added
- `Dockerfile`: multi-stage build — Poetry builder stage + Gunicorn runtime stage
- `docker-compose.yml`: three services (web, redis:7-alpine, nginx:alpine) with read-only volume mounts for gitignored data
- `nginx/nginx.conf`: reverse proxy to Gunicorn, serves `/static/` directly with 1h cache
- `.env.example`: template for `SECRET_KEY`, `REDIS_URL`, `FLASK_ENV`
- `.dockerignore`: excludes historical GeoJSON, CShapes, tests, `.git`, `.venv` from build context

---

## [0.5.0] — Phase 5: CShapes Integration

### Added
- `scripts/generate_gwcode_iso.py`: one-shot script — spatial join CShapes capitals × Natural Earth + 33 manual overrides → `gwcode_iso.json`
- `data/calendars/gwcode_iso.json`: mapping gwcode (int) → ISO alpha-2 for all 252 CShapes countries
- `data/geojson/cshapes/`: CShapes 2.0 data (GeoJSON + Shapefile), gitignored — CC BY 4.0, ETH Zurich
- `maps/loader.py`: `load_cshapes(target_date)` — filters CShapes by date-range (gwsyear/gwsmonth/gwsday fields), adds ISO_A2 from gwcode_iso.json
- `templates/index.html`: `<input type="date" id="date-input">` alongside the year slider
- `static/js/map.js`: `updateBorders(year, month, day)`, `updateCalendarOverlay(year, month, day)`, bidirectional slider↔date sync, BCE label via type="text" switch

### Changed
- `api/borders.py`: three-source routing — aourednik (< 1886) / CShapes (1886–2019) / Natural Earth (> 2019); added `month` and `day` query params (default June 15)
- `api/calendars.py`: `/calendars/overlay` accepts `month` and `day` params; June 15 hardcode removed

### Fixed
- `static/js/map.js`: year zero-padded to 4 digits for `<input type="date">` (browser rejects years < 4 digits)
- `static/js/map.js`: BCE years switch input to `type="text"` and display "BCE N" instead of empty placeholder

### Architecture
- Three-source pipeline: aourednik (< 1886) / CShapes (1886–2019) / Natural Earth (> 2019)
- Future snapshots before 1886: use aourednik format (one GeoJSON file per year, auto-detected by `get_available_years()`)
- CShapes gwcode↔ISO mapping: 226/252 via spatial join, 33 manual overrides for small islands and NE "-99" territories

---

## [0.4.0] — Phase 4: Calendar Overlay on Map

---

### Added
- `calendars/dispatcher.py`: `_CALENDAR_PRIORITY` dict + `get_primary_calendar(region_id, jdn)` → `tuple[str, CalendarDate]` (internal key + date)
- `api/calendars.py`: `GET /api/calendars/panel` (HTMX HTML fragment) + `GET /api/calendars/overlay?year=<int>` (JSON per-country calendar data)
- `templates/partials/calendar_panel.html`: Jinja2 fragment injected by HTMX on country click
- `static/js/map.js`: `CALENDAR_COLORS` dict, `labelsLayer` (L.layerGroup), `rebuildLabels()`, `updateCalendarOverlay()`, zoom handler, CartoDB Positron basemap
- `templates/index.html`: calendar legend (8 systems), `.calendar-label` CSS with white text-shadow halo, `.cal-*` color classes, HTMX CDN

### Changed
- `static/js/map.js`: basemap switched from OSM to CartoDB Positron (better contrast for overlay colors)
- `static/js/map.js`: `updateBorders()` chains `updateCalendarOverlay()` after `addData()`

### Fixed
- `templates/index.html`: missing `}` on `#calendar-panel` caused `.calendar-label` CSS to be nested inside (browser ignored all label styles)
- `api/calendars.py`: `from convertdate import gregorian` (not `from calendars import gregorian`) — wrong module import
- `calendars/dispatcher.py`: `get_primary_calendar()` now returns `(internal_key, CalendarDate)` tuple — avoids JS name-mismatch (`"Islamic"` vs `"hijri"`) that caused all countries to fall back to default blue

### Key Notes
- Calendar overlay active only for `year > 2010` (Natural Earth has `ISO_A2`; aourednik historical GeoJSON does not)
- Labels hidden below zoom level 4 to avoid overlap at world view
- `get_primary_calendar()` returns internal key (`hijri`, `persian`…) matching JS `CALENDAR_COLORS` dict, not display name (`Islamic`, `Persian`…)
- Mid-year JDN: `gregorian.to_jd(year, 6, 15)` used as representative date — dynamic in Phase 5

---

## [0.3.0] — Phase 3: Historical Borders Timeline

### Added
- `maps/loader.py`: `get_available_years()` — scans `data/geojson/historical/`, parses `world_bc<N>.geojson` → negative int and `world_<N>.geojson` → positive int, returns sorted list
- `maps/loader.py`: `find_nearest_year(year, available)` — returns largest available snapshot year ≤ requested year (no future prediction)
- `templates/index.html`: `<input type="range">` timeline slider (−3000 to 2010 CE) with BCE/CE label overlay
- `static/js/map.js`: `formatYear(year)` — formats signed integer as "500 BCE" / "Year 0" / "2010 CE"
- `static/js/map.js`: slider `input` event listener with 300ms debounce to avoid flooding the API while dragging
- `README.md`: Data Sources section with GPL v3 attribution for aourednik/historical-basemaps

### Changed
- `api/borders.py`: `GET /api/borders?year=<int>` — optional `year` param routes to historical snapshot; absent → Natural Earth contemporary data
- `api/borders.py`: cache decorator updated to `query_string=True` so each `?year=X` is cached independently
- `static/js/map.js`: `updateBorders(year)` now accepts integer year and builds `?year=` query param
- `maps/loader.py`: added docstrings to all three functions

### Data
- `data/geojson/historical/world_*.geojson`: 51 snapshots from aourednik/historical-basemaps (−123000 to 2010 CE), gitignored — GPL v3, author Alexandre Ourednik

---

## [0.2.0] — Phase 2: Calendar Conversion Engine

### Added
- `calendars/base.py`: `CalendarDate` dataclass + `CalendarConverter` ABC
- `calendars/gregorian.py`: Gregorian calendar converter (stdlib `datetime`)
- `calendars/julian.py`: Julian calendar converter (`convertdate.julian`)
- `calendars/coptic.py`: Coptic calendar converter (`convertdate.coptic`)
- `calendars/ethiopian.py`: Ethiopian calendar converter (via Coptic + 276-year epoch offset)
- `calendars/hijri.py`: Hijri/Islamic calendar (Umm al-Qura via `hijridate` + tabular fallback via `convertdate.islamic`)
- `calendars/hebrew.py`: Hebrew calendar converter (`pyluach`, Nisan-based month numbering)
- `calendars/persian.py`: Persian/Jalali calendar converter (`convertdate.persian`)
- `calendars/japanese.py`: Japanese Imperial calendar converter (JSON era lookup, 248 eras, UTF-8)
- `calendars/dispatcher.py`: `get_calendars(region, jdn)` routing by ISO country code
- `calendars/__init__.py`: exports all 8 converters
- `data/calendars/japanese_eras.json`: 248 Japanese imperial eras from Taika (645 CE) to Reiwa (2019–present)
- `data/calendars/region_calendar_map.json`: 195+ ISO country → applicable calendar list mapping
- `api/calendars.py`: Blueprint + `GET /api/calendars?date=YYYY-MM-DD&region=ISO`
- Unit tests for all 8 converters + dispatcher (`tests/calendars/`)

### Changed
- `app.py`: registered `calendars_bp` Blueprint under `/api`
- `api/borders.py`: added docstring documenting endpoint, cache, and compression behaviour
- `api/calendars.py`: accepts `?date=YYYY-MM-DD` (ISO string) instead of raw `?jdn=<int>`
- `calendars/dispatcher.py`: switched from relative to absolute path for `region_calendar_map.json`
- `calendars/japanese.py`: switched from relative to absolute path + explicit `encoding='utf-8'` for era file
- `.gitignore`: added `data/geojson/historical/` for Phase 3 data

### Dependencies added
- `convertdate >= 2.4` — Julian, Coptic, Islamic tabular calendars
- `hijridate >= 2.3` — Umm al-Qura calendar (replaces deprecated `hijri-converter`)
- `jdatetime >= 4.1` — Persian/Jalali calendar
- `pyluach >= 1.2` — Hebrew calendar

---

## [0.1.0] — Phase 1: Contemporary Map

### Added
- Flask Application Factory pattern (`create_app()` in `app.py`)
- `maps/loader.py`: `load_geojson()` loading GeoJSON via GeoPandas
- `api/borders.py`: Blueprint + `GET /api/borders` returning Natural Earth 110m GeoJSON
- `static/js/map.js`: Leaflet.js map initialisation + border GeoJSON layer
- `templates/index.html`: Leaflet CDN + map container, external JS reference
- `flask-caching` — in-memory cache (dev) / Redis (prod), 1h TTL on borders
- `flask-compress` — gzip compression (~80% size reduction on GeoJSON responses)
- `orjson` — fast JSON serialisation for API responses

---

## [0.0.1] — Phase 0: Project Bootstrap

### Added
- Flask Application Factory (`app.py`, `config.py` with Dev/Test/Prod configs)
- Poetry project setup (`pyproject.toml`, `package-mode = false`)
- Base project structure: `api/`, `maps/`, `calendars/`, `data/`, `static/`, `templates/`
