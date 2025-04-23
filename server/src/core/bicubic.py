import cv2
import time

from fastapi import status
from src.models.SSEResponse import SSEResponseModel


def bicubic(image, scaleFactor, container: dict):
    yield SSEResponseModel(
        status="processing",
        message="Enhancing resolution",
        code=status.HTTP_200_OK,
    ).to_sse()

    height = image.shape[0]
    width = image.shape[1]
    sr = cv2.resize(
        image,
        (width * scaleFactor, height * scaleFactor),
        interpolation=cv2.INTER_CUBIC,
    )

    container["sr"] = sr

    time.sleep(1)

    yield SSEResponseModel(
        status="completed",
        message="Processing completed!",
        code=status.HTTP_200_OK,
    ).to_sse()
