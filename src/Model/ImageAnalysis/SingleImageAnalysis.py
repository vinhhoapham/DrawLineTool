import numpy as np
from PIL import Image
import cv2
from .RiseDistance import rise_distance


def calculate_image_property_from_cartesian_coordinate(image, line_points, mid_x, mid_y, diameter, is_object_lighter):
    (x1, y1), (x2, y2) = line_points
    dx = x2 - x1
    dy = y2 - y1

    is_horizontal = abs(dx) > abs(dy)

    slope = dy / dx if dx != 0 else float('inf')
    intercept = y1 - slope * x1

    radius = diameter // 2
    side1_pixels = []
    side2_pixels = []

    for x in range(mid_x - radius, mid_x + radius):
        for y in range(mid_y - radius, mid_y + radius):
            if (x - mid_x) ** 2 + (y - mid_y) ** 2 < radius ** 2:
                line_y = slope * x + intercept if is_horizontal else (y - intercept) / slope if slope != 0 else x
                distance = (y - line_y) if is_horizontal else (x - line_y)
                pixel_value = image[y, x]
                if distance >= 0:
                    side1_pixels.append(pixel_value)
                else:
                    side2_pixels.append(pixel_value)

    p1 = np.mean(side1_pixels) if side1_pixels else 0
    p2 = np.mean(side2_pixels) if side2_pixels else 0
    contrast = abs((p2 - p1) / (p2 + p1)) if (p2 + p1) != 0 else 0

    angle = np.arctan(slope) * 180 / np.pi
    darker_side_on_left_or_above = p1 > p2

    blurriness = rise_distance(image_array=image, line=(slope, intercept), radius=diameter // 2)
    darker_side_on_left_or_above = (darker_side_on_left_or_above == (not is_object_lighter))

    if is_horizontal:
        base_angle = 360 if darker_side_on_left_or_above else 180
        adjusted_angle = (base_angle - angle) % 360
    else:
        if darker_side_on_left_or_above:
            if angle < 0:
                adjusted_angle = abs(angle)
            else:
                adjusted_angle = 90 + abs(90 - angle)
        else:
            if angle < 0:
                adjusted_angle = 270 - abs(90 - abs(angle))
            else:
                adjusted_angle = 270 + abs(90 - angle)

    return adjusted_angle, contrast, blurriness


class SingleImageAnalysis:
    def __init__(self, image, line_points, is_object_lighter, diameter=236):
        self.image = image
        self.line_points = line_points
        self.diameter = diameter
        self.is_object_lighter = is_object_lighter

    def draw_line_and_text_from_cartesian_coordinate(self, image, line_points, angle, contrast, blurriness,
                                                     color=(0, 0, 255)):
        (x1, y1), (x2, y2) = line_points
        cv2.line(image, (x1, y1), (x2, y2), color, 2)
        mid_x, mid_y = self.image.size[0] // 2, self.image.size[1] // 2
        cv2.circle(image, (mid_x, mid_y), self.diameter // 2, (0, 255, 0), 2)
        info_text = f'Angle: {angle:.3f} deg, Contrast: {contrast:.3f}, Blurriness: {blurriness:.5f}'
        cv2.putText(image, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (147, 155, 26), 2)

    def get_analysis(self):
        line_overlay_image = self.image.copy()
        line_overlay_image_np = np.array(line_overlay_image)
        mid_x, mid_y = line_overlay_image.size[0] // 2, line_overlay_image.size[1] // 2

        # Calculate properties using Cartesian coordinates
        angle, contrast, blurriness = calculate_image_property_from_cartesian_coordinate(line_overlay_image_np,
                                                                                         self.line_points,
                                                                                         mid_x, mid_y, self.diameter,
                                                                                         self.is_object_lighter)

        line_overlay_image_color = cv2.cvtColor(line_overlay_image_np, cv2.COLOR_BGR2RGB)
        self.draw_line_and_text_from_cartesian_coordinate(line_overlay_image_color, self.line_points, angle,
                                                          contrast, blurriness, self.diameter)

        line_overlay_image_pil = Image.fromarray(line_overlay_image_color)
        return contrast, angle, blurriness, line_overlay_image_pil
