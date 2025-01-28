import matplotlib.pyplot as plt
from PIL import Image
import io
import cv2


def display_images(images):
    # Tính số lượng hàng cần thiết
    num_images = len(images)
    num_columns = 2  # Số cột tối đa là 2
    num_rows = (num_images + num_columns - 1) // num_columns  # Tính số hàng

    plt.figure(figsize=(15, 5 * num_rows))  # Điều chỉnh kích thước figure

    for i, img in enumerate(images):
        plt.subplot(num_rows, num_columns, i + 1)  # Sử dụng số hàng và cột
        plt.imshow(img)
        plt.axis("off")
        plt.title(f"Image {i + 1}")

    plt.tight_layout()  # Đảm bảo các subplot không bị chồng lên nhau
    plt.show()


def downsample_image(image, scale=4):
    """
    Downsample the input image by a given scale factor.

    Parameters:
    - image: Input image (numpy array)
    - scale: Scale factor for downsampling (default is 4)

    Returns:
    - downsampled_image: Downsampled image (numpy array)
    """
    # Kiểm tra kích thước ảnh
    height, width = image.shape[:2]

    # Tính kích thước mới
    new_size = (width // scale, height // scale)

    # Downsample ảnh
    downsampled_image = cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)

    return downsampled_image
