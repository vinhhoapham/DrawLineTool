from tkinter import Tk, filedialog, messagebox, ttk
from .ControlPanelComponent import ControlPanelComponent
from .BottomMenu import BottomMenu
from .ImageCanvas import ImageCanvas
from .SettingsPopupComponent import SettingsPopupComponent
import threading
import time


class MainView:
    def __init__(self, master, view_model):
        self.master = master
        self.view_model = view_model

        # Initialize components
        self.control_panel = ControlPanelComponent(master, self.load_folder, self.export_analysis,
                                                   self.open_settings, self.on_checkbox_toggle)
        self.control_panel.pack(side="top", fill="x")

        self.bottom_menu = BottomMenu(master, self.prev_image, self.next_image)
        self.bottom_menu.pack(side="bottom", fill="x")

        self.image_canvas = ImageCanvas(master, self.on_image_click, self.view_model)
        self.image_canvas.pack(expand=True, fill="both")

        self.master.bind('<Left>', self.prev_image)
        self.master.bind('<Right>', self.next_image)
        self.master.bind('<Escape>', self.clear_clicked_points)

    def update_image_info(self):
        image_info = self.view_model.get_current_image_info()
        print(f'Test')
        self.control_panel.update_image_info(**image_info)

    def load_folder(self):
        directory = filedialog.askdirectory()
        if not directory:
            self.update_status("No folder loaded")
            messagebox.showwarning("Invalid Selection", "No folder was selected. Please select a valid folder.")
            return

        self.control_panel.update_checkbox_state(self.view_model.is_object_lighter)
        self.update_status("Loading...")

        if self.view_model.get_option("run_auto_detection"):
            threading.Thread(target=self.run_auto_detection, args=(directory,), daemon=True).start()
            self.finalize_directory_loading()
        else:
            self.load_directory_without_auto_detection(directory)

        self.update_image_info()

    def export_analysis(self):
        try:
            self.view_model.model.export_analysis()
            messagebox.showinfo("Success", "Analysis exported successfully")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

        self.view_model.reset_state()
        self.reset_view_state()

    def reset_view_state(self):
        self.image_canvas.clear_image_set()
        self.update_status("No folder loaded")

    def prev_image(self, event=None):
        image = self.view_model.cycle_previous_file()
        self.control_panel.update_checkbox_state(self.view_model.is_object_lighter)
        self.image_canvas.display_image(image)
        self.update_status()
        self.update_image_info()

    def next_image(self, event=None):
        image = self.view_model.cycle_next_file()
        self.control_panel.update_checkbox_state(self.view_model.is_object_lighter)
        self.image_canvas.display_image(image)
        self.update_status()
        self.update_image_info()

    def on_image_click(self, x, y):
        result = self.view_model.on_image_click(x, y)
        if result is not None:
            self.image_canvas.display_image(result)
            self.update_status()
            self.control_panel.update_checkbox_state(self.view_model.is_object_lighter)
            self.update_image_info()

    def update_status(self, message=None):
        if message:
            status = message
        else:
            if self.view_model.is_folder_loaded():
                current_file = self.view_model.get_current_file_name()
                total_files = self.view_model.get_number_of_files()
                processed_images_count = len(self.view_model.model.analysis)
                status = f" File: {current_file}  | {self.view_model.model.current_file_index + 1}/{total_files}  |   {processed_images_count} images processed"
            else:
                status = "No folder loaded"

        self.bottom_menu.update_status(status)

    def open_settings(self):
        SettingsPopupComponent(self.master, self.view_model)

    def on_checkbox_toggle(self):
        self.view_model.is_object_lighter = self.control_panel.is_object_lighter_var.get()

    def clear_clicked_points(self, event=None):
        self.view_model.reset_clicked_points()
        self.image_canvas.clear_canvas_elements()

    def run_auto_detection(self, directory):
        self.start_time = time.time()
        self.view_model.load_directory(directory, self.update_progress)
        self.update_progress(100)
        self.next_image()

    def load_directory_without_auto_detection(self, directory):
        try:
            self.reset_view_state()
            self.view_model.load_directory(directory)
            self.finalize_directory_loading()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def finalize_directory_loading(self):
        image = self.view_model.get_image_to_display()
        self.image_canvas.display_image(image)
        self.update_status()

    def update_progress(self, progress):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        total_estimated_time = elapsed_time / progress * 100
        remaining_time = total_estimated_time - elapsed_time

        formatted_time = f"{remaining_time // 60:.0f}m {remaining_time % 60:.0f}s"
        status_message = f"Processing - {progress:.2f}% - Remaining: {formatted_time}"

        self.bottom_menu.update_progress(progress)
        self.bottom_menu.update_status(status_message)
