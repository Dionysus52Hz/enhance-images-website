import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.fft import fft2, ifft2
from scipy.spatial import Delaunay
from scipy.interpolate import NearestNDInterpolator, LinearNDInterpolator


def downsample(image, factor):
    if image.ndim == 2:
        return image[::factor, ::factor]
    elif image.ndim == 3:
        return image[::factor, ::factor, :]
    else:
        raise ValueError("Invalid input image")


def shiftMatrix(matrix, shiftX, shiftY):
    M = np.float32([[1, 0, shiftX], [0, 1, shiftY]])
    return cv2.warpAffine(
        matrix, M, (matrix.shape[1], matrix.shape[0]), borderMode=cv2.BORDER_REFLECT
    )


def rotateMatrix(matrix, centerX, centerY, angle, scale=1.0):
    M = cv2.getRotationMatrix2D((centerX, centerY), angle, scale)
    return cv2.warpAffine(
        matrix, M, (matrix.shape[1], matrix.shape[0]), borderMode=cv2.BORDER_REFLECT
    )


def generateLRImages(image):
    shifts = [
        (0.00, 0.00),
        (0.075, -0.075),
        (0.05, -0.05),
        (-0.075, 0.075),
    ]

    # shifts = [(0, 0)]
    angles = [0, 0, 0, 0]
    # angles = [0]
    centerX = image.shape[1] // 2
    centerY = image.shape[0] // 2
    LRImages = [
        rotateMatrix(shiftMatrix(image, shiftX, shiftY), centerX, centerY, angle)
        for (shiftX, shiftY), angle in zip(shifts, angles)
    ]
    return LRImages


def computeGaussianDerivatives(image, centerX, centerY, sigma=1.0):
    N, M = image.shape
    h = np.zeros((N, M), dtype=np.float32)
    hx = np.zeros((N, M), dtype=np.float32)
    hy = np.zeros((N, M), dtype=np.float32)
    for y in range(N):
        for x in range(M):
            exponent = -(((x - centerX) ** 2 + (y - centerY) ** 2) / (2 * sigma**2))
            h[y, x] = (1 / (2 * np.pi * sigma**2)) * np.exp(exponent)
            hx[y, x] = -(x - centerX) / (2 * np.pi * sigma**4) * np.exp(exponent)
            hy[y, x] = -(y - centerY) / (2 * np.pi * sigma**4) * np.exp(exponent)
    return h, hx, hy


def motionEstimation(reference, centerX, centerY, warpImages):
    ME = []
    h, hx, hy = computeGaussianDerivatives(reference, centerX, centerY)
    fftReference = fft2(reference)
    fftH = fft2(h)
    fftHx = fft2(hx)
    fftHy = fft2(hy)

    T1 = np.real(ifft2(fftReference * fftH))
    T2 = np.real(ifft2(fftReference * fftHx))
    T3 = np.real(ifft2(fftReference * fftHy))

    N, M = reference.shape
    R = np.zeros((N, M), dtype=np.float32)
    for y in range(N):
        for x in range(M):
            R[y, x] = T3[y, x] * (x - centerX) - T2[y, x] * (y - centerY)

    A = np.zeros((3, 3))

    A[0, 0] = np.sum(T2 * T2)
    A[0, 1] = np.sum(T2 * T3)
    A[0, 2] = np.sum(R * T2)

    A[1, 0] = np.sum(T2 * T3)
    A[1, 1] = np.sum(T3 * T3)
    A[1, 2] = np.sum(R * T3)

    A[2, 0] = np.sum(R * T2)
    A[2, 1] = np.sum(R * T3)
    A[2, 2] = np.sum(R * R)

    inversedA = np.linalg.inv(A)

    for image in warpImages:
        b = np.zeros((3, 1))
        T4 = np.real(ifft2(fft2(image) * fftH))
        b[0] = np.sum(T2 * (T4 - T1))
        b[1] = np.sum(T3 * (T4 - T1))
        b[2] = np.sum(R * (T4 - T1))
        m = inversedA @ b
        ME.append(m.T.ravel() * -1)

    return ME


def gridMapping(LRImages, motionVectors, scaleFactor):
    points = []
    values = []
    for image, (a, b, theta) in zip(LRImages, motionVectors):
        heightLR, widthLR = LRImages[0].shape[:2]
        heightSR = LRImages[0].shape[0] * scaleFactor
        widthSR = LRImages[0].shape[1] * scaleFactor
        SR = np.zeros((heightSR, widthSR), dtype=np.float32)
        x0 = widthLR // 2
        y0 = heightLR // 2
        for y in range(heightLR):
            for x in range(widthLR):
                x_mapped = (
                    scaleFactor * (x - x0) * np.cos(theta)
                    - scaleFactor * (y - y0) * np.sin(theta)
                    + a * scaleFactor
                    + x0 * scaleFactor
                )

                y_mapped = (
                    scaleFactor * (y - y0) * np.cos(theta)
                    + scaleFactor * (x - x0) * np.sin(theta)
                    + b * scaleFactor
                    + scaleFactor * y0
                )

                if (0 <= x_mapped <= widthSR - 1) and (0 <= y_mapped <= heightSR - 1):
                    points.append((round(y_mapped, 4), round(x_mapped, 4)))
                    values.append(image[y, x])
                    SR[round(y_mapped), round(x_mapped)] = image[y, x]

    values = np.array(values)
    return points, values, SR


def findQueryPoints(SRGridShape, mappedPoints):
    height, width = SRGridShape
    mask = np.zeros((height, width))
    i = 0
    for y, x in mappedPoints:
        if y.is_integer() and x.is_integer():
            y = int(y)
            x = int(x)
            mask[y, x] = 1
            i += 1

    queryPoints = np.column_stack(np.where(mask == 0))
    return queryPoints


def circumcenter(A, B, C):
    Ay, Ax = A
    By, Bx = B
    Cy, Cx = C
    bx, by = Bx - Ax, By - Ay
    cx, cy = Cx - Ax, Cy - Ay

    d = bx * cy - by * cx

    if abs(d) < 1e-10:
        return None

    d *= 2
    b2 = bx * bx + by * by
    c2 = cx * cx + cy * cy

    x = (cy * b2 - by * c2) / d
    y = (bx * c2 - cx * b2) / d

    X = x + Ax
    Y = y + Ay

    return (Y, X)


def isPointInCircumcircle(A, B, C, D):
    Ay, Ax = A
    By, Bx = B
    Cy, Cx = C
    Dy, Dx = D
    matrix = np.array(
        [
            [Ax - Dx, Ay - Dy, (Ax - Dx) ** 2 + (Ay - Dy) ** 2],
            [Bx - Dx, By - Dy, (Bx - Dx) ** 2 + (By - Dy) ** 2],
            [Cx - Dx, Cy - Dy, (Cx - Dx) ** 2 + (Cy - Dy) ** 2],
        ]
    )
    h = np.linalg.det(matrix)
    if h > 0:
        return True
    else:
        return False


def determinant(A, B, C):
    matrix = np.array([[A[1], A[0], 1], [B[1], B[0], 1], [C[1], C[0], 1]])
    return np.linalg.det(matrix)


def interpolate(mappedPoints, mappedValues, delaunayMesh, q):
    n = 0
    d = 0
    tr = delaunayMesh.find_simplex(q)
    neighborsTr = delaunayMesh.neighbors[tr]
    neighborsTr = np.append(neighborsTr, tr)
    for t in neighborsTr:
        if t == -1:
            continue
        vertexIndexes = delaunayMesh.simplices[t]  # Chi so cac dinh
        vertices = mappedPoints[vertexIndexes]
        if not isPointInCircumcircle(vertices[0], vertices[1], vertices[2], q):
            continue
        tc = circumcenter(vertices[0], vertices[1], vertices[2])
        if tc is None:
            continue
        cc = []
        for i in range(3):
            cci = circumcenter(q, vertices[(i + 1) % 3], vertices[(i + 2) % 3])
            cc.append(cci)

        for i in range(3):
            k = 0.5 * determinant(cc[(i + 1) % 3], cc[(i + 2) % 3], tc)
            n += mappedValues[vertexIndexes[i]] * k
            d += k
    if d == 0:
        d = 1e-10
    fq = n / d
    return fq


def interpolate2(mappedPoints, mappedValues, delaunayMesh, q, alternativeInterpolator):
    n = 0
    d = 0
    weights = {}
    tr = delaunayMesh.find_simplex(q)
    neighborsTr = delaunayMesh.neighbors[tr]
    neighborsTr = np.append(neighborsTr, tr)
    for t in neighborsTr:
        d = 0
        if t == -1:
            continue
        vertexIndexes = delaunayMesh.simplices[t]  # Chi so cac dinh
        vertices = mappedPoints[vertexIndexes]
        if not isPointInCircumcircle(vertices[0], vertices[1], vertices[2], q):
            continue
        tc = circumcenter(vertices[0], vertices[1], vertices[2])
        if tc is None:
            continue
        cc = []
        for i in range(3):
            cci = circumcenter(q, vertices[(i + 1) % 3], vertices[(i + 2) % 3])
            if cci is None:
                continue
            cc.append(cci)

        for i in range(len(cc)):
            k = 0.5 * abs(determinant(cc[(i + 1) % len(cc)], cc[(i + 2) % len(cc)], tc))
            j = vertexIndexes[i]
            if weights.get(j):
                weights.update({j: weights[j] + k})
            else:
                weights.update({j: k})
    if weights:
        total = sum(weights.values())
        weights = {key: value / total for key, value in weights.items()}
        fq = sum(mappedValues[key] * value for key, value in weights.items())
    else:
        fq = alternativeInterpolator(q[0], q[1])
    return fq


import multiprocessing as mp


def interpolate_point(args):
    p, points, values, tri, alternativeInterpolator = args
    return tuple(p), interpolate2(
        points, values, tri, p, alternativeInterpolator=alternativeInterpolator
    )


def parallel_interpolation(points, values, tri, queryPoints):
    interpolator = LinearNDInterpolator(points, values)

    with mp.Pool(max(1, mp.cpu_count() - 1)) as pool:
        results = pool.map(
            interpolate_point,
            [(p, points, values, tri, interpolator) for p in queryPoints],
        )

    return dict(results)


def nni(image, scaleFactor):
    start = time.time()
    image = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    Y, Cr, Cb = cv2.split(image)
    LRImages = generateLRImages(Y)

    centerX = Y.shape[1] // 2
    centerY = Y.shape[0] // 2

    A = motionEstimation(Y, centerX, centerY, LRImages)

    points, values, SR = gridMapping(LRImages, A, scaleFactor)
    points = np.array(points)

    queryPoints = findQueryPoints(
        (Y.shape[0] * scaleFactor, Y.shape[1] * scaleFactor), points
    )

    print(f"Number of known points: {(points.shape)}")
    print(values.shape)
    print(f"Number of unknown points: {len(queryPoints)}")
    print(f"Total points of SR: {Y.shape[1] * Y.shape[0] * scaleFactor**2}")

    tri = Delaunay(points)
    result = {tuple(p): 0 for p in queryPoints}
    interpolator = LinearNDInterpolator(points, values)

    for p in queryPoints:
        fq = interpolate2(points, values, tri, p, alternativeInterpolator=interpolator)
        result[tuple(p)] = fq

    end = time.time()
    print(f"Thời gian chạy: {end - start:.6f} giây")

    keys = np.array(list(result.keys()))
    values = np.array(list(result.values()))
    SR[keys[:, 0], keys[:, 1]] = values

    SR = np.clip(SR, 0, 255).astype(np.uint8)
    Cr = cv2.resize(
        Cr,
        (Cr.shape[1] * scaleFactor, Cr.shape[0] * scaleFactor),
        interpolation=cv2.INTER_LINEAR,
    )
    Cb = cv2.resize(
        Cb,
        (Cb.shape[1] * scaleFactor, Cb.shape[0] * scaleFactor),
        interpolation=cv2.INTER_LINEAR,
    )

    SR = cv2.merge([SR, Cr, Cb])
    SR = cv2.cvtColor(SR, cv2.COLOR_YCrCb2RGB)
    return SR
