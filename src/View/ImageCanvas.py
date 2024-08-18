from tkinter import Canvas
from PIL import ImageTk


class ImageCanvas(Canvas):
    def __init__(self, master, image_click_callback, view_model):
        super().__init__(master)
        self.image_click_callback = image_click_callback
        self.view_model = view_model
        self.bind("<Button-1>", self.on_canvas_click)
        self.image_on_canvas = None
        self.line_on_canvas = None
        self.current_image = None
        self.center_oval = None
        self.red_dots = []  # List to keep track of red dots

    def display_image(self, image):
        self.current_image = ImageTk.PhotoImage(image)
        image_width = self.current_image.width()
        image_height = self.current_image.height()
        if self.image_on_canvas:
            self.itemconfig(self.image_on_canvas, image=self.current_image)
        else:
            self.image_on_canvas = self.create_image(0, 0, anchor="nw", image=self.current_image)
        self.display_center_circle(image_width, image_height)

    def display_center_circle(self, width, height, diameter=236):
        # Calculate the center coordinates
        center_x, center_y = width // 2, height // 2
        # Calculate the top-left and bottom-right coordinates of the circle
        top_left_x = center_x - diameter // 2
        top_left_y = center_y - diameter // 2
        bottom_right_x = center_x + diameter // 2
        bottom_right_y = center_y + diameter // 2
        # Create the circle
        self.center_oval = self.create_oval(top_left_x, top_left_y, bottom_right_x, bottom_right_y, outline='green')

    def on_canvas_click(self, event):
        new_image = self.image_click_callback(event.x, event.y)
        if new_image:
            self.display_image(new_image)
            self.clear_canvas_elements()

        if len(self.view_model.clicked_points) == 1:
            self.display_red_dot(*self.view_model.clicked_points[0])
            self.bind("<Motion>", self.update_line_to_mouse)
        elif len(self.view_model.clicked_points) == 0:
            self.clear_canvas_elements()

    def update_line_to_mouse(self, event):
        if len(self.view_model.clicked_points) == 1:
            if self.line_on_canvas:
                self.coords(self.line_on_canvas, *self.view_model.clicked_points[0], event.x, event.y)
            else:
                self.line_on_canvas = self.create_line(*self.view_model.clicked_points[0], event.x, event.y, fill='red')

    def display_red_dot(self, x, y):
        red_dot = self.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red', outline='red')
        self.red_dots.append(red_dot)

    def clear_canvas_elements(self):
        if self.line_on_canvas:
            self.delete(self.line_on_canvas)
            self.line_on_canvas = None
        for dot in self.red_dots:
            self.delete(dot)
        self.red_dots.clear()
        self.unbind("<Motion>")

    def clear_image_set(self):
        if self.image_on_canvas:
            self.delete(self.image_on_canvas)
            self.image_on_canvas = None
            self.delete(self.center_oval)
            self.center_oval = None

        self.current_image = None
