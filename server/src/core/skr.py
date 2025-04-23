import cv2
import numpy as np
import math
import json
import time
import numpy as np
import multiprocessing as mp

from scipy.ndimage import gaussian_filter
from scipy.linalg import svd, inv, pinv
from scipy.signal import convolve2d
from skimage.metrics import structural_similarity
from src.models.SSEResponse import SSEResponseModel
from fastapi import status


def adaptiveKernel(image, originalY, originalX, kernelSize):
    patchSize = kernelSize + 2
    halfPatch = patchSize // 2

    patch = image[
        max(originalY - halfPatch, 0) : min(originalY + halfPatch + 1, image.shape[0]),
        max(originalX - halfPatch, 0) : min(originalX + halfPatch + 1, image.shape[1]),
    ]

    normalizedPatch = patch.astype(np.float64) / 255.0

    localVariance = np.var(normalizedPatch, axis=(0, 1))
    adaptiveSize = max(3, kernelSize + int(np.mean(localVariance) * 10))
    if adaptiveSize % 2 == 0:
        adaptiveSize += 1
    adaptiveSigma = np.clip(np.mean(localVariance) * 2, 0.1, 10)

    return adaptiveSize, adaptiveSigma


def createRotateGaussianKernel(kernelSize, sigma, angle):
    halfSize = kernelSize // 2
    x, y = np.meshgrid(
        np.arange(-halfSize, halfSize + 1),
        np.arange(-halfSize, halfSize + 1),
    )

    cosTheta = np.cos(angle)
    sinTheta = np.sin(angle)
    xRotated = x * cosTheta + y * sinTheta
    yRotated = -x * sinTheta + y * cosTheta

    kernel = (1 / (2 * np.pi * sigma**2)) * np.exp(
        -(xRotated**2 + yRotated**2) / (2 * sigma**2)
    )
    return kernel / np.sum(kernel)


def calculateWeights(kernelSize, centerX, centerY, angle):
    halfSize = kernelSize // 2
    x, y = np.meshgrid(
        np.arange(-halfSize, halfSize + 1),
        np.arange(-halfSize, halfSize + 1),
    )

    distances = np.sqrt((x) ** 2 + (y) ** 2)

    distancesWeights = np.exp(-(distances**2) / (2 * (kernelSize / 8) ** 2))

    orientationWeights = np.exp(
        -((np.arctan2(y, x) - angle) ** 2) / (2 * (np.pi / 8) ** 2)
    )

    weights = distancesWeights * orientationWeights

    return distancesWeights / np.sum(distancesWeights)


def sharpen(image, gamma=1.5, k=1):
    channels = image.shape[2] if len(image.shape) > 2 else 1

    b = None
    g = None
    r = None
    a = None

    if channels == 4:
        imageBGR = image[:, :, :3]
        b, g, r = cv2.split(imageBGR)
    elif channels == 3:
        imageBGR = image
        b, g, r = cv2.split(imageBGR)
    elif channels == 2:
        imageBGR = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        r = g = b = imageBGR
    else:
        raise ValueError("Unsupported number of channels: {}".format(channels))

    image = cv2.GaussianBlur(image, (7, 7), 0)

    imageFloat = image.astype(np.float32)
    inverted = 255.0 - imageFloat
    powerTransformed = k * (inverted / 255.0) ** gamma
    powerTransformed = 255.0 - np.clip(powerTransformed * 255, 0, 255)

    sobelXB = cv2.Sobel(b, cv2.CV_64F, 1, 0, ksize=3)
    sobelYB = cv2.Sobel(b, cv2.CV_64F, 0, 1, ksize=3)
    sobelXG = cv2.Sobel(g, cv2.CV_64F, 1, 0, ksize=3)
    sobelYG = cv2.Sobel(g, cv2.CV_64F, 0, 1, ksize=3)
    sobelXR = cv2.Sobel(r, cv2.CV_64F, 1, 0, ksize=3)
    sobelYR = cv2.Sobel(r, cv2.CV_64F, 0, 1, ksize=3)

    edgesB = cv2.magnitude(sobelXB, sobelYB)
    edgesG = cv2.magnitude(sobelXG, sobelYG)
    edgesR = cv2.magnitude(sobelXR, sobelYR)

    edgesB = cv2.normalize(edgesB, None, 0, 255, cv2.NORM_MINMAX)
    edgesG = cv2.normalize(edgesG, None, 0, 255, cv2.NORM_MINMAX)
    edgesR = cv2.normalize(edgesR, None, 0, 255, cv2.NORM_MINMAX)

    combinedEdges = cv2.merge((edgesB, edgesG, edgesR))

    if channels == 4:
        temp = cv2.addWeighted(imageBGR, 1, combinedEdges, 0.5, 0)
        enhancedImage = np.zeros_like(image, dtype=np.uint8)
        enhancedImage[:, :, :3] = np.clip(temp, 0, 255).astype(np.uint8)
        enhancedImage[:, :, 3] = image[:, :, 3]
    elif channels == 3:
        enhancedImage = cv2.addWeighted(
            imageBGR, 1, combinedEdges, 0.5, 0, dtype=cv2.CV_64F
        )
    else:
        enhancedImage = cv2.addWeighted(imageBGR, edgesB, 0.5, 0, dtype=cv2.CV_64F)

    return enhancedImage


def skr2(image, scaleFactor, kernelSize=5):
    channels = image.shape[2] if len(image.shape) > 2 else 1
    height, width, _ = image.shape
    newHeight = int(height * scaleFactor)
    newWidth = int(width * scaleFactor)

    upscaledImage = cv2.resize(
        image, (newWidth, newHeight), interpolation=cv2.INTER_LINEAR
    )

    if channels == 4:
        imageRGB = upscaledImage[:, :, :3]
    elif channels == 3:
        imageRGB = upscaledImage
    elif channels == 2:
        imageRGB = cv2.cvtColor(upscaledImage, cv2.COLOR_GRAY2RGB)
    else:
        raise ValueError("Unsupported number of channels: {}".format(channels))

    srImage = np.zeros((newHeight, newWidth, 3), dtype=np.float64)

    sobelX = [cv2.Sobel(imageRGB[:, :, i], cv2.CV_64F, 1, 0, ksize=3) for i in range(3)]
    sobelY = [cv2.Sobel(imageRGB[:, :, i], cv2.CV_64F, 0, 1, ksize=3) for i in range(3)]
    theta = [np.arctan2(sobelY[i], sobelX[i]) for i in range(3)]

    for y in range(kernelSize // 2, newHeight - kernelSize // 2):
        for x in range(kernelSize // 2, newWidth - kernelSize // 2):
            originalY = int(y / scaleFactor)
            originalX = int(x / scaleFactor)

            adaptiveSize, adaptiveSigma = adaptiveKernel(
                imageRGB, originalY, originalX, kernelSize
            )

            newPixelValue = np.zeros(3)

            for channel in range(3):
                angle = theta[channel][originalY, originalX]
                rotatedKernel = createRotateGaussianKernel(
                    adaptiveSize, adaptiveSigma, angle
                )

                halfSize = adaptiveSize // 2
                xStart = max(x - halfSize, 0)
                xEnd = min(x + halfSize + 1, imageRGB.shape[1])
                yStart = max(y - halfSize, 0)
                yEnd = min(y + halfSize + 1, imageRGB.shape[0])

                patch = imageRGB[yStart:yEnd, xStart:xEnd]
                if patch.shape[0] != adaptiveSize or patch.shape[1] != adaptiveSize:
                    patch = cv2.resize(patch, (adaptiveSize, adaptiveSize))

                weights = calculateWeights(adaptiveSize, originalX, originalY, angle)
                weightedKernel = rotatedKernel * weights
                weightedKernel = weightedKernel / np.sum(weightedKernel)
                # if x == 100 and y == 100:
                #     print("rotated:", rotatedKernel)
                #     print("weight: ", weights)
                #     print(np.sum(weights))
                #     print(np.sum(rotatedKernel))
                #     print(np.sum(weightedKernel))
                #     print("weighted kernel: ", weightedKernel)
                patchChannel = patch[:, :, channel]
                # print("Patch shape: ", patch.shape)
                # print("Patch channel shape: ", patchChannel.shape)
                # print("Rotate kernel shape: ", rotatedKernel.shape)
                # print("Weighted kernel shape: ", weightedKernel.shape)

                newPixelValue[channel] = np.sum(patchChannel * weightedKernel)

            # print(newPixelValue)
            srImage[y, x, :3] = newPixelValue

    if channels == 4:
        result = np.zeros((newHeight, newWidth, 4), dtype=np.uint8)
        result[:, :, :3] = np.clip(srImage, 0, 255).astype(np.uint8)
        result[:, :, 3] = upscaledImage[:, :, 3]
        return upscaledImage, result

    else:
        result = np.clip(srImage, 0, 255).astype(np.uint8)
        return upscaledImage, result


def skr3(image, scaleFactor, kernelSize=3):
    channels = image.shape[2] if len(image.shape) > 2 else 1
    height, width, _ = image.shape
    newHeight = int(height * scaleFactor)
    newWidth = int(width * scaleFactor)

    print(image.shape)
    print(scaleFactor)
    print(type(scaleFactor))

    bicubicUpsample = cv2.resize(
        image, (newWidth, newHeight), interpolation=cv2.INTER_LINEAR
    )
    # bicubicUpsample = None

    if channels == 4:
        imageRGB = image[:, :, :3]
    elif channels == 3:
        imageRGB = image
    elif channels == 2:
        imageRGB = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        raise ValueError("Unsupported number of channels: {}".format(channels))

    srImage = np.zeros((newHeight, newWidth, 3), dtype=np.float32)

    sobelX = [cv2.Sobel(imageRGB[:, :, i], cv2.CV_64F, 1, 0, ksize=3) for i in range(3)]
    sobelY = [cv2.Sobel(imageRGB[:, :, i], cv2.CV_64F, 0, 1, ksize=3) for i in range(3)]
    theta = [np.arctan2(sobelY[i], sobelX[i]) for i in range(3)]

    for y in range(kernelSize // 2, newHeight - kernelSize // 2):
        for x in range(kernelSize // 2, newWidth - kernelSize // 2):
            originalY = int(y / scaleFactor)
            originalX = int(x / scaleFactor)

            adaptiveSize, adaptiveSigma = adaptiveKernel(
                imageRGB, originalY, originalX, kernelSize
            )

            newPixelValue = np.zeros(3)

            for channel in range(3):
                angle = theta[channel][originalY, originalX]
                rotatedKernel = createRotateGaussianKernel(
                    adaptiveSize, adaptiveSigma, angle
                )

                halfSize = adaptiveSize // 2
                xStart = max(originalX - halfSize, 0)
                xEnd = min(originalX + halfSize + 1, width)
                yStart = max(originalY - halfSize, 0)
                yEnd = min(originalY + halfSize + 1, height)

                patch = imageRGB[yStart:yEnd, xStart:xEnd]

                if patch.shape[0] != adaptiveSize or patch.shape[1] != adaptiveSize:
                    patch = cv2.resize(patch, (adaptiveSize, adaptiveSize))

                weights = calculateWeights(adaptiveSize, originalX, originalY, angle)
                weightedKernel = rotatedKernel * weights
                weightedKernel = weightedKernel / np.sum(weightedKernel)
                # if x == 100 and y == 100:
                #     print("rotated:", rotatedKernel)
                #     print("weight: ", weights)
                #     print(np.sum(weights))
                #     print(np.sum(rotatedKernel))
                #     print(np.sum(weightedKernel))
                #     print("weighted kernel: ", weightedKernel)
                patchChannel = patch[:, :, channel]
                # print("Patch shape: ", patch.shape)
                # print("Patch channel shape: ", patchChannel.shape)
                # print("Rotate kernel shape: ", rotatedKernel.shape)
                # print("Weighted kernel shape: ", weightedKernel.shape)

                newPixelValue[channel] = np.sum(patchChannel * weightedKernel)

            # print(newPixelValue)
            srImage[y, x, :3] = newPixelValue

    # invertedImage = sharpen(srImage)
    # invertedImage = np.clip(invertedImage, 0, 255).astype(np.uint8)
    # print(invertedImage.shape)
    # srImage = sharpen(srImage)
    srImage = cv2.GaussianBlur(srImage, (5, 5), 0)

    if channels == 4:
        result = np.zeros((newHeight, newWidth, 4), dtype=np.uint8)
        result[:, :, :3] = np.clip(srImage, 0, 255).astype(np.uint8)
        result[:, :, 3] = bicubicUpsample[:, :, 3]
        return bicubicUpsample, result

    else:
        result = np.clip(srImage, 0, 255).astype(np.uint8)

        return bicubicUpsample, result


# def rmse(image1, image2):
#     mse = mean_squared_error(image1.flatten(), image2.flatten())

#     return np.sqrt(mse)


def edgeMirror(image, width):
    if not isinstance(image, np.ndarray):
        raise ValueError("Input image must be a numpy array")

    if len(image.shape) not in [2, 3]:
        raise ValueError("Input image must be grayscale or color")

    if len(width) != 2:
        raise ValueError("Width parameter must be [x, y] format")

    if width[0] < 0 or width[1] < 0:
        raise ValueError("Mirror width cannot be negative")

    leftMirror = image[:, width[1] : 0 : -1]
    rightMirror = image[:, -2 : -width[1] - 2 : -1]
    result = np.concatenate([leftMirror, image, rightMirror], axis=1)

    topMirror = result[width[0] : 0 : -1, :]
    bottomMirror = result[-2 : -width[0] - 2 : -1, :]
    result = np.concatenate([topMirror, result, bottomMirror], axis=0)

    return result


def downsample(image, factor):
    if image.ndim == 2:
        return image[::factor, ::factor]
    elif image.ndim == 3:
        return image[::factor, ::factor, :]
    else:
        raise ValueError("Invalid input image")


def getDiskKernel(radius, gridSize=500):
    size = 2 * radius + 1
    kernel = np.zeros((size, size))
    center = radius

    samples = np.linspace(-0.5, 0.5, gridSize)
    dx = samples[1] - samples[0]

    for i in range(size):
        for j in range(size):
            x0, y0 = i - center, j - center
            x, y = np.meshgrid(x0 + samples, y0 + samples)
            mask = (x**2 + y**2) <= radius**2
            kernel[i, j] = np.sum(mask) * dx**2

    kernel /= np.sum(kernel)
    return kernel


def processBlockClassicKernel(args):
    (
        image,
        smoothing,
        covariance00,
        covariance01,
        covariance11,
        determinant,
        scaleFactor,
        kernelSize,
        n,
        m,
        i,
        j,
        y,
        x,
        channels,
    ) = args

    sampledX = downsample(x[scaleFactor - i - 1 :, scaleFactor - j - 1 :], scaleFactor)
    sampledY = downsample(y[scaleFactor - i - 1 :, scaleFactor - j - 1 :], scaleFactor)

    featureMatrix = np.column_stack(
        [
            np.ones(kernelSize**2),
            sampledX.ravel(order="F"),
            sampledY.ravel(order="F"),
            sampledX.ravel(order="F") ** 2,
            sampledX.ravel(order="F") * sampledY.ravel(order="F"),
            sampledY.ravel(order="F") ** 2,
        ]
    )

    cov00_win = covariance00[n : n + kernelSize, m : m + kernelSize]
    cov01_win = covariance01[n : n + kernelSize, m : m + kernelSize]
    cov11_win = covariance11[n : n + kernelSize, m : m + kernelSize]
    det_win = determinant[n : n + kernelSize, m : m + kernelSize]

    weight = sampledX * (cov00_win * sampledX + cov01_win * sampledY) + sampledY * (
        cov01_win * sampledX + cov11_win * sampledY
    )

    weightMatrix = np.exp(-0.5 * weight / smoothing**2) * det_win
    weightMatrix = weightMatrix.ravel(order="F")
    weightedFeatures = featureMatrix * weightMatrix[:, np.newaxis]
    regressionMatrix = (
        inv(featureMatrix.T @ (weightedFeatures) + np.eye(6) * 1e-7)
        @ weightedFeatures.T
    )

    upscaledPixel = np.zeros(channels)
    for c in range(channels):
        neighborhoodSamples = (
            image[n : n + kernelSize, m : m + kernelSize]
            if channels == 1
            else image[n : n + kernelSize, m : m + kernelSize, c]
        )
        upscaledPixel[c] = regressionMatrix[0] @ neighborhoodSamples.ravel(order="F")

    return (n * scaleFactor + i, m * scaleFactor + j, upscaledPixel)


def upscaleWithClassicKernel(image, smoothing, scaleFactor, kernelSize):
    if image.ndim == 2:
        image = image[..., np.newaxis]

    height, width, channels = image.shape
    upscaledImage = np.zeros((height * scaleFactor, width * scaleFactor, channels))
    gradientX = np.zeros((height * scaleFactor, width * scaleFactor, channels))
    gradientY = np.zeros((height * scaleFactor, width * scaleFactor, channels))

    kernelRadius = (kernelSize - 1) // 2
    y, x = np.meshgrid(
        np.linspace(
            -kernelRadius - (scaleFactor - 1) / scaleFactor,
            kernelRadius,
            kernelSize * scaleFactor,
        ),
        np.linspace(
            -kernelRadius - (scaleFactor - 1) / scaleFactor,
            kernelRadius,
            kernelSize * scaleFactor,
        ),
    )

    kernelMatrix = np.zeros((6, kernelSize**2, scaleFactor, scaleFactor))

    for i in range(scaleFactor):
        for j in range(scaleFactor):
            sampledX = downsample(
                x[scaleFactor - i - 1 :, scaleFactor - j - 1 :], scaleFactor
            )
            sampledY = downsample(
                y[scaleFactor - i - 1 :, scaleFactor - j - 1 :], scaleFactor
            )

            featureMatrix = np.column_stack(
                [
                    np.ones(kernelSize**2),
                    sampledX.ravel(),
                    sampledY.ravel(),
                    sampledX.ravel() ** 2,
                    sampledX.ravel() * sampledY.ravel(),
                    sampledY.ravel() ** 2,
                ]
            )
            weightMatrix = np.exp(-0.5 * (sampledX**2 + sampledY**2) / smoothing**2)
            weightedFeatures = featureMatrix * weightMatrix.ravel()[:, None]

            kernelMatrix[:, :, i, j] = (
                np.linalg.pinv(featureMatrix.T @ weightedFeatures) @ weightedFeatures.T
            )

    paddedImage = edgeMirror(image, [kernelRadius, kernelRadius])

    for c in range(channels):
        for n in range(height):
            for m in range(width):
                neighborhoodSamples = paddedImage[
                    n : n + kernelSize, m : m + kernelSize, c
                ]

                for i in range(scaleFactor):
                    upsampledN = n * scaleFactor + i
                    for j in range(scaleFactor):
                        upsampledM = m * scaleFactor + j

                        upscaledImage[upsampledN, upsampledM, c] = (
                            kernelMatrix[0, :, i, j] @ neighborhoodSamples.ravel()
                        )
                        gradientX[upsampledN, upsampledM, c] = (
                            kernelMatrix[1, :, i, j] @ neighborhoodSamples.ravel()
                        )
                        gradientY[upsampledN, upsampledM, c] = (
                            kernelMatrix[2, :, i, j] @ neighborhoodSamples.ravel()
                        )

    if upscaledImage.shape[2] == 1:
        upscaledImage = upscaledImage[..., 0]
        gradientX = gradientX[..., 0]
        gradientY = gradientY[..., 0]

    return upscaledImage, gradientX, gradientY


def processBlockSteering(args):
    (
        gradientX,
        gradientY,
        position,
        kernel,
        lambda_,
        alpha,
        windowSize,
        windowRadius,
        i,
        j,
        channels,
    ) = args
    if position[i, j] == 0:
        return i, j, np.zeros((2, 2))

    steeringMatrixChannel = np.zeros((2, 2, channels))
    for c in range(channels):
        Gx = gradientX[i : i + windowSize, j : j + windowSize, c] * kernel
        Gy = gradientY[i : i + windowSize, j : j + windowSize, c] * kernel

        G = np.column_stack((Gx.ravel(), Gy.ravel()))
        lenKernel = np.sum(kernel)

        U, S, Vt = svd(G, full_matrices=False)

        S1 = (S[0] + lambda_) / (S[1] + lambda_)
        S2 = (S[1] + lambda_) / (S[0] + lambda_)

        steeringMatrixChannel[:, :, c] = (
            S1 * np.outer(Vt[0], Vt[0]) + S2 * np.outer(Vt[1], Vt[1])
        ) * ((S[0] * S[1] + 1e-7) / lenKernel) ** alpha

    return i, j, np.mean(steeringMatrixChannel, axis=2)


def steering(gradientX, gradientY, position, windowSize, lambda_, alpha):
    if gradientX.ndim == 2:
        gradientX = gradientX[:, :, np.newaxis]
        gradientY = gradientY[:, :, np.newaxis]
    elif gradientX.ndim == 3 and gradientX.shape[2] in [3, 4]:
        pass
    else:
        raise ValueError("Invalid gradient")

    height, width, channels = gradientX.shape

    steeringMatrix = np.zeros((2, 2, height, width))

    if windowSize % 2 == 0:
        windowSize += 1
    windowRadius = windowSize // 2

    kernel = getDiskKernel(windowRadius)
    kernel /= kernel[windowRadius, windowRadius]
    # kernel = np.array(
    #     [
    #         [0.078787, 0.45661, 0.078787],
    #         [0.45661, 1, 0.45661],
    #         [0.078787, 0.45661, 0.078787],
    #     ]
    # )

    paddedGradientX = edgeMirror(gradientX, [windowRadius, windowRadius])
    paddedGradientY = edgeMirror(gradientY, [windowRadius, windowRadius])

    for i in range(height):
        for j in range(width):
            if position[i, j] == 0:
                continue

            steeringMatrixChannel = np.zeros((2, 2, channels))

            for c in range(channels):
                Gx = paddedGradientX[i : i + windowSize, j : j + windowSize, c] * kernel
                Gy = paddedGradientY[i : i + windowSize, j : j + windowSize, c] * kernel

                G = np.column_stack((Gx.ravel(), Gy.ravel()))
                lenKernel = np.sum(kernel)

                U, S, Vt = svd(G, full_matrices=False)

                S1 = (S[0] + lambda_) / (S[1] + lambda_)
                S2 = (S[1] + lambda_) / (S[0] + lambda_)

                steeringMatrixChannel[:, :, c] = (
                    S1 * np.outer(Vt[0], Vt[0]) + S2 * np.outer(Vt[1], Vt[1])
                ) * ((S[0] * S[1] + 1e-7) / lenKernel) ** alpha

            steeringMatrix[:, :, i, j] = np.mean(steeringMatrixChannel, axis=2)
    # args_list = [
    #     (
    #         paddedGradientX,
    #         paddedGradientY,
    #         position,
    #         kernel,
    #         lambda_,
    #         alpha,
    #         windowSize,
    #         windowRadius,
    #         i,
    #         j,
    #         channels,
    #     )
    #     for i in range(height)
    #     for j in range(width)
    # ]

    # with mp.Pool(mp.cpu_count()) as pool:
    #     results = pool.map(processBlockSteering, args_list)

    # for i, j, matrix in results:
    #     steeringMatrix[:, :, i, j] = matrix

    return steeringMatrix


def steeringKernelRegression(
    image, smoothing, covarianceMatrices, scaleFactor, kernelSize
):
    if image.ndim == 2:
        channels = 1
    elif image.ndim == 3:
        channels = image.shape[2]
    else:
        raise ValueError("Invalid input image")

    if kernelSize % 2 == 0:
        raise ValueError("Kernel size must be an odd value")

    height, width = image.shape[:2]

    upscaledImage = np.zeros((height * scaleFactor, width * scaleFactor, channels))
    gradientX = np.zeros_like(upscaledImage)
    gradientY = np.zeros_like(upscaledImage)

    kernelRadius = (kernelSize - 1) // 2
    y, x = np.meshgrid(
        np.linspace(
            -kernelRadius - (scaleFactor - 1) / scaleFactor,
            kernelRadius,
            kernelSize * scaleFactor,
        ),
        np.linspace(
            -kernelRadius - (scaleFactor - 1) / scaleFactor,
            kernelRadius,
            kernelSize * scaleFactor,
        ),
    )

    covariance00 = covarianceMatrices[0, 0, :, :]
    covariance01 = covarianceMatrices[0, 1, :, :]
    covariance11 = covarianceMatrices[1, 1, :, :]
    determinant = np.sqrt(np.linalg.det(covarianceMatrices.transpose(2, 3, 0, 1)))

    image = edgeMirror(image, [kernelRadius, kernelRadius])
    covariance00 = edgeMirror(covariance00, [kernelRadius, kernelRadius])
    covariance01 = edgeMirror(covariance01, [kernelRadius, kernelRadius])
    covariance11 = edgeMirror(covariance11, [kernelRadius, kernelRadius])
    determinant = edgeMirror(determinant, [kernelRadius, kernelRadius])

    a = 0
    for i in range(scaleFactor):
        for j in range(scaleFactor):
            sampledX = downsample(
                x[scaleFactor - i - 1 :, scaleFactor - j - 1 :], scaleFactor
            )
            sampledY = downsample(
                y[scaleFactor - i - 1 :, scaleFactor - j - 1 :], scaleFactor
            )

            featureMatrix = np.column_stack(
                [
                    np.ones(kernelSize**2),
                    sampledX.ravel(order="F"),
                    sampledY.ravel(order="F"),
                    sampledX.ravel(order="F") ** 2,
                    sampledX.ravel(order="F") * sampledY.ravel(order="F"),
                    sampledY.ravel(order="F") ** 2,
                ]
            )

            # print(sampledX.shape, sampledY.shape)

            for n in range(height):
                upsampledN = n * scaleFactor + i
                for m in range(width):
                    a += 1
                    upsampledM = m * scaleFactor + j

                    # weight = sampledX * (
                    #     covariance00[n, m] * sampledX + covariance01[n, m] * sampledY
                    # ) + sampledY * (
                    #     covariance01[n, m] * sampledX + covariance11[n, m] * sampledY
                    # )
                    covariance00Window = covariance00[
                        n : n + kernelSize, m : m + kernelSize
                    ]
                    covariance01Window = covariance01[
                        n : n + kernelSize, m : m + kernelSize
                    ]
                    covariance11Window = covariance11[
                        n : n + kernelSize, m : m + kernelSize
                    ]

                    weight = sampledX * (
                        covariance00Window * sampledX + covariance01Window * sampledY
                    ) + sampledY * (
                        covariance01Window * sampledX + covariance11Window * sampledY
                    )

                    weightMatrix = (
                        np.exp(-0.5 * weight / smoothing**2)
                        * determinant[n : n + kernelSize, m : m + kernelSize]
                    )
                    weightMatrix = weightMatrix.ravel(order="F")
                    weightedFeatures = featureMatrix * weightMatrix[:, np.newaxis]
                    regressionMatrix = (
                        inv(featureMatrix.T @ weightedFeatures + np.eye(6) * 1e-7)
                        @ weightedFeatures.T
                    )
                    # if n == 1 and m == 1 and i == 1 and j == 1:
                    #     print("--------sampleX")
                    #     print(sampledX)
                    #     print("--------sampleY")
                    #     print(sampledY)
                    #     print("weight matrix----------------")
                    #     print(sampledX)
                    #     print(sampledY)
                    #     print(featureMatrix)
                    #     print(weightMatrix)
                    #     print(weightedFeatures)

                    for c in range(channels):
                        if channels == 1:
                            neighborhoodSamples = image[
                                n : n + kernelSize, m : m + kernelSize
                            ]
                        else:
                            neighborhoodSamples = image[
                                n : n + kernelSize, m : m + kernelSize, c
                            ]

                        upscaledImage[upsampledN, upsampledM, c] = regressionMatrix[
                            0
                        ] @ neighborhoodSamples.ravel(order="F")
                        # gradientX[upsampledN, upsampledM, c] = regressionMatrix[
                        #     1
                        # ] @ neighborhoodSamples.ravel(order="F")
                        # gradientY[upsampledN, upsampledM, c] = regressionMatrix[
                        #     2
                        # ] @ neighborhoodSamples.ravel(order="F")

    print(f"Number of iterations: {a}")

    if channels == 1:
        upscaledImage = upscaledImage[:, :, 0]
        gradientX = gradientX[:, :, 0]
        gradientY = gradientY[:, :, 0]

    return upscaledImage, gradientX, gradientY


def process_block(args):
    (
        image,
        smoothing,
        covariance00,
        covariance01,
        covariance11,
        determinant,
        scaleFactor,
        kernelSize,
        n,
        m,
        i,
        j,
        y,
        x,
        channels,
    ) = args

    sampledX = downsample(x[scaleFactor - i - 1 :, scaleFactor - j - 1 :], scaleFactor)
    sampledY = downsample(y[scaleFactor - i - 1 :, scaleFactor - j - 1 :], scaleFactor)

    featureMatrix = np.column_stack(
        [
            np.ones(kernelSize**2),
            sampledX.ravel(order="F"),
            sampledY.ravel(order="F"),
            sampledX.ravel(order="F") ** 2,
            sampledX.ravel(order="F") * sampledY.ravel(order="F"),
            sampledY.ravel(order="F") ** 2,
        ]
    )

    cov00_win = covariance00[n : n + kernelSize, m : m + kernelSize]
    cov01_win = covariance01[n : n + kernelSize, m : m + kernelSize]
    cov11_win = covariance11[n : n + kernelSize, m : m + kernelSize]
    det_win = determinant[n : n + kernelSize, m : m + kernelSize]

    weight = sampledX * (cov00_win * sampledX + cov01_win * sampledY) + sampledY * (
        cov01_win * sampledX + cov11_win * sampledY
    )

    weightMatrix = np.exp(-0.5 * weight / smoothing**2) * det_win
    weightMatrix = weightMatrix.ravel(order="F")
    weightedFeatures = featureMatrix * weightMatrix[:, np.newaxis]
    regressionMatrix = (
        inv(featureMatrix.T @ (weightedFeatures) + np.eye(6) * 1e-7)
        @ weightedFeatures.T
    )

    upscaledPixel = np.zeros(channels)
    for c in range(channels):
        neighborhoodSamples = (
            image[n : n + kernelSize, m : m + kernelSize]
            if channels == 1
            else image[n : n + kernelSize, m : m + kernelSize, c]
        )
        upscaledPixel[c] = regressionMatrix[0] @ neighborhoodSamples.ravel(order="F")

    return (n * scaleFactor + i, m * scaleFactor + j, upscaledPixel)


def steeringKernelRegression_multiprocessing(
    image, smoothing, covarianceMatrices, scaleFactor, kernelSize
):

    height, width, channels = (
        image.shape if image.ndim == 3 else (image.shape[0], image.shape[1], 1)
    )
    kernelRadius = (kernelSize - 1) // 2
    upscaledImage = np.zeros((height * scaleFactor, width * scaleFactor, channels))
    y, x = np.meshgrid(
        np.linspace(
            -kernelRadius - (scaleFactor - 1) / scaleFactor,
            kernelRadius,
            kernelSize * scaleFactor,
        ),
        np.linspace(
            -kernelRadius - (scaleFactor - 1) / scaleFactor,
            kernelRadius,
            kernelSize * scaleFactor,
        ),
    )

    covariance00 = covarianceMatrices[0, 0, :, :]
    covariance01 = covarianceMatrices[0, 1, :, :]
    covariance11 = covarianceMatrices[1, 1, :, :]
    determinant = np.sqrt(np.linalg.det(covarianceMatrices.transpose(2, 3, 0, 1)))

    image = edgeMirror(image, [kernelRadius, kernelRadius])
    covariance00 = edgeMirror(covariance00, [kernelRadius, kernelRadius])
    covariance01 = edgeMirror(covariance01, [kernelRadius, kernelRadius])
    covariance11 = edgeMirror(covariance11, [kernelRadius, kernelRadius])
    determinant = edgeMirror(determinant, [kernelRadius, kernelRadius])

    args_list = [
        (
            image,
            smoothing,
            covariance00,
            covariance01,
            covariance11,
            determinant,
            scaleFactor,
            kernelSize,
            n,
            m,
            i,
            j,
            y,
            x,
            channels,
        )
        for i in range(scaleFactor)
        for j in range(scaleFactor)
        for n in range(height)
        for m in range(width)
    ]

    with mp.Pool(max(1, mp.cpu_count() - 1)) as pool:
        results = pool.map(process_block, args_list)

    for upsampledN, upsampledM, upscaledPixel in results:
        upscaledImage[upsampledN, upsampledM] = upscaledPixel

    return upscaledImage


def preprocessImages(hr, sr):
    if hr.shape != sr.shape:
        print(f"HR size: {hr.shape} | SR size: {sr.shape}")

        heightDiff = sr.shape[0] - hr.shape[0]
        widthDiff = sr.shape[1] - hr.shape[1]

        if heightDiff > 0:
            sr = sr[: hr.shape[0], :]
        elif heightDiff < 0:
            sr = np.pad(sr, ((abs(heightDiff), 0), (0, 0)), mode="constant")

        if widthDiff > 0:
            sr = sr[:, : hr.shape[1]]
        elif widthDiff < 0:
            sr = np.pad(sr, ((0, 0), (abs(widthDiff), 0)), mode="constant")
    return hr, sr


def mse(hr, sr):
    result = np.mean((hr - sr) ** 2, axis=(0, 1))
    result = np.mean(result)
    return result


def rmse(hr, sr):
    m = mse(hr, sr)
    result = np.sqrt(m)
    return result


def psnr(hr, sr):
    m = mse(hr, sr)
    if m == 0:
        return float("inf")
    maxPixel = 255.0
    result = 10 * np.log10((maxPixel**2) / m)
    return result


def ssim(hr, sr):
    if hr.ndim == 2:
        return structural_similarity(hr, sr)
    elif hr.ndim == 3:
        ssimR = structural_similarity(hr[:, :, 0], sr[:, :, 0])

        result = np.mean([ssimR])
        return result
    else:
        raise ValueError("Invalid input image")


def skr(image, scaleFactor, container: dict):

    # SKR on all channels
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    height, width, channels = image.shape

    start = time.time()
    yield SSEResponseModel(
        status="processing",
        message="Computing initial gradients",
        code=status.HTTP_200_OK,
    ).to_sse()

    upscale, gx, gy = upscaleWithClassicKernel(image, 0.5, 1, 5)

    windowSize = 3
    lambda_ = 1
    alpha = 0.05

    yield SSEResponseModel(
        status="processing",
        message="Calculating steering matrices",
        code=status.HTTP_200_OK,
    ).to_sse()

    C = steering(
        gx,
        gy,
        np.ones((height, width)),
        windowSize,
        lambda_,
        alpha,
    )

    yield SSEResponseModel(
        status="processing",
        message="Applying steering kernel regression",
        code=status.HTTP_200_OK,
    ).to_sse()

    smoothing = 0.75
    k = 7

    sr = steeringKernelRegression_multiprocessing(image, smoothing, C, scaleFactor, k)
    end = time.time()
    print(f"Thời gian chạy: {end - start:.6f} giây")

    sr = np.clip(sr, 0, 255).astype(np.uint8)

    container["sr"] = sr
    yield SSEResponseModel(
        status="completed",
        message="Processing completed!",
        code=status.HTTP_200_OK,
    ).to_sse()
    # return sr
