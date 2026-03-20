Plan: Calendiorama-Atlas-Temporis — Interactive Historical World Map
Context
Interactive Python web application displaying a dynamic world map with a chronological timeline. For any selected date, the map shows:

Historical borders of that era
Local calendar dates per region (Gregorian, Hijri, Hebrew, Persian, Japanese Imperial, Julian, Coptic, Ethiopian…)
Developer profile: Advanced Python, experienced with Docker. Flask, GeoPandas, and Leaflet.js to learn. Working style: Code together step by step, with concept explanations before writing code.

What Was Missing From the Initial Plan
Need	Chosen Solution
Calendar conversion libraries	convertdate, hijri-converter, jdatetime, pyluach
Historical border data sources	CShapes 2.0 (1886–present) + aourednik/historical-basemaps (–3000 to 2000)
Fast dynamic map rendering	Direct Leaflet.js (not Folium: too slow for live updates)
Partial UI updates	HTMX for info panels (not for the map itself)
GeoJSON response caching	flask-caching (SimpleCache dev / Redis prod)
Large GeoJSON compression	flask-compress (gzip)
Production server	Gunicorn behind Nginx
BCE date handling in JS	Integer year slider, not JS Date object
Spatial queries (point-in-polygon)	rtree via GeoPandas
Full Technology Stack
Python Backend
# To add in pyproject.toml
convertdate     = ">=2.4"    # Julian, Coptic, Ethiopian, Islamic tabular
hijri-converter = ">=2.3"    # Islamic Hijri Umm al-Qura (high precision, 1356–1500 AH)
jdatetime       = ">=4.1"    # Persian/Jalali Solar Hijri (mirrors datetime API)
pyluach         = ">=1.4"    # Hebrew calendar (exact for all dates)
flask-caching   = ">=2.3"    # Cache (SimpleCache or Redis)
flask-compress  = ">=1.14"   # Gzip compression for GeoJSON responses
gunicorn        = ">=22.0"   # Production WSGI server
orjson          = ">=3.9"    # Fast JSON serialization (10× stdlib) for GeoJSON
rtree           = ">=1.2"    # R-tree spatial index
Frontend (static files, no Python dependencies)
Leaflet.js vendored in static/vendor/leaflet/
HTMX for sidebar panel updates (no custom JS needed for this)
Vanilla JS only for the timeline slider and Leaflet layer management
Target Project Structure
calendiorama-atlas-temporis/
├── CLAUDE.md                       # Claude Code instructions for this project
├── app.py                          # create_app() factory + blueprint registration
├── config.py                       # DevelopmentConfig / ProductionConfig
├── Dockerfile                      # Multi-stage, GDAL-capable base
├── docker-compose.yml              # Prod: web + redis + nginx
├── docker-compose.dev.yml          # Dev override: Flask debug, no Redis
├── .env.example
├── pyproject.toml
│
├── calendars/
│   ├── base.py                     # CalendarDate dataclass + CalendarConverter ABC
│   ├── gregorian.py
│   ├── julian.py
│   ├── hijri.py                    # hijri-converter + convertdate fallback
│   ├── hebrew.py                   # pyluach
│   ├── persian.py                  # jdatetime
│   ├── japanese.py                 # JSON lookup table
│   ├── coptic.py                   # convertdate
│   ├── ethiopian.py                # convertdate
│   ├── dispatcher.py               # Region + date → list of converters
│   └── tests/
│
├── maps/
│   ├── loader.py                   # GeoJSON loading + temporal index
│   ├── renderer.py                 # GeoJSON assembly for API + simplification
│   ├── borders.py                  # "Borders for a given date" query
│   └── spatial_index.py
│
├── api/
│   ├── borders.py                  # GET /api/borders
│   ├── calendars.py                # GET /api/calendars
│   └── timeline.py                 # GET /api/timeline/metadata
│
├── data/
│   ├── geojson/
│   │   ├── raw/                    # Downloaded raw data (gitignored)
│   │   ├── processed/              # Normalized GeoJSON by era (committed)
│   │   └── index.json              # Temporal manifest
│   ├── calendars/
│   │   ├── japanese_eras.json
│   │   ├── gregorian_adoption.json
│   │   └── region_calendar_map.json
│   └── scripts/
│       ├── download_data.py
│       ├── process_cshapes.py
│       ├── process_aourednik.py
│       └── build_index.py
│
├── static/
│   ├── css/
│   ├── js/
│   │   ├── map.js
│   │   ├── timeline.js
│   │   └── calendar_labels.js
│   └── vendor/                     # Leaflet.js + HTMX (pinned versions)
│
└── templates/
    ├── base.html
    ├── index.html
    └── components/
        ├── timeline.html
        ├── region_info.html
        └── calendar_popup.html
Development Phases (Detailed)
Phase 0 — Fix the Base and Learn Flask (1–2 days)
What you'll learn:

How Flask works: routes, Jinja2 templates, context variables
The Application Factory pattern (create_app()): why it's essential for testing and deployment
Flask Blueprints: how to organize code into modules
Why this pattern? Flask can work with a simple global app = Flask(__name__), but this is an anti-pattern for non-trivial projects. The create_app() factory lets you instantiate the app with different configs (dev/test/prod) and register blueprints cleanly. You'll see this pattern in every serious Flask project.

Files to work on:

app.py — full refactor
config.py — create from scratch
templates/index.html — rebuild from scratch
maps/loader.py — fix quote mismatch bug
Step-by-step:

Create config.py with DevelopmentConfig / ProductionConfig classes
Refactor app.py: transform into create_app(config_name) factory that returns the app
Fix the 4 bugs in app.py (detailed below)
Rebuild templates/index.html: valid HTML, Leaflet.js loaded directly (not via Folium), full-screen #map div
Create templates/base.html with common layout (head, scripts, body)
Bugs to fix in app.py:

Line ~22: m.get_root().__repr_html__() → m._repr_html_()
Line ~42: if __name__ = '__main__': → if __name__ == '__main__':
Line ~43: missing indentation under the if
Orphan def index() with no @app.route: remove or fix
Template variable mismatch: annee_actuelle in HTML but current_year in Python → unify
Flask concepts to understand before coding:

# Simple route
@app.route('/')
def home():
    return render_template('index.html', variable=value)

# Application factory
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from api.borders import borders_bp
    app.register_blueprint(borders_bp, url_prefix='/api')

    return app

# Blueprint (in api/borders.py)
borders_bp = Blueprint('borders', __name__)

@borders_bp.route('/borders')
def get_borders():
    return jsonify({...})
Milestone: flask run → http://localhost:5000/ shows a #map div without JavaScript errors.

Phase 1 — Contemporary Map via API (1 week)
What you'll learn:

GeoPandas: read a GeoJSON file, filter, access geometries
How to serve GeoJSON from Flask
Leaflet.js fundamentals: initialize a map, add a GeoJSON layer, style polygons
REST API pattern: why separating data (API) from HTML (views) matters
Why Leaflet.js and not Folium? Folium generates a complete, self-contained HTML document on every call — you can't update just the borders without regenerating the whole page. Leaflet.js runs in the browser: it keeps the map in memory and you can add/remove layers on the fly via JavaScript. This is essential for a responsive timeline slider.

Files to work on:

maps/loader.py — implement load_geojson()
api/ — create module + api/borders.py
static/js/map.js — Leaflet init + API fetch
pyproject.toml — add flask-caching, flask-compress
Steps:

Download Natural Earth ne_110m_admin_0_countries.geojson (contemporary borders, ~500 KB)
Implement maps/loader.py: function load_geojson(path: Path) -> gpd.GeoDataFrame
Create api/__init__.py and api/borders.py with borders_bp
Implement GET /api/borders: load GeoJSON via GeoPandas, return via orjson (ignore date param for now)
Add flask-caching (SimpleCache) and flask-compress in create_app()
Write static/js/map.js: init Leaflet centered on (20, 0) zoom 2, fetch the API, add L.geoJSON() layer
GeoPandas concepts to understand:

import geopandas as gpd

gdf = gpd.read_file('data/geojson/world.geojson')
# gdf is a DataFrame with a special 'geometry' column
print(gdf.columns)  # ['name', 'iso_a3', 'pop_est', ..., 'geometry']
print(gdf.crs)      # EPSG:4326 (standard lat/lon)

# Filter like any Pandas DataFrame
france = gdf[gdf['iso_a3'] == 'FRA']

# Simplify geometries (reduce size)
gdf['geometry'] = gdf.geometry.simplify(0.01, preserve_topology=True)

# Convert to GeoJSON string
geojson_string = gdf.to_json()
Leaflet.js concepts to understand (in map.js):

const map = L.map('map').setView([20, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

const bordersLayer = L.geoJSON(null, {
    style: { color: '#ffffff', weight: 1, fillColor: '#3388ff', fillOpacity: 0.3 }
}).addTo(map);

function updateBorders(date) {
    fetch(`/api/borders?date=${date}`)
        .then(r => r.json())
        .then(geojson => {
            bordersLayer.clearLayers();
            bordersLayer.addData(geojson);
        });
}
updateBorders('2024-01-01');
Milestone: Contemporary world map with national borders in the browser.

Phase 2 — Calendar Engine (1 week)
What you'll learn:

Python abstract classes (ABC, @abstractmethod) to define an interface
Python dataclasses for clean data structures
Using 4 calendar conversion libraries
Handling temporal edge cases (calendar transitions, historical limits)
Why an abstract class here? You'll have ~8 calendar converters that all do the same thing: take a Gregorian date and return a CalendarDate. The ABC forces each converter to implement from_gregorian() and to_gregorian(). The dispatcher.py can then handle any converter uniformly without knowing which one it is.

Files to work on:

calendars/base.py — create
calendars/gregorian.py, hijri.py, hebrew.py, persian.py, japanese.py — create
calendars/dispatcher.py — create
data/calendars/japanese_eras.json — create
data/calendars/region_calendar_map.json — create
data/calendars/gregorian_adoption.json — create
api/calendars.py — create
Steps:

Write calendars/base.py: CalendarDate dataclass + CalendarConverter ABC
Write calendars/gregorian.py: pass-through (Gregorian = internal reference)
Create data/calendars/japanese_eras.json with Meiji→Reiwa eras
Write converters in increasing order of complexity: persian.py → hebrew.py → hijri.py → japanese.py
Write the three JSON data files
Write calendars/dispatcher.py
Write api/calendars.py and register it in create_app()
Write unit tests with known historical test vectors
Test vectors to implement:

# 24 October 1648 (Peace of Westphalia)
assert hijri.from_gregorian(date(1648, 10, 24)).display_label == "17 Muharram 1059 AH"

# 1 January 2024
assert hebrew.from_gregorian(date(2024, 1, 1)).display_label == "10 Tevet 5784"
assert persian.from_gregorian(date(2024, 1, 1)).display_label == "11 Dey 1402"
assert japanese.from_gregorian(date(2024, 1, 1)).display_label == "Reiwa 6, January 1"

# Russia before Gregorian reform (14 Feb 1918 NS = 1 Feb 1918 OS/Julian)
assert julian.from_gregorian(date(1918, 2, 14)).day == 1
Milestone: GET /api/calendars?date=1648-10-24&region_id=IR returns the correct Persian date.

Phase 3 — Timeline Slider + Dynamic Borders (2 weeks)
What you'll learn:

Advanced GeoPandas: temporal filtering on GeoDataFrames, adaptive simplification
Building a temporal index in Python (efficient data structure)
JavaScript: <input type="range"> + debounce + fetch API
"Partial update" pattern: change only the Leaflet layer without reloading the page
Files to work on:

data/scripts/process_aourednik.py — create
data/scripts/build_index.py — create
maps/borders.py — create
static/js/timeline.js — create
templates/components/timeline.html — create
Normalized GeoJSON schema (required properties):

{
  "properties": {
    "region_id": "FR",
    "region_name": "Kingdom of France",
    "valid_from": "1648-10-24",
    "valid_until": "1789-07-14",
    "calendar_primary": "gregorian",
    "data_source": "aourednik",
    "confidence": "snapshot"
  }
}
Timeline slider (debounce pattern):

const slider = document.getElementById('timeline-slider');
let debounceTimer;
slider.addEventListener('input', () => {
    document.getElementById('year-display').textContent = slider.value;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => updateBorders(slider.value), 300);
});
Milestone: Dragging the timeline shows different historical borders (snapshot-based).

Phase 4 — Calendar Labels on the Map (1 week)
What you'll learn:

Advanced Leaflet.js: L.divIcon, tooltips, click events on layers
HTMX: partial DOM updates without custom JavaScript
GeoPandas: centroid calculation (gdf.centroid)
Milestone: Clicking on Iran shows "4 Aban 1027 (Persian Calendar)" in the side panel.

Phase 5 — CShapes Data (Day-Level Precision, 1886+) (2 weeks)
What you'll learn:

Shapefile manipulation with GeoPandas
R-tree spatial index for performant geographic queries
Cache strategies and warm-up on startup
Milestone: Borders on 11 November 1918 (armistice) differ from 10 November.

Phase 6 — Docker + Production (1 week)
What you'll learn:

Multi-stage Docker build: why two stages (builder + runtime) for a lean image
Gunicorn: workers, timeout, Flask configuration
Nginx: reverse proxy, compression, static file serving
Dockerfile structure:

FROM python:3.11-slim AS builder
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8 AS runtime
COPY --from=builder /requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:create_app()"]
Milestone: docker-compose up → application accessible at http://localhost:80/.

Historical Data Sources
Source	Coverage	License	URL
CShapes 2.0 (ETH Zurich)	1886–2019, day-level precision	CC BY 4.0	icr.ethz.ch/data/cshapes/
aourednik/historical-basemaps	–3000 to 2000 CE, ~100-year snapshots	CC BY-SA 4.0	github.com/aourednik/historical-basemaps
Natural Earth	Contemporary (base map)	Public domain	naturalearthdata.com
AWMC	Greco-Roman antiquity	CC BY	awmc.unc.edu/awmc/map_data/
Key Technical Challenges
BCE dates in JavaScript — Date object unreliable before 100 CE. Use integer year on slider.
Historical Hijri accuracy — hijri-converter only covers 1937–2077. Older dates: fall back to convertdate.islamic (tabular, ±1–2 days). Document this limitation in UI.
aourednik data quality — Some malformed polygons. Load per-feature in try/except, log errors without crashing.
GeoJSON response size — Full-resolution world GeoJSON = 20–50 MB. Server-side simplification is mandatory. Frontend passes current zoom → tolerance (zoom 2 → 0.5°, zoom 6 → 0.05°).
Gregorian reform by country — Each country adopted Gregorian on a different date. gregorian_adoption.json must be comprehensive.
Antimeridian crossing — Russia, Alaska, Pacific islands. Use leaflet-antimeridian plugin or preprocess with Shapely.
Development Order
Phase 0 (Flask basics)
    ↓
Phase 1 (contemporary map) ←→ Phase 2 (calendars) — independent, parallelizable
    ↓                               ↓
        Phase 3 (timeline + dynamic borders)
                    ↓
        Phase 4 (calendar labels on map)
                    ↓
        Phase 5 (CShapes day-level precision)
                    ↓
        Phase 6 (Docker production)
End-to-End Verification
pytest calendars/tests/ — historical test vectors for each calendar system
pytest tests/test_api_*.py — test endpoints with known dates
Manual UI test:
Drag timeline to 1914 → verify Austria-Hungary appears (disappears after 1918)
Click Iran on 01/01/1979 → "10 Dey 1357 (Persian)"
Click Israel on 05/06/1967 → correct Hebrew date
docker-compose up → access at http://localhost:80/