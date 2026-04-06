from flask import Blueprint, request, current_app as app
from calendars import *
from calendars.dispatcher import get_calendars
import dataclasses
import orjson

calendars_bp = Blueprint('calendars', __name__)

@calendars_bp.route('/calendars')
def get_calendars_endpoint():
    try:
        region = request.args.get('region')
        jdn    = request.args.get('jdn', type=int)

        if not region or jdn is None:
            return app.response_class(orjson.dumps({'error': 'Missing region or JDN'}),
                                      status=400,
                                      mimetype='application/json'
                                      )   
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

