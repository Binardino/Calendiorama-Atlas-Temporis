# Changelog

All notable changes to Calendiorama Atlas Temporis are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — Phase 3: Historical Borders Timeline

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
