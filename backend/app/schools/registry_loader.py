import json
from pathlib import Path

import httpx

from app.schools.geo import is_within_lahore
from app.schools.manual_schools import MANUAL_SCHOOLS

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT_SECONDS = 30.0
OVERPASS_MAX_RESULTS = 40
SEED_FILE_PATH = Path(__file__).parent / "seed_schools.json"

OVERPASS_QUERY = """
[out:json][timeout:25];
area["name"="Lahore"]["boundary"="administrative"]->.searchArea;
(
  node["amenity"="school"](area.searchArea);
  way["amenity"="school"](area.searchArea);
);
out center;
"""


def fetch_overpass_schools() -> list[dict]:
    for attempt in range(2):
        try:
            response = httpx.post(
                OVERPASS_URL, data={"data": OVERPASS_QUERY}, timeout=OVERPASS_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            return _parse_overpass_elements(response.json().get("elements", []))
        except (httpx.HTTPError, ValueError):
            continue
    return []


def _parse_overpass_elements(elements: list[dict]) -> list[dict]:
    schools = []
    for element in elements:
        name = element.get("tags", {}).get("name")
        if not name:
            continue
        center = element.get("center", element)
        lat, lon = center.get("lat"), center.get("lon")
        if lat is None or lon is None or not is_within_lahore(lat, lon):
            continue
        schools.append({"name": name, "zone": "Overpass", "lat": lat, "lon": lon, "source": "overpass"})
        if len(schools) >= OVERPASS_MAX_RESULTS:
            break
    return schools


def build_seed_file() -> list[dict]:
    manual_entries = [
        {**school, "source": "manual"}
        for school in MANUAL_SCHOOLS
        if is_within_lahore(school["lat"], school["lon"])
    ]
    overpass_entries = fetch_overpass_schools()
    combined = manual_entries + overpass_entries

    SEED_FILE_PATH.write_text(json.dumps(combined, indent=2, ensure_ascii=False))
    return combined


if __name__ == "__main__":
    schools = build_seed_file()
    print(f"wrote {len(schools)} schools ({sum(1 for s in schools if s['source'] == 'manual')} manual, "
          f"{sum(1 for s in schools if s['source'] == 'overpass')} overpass) to {SEED_FILE_PATH}")
