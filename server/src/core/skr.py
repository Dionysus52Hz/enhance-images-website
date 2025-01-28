import numpy as np
import cv2
from skimage import img_as_float
from skimage.util import view_as_windows
from src.utils.images import display_images


def steering_kernel(theta, sigma):
    """Generate steering kernel."""
    size = 2 * int(3 * sigma) + 1
    kernel = np.zeros((size, size))
    for x in range(size):
        for y in range(size):
            x_center = x - size // 2
            y_center = y - size // 2
            kernel[x, y] = np.exp(
                -(x_center**2 + y_center**2) / (2 * sigma**2)
            ) * np.cos(theta)
    return kernel / np.sum(kernel)


def apply_kernel(image, kernel):
    """Convolve image with kernel."""
    return cv2.filter2D(image, -1, kernel)


def increase_resolution(image, scale=2, sigma=1.0):
    """Increase the resolution of the image using Steering Kernel Regression."""
    # Convert image to float
    image = img_as_float(image)

    # Get image dimensions
    height, width, channels = image.shape
    new_height, new_width = height * scale, width * scale

    # Create an empty array for the high-resolution image
    high_res_image = np.zeros((new_height, new_width, channels))

    for theta in np.linspace(0, np.pi, num=8):
        kernel = steering_kernel(theta, sigma)
        low_res_image = apply_kernel(image, kernel)

        # Resize the low-resolution image to high resolution
        low_res_image_resized = cv2.resize(
            low_res_image, (new_width, new_height), interpolation=cv2.INTER_CUBIC
        )

        # Add the result to the high-resolution image
        high_res_image += low_res_image_resized

    return np.clip(high_res_image / 8, 0, 1)  # Average the contributions
