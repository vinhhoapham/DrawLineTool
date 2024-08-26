import os
import PIL

from .ImageAnalysis.AutoAnalysis import auto_detection, get_last_segment_of_path
from .ImageAnalysis.SingleImageAnalysis import SingleImageAnalysis
from .Settings import Settings
from .Export import *
from pathlib import Path


class DrawLineToolModel:

    def __init__(self):
        self.current_dir = None
        self.files = []
        self.current_file_index = None
        self.analysis = dict()
        self.settings = Settings()
        self.output_processed_folder = None

    def load_directory(self, directory,progress_callback=None):
        self.current_dir = directory
        self.files = [file for file in os.listdir(directory) if file.endswith((".JPG", ".jpeg", ".jpg", ".png"))]
        self.current_file_index = 0
        if self.settings.get_option("run_auto_detection"):
            self.analysis, self.output_processed_folder = auto_detection(directory, progress_callback)
        else:
            last_segment = get_last_segment_of_path(directory)
            self.output_processed_folder = f"{directory}/{last_segment}_processed"
            os.makedirs(self.output_processed_folder, exist_ok=True)

    def get_current_file(self):
        return self.files[self.current_file_index]

    def cycle_next_file(self):
        self.current_file_index += 1
        if self.current_file_index >= len(self.files):
            self.current_file_index = 0
        return self.get_current_file()

    def cycle_previous_file(self):
        self.current_file_index -= 1
        if self.current_file_index < 0:
            self.current_file_index = len(self.files) - 1
        return self.get_current_file()

    def get_current_image(self):
        current_image_path = os.path.join(self.current_dir, self.get_current_file())
        return PIL.Image.open(current_image_path).convert("L")

    def get_analysis_for_current_image(self, line_points, is_object_lighter):
        if line_points is not None:
            image = self.get_current_image()
            contrast, angle, blurriness, line_overlay_image = SingleImageAnalysis(
                image, line_points,
                is_object_lighter
            ).get_analysis()

            self.analysis[self.get_current_file()] = {
                'angle': angle,
                'contrast': contrast,
                'blurriness': blurriness
            }

            image_save_path = os.path.join(self.output_processed_folder, f"{Path(self.get_current_file()).stem}_processed.jpg")

            if os.path.exists(image_save_path):
                os.remove(image_save_path)
            line_overlay_image.save(image_save_path)

        else:
            raise ValueError("No line points provided")

    def reset(self):
        self.current_dir = None
        self.files = []
        self.current_file_index = None
        self.analysis = dict()

    def export_analysis(self):
        export_path = self.settings.get_option("analysis_export_path")
        analysis_formatted = [
            {**data, 'file': filename} for filename, data in self.analysis.items()
        ]
        if self.settings.get_option("export_to_csv"):
            export_to_csv(analysis_formatted,os.path.join(export_path, "analysis.csv"))
        if self.settings.get_option("export_to_excel"):
            export_to_excel(analysis_formatted,os.path.join(export_path, "analysis.xlsx"))
        if self.settings.get_option("export_to_mat"):
            export_to_mat(analysis_formatted,os.path.join(export_path, "analysis.mat"))

        self.reset()

