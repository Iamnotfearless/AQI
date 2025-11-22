# Objective: Creating a simple AQI meter cum calculator that shows a clear output
# calculating the sub index of common pollutants (examples included: PM2.5, PM10)

from typing import List, Tuple, Optional, Dict


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