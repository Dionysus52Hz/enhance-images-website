from flask import Blueprint, jsonify, request

filters = Blueprint("filters", __name__, url_prefix="/filters")


@filters.route("/", methods=["GET", "POST"])
def index_filters():
    if request.method == "GET":
        return {"value": 3}
    else:
        return {"value": 4}
