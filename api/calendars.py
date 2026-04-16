from datetime import date
from flask import Blueprint, request, render_template ,current_app as app
from calendars import *
from convertdate import gregorian
from calendars.dispatcher import get_primary_calendar, _region_map, get_calendars
import dataclasses
import orjson
from app import cache

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


@calendars_bp.route('/calendars/panel')
@cache.cached(timeout=3600, query_string=True)  # Cache this endpoint for 1 hour
def get_calendar_panel_endpoint():
    """
    GET /api/calendars/panel?date=YYYY-MM-DD&region=ISO

    Returns an HTML fragment (not JSON) rendered by Jinja2 and injected into
    #calendar-panel by HTMX on country click. This is the "HTML over the wire"
    pattern: the server renders the UI, not the client.

    Query params:
        date   (str) : ISO date string, e.g. "2024-01-15"
        region (str) : ISO 3166-1 alpha-2 country code, e.g. "IR", "IL", "JP"

    Response (200): HTML fragment (partials/calendar_panel.html)
    Response (400): HTML error fragment — missing or invalid parameters
    Response (500): HTML error fragment — internal conversion error
    """
    region     = request.args.get('region')
    input_date = request.args.get('date', type=date.fromisoformat)
    # name is passed by JS from feature.properties.NAME for display purposes.
    # Falls back to the ISO code if absent.
    name       = request.args.get('name', default=region)

    if not region or input_date is None:
        return '<p class="error">Missing date or region.</p>', 400

    try:
        # Convert Gregorian date to Julian Day Number (universal calendar pivot).
        jdn = input_date.toordinal() + 1721425
        results = get_calendars(region, jdn)

        return render_template('partials/calendar_panel.html',
                               region_name=name,
                               date_str=input_date.isoformat(),
                               results=results
                               )
    except Exception as e:
        app.logger.error(f"ERROR getting calendar panel: {e}")
        return '<p class="error">Internal server error.</p>', 500


@calendars_bp.route('/calendars/overlay')
@cache.cached(timeout=3600, query_string=True)
def get_calendar_overlay_endpoint():
    """
    GET /api/calendars/overlay?year=YYYY

    Returns the primary calendar date for every known region in a single request.
    Used by the map overlay to color countries by calendar system and display
    local date labels directly on the map.

    Accepts a plain integer year instead of a full ISO date because:
    - The timeline slider only provides a year (no month/day).
    - Python's datetime.date does not support BCE years (≤ 0).
    - convertdate.gregorian.to_jd() handles the full range including BCE.

    JDN is computed for June 15 of the given year (mid-year representative).
    This is a known approximation: see project memory for planned improvement
    in Phase 5 when day-level precision becomes available.

    Query params:
        year (int)  : Gregorian year, e.g. 2024, 1500, -500 (500 BCE)
        month (int) : Month of the year, e.g. 1 (January) to 12 (December)
        day (int)   : Day of the month, e.g. 1 to 31

    Response (200): JSON object keyed by ISO 3166-1 alpha-2 region code
        {
            "FR": {"primary_calendar": "gregorian", "formatted": "2024-06-15"},
            "IR": {"primary_calendar": "persian",   "formatted": "1403-03-25"},
            ...
        }
    Response (400): JSON error — missing or invalid year parameter
    """
    year  = request.args.get('year', type=int)
    month = request.args.get('month', default=6, type=int)
    day   = request.args.get('day', default=15, type=int)

    if year is None:
        return app.response_class(orjson.dumps({'error': 'Missing or invalid year'}),
                                  status=400,
                                  mimetype='application/json'
                                  )

    # JDN computed for the requested date (defaults to June 15 if month/day not provided).
    jdn = int(gregorian.to_jd(year, month, day))

    result = {}
    for region_id in _region_map:
        # 'default' is a fallback key in the map, not a real region — skip it.
        if region_id == 'default':
            continue
        cal_key, calendar = get_primary_calendar(region_id, jdn)
        # cal_key is the internal name ('hijri', 'persian', ...) matching CALENDAR_COLORS in JS.
        # calendar.calendar_name is the display name ('Islamic', 'Persian', ...) — not used here.
        result[region_id] = {
            "primary_calendar": cal_key,
            "formatted": calendar.formatted,
        }

    return app.response_class(orjson.dumps(result), mimetype='application/json')