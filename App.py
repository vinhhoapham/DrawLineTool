import tkinter as tk
from View import DrawLineToolView
from Model.DrawLineToolModel import DrawLineToolModel
from ViewModel.DrawLineToolViewModel import DrawLineToolViewModel


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Draw Line Tool")
        self.attributes("-fullscreen", True)
        self.model = DrawLineToolModel()
        self.view_model = DrawLineToolViewModel(self.model)
        self.main_view = DrawLineToolView.MainView(self, self.view_model)


if __name__ == "__main__":
    app = App()
    app.mainloop()
