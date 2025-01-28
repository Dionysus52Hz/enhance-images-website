import os
import cv2
from flask import Blueprint, jsonify, request, send_file
from PIL import Image
from src.db.db import mongo
from src.models.images import (
    create_image,
    get_images,
    get_image_by_id,
    delete_image_by_id,
    update_image_by_id,
)

images = Blueprint("images", __name__, url_prefix="/images")


@images.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        images = get_images()
        return {
            "images": images,
        }
    else:
        return {"value": 4}


@images.route("/<id>", methods=["GET", "DELETE"])
def handle_image(id):
    if request.method == "GET":
        image_path = get_image_by_id(id)
        image = cv2.imread(image_path)

        return send_file(
            image_path,
            mimetype="image/jpeg",
        )
    elif request.method == "DELETE":
        image = delete_image_by_id(id)
        return {"image_delete": image}


@images.route("/<id>", methods=["PUT"])
def update_image(id):
    data = request.get_json()
    image = update_image_by_id(id, data)
    return {"image_updated": image}


UPLOAD_FOLDER = "src/images/originals"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


uploaded_files = []
uploaded_images = []


@images.route("/uploads", methods=["POST"])
def upload_images():

    uploaded_files.clear()
    uploaded_images.clear()
    files = request.files.getlist("files")
    names = request.form.getlist("names")
    sizes = request.form.getlist("sizes")
    widths = request.form.getlist("widths")
    heights = request.form.getlist("heights")
    models = request.form.getlist("models")
    factors = request.form.getlist("factors")

    for i, file in enumerate(files):
        if file.filename == "":
            continue
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        image_data = {
            "name": names[i],
            "size": sizes[i],
            "width": widths[i],
            "height": heights[i],
            "state": "Ready",
            "path": file_path,
            "model": models[i],
            "factor": factors[i],
        }
        image_id = create_image(image_data)
        uploaded_images.append(
            {
                "id": image_id,
                "path": file_path,
                "model": models[i],
                "factor": factors[i],
            }
        )

    return (
        jsonify({"message": "Files uploaded successfully!", "images": uploaded_images}),
        200,
    )
