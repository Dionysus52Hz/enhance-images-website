from flask_pymongo import PyMongo
from pymongo import ReturnDocument
from flask import jsonify
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from src.db.db import mongo


def create_image(data):
    try:
        image_id = mongo.db.images.insert_one(data).inserted_id
        return str(image_id)
    except Exception as e:
        return jsonify(
            {
                "message": "Create image failed!",
                "error": e,
            }
        )


def get_images():
    try:
        images = list(mongo.db.images.find())
        images_data_as_json = dumps(images)
        return images_data_as_json
    except Exception as e:
        return jsonify(
            {
                "message": "Get images failed!",
                "error": e,
            }
        )


def get_image_by_id(id):
    try:
        image = mongo.db.images.find_one({"_id": ObjectId(id)})
        image_path = image["path"]
        return image_path
    except Exception as e:
        return jsonify(
            {
                "message": "Get image by id failed!",
                "error": e,
            }
        )


def update_image_by_id(id, data):
    try:
        print(data)
        image = mongo.db.images.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data}, return_document=ReturnDocument.AFTER
        )

        image["_id"] = str(image["_id"])
        return image
    except Exception as e:
        return jsonify(
            {
                "message": "Update image failed!",
                "error": e,
            }
        )


def delete_image_by_id(id):
    try:
        image = mongo.db.images.find_one({"_id": ObjectId(id)})
        mongo.db.images.delete_one({"_id": ObjectId(id)})
        image["_id"] = str(image["_id"])
        return image
    except Exception as e:
        return jsonify(
            {
                "message": "Delete image by id failed!",
                "error": e,
            }
        )
