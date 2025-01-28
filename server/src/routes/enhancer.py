from flask import Blueprint, jsonify, request, send_file
import os
import io
import cv2
import base64
import numpy as np
from PIL import Image
from src.utils.images import display_images, downsample_image

enhancer = Blueprint("enhancer", __name__, url_prefix="/enhancers")

DOWNSAMPLED_DIR = "src/images/downsampled"
os.makedirs(DOWNSAMPLED_DIR, exist_ok=True)


@enhancer.route("", methods=["GET", "POST"])
def index_enhancer():
    if request.method == "GET":
        img = cv2.imread(
            "src\\uploads\\468506546_908643214705823_1726609296258497269_n.jpg"
        )
        downsampled_img = downsample_image(img, scale=4)
        save_path = os.path.join(DOWNSAMPLED_DIR, "downsampled.jpg")
        cv2.imwrite(save_path, downsampled_img)

        return send_file(
            save_path,
            mimetype="image/jpeg",
        )

    else:
        print(request.data)
        return request.data
