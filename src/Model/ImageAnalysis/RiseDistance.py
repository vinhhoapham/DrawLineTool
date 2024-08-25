import numpy as np
from collections import defaultdict
from scipy.optimize import curve_fit
from scipy.special import erf


def slope_intercept_to_standard(slope, intercept):
    return slope, -1, intercept


def distance_from_point_line(point, line):
    slope, intercept = line
    x, y = point
    a, b, c = slope_intercept_to_standard(slope, intercept)
    distance = (a * x + b * y + c) / np.sqrt(a ** 2 + b ** 2)
    return distance


def round_to_the_nearest_bin(n, sample_bins=4):
    return round(n * sample_bins) / sample_bins


def edge_spread_function(image_array, line, radius):
    bins = defaultdict(list)
    mid_x, mid_y = np.shape(image_array)[1] // 2, np.shape(image_array)[0] // 2

    for col in range(mid_x - radius, mid_x + radius):
        for row in range(mid_y - radius, mid_y + radius):
            if (col - mid_x) ** 2 + (row - mid_y) ** 2 < radius ** 2:
                pixel = image_array[row, col]
                distance = round_to_the_nearest_bin(distance_from_point_line(point=(col, row), line=line),
                                                    sample_bins=2)
                bins[distance].append(pixel)

    esf = [(distance, np.mean(pixels)) for distance, pixels in bins.items()]
    return esf


def edge_model(x, a1, a3, sigma, a2):
    return a1 * erf((x - a3) / (sigma * np.sqrt(2))) + a2


def rise_distance(image_array, line, radius):
    slope, intercept = line
    esf = edge_spread_function(image_array, line, radius)
    distances, pixels = zip(*esf)
    distances = np.array(distances)
    pixels = np.array(pixels)
    initial_guesses = [np.max(pixels), np.mean(distances), 10, 10]
    popt, _ = curve_fit(edge_model, distances, pixels, p0=initial_guesses, ftol=5e-5, xtol=5e-5)
    sigma = abs(popt[2])
    return sigma
