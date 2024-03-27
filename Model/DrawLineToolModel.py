import os
import PIL
import pandas as pd
from .ImageAnalysis.AutoAnalysis import auto_detection, get_last_segment_of_path
from .ImageAnalysis.SingleImageAnalysis import SingleImageAnalysis
from .Settings import Settings
from scipy.io import savemat


class DrawLineToolModel:

    def __init__(self):
        self.current_dir = None
        self.files = []
        self.current_file_index = None
        self.analysis = pd.DataFrame()
        self.settings = Settings()
        self.output_processed_folder = None

    def load_directory(self, directory,progress_callback=None):
        self.current_dir = directory
        self.files = [file for file in os.listdir(directory) if file.endswith((".JPG", ".jpeg"))]
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

    def get_analysis_for_current_image(self, line_points, is_object_lighter, diameter=236):
        if line_points is not None:
            image = self.get_current_image()
            contrast, angle, blurriness, line_overlay_image = SingleImageAnalysis(image, line_points,
                                                                                  is_object_lighter).get_analysis()
            if self.settings.get_option("run_auto_detection"):
                filename = self.get_current_file()
                analysis = self.analysis[self.analysis["file_name"] == filename]
                new_data = pd.DataFrame({
                    "file_name": [filename],
                    "contrast": [contrast],
                    "angle": [angle],
                    "blurriness": [blurriness]
                })
                if analysis.empty:
                    self.analysis = pd.concat([self.analysis, new_data], ignore_index=True)
                else:
                    for col in ["contrast", "angle", "blurriness"]:
                        self.analysis.loc[self.analysis["file_name"] == filename, col] = new_data[col].iloc[0]
            else:
                new_data = pd.DataFrame({
                    "file_name": [self.get_current_file()],
                    "contrast": [contrast],
                    "angle": [angle],
                    "blurriness": [blurriness]
                })
                self.analysis = pd.concat([self.analysis, new_data], ignore_index=True)

            line_overlay_image.save(
                os.path.join(self.output_processed_folder, f"{self.get_current_file()}_processed.jpg"))

        else:
            raise ValueError("No line points provided")

    def export_analysis(self):
        if self.analysis.empty:
            raise ValueError("No analysis to export")
        export_path = self.settings.get_option("analysis_export_path")

        if self.settings.get_option("export_to_csv"):
            self.analysis.to_csv(os.path.join(export_path, "analysis.csv"), index=False)
        if self.settings.get_option("export_to_excel"):
            self.analysis.to_excel(os.path.join(export_path, "analysis.xlsx"), index=False)
        if self.settings.get_option("export_to_mat"):
            savemat(os.path.join(export_path, "analysis.mat"), {"analysis": self.analysis.to_dict(orient="list")})

        self.current_dir = None
        self.files = []
        self.current_file_index = None
        self.analysis = pd.DataFrame()
