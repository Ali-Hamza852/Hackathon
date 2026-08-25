PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 350.4, 301, 400),
    (350.5, 500.4, 401, 500),
]


def pm25_to_aqi(pm25: float) -> int:
    clamped = max(0.0, min(pm25, PM25_BREAKPOINTS[-1][1]))
    for concentration_low, concentration_high, aqi_low, aqi_high in PM25_BREAKPOINTS:
        if concentration_low <= clamped <= concentration_high:
            ratio = (aqi_high - aqi_low) / (concentration_high - concentration_low)
            return round(ratio * (clamped - concentration_low) + aqi_low)
    return PM25_BREAKPOINTS[-1][3]
