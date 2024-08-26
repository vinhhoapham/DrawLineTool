import tkinter as tk
from View import DrawLineToolView
from Model.DrawLineToolModel import DrawLineToolModel
from ViewModel.DrawLineToolViewModel import DrawLineToolViewModel


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Draw Line Tool")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.geometry(f"{screen_width}x{screen_height}")

        self.model = DrawLineToolModel()
        self.view_model = DrawLineToolViewModel(self.model)
        self.main_view = DrawLineToolView.MainView(self, self.view_model)


if __name__ == "__main__":
    app = App()
    app.mainloop()
