from maps.loader import load_geojson, get_available_years, find_nearest_year, load_cshapes
import json
import orjson
from flask import Blueprint, request, current_app as app
from pathlib import Path
from app import cache
from datetime import date
# Blueprint groups all /borders routes under a single registrable unit.
# Registered in create_app() with url_prefix='/api' → final path: /api/borders
borders_bp = Blueprint('borders', __name__)

@borders_bp.route('/borders')
@cache.cached(timeout=3600, query_string=True)  # Cache each string for 1 hour, vary by query params
def get_borders():
    """
    GET /api/borders?year=<int>&month=<int>&day=<int>

    Returns country borders as a GeoJSON FeatureCollection for the requested date.
    Source is selected automatically by year:
      - year > 2019 or absent : Natural Earth 110m (contemporary, public domain)
      - 1886 <= year <= 2019  : CShapes 2.0 (day-level precision, CC BY 4.0)
      - year < 1886           : aourednik/historical-basemaps (year snapshots, GPL v3)

    month and day default to June 15 when omitted.

    Response (200): GeoJSON FeatureCollection (application/json)
    Response (500): loading or serialization error

    Cached 1 hour per unique (year, month, day) combination (query_string=True).
    flask-compress gzip-encodes the response, reducing transfer size by ~80%.
    """
    try:
        year  = request.args.get('year', type=int)
        # month/day default to June 15 — mid-year, avoids edge cases at year boundaries
        month = request.args.get('month', default=6, type=int)
        day   = request.args.get('day',   default=15, type=int)

        if year is None or year > 2019:
            # Contemporary borders: Natural Earth 110m (public domain)
            borders_gdf = load_geojson(Path("raw/ne_110m_admin_0_countries.geojson"))

        elif year >= 1886:
            # CShapes 2.0: day-level precision, 710 features, 1886–2019 (CC BY 4.0)
            borders_gdf = load_cshapes(date(year, month, day))

        else:
            # aourednik/historical-basemaps: year snapshots, BCE to 1886 (GPL v3)
            nearest_year = find_nearest_year(year, get_available_years())
            if nearest_year < 0:
                filename = f"historical/world_bc{abs(nearest_year)}.geojson"
            else:
                filename = f"historical/world_{nearest_year}.geojson"
            borders_gdf = load_geojson(Path(filename))

        # geopandas .to_json() returns a GeoJSON string; json.loads() converts it
        # to a Python dict so orjson can re-serialize it faster than stdlib json.
        geojson_dict = json.loads(borders_gdf.to_json())

    except Exception as e:
        app.logger.error(f"Error loading borders: {e}")
        return app.response_class(orjson.dumps({"error": "Could not load borders"}),
                                  mimetype='application/json',
                                  status=500)

    return app.response_class(orjson.dumps(geojson_dict), mimetype='application/json')
