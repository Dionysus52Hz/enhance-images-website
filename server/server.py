from flask import Flask
from flask_cors import CORS, cross_origin
from src.routes.api import api
from src.db.db import init_app

app = Flask(__name__)
init_app(app)


CORS(app)

app.register_blueprint(api)


@app.route("/")
@cross_origin()
def home():
    return "Welcome to Flask"


if __name__ == "__main__":
    app.run()
