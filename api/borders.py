from maps.loader import load_geojson
import json
import orjson
from flask import Blueprint, current_app as app
from pathlib import Path
from app import cache

# Blueprint groups all /borders routes under a single registrable unit.
# Registered in create_app() with url_prefix='/api' → final path: /api/borders
borders_bp = Blueprint('borders', __name__)


@borders_bp.route('/borders')
@cache.cached(timeout=3600)
def get_borders():
    """
    GET /api/borders

    Returns the GeoJSON FeatureCollection of contemporary country borders
    (Natural Earth 110m dataset).

    Response (200): GeoJSON FeatureCollection (application/json)
    Response (500): loading or serialization error

    The result is cached for 1 hour (flask-caching SimpleCache).
    flask-compress automatically gzip-encodes the response for capable clients,
    reducing transfer size by ~80% on large GeoJSON payloads.
    """
    try:
        borders_gdf  = load_geojson(Path("raw/ne_110m_admin_0_countries.geojson"))
        # geopandas .to_json() returns a GeoJSON string; json.loads() converts it
        # to a Python dict so orjson can re-serialize it faster than stdlib json.
        geojson_dict = json.loads(borders_gdf.to_json())

    except Exception as e:
        app.logger.error(f"Error loading borders: {e}")
        return app.response_class(orjson.dumps({"error": "Could not load borders"}),
                                  mimetype='application/json',
                                  status=500)

    return app.response_class(orjson.dumps(geojson_dict), mimetype='application/json')
