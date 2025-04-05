import matplotlib.pyplot as plt
from PIL import Image
import io
import cv2
import os

from fastapi import UploadFile

import mimetypes
import io


def create_upload_file(image_as_byte: bytes, filename: str) -> UploadFile:
    content_type, _ = mimetypes.guess_type(filename)
    content_type = content_type or "application/octet-stream"

    file_object = io.BytesIO(image_as_byte)
    file_object.name = filename

    upload_file = UploadFile(filename=filename, file=file_object)

    return upload_file


def read(path):
    image = cv2.imread(path)
    if image is None:
        print(f"Error: Could not find the image at {path}")
        return
    return image


def write(imageFileName, file, scaleFactor):
    baseName, extension = os.path.splitext(imageFileName)
    outputPath = os.path.join(
        "src/images", f"{baseName}", f"{baseName}_x{scaleFactor}{extension}"
    )
    cv2.imwrite(outputPath, file)
    print(f"SR image saved as: {outputPath}")
    return outputPath
