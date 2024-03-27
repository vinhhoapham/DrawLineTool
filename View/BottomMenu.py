from tkinter import Frame, Label, Button, font


class BottomMenu(Frame):
    def __init__(self, master, prev_callback, next_callback, status_text="Unloaded"):
        super().__init__(master, bg='black')  # Set the frame background to dark

        # Font and button styling
        modern_font = font.Font(family="Helvetica", size=14)
        button_style = {'font': modern_font, 'relief': 'flat', 'bg': 'white',
                        'borderwidth': 0, 'fg': 'black'}

        # Status Label
        self.status_label = Label(self, text=status_text, font=modern_font, bg='black', fg='white')  # Set label colors
        self.status_label.pack(side="left", padx=10, pady=10)

        # Previous Button
        self.prev_button = Button(self, text="←", command=prev_callback, **button_style)
        self.prev_button.pack(side="right", padx=10, pady=10)

        # Next Button
        self.next_button = Button(self, text="→", command=next_callback, **button_style)
        self.next_button.pack(side="right", padx=10, pady=10)

        # Center the frame contents
        self.pack(anchor="center")

    def update_status(self, new_status):
        self.status_label.config(text=new_status)
