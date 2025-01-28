from flask_pymongo import PyMongo
from pymongo.errors import ConnectionFailure

mongo = PyMongo()


def init_app(app):
    app.config["MONGO_URI"] = (
        "mongodb+srv://Database-NLCS-Dionysus:NaIRtA3gTb0ANoTC@cluster-nlcs-dionysus.fi0wsvo.mongodb.net/Enhance-Images-Database?retryWrites=true&w=majority&appName=Cluster-NLCS-Dionysus"
    )

    mongo.init_app(app)
    
    try:
        mongo.db.command("ping")
        print("Connect to database successfully!")
    except ConnectionFailure:
        print("Connect to database failed!")
    except Exception as e:
        print(e)
