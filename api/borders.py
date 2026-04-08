from maps.loader import load_geojson, get_available_years, find_nearest_year
import json
import orjson
from flask import Blueprint, request, current_app as app
from pathlib import Path
from app import cache
# Blueprint groups all /borders routes under a single registrable unit.
# Registered in create_app() with url_prefix='/api' → final path: /api/borders
borders_bp = Blueprint('borders', __name__)


@borders_bp.route('/borders')
@cache.cached(timeout=3600, query_string=True)  # Cache each string for 1 hour, vary by query params
def get_borders():
    """
    GET /api/borders

    Returns the GeoJSON FeatureCollection of input year country borders
    (Natural Earth 110m dataset).

    Response (200): GeoJSON FeatureCollection (application/json)
    Response (500): loading or serialization error

    The result is cached for 1 hour (flask-caching SimpleCache).
    flask-compress automatically gzip-encodes the response for capable clients,
    reducing transfer size by ~80% on large GeoJSON payloads.
    """
    try:
        year = request.args.get('year', type=int)
        if year is None:
            map_path = Path("raw/ne_110m_admin_0_countries.geojson")

        else:
            nearest_year = find_nearest_year(year, get_available_years())
            
            if nearest_year < 0:
                filename = f"historical/world_bc{abs(nearest_year)}.geojson"
            else:
                filename = f"historical/world_{nearest_year}.geojson"

            map_path     = Path(filename)

        borders_gdf  = load_geojson(map_path)
        # geopandas .to_json() returns a GeoJSON string; json.loads() converts it
        # to a Python dict so orjson can re-serialize it faster than stdlib json.
        geojson_dict = json.loads(borders_gdf.to_json())

    except Exception as e:
        app.logger.error(f"Error loading borders: {e}")
        return app.response_class(orjson.dumps({"error": "Could not load borders"}),
                                  mimetype='application/json',
                                  status=500)

    return app.response_class(orjson.dumps(geojson_dict), mimetype='application/json')
