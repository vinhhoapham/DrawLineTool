import numpy as np
from collections import defaultdict


def slope_intercept_to_standard(slope, intercept):
    return slope, -1, intercept


def distance_from_point_line(point, line):
    slope, intercept = line
    x, y = point
    a, b, c = slope_intercept_to_standard(slope, intercept)
    distance = (a * x + b * y + c) / np.sqrt(a ** 2 + b ** 2)
    return distance


def edge_spread_function(image_array, line, radius):
    bins = defaultdict(list)
    mid_x, mid_y = np.shape(image_array)[1] // 2, np.shape(image_array)[0] // 2

    for col in range(mid_x - radius, mid_x + radius):
        for row in range(mid_y - radius, mid_y + radius):
            if (col - mid_x) ** 2 + (row - mid_y) ** 2 < radius ** 2:
                pixel = image_array[row, col]
                distance = int(distance_from_point_line(point=(col, row), line=line))
                bins[distance].append(pixel)

    esf = [(distance, np.mean(pixels)) for distance, pixels in bins.items()]
    return esf


def find_closest_distance_within_range(distances, pixels, percentile, range_width):
    threshold_value = np.percentile(pixels, percentile)
    low, high = threshold_value * (1 - range_width), threshold_value * (1 + range_width)

    min_dist = float('inf')
    closest_distance = 0

    def is_within_range(value, low, high):
        return low <= value <= high

    for distance, pixel in zip(distances, pixels):
        if is_within_range(pixel, low, high) and abs(distance) < min_dist:
            min_dist = abs(distance)
            closest_distance = distance

    return closest_distance


def rise_distance(image_array, line, radius):
    esf = edge_spread_function(image_array, line, radius)
    distances, pixels = zip(*esf)
    distances = np.array(distances)
    pixels = np.array(pixels)
    low_threshold = 25
    high_threshold = 75
    tolerance_range = 0.03

    low_threshold_distance = find_closest_distance_within_range(distances, pixels, low_threshold, tolerance_range)
    high_threshold_distance = find_closest_distance_within_range(distances, pixels, high_threshold, tolerance_range)

    return abs(high_threshold_distance - low_threshold_distance) / (2 * radius)
