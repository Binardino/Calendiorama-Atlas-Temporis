from datetime import date
from flask import Blueprint, request, current_app as app
from calendars import *
from calendars.dispatcher import get_calendars
import dataclasses
import orjson

# Blueprint groups all /calendars routes under a single registrable unit.
# Registered in create_app() with url_prefix='/api' → final path: /api/calendars
calendars_bp = Blueprint('calendars', __name__)


@calendars_bp.route('/calendars')
def get_calendars_endpoint():
    """
    GET /api/calendars?date=YYYY-MM-DD&region=ISO

    Returns all calendar dates applicable to the given region for the given date.

    Query params:
        date   (str) : ISO date string, e.g. "2024-01-15"
        region (str) : ISO 3166-1 alpha-2 country code, e.g. "IR", "IL", "JP"

    Response (200): JSON array of CalendarDate objects
        [{"year": ..., "month": ..., "day": ..., "calendar_name": ..., "formatted": ...}, ...]
    Response (400): missing or invalid parameters
    Response (500): internal conversion error
    """
    try:
        region     = request.args.get('region')
        # type=date.fromisoformat: Flask applies this callable to the raw string.
        # Returns None if the param is absent or if fromisoformat() raises ValueError.
        input_date = request.args.get('date', type=date.fromisoformat)

        if not region or input_date is None:
            return app.response_class(orjson.dumps({'error': 'Missing region or date'}),
                                      status=400,
                                      mimetype='application/json'
                                      )

        # Convert Gregorian date to Julian Day Number (universal calendar pivot).
        # Formula: Python ordinal counts from year 1 Jan 1; JDN epoch is 4713 BCE.
        # Offset 1721425 bridges the two systems.
        jdn     = input_date.toordinal() + 1721425
        results = get_calendars(region, jdn)

        # dataclasses.asdict() converts each CalendarDate dataclass to a plain dict,
        # which orjson can then serialize to JSON bytes.
        return app.response_class(
            orjson.dumps([dataclasses.asdict(r) for r in results]),
            mimetype='application/json'
        )

    except Exception as e:
        app.logger.error(f"ERROR getting calendars : {e}")
        return app.response_class(orjson.dumps({'error': 'Internal Server Error'}),
                                  status=500,
                                  mimetype='application/json'
                                  )

