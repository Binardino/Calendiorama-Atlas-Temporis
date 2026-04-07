from datetime import date
from flask import Blueprint, request, current_app as app
from calendars import *
from calendars.dispatcher import get_calendars
import dataclasses
import orjson

calendars_bp = Blueprint('calendars', __name__)

@calendars_bp.route('/calendars')
def get_calendars_endpoint():
    try:
        region       = request.args.get('region')
        input_date   = request.args.get('date', type=date.fromisoformat)

        if not region or input_date is None:
            return app.response_class(orjson.dumps({'error': 'Missing region or date'}),
                                      status=400,
                                      mimetype='application/json'
                                      )   
        jdn     = input_date.toordinal() + 1721425
        results = get_calendars(region, jdn)

        
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

