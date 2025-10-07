from flask import Blueprint

from api.routes.actor import actors_router
from api.routes.film import films_router

# base router
routes = Blueprint('api', __name__, url_prefix='/api')

routes.register_blueprint(actors_router)
routes.register_blueprint(films_router)
