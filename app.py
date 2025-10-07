from flask import Flask
from flask_cors import CORS

from api.config import config
from api.routes import routes


def create_app():

    app = Flask(__name__)
    # set configuration
    app.config.from_object(config)
    # apply CORS to all blueprints (global)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    
    # set up models
    from api.models import db
    db.init_app(app)

    # set up schemas
    from api.schemas import ma
    ma.init_app(app)

    app.register_blueprint(routes)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
