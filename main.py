# Objective: Creating a simple AQI meter cum calculator that shows a clear output
# calculating the sub index of common pollutants (examples included: PM2.5, PM10)

from typing import List, Tuple, Optional, Dict
import tkinter as tk
import random
import AQI_Meter



# EPA-style breakpoint tables for common particulates (conc in µg/m3)
# Each entry: (BP_lo, BP_hi, I_lo, I_hi)
PM25_BREAKPOINTS: List[Tuple[float, float, int, int]] = [
	(0.0, 12.0, 0, 50),
	(12.1, 35.4, 51, 100),
	(35.5, 55.4, 101, 150),
	(55.5, 150.4, 151, 200),
	(150.5, 250.4, 201, 300),
	(250.5, 350.4, 301, 400),
	(350.5, 500.4, 401, 500),
]

PM10_BREAKPOINTS: List[Tuple[float, float, int, int]] = [
	(0, 54, 0, 50),
	(55, 154, 51, 100),
	(155, 254, 101, 150),
	(255, 354, 151, 200),
	(355, 424, 201, 300),
	(425, 504, 301, 400),
	(505, 604, 401, 500),
]


def aqi_for_concentration(C: float, breakpoints: List[Tuple[float, float, int, int]]) -> Optional[int]:
	"""Compute AQI for a single pollutant concentration using linear interpolation.

	Returns the rounded AQI integer, or None if concentration is out of range.
	"""
	for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
		if bp_lo <= C <= bp_hi:
			aqi = (i_hi - i_lo) / (bp_hi - bp_lo) * (C - bp_lo) + i_lo
			return int(round(aqi))
	return None


def aqi_category(aqi: int) -> str:
	if aqi <= 50:
		return "Good"
	if aqi <= 100:
		return "Moderate"
	if aqi <= 150:
		return "Unhealthy for Sensitive Groups"
	if aqi <= 200:
		return "Unhealthy"
	if aqi <= 300:
		return "Very Unhealthy"
	return "Hazardous"


def compute_aqi_for_pollutants(concs: Dict[str, float]) -> Dict[str, Optional[int]]:
	"""Given a dict of pollutant concentrations, return a dict of pollutant->AQI.

	Supported keys (case-insensitive): 'pm2.5', 'pm25', 'pm10'.
	"""
	results: Dict[str, Optional[int]] = {}
	for k, v in concs.items():
		key = k.strip().lower()
		if key in ("pm2.5", "pm25"):
			results[k] = aqi_for_concentration(float(v), PM25_BREAKPOINTS)
		elif key == "pm10":
			results[k] = aqi_for_concentration(float(v), PM10_BREAKPOINTS)
		else:
			results[k] = None
	return results


def print_aqi_table(concs: Dict[str, float], aqi_map: Dict[str, Optional[int]]):
	"""Print a neat table of pollutant, concentration, AQI, and category.

	Tries to use `tabulate` if installed, otherwise falls back to formatted text.
	"""
	rows = []
	for pollutant, conc in concs.items():
		aqi = aqi_map.get(pollutant)
		cat = aqi_category(aqi) if isinstance(aqi, int) else "N/A"
		rows.append((pollutant, f"{conc}", str(aqi) if aqi is not None else "N/A", cat))

	headers = ("Pollutant", "Concentration", "AQI", "Category")

	try:
		from tabulate import tabulate

		print(tabulate(rows, headers=headers, tablefmt="github"))
	except Exception:
		# fallback: simple column widths
		col_widths = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
		fmt = "  ".join("{:<" + str(w) + "}" for w in col_widths)
		print(fmt.format(*headers))
		print("-" * (sum(col_widths) + 2 * (len(col_widths) - 1)))
		for r in rows:
			print(fmt.format(*r))


if __name__ == "__main__":
	# Example usage/demo
	sample = {
		"PM2.5": 35.0,  # µg/m3
		"PM10": 80,
		"CO": 0.7,  # not supported in this minimal example
	}

	aqi_results = compute_aqi_for_pollutants(sample)
	print_aqi_table(sample, aqi_results)

	# Overall AQI (max of available pollutant AQIs)
	valid_aqis = [v for v in aqi_results.values() if isinstance(v, int)]
	if valid_aqis:
		overall = max(valid_aqis)
		print()
		print(f"Overall AQI: {overall} ({aqi_category(overall)})")
	else:
		print()
		print("No supported pollutant concentrations provided to compute AQI.")
		


def AQI_Meter():
    """
    Return an AQI integer (0-500).
    Replace this implementation with real data source (sensor / API).
    """
    return overall 

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