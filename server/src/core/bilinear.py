import cv2


def bilinear(image, scaleFactor):
    height = image.shape[0]
    width = image.shape[1]
    return cv2.resize(
        image,
        (width * scaleFactor, height * scaleFactor),
        interpolation=cv2.INTER_LINEAR,
    )
