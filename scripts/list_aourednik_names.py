"""
Extract all unique NAME values from aourednik historical GeoJSON snapshots.

Output: data/calendars/aourednik_names_raw.txt — one name per line, sorted.
Used to build aourednik_calendar_map.json (manual step: fill via LLM + review).

Usage:
    python scripts/list_aourednik_names.py
"""

import json
from pathlib import Path

HISTORICAL_DIR = Path(__file__).parent.parent / "data" / "geojson" / "historical"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "calendars" / "aourednik_names_raw.txt"


def extract_names() -> set[str]:
    names: set[str] = set()
    files = sorted(HISTORICAL_DIR.glob("*.geojson"))
    if not files:
        raise FileNotFoundError(f"No GeoJSON files found in {HISTORICAL_DIR}")

    for path in files:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        for feature in data.get("features", []):
            name = feature.get("properties", {}).get("NAME")
            if name:
                names.add(name.strip())

    return names


def main() -> None:
    names = extract_names()
    sorted_names = sorted(names, key=str.casefold)
    OUTPUT_FILE.write_text("\n".join(sorted_names) + "\n", encoding="utf-8")
    print(f"{len(sorted_names)} unique NAMEs written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
