import tkinter as tk
import random

def AQI_Meter():
    """
    Return an AQI integer (0-500).
    Replace this implementation with real data source (sensor / API).
    """
    return random.randint(0, 500)

# AQI categories with colors and ranges
CATEGORIES = [
    ("Good", 0, 50, "#00e400"),
    ("Moderate", 51, 100, "#ffff00"),
    ("Unhealthy for Sensitive", 101, 150, "#ff7e00"),
    ("Unhealthy", 151, 200, "#ff0000"),
    ("Very Unhealthy", 201, 300, "#8f3f97"),
    ("Hazardous", 301, 500, "#7e0023"),
]

class AQIMeterApp:
    def __init__(self, root):
        self.root = root
        root.title("AQI meter")

        self.heading = tk.Label(root, text="AQI meter", font=("Segoe UI", 20, "bold"))
        self.heading.pack(pady=(10, 6))

        self.canvas_width = 600
        self.canvas_height = 80
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(padx=12, pady=6)

        info_frame = tk.Frame(root)
        info_frame.pack(fill="x", padx=12, pady=(0,10))
        self.value_label = tk.Label(info_frame, text="AQI: --", font=("Segoe UI", 14))
        self.value_label.pack(side="left")
        self.cat_label = tk.Label(info_frame, text="Category: --", font=("Segoe UI", 14))
        self.cat_label.pack(side="left", padx=20)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=(0,12))
        self.refresh_btn = tk.Button(btn_frame, text="Refresh", command=self.update_meter)
        self.refresh_btn.pack(side="left", padx=6)
        self.auto_var = tk.BooleanVar(value=True)
        self.auto_chk = tk.Checkbutton(btn_frame, text="Auto update (5s)", variable=self.auto_var, command=self.toggle_auto)
        self.auto_chk.pack(side="left")

        # initial draw
        self.draw_meter_base()
        self.pointer = None
        self.update_meter()

    def draw_meter_base(self):
        # Draw colored segments representing AQI ranges
        self.canvas.delete("base")
        w = self.canvas_width
        for name, start, end, color in CATEGORIES:
            x1 = (start / 500) * w
            x2 = (end / 500) * w
            self.canvas.create_rectangle(x1, 10, x2, self.canvas_height-10, fill=color, outline="#cccccc", tags="base")
            # small label for segment (only first 2-3 chars to avoid clutter)
            mid = (x1 + x2) / 2
            self.canvas.create_text(mid, self.canvas_height-20, text=name.split()[0], font=("Segoe UI", 9), fill="#000", tags="base")

        # outline
        self.canvas.create_rectangle(0, 10, w, self.canvas_height-10, outline="#666", width=1, tags="base")

    def aqi_to_category(self, aqi):
        for name, start, end, color in CATEGORIES:
            if start <= aqi <= end:
                return name, color
        # fallback
        return "Out of range", "#666"

    def update_meter(self):
        aqi = AQI_Meter()
        # clamp between 0 and 500
        aqi = max(0, min(500, int(aqi)))
        name, color = self.aqi_to_category(aqi)

        # update labels
        self.value_label.config(text=f"AQI: {aqi}")
        self.cat_label.config(text=f"Category: {name}", fg=color)

        # draw pointer
        self.canvas.delete("pointer")
        x = (aqi / 500) * self.canvas_width
        self.canvas.create_line(x, 5, x, self.canvas_height-5, fill="#000000", width=3, tags="pointer")
        # small circle at top
        self.canvas.create_oval(x-6, (self.canvas_height/2)-6, x+6, (self.canvas_height/2)+6, fill="#ffffff", outline="#000", tags="pointer")
        # numeric marker above pointer
        self.canvas.create_text(x, 2, text=str(aqi), anchor="s", font=("Segoe UI", 9, "bold"), tags="pointer")

        # schedule next update if auto enabled
        if self.auto_var.get():
            self.root.after(5000, self.update_meter)

    def toggle_auto(self):
        if self.auto_var.get():
            # start auto updates
            self.root.after(5000, self.update_meter)

if __name__ == "__main__":
    root = tk.Tk()
    app = AQIMeterApp(root)
    root.mainloop()