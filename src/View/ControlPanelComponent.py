from tkinter import Frame, Button, font, Checkbutton, BooleanVar


class ControlPanelComponent(Frame):
    def __init__(self, master, load_folder_callback, export_analysis_callback,
                 open_settings_callback, on_checkbox_toggle):
        super().__init__(master, bg='black')

        # Font and button styling
        modern_font = font.Font(family="Helvetica", size=12)
        button_style = {'font': modern_font, 'relief': 'flat', 'bg': 'white', 'fg': 'black',
                        'borderwidth': 0}

        # Load Folder Button
        self.load_folder_button = Button(self, text="Load Folder", command=load_folder_callback, **button_style)
        self.load_folder_button.pack(side="left", padx=10, pady=10)

        # Export Analysis Button
        self.export_analysis_button = Button(self, text="Export Analysis", command=export_analysis_callback,
                                             **button_style)
        self.export_analysis_button.pack(side="left", padx=10, pady=10)

        # Settings Button
        self.settings_button = Button(self, text="Settings", command=open_settings_callback, **button_style)
        self.settings_button.pack(side="left", padx=10, pady=10)

        self.is_object_lighter_var = BooleanVar()
        self.is_object_lighter_checkbox = Checkbutton(self, text="Object is Lighter", var=self.is_object_lighter_var,
                                                      command=on_checkbox_toggle, selectcolor='black',
                                                      fg='white', bg='black')
        self.is_object_lighter_checkbox.pack(side="right", padx=10, pady=10)

        # Center the buttons
        self.pack(anchor="center")

    def update_checkbox_state(self, is_lighter):
        self.is_object_lighter_var.set(is_lighter)