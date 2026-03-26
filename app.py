from flask import Flask, render_template
from config import config
from flask_caching import Cache
from flask_compress import Compress

cache    = Cache()
compress = Compress()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    cache.init_app(app)
    compress.init_app(app)

    from api.borders import borders_bp
    app.register_blueprint(borders_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()