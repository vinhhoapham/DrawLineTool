from tkinter import Frame, Button, font, Checkbutton, BooleanVar, Label


class ControlPanelComponent(Frame):

    # TODO: Break each component to smaller one
    def __init__(self, master, load_folder_callback, export_analysis_callback,
                 open_settings_callback, on_checkbox_toggle):
        super().__init__(master, bg='black')

        # Font and button styling
        modern_font = font.Font(family="Helvetica", size=14)
        italic_font = font.Font(family="Helvetica", size=14, slant="italic")
        button_style = {'font': modern_font, 'relief': 'flat', 'bg': 'white', 'fg': 'black',
                        'borderwidth': 0}

        # Left frame for buttons
        left_frame = Frame(self, bg='black')
        left_frame.pack(side="left", padx=10, pady=10)

        # Load Folder Button
        self.load_folder_button = Button(left_frame, text="Load Folder", command=load_folder_callback, **button_style)
        self.load_folder_button.pack(side="left", pady=5)

        # Export Analysis Button
        self.export_analysis_button = Button(left_frame, text="Export Analysis", command=export_analysis_callback,
                                             **button_style)
        self.export_analysis_button.pack(side="left", pady=5)

        # Settings Button
        self.settings_button = Button(left_frame, text="Settings", command=open_settings_callback, **button_style)
        self.settings_button.pack(side="left", pady=5)

        # Middle frame for image analysis info
        middle_frame = Frame(self, bg='black')
        middle_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # Image Analysis Info
        self.info_frame = Frame(middle_frame, bg='black')
        self.info_frame.pack(expand=True)

        self.angle_label = Label(self.info_frame, text="Angle:", fg='white', bg='black', font=modern_font)
        self.angle_label.pack(side="left", anchor="center")
        self.angle_value = Label(self.info_frame, text="N/A", fg='white', bg='black', font=italic_font)
        self.angle_value.pack(side="left", anchor="center")

        self.contrast_label = Label(self.info_frame, text="Contrast:", fg='white', bg='black', font=modern_font)
        self.contrast_label.pack(side="left", anchor="center")
        self.contrast_value = Label(self.info_frame, text="N/A", fg='white', bg='black', font=italic_font)
        self.contrast_value.pack(side="left", anchor="center")

        self.blurriness_label = Label(self.info_frame, text="Blurriness:", fg='white', bg='black', font=modern_font)
        self.blurriness_label.pack(side="left", anchor="center")
        self.blurriness_value = Label(self.info_frame, text="N/A", fg='white', bg='black', font=italic_font)
        self.blurriness_value.pack(side="left", anchor="center")

        # Right frame for checkbox
        right_frame = Frame(self, bg='black')
        right_frame.pack(side="right", padx=10, pady=10)

        self.is_object_lighter_var = BooleanVar()
        self.is_object_lighter_checkbox = Checkbutton(right_frame, text="Object is Lighter",
                                                      var=self.is_object_lighter_var,
                                                      command=on_checkbox_toggle, selectcolor='black',
                                                      fg='white', bg='black')
        self.is_object_lighter_checkbox.pack(side="top")

    def update_checkbox_state(self, is_lighter):
        self.is_object_lighter_var.set(is_lighter)

    def update_image_info(self, blurriness=None, contrast=None, angle=None):
        blurriness_str = f"{blurriness:.5f}" if blurriness else "N/A"
        contrast_str = f"{contrast:.3f}" if contrast else "N/A"
        angle_str = f"{angle:.3f}" if angle else "N/A"
        self.blurriness_value.config(text=blurriness_str)
        self.contrast_value.config(text=contrast_str)
        self.angle_value.config(text=angle_str)
