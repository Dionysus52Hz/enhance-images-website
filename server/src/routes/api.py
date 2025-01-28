from flask import Blueprint
from src.routes.enhancer import enhancer
from src.routes.filters import filters
from src.routes.images import images

api = Blueprint("api", __name__, url_prefix="/api")

api.register_blueprint(enhancer)
api.register_blueprint(filters)
api.register_blueprint(images)
