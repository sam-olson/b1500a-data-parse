import tkinter as tk

from b1500a.gui import App

if __name__ == "__main__":
    root = tk.Tk()
    root.title("B1500A Data Analysis")
    root.resizable(False, False)
    app = App(master=root)
    app.mainloop()
