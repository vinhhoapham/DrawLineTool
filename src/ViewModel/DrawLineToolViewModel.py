import os
from PIL import Image


class DrawLineToolViewModel:
    def __init__(self, model):
        self.model = model
        self.folder_loaded = False
        self.is_displaying_original_image = False
        self.clicked_points = []
        self.is_object_lighter = False

    def get_current_file_name(self):
        return self.model.get_current_file()

    def get_number_of_files(self):
        return len(self.model.files)

    def get_image_to_display(self, force_to_display_original=False):
        if (not force_to_display_original) and self.model.settings.get_option("run_auto_detection"):
            original_filename = self.model.get_current_file()  # The original file name
            processed_filename = f"{os.path.splitext(original_filename)[0]}_processed.jpg"
            if processed_filename in os.listdir(self.model.output_processed_folder):
                image = Image.open(f"{self.model.output_processed_folder}/{processed_filename}")
                return image

        self.is_displaying_original_image = True
        return self.model.get_current_image()

    def load_directory(self, directory, progress_callback=None):
        self.model.load_directory(directory, progress_callback)
        self.folder_loaded = True
        self.is_object_lighter = False
        return self.get_image_to_display()

    def is_folder_loaded(self):
        return self.folder_loaded

    def cycle_next_file(self):
        self.model.cycle_next_file()
        if not self.model.settings.get_option("run_auto_detection"):
            self.is_displaying_original_image = False
        self.is_object_lighter = False
        return self.get_image_to_display()

    def cycle_previous_file(self):
        self.model.cycle_previous_file()
        if not self.model.settings.get_option("run_auto_detection"):
            self.is_displaying_original_image = False
        self.is_object_lighter = False
        return self.get_image_to_display()

    def update_settings(self, option, value):
        self.model.settings.update_option(option, value)

    def get_option(self, option):
        return self.model.settings.get_option(option)

    def on_image_click(self, x, y):
        if not self.is_displaying_original_image:
            self.is_displaying_original_image = True
            image = self.get_image_to_display(True)
            return image
        else:
            if len(self.clicked_points) < 2:
                self.clicked_points.append((x, y))
                if len(self.clicked_points) == 2:
                    self.model.get_analysis_for_current_image(self.clicked_points, self.is_object_lighter)
                    self.clicked_points.clear()
                    self.is_displaying_original_image = False
                    self.is_object_lighter = False
                    return self.cycle_next_file()
            return None

    def reset_clicked_points(self):
        self.clicked_points.clear()

    def reset_state(self):
        self.folder_loaded = False
        self.is_displaying_original_image = False
        self.clicked_points.clear()
        self.is_object_lighter = False
