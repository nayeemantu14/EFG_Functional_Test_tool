import tkinter as tk
from gui import STM32ProgrammerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = STM32ProgrammerApp(root)
    root.mainloop()
