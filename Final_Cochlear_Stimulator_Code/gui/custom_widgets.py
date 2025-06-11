import tkinter as tk

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, width, height, corner_radius=40, border_width=6, bg_color="#fffdf6", border_color="#5a4032"):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=bg_color)
        self.rounded_rect = self._create_rounded_rect(0, 0, width, height, corner_radius, border_width, bg_color, border_color)

    def _create_rounded_rect(self, x1, y1, x2, y2, radius, border_width, fill, outline):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, fill=fill, outline=outline, width=border_width)
