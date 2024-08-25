import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import os
from pathlib import Path
import time
from .SingleImageAnalysis import calculate_image_property_from_cartesian_coordinate

def get_last_segment_of_path(path):
    return Path(path).name


def open_and_convert_to_grayscale(image_path):
    original_image = Image.open(image_path).convert('L')
    return np.array(original_image)


def apply_gaussian_blur(image, kernel_size=(5, 5), sigmaX=5, sigmaY=5):
    return cv2.GaussianBlur(image, kernel_size, sigmaX, sigmaY)


def crop_to_circle(image, diameter):
    midX, midY = image.shape[1] // 2, image.shape[0] // 2
    radius = diameter // 2
    return image[midY - radius:midY + radius, midX - radius:midX + radius]


def kmeans_clustering(image):
    data = [(row, col, image[row, col])
            for row in range(image.shape[0])
            for col in range(image.shape[1])
            if (row - 118) ** 2 + (col - 118) ** 2 <= 118 ** 2]

    kmeans = KMeans(n_clusters=2).fit(data)
    labels = kmeans.labels_

    clustered_image = np.zeros(image.shape, dtype=np.uint8)
    for idx, (row, col, _) in enumerate(data):
        clustered_image[row, col] = 255 if labels[idx] == 1 else 0

    return clustered_image


def edge_detection(image):
    return cv2.Canny(image, 50, 100, apertureSize=3)


def find_closest_line_to_center(lines, center):
    min_distance = float('inf')
    closest_line = None

    for line in lines:
        rho, theta = line[0]
        distance = abs(rho - center[0] * np.cos(theta) - center[1] * np.sin(theta))
        if distance < min_distance:
            min_distance = distance
            closest_line = line

    return closest_line


def calculate_image_property(image, line, mid_x, mid_y, diameter):
    rho, theta = line[0]
    a, b = np.cos(theta), np.sin(theta)
    radius = diameter // 2
    x0 = a * rho + mid_x - radius
    y0 = b * rho + mid_y - radius
    x1 = int(x0 + 10000 * (-b))
    y1 = int(y0 + 10000 * (a))
    x2 = int(x0 - 10000 * (-b))
    y2 = int(y0 - 10000 * (a))
    point1, point2 = (x1, y1), (x2,y2)
    adjusted_angle, contrast, blurriness = calculate_image_property_from_cartesian_coordinate(
        image=image, line_points=(point1, point2),
        mid_x = mid_x, mid_y=mid_y, diameter=diameter, is_object_lighter= False
    )
    return adjusted_angle, contrast, blurriness


def draw_line_and_text_from_auto_detection(image, line, angle, contrast, blurriness, mid_x, mid_y, diameter, color=(0, 0, 255)):
    if line is not None:
        rho, theta = line[0]
        a, b = np.cos(theta), np.sin(theta)
        radius = diameter // 2
        x0 = a * rho + mid_x - radius
        y0 = b * rho + mid_y - radius
        x1 = int(x0 + 10000 * (-b))
        y1 = int(y0 + 10000 * a)
        x2 = int(x0 - 10000 * (-b))
        y2 = int(y0 - 10000 * a)
        cv2.line(image, (x1, y1), (x2, y2), color, 2)

    info_text = f'Angle: {angle:.3f} deg, Contrast: {contrast:.3f}, Blurriness: {blurriness:.5f}'
    cv2.putText(image, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (147, 155, 26), 2)


def process_image(image_path, diameter=236):
    original_image = open_and_convert_to_grayscale(image_path)
    original_color_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
    blurred_image = apply_gaussian_blur(original_image)
    cropped_image = crop_to_circle(blurred_image, diameter)
    clustered_image = kmeans_clustering(cropped_image)
    edges = edge_detection(clustered_image)

    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=50)
    radius = diameter // 2
    mid_x, mid_y = original_image.shape[1] // 2, original_image.shape[0] // 2
    closest_line = find_closest_line_to_center(lines, (mid_x, mid_y)) if lines is not None else None

    line_angle, contrast, blurriness = (None, None, None)
    if closest_line is not None:
        line_angle, contrast, blurriness = calculate_image_property(original_image, closest_line, mid_x, mid_y,
                                                                    diameter)
        draw_line_and_text_from_auto_detection(original_color_image, closest_line, line_angle,
                           contrast, blurriness, mid_x, mid_y, diameter)
        draw_line_and_text_from_auto_detection(clustered_image, closest_line, line_angle, contrast, blurriness,
                           radius, radius, diameter, color=(155, 155, 155))

    cv2.circle(original_color_image, (mid_x, mid_y), radius, (0, 255, 0), 2)

    return original_color_image, clustered_image, line_angle, contrast, blurriness


def auto_detection(folder_path, progress_callback=None):
    start_time = time.time()

    last_segment = get_last_segment_of_path(folder_path)
    output_folder = f"{folder_path}/{last_segment}_processed"
    os.makedirs(output_folder, exist_ok=True)

    results = dict()
    image_files = [file for file in os.listdir(folder_path) if file.endswith((".JPG", ".jpeg"))]
    total_files = len(image_files)
    for index, filename in enumerate(image_files):
        image_path = os.path.join(folder_path, filename)
        processed_image, clustered_image, angle, contrast, blurriness = process_image(image_path)

        if progress_callback:
            progress = (index + 1) / total_files * 100
            progress_callback(progress)

        elapsed_time = time.time() - start_time
        estimated_total_time = elapsed_time / (index + 1) * total_files
        remaining_time = estimated_total_time - elapsed_time

        if angle is not None and contrast is not None:
            results[filename] = {
                'angle': angle,
                'contrast': contrast,
                'blurriness': blurriness
            }

        # Save the processed image
        processed_image_path = os.path.join(output_folder, f"{Path(filename).stem}_processed.jpg")
        if os.path.exists(processed_image_path):
            os.remove(processed_image_path)
        cv2.imwrite(processed_image_path, processed_image)

    return results, output_folder
