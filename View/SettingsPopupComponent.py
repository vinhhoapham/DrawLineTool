from tkinter import Toplevel, Label, Entry, Button, Checkbutton, BooleanVar, StringVar, filedialog, Frame


class SettingsPopupComponent:
    def __init__(self, parent, view_model):
        self.view_model = view_model
        self.top = Toplevel(parent)
        self.top.title("Settings")

        # Initialize variables
        self.export_to_csv_var = BooleanVar(value=self.view_model.get_option("export_to_csv"))
        self.export_to_excel_var = BooleanVar(value=self.view_model.get_option("export_to_excel"))
        self.export_to_mat_var = BooleanVar(value=self.view_model.get_option("export_to_mat"))
        self.run_auto_detection_var = BooleanVar(value=self.view_model.get_option("run_auto_detection"))

        # Auto Detection Checkbox
        auto_detect_frame = Frame(self.top)
        auto_detect_frame.pack(fill='x', padx=10, pady=5)
        self.run_auto_detection_button = Checkbutton(auto_detect_frame, text="Run auto detection",
                                                     variable=self.run_auto_detection_var)
        self.run_auto_detection_button.pack(side='left')

        # Export Options Checkboxes
        export_frame = Frame(self.top)
        export_frame.pack(fill='x', padx=10, pady=5)
        self.export_to_csv_button = Checkbutton(export_frame, text="Export to CSV", variable=self.export_to_csv_var)
        self.export_to_csv_button.pack(side='left')
        self.export_to_excel_button = Checkbutton(export_frame, text="Export to Excel",
                                                  variable=self.export_to_excel_var)
        self.export_to_excel_button.pack(side='left')
        self.export_to_mat_button = Checkbutton(export_frame, text="Export to MAT", variable=self.export_to_mat_var)
        self.export_to_mat_button.pack(side='left')

        # Analysis Export Path
        export_path_frame = Frame(self.top)
        export_path_frame.pack(fill='x', padx=10, pady=5)
        self.analysis_export_path_label = Label(export_path_frame, text="Analysis Export Path:")
        self.analysis_export_path_label.pack(side='left')
        self.analysis_export_path_var = StringVar(value=self.view_model.get_option("analysis_export_path"))
        self.analysis_export_path_entry = Entry(export_path_frame, textvariable=self.analysis_export_path_var, width=50)
        self.analysis_export_path_entry.pack(side='left', padx=5)
        self.browse_button = Button(export_path_frame, text="Browse", command=self.browse_path)
        self.browse_button.pack(side='left')

        # Save Button
        self.save_button = Button(self.top, text="Save", command=self.save_settings)
        self.save_button.pack(pady=10)

    def browse_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.analysis_export_path_var.set(directory)

    def save_settings(self):
        self.view_model.update_settings("export_to_csv", self.export_to_csv_var.get())
        self.view_model.update_settings("export_to_excel", self.export_to_excel_var.get())
        self.view_model.update_settings("export_to_mat", self.export_to_mat_var.get())
        self.view_model.update_settings("run_auto_detection", self.run_auto_detection_var.get())
        self.view_model.update_settings("analysis_export_path", self.analysis_export_path_var.get())

        self.top.destroy()
