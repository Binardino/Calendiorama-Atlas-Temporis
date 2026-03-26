from maps.loader import load_geojson
import json
import orjson
from flask import Blueprint, current_app as app
from pathlib import Path
from app import cache

borders_bp = Blueprint('borders', __name__)

@borders_bp.route('/borders')
@cache.cached(timeout=3600)
def get_borders():
    try:
        borders_gdf = load_geojson(Path("raw/ne_110m_admin_0_countries.geojson"))
        geojson_dict = json.loads(borders_gdf.to_json())

    except Exception as e:
        app.logger.error(f"Error loading borders: {e}")
        return app.response_class(orjson.dumps({"error": "Could not load borders"}), mimetype='application/json', status=500)

    return app.response_class(orjson.dumps(geojson_dict), mimetype='application/json')
