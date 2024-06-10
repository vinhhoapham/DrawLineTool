import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import os
from pathlib import Path
import pandas as pd
import time
from .RiseDistance import rise_distance

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


def measure_blurriness(image_array, line, diameter):
    bluriness_measurement = rise_distance(image_array, line, diameter // 2 )
    return bluriness_measurement


def calculate_image_property(image, line, mid_x, mid_y, diameter, debug_mode=False):
    rho, theta = line[0]
    a, b = np.cos(theta), np.sin(theta)
    side1_pixels = []
    side2_pixels = []
    radius = diameter // 2
    x0 = a * rho + mid_x - radius
    y0 = b * rho + mid_y - radius
    x1 = int(x0 + 10000 * (-b))
    y1 = int(y0 + 10000 * (a))
    x2 = int(x0 - 10000 * (-b))
    y2 = int(y0 - 10000 * (a))
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    is_horizontal = dx > dy
    A = np.array([[x1, 1], [x2, 1]]) if is_horizontal else np.array([[y1, 1], [y2, 1]])
    B = np.array([y1, y2]) if is_horizontal else np.array([x1, x2])

    slope, intercept = np.linalg.solve(A, B)

    for x in range(mid_x - radius, mid_x + radius):
        for y in range(mid_y - radius, mid_y + radius):
            if (x - mid_x) ** 2 + (y - mid_y) ** 2 < radius ** 2:
                line = slope * x + intercept if is_horizontal else slope * y + intercept
                distance = (y - line) if is_horizontal else (x - line)
                pixel_value = image[y, x]
                if distance >= 0:
                    side1_pixels.append(pixel_value)
                elif distance < 0:
                    side2_pixels.append(pixel_value)

    p1 = np.mean(side1_pixels) if side1_pixels else 0
    p2 = np.mean(side2_pixels) if side2_pixels else 0
    contrast = abs((p2 - p1) / (p2 + p1)) if (p2 + p1) != 0 else 0
    darker_side_on_left_or_above = p1 > p2

    line_angle = theta * 180 / np.pi
    if debug_mode:
        print(f"Line angle: {line_angle}")
    adjusted_angle = line_angle

    # Adjust the angle based on the sides of the object (darker side)

    if is_horizontal:
        if darker_side_on_left_or_above:
            if debug_mode:
                print(f"Darker side is above, line angle: {line_angle}")
            adjusted_angle = abs(90 - line_angle)
        else:
            if debug_mode:
                print(f"Darker side is below, line angle: {line_angle}")
            adjusted_angle = abs(270 - line_angle)
    else:
        if darker_side_on_left_or_above:
            if debug_mode:
                print(f"Darker side is on the left, line angle: {line_angle}")
            adjusted_angle = abs(line_angle - 90)
        else:
            if debug_mode:
                print(f"Darker side is on the right, line angle: {line_angle}")
            if line_angle < 90:
                line_angle += 180
            adjusted_angle = abs(line_angle + 90)

    slope = abs(dy / dx) if dx != 0 else float('inf')
    intercept = y1 - slope * x1
    blurriness = measure_blurriness(image, line=(slope, intercept), diameter=diameter)
    return adjusted_angle, contrast, blurriness


def draw_line_and_text(image, line, angle, contrast, blurriness, mid_x, mid_y, diameter, color=(0, 0, 255)):
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
        line_angle, contrast, blurriness = calculate_image_property(original_image, closest_line, mid_x, mid_y,diameter)
        draw_line_and_text(original_color_image, closest_line, line_angle,
                           contrast, blurriness, mid_x, mid_y, diameter)
        draw_line_and_text(clustered_image, closest_line, line_angle, contrast, blurriness,
                           radius, radius, diameter, color=(155, 155, 155))

    # Draw the circle at the center of the original color image with the diameter
    cv2.circle(original_color_image, (mid_x, mid_y), radius, (0, 255, 0), 2)

    return original_color_image, clustered_image, line_angle, contrast, blurriness


def auto_detection(folder_path, progress_callback=None):
    start_time = time.time()

    last_segment = get_last_segment_of_path(folder_path)
    output_folder = f"{folder_path}/{last_segment}_processed"
    os.makedirs(output_folder, exist_ok=True)

    results = []
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
            results.append({
                'file_name': filename,
                'angle': angle,
                'contrast': contrast,
                'blurriness': blurriness
            })

        # Save the processed image
        processed_image_path = os.path.join(output_folder, f"{Path(filename).stem}_processed.jpg")
        cv2.imwrite(processed_image_path, processed_image)

    results_dataframe = pd.DataFrame(results)
    return results_dataframe, output_folder
