import os
import json


class Settings:
    def __init__(self):
        self.values = {
            "analysis_export_path": ".",
            "export_to_csv": True,
            "export_to_excel": True,
            "export_to_mat": True,
            "run_auto_detection": True
        }
        self.settings_file = "settings.json"
        if os.path.exists(self.settings_file):
            self.load_settings()
        else:
            self.export_settings()

    def get_option(self, option):
        return self.values.get(option, None)

    def update_option(self, option, value):
        if option in self.values:
            self.values[option] = value
            self.export_settings()
        else:
            raise ValueError(f"Option '{option}' does not exist.")

    def load_settings(self):
        with open(self.settings_file, 'r') as file:
            self.values = json.load(file)

    def export_settings(self):
        with open(self.settings_file, 'w') as file:
            json.dump(self.values, file, indent=4)