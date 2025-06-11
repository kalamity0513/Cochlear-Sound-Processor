import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import tkinter as tk
from gui.app_gui import CochlearImplantApp

if __name__ == "__main__":
    root = tk.Tk()
    app = CochlearImplantApp(root)
    root.mainloop()
