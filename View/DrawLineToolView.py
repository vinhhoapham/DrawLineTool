from tkinter import Tk, filedialog, messagebox
from .ControlPanelComponent import ControlPanelComponent
from .BottomMenu import BottomMenu
from .ImageCanvas import ImageCanvas
from .SettingsPopupComponent import SettingsPopupComponent


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

        # ImageCanvas now takes a callback and the view model
        self.image_canvas = ImageCanvas(master, self.on_image_click, self.view_model)
        self.image_canvas.pack(expand=True, fill="both")

        self.master.bind('<Left>', self.prev_image)
        self.master.bind('<Right>', self.next_image)
        self.master.bind('<Escape>', self.clear_clicked_points)

    def load_folder(self):
        directory = filedialog.askdirectory()
        self.control_panel.update_checkbox_state(self.view_model.is_object_lighter)
        if self.view_model.get_option("run_auto_detection"):
            self.update_status("Running auto line detection script")

        if directory:
            image = self.view_model.load_directory(directory)
            self.image_canvas.display_image(image)
            self.update_status()
        else:
            self.update_status("No folder loaded")
            messagebox.showwarning("Invalid Selection", "No folder was selected. Please select a valid folder.")

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

    def next_image(self, event=None):
        image = self.view_model.cycle_next_file()
        self.control_panel.update_checkbox_state(self.view_model.is_object_lighter)
        self.image_canvas.display_image(image)
        self.update_status()

    def on_image_click(self, x, y):
        result = self.view_model.on_image_click(x, y)
        if result is not None:
            self.image_canvas.display_image(result)
            self.update_status()
            self.control_panel.update_checkbox_state(self.view_model.is_object_lighter)

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
