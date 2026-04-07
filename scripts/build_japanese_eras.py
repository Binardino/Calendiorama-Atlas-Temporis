"""
build_japanese_eras.py
======================
One-time script: downloads jeraconv.json from GitHub and converts it to
data/calendars/japanese_eras.json used by JapaneseCalendar.

Usage:
    poetry run python scripts/build_japanese_eras.py

Output:
    data/calendars/japanese_eras.json

Attribution / License:
    Source data: jeraconv by slangsoft
    Repository:  https://github.com/slangsoft/jeraconv
    License:     MIT License — Copyright (c) 2019 slangsoft
    The MIT License permits use, copy, modification, and redistribution
    with attribution.  The "_source" metadata block in the output file
    satisfies that requirement.
"""

import json
import urllib.request
from datetime import date
from pathlib import Path

SOURCE_URL = (
    "https://raw.githubusercontent.com/slangsoft/jeraconv"
    "/master/jeraconv/data/jeraconv.json"
)

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "calendars" / "japanese_eras.json"

# Current year: end dates beyond this threshold are treated as "ongoing".
# Reiwa started 2019 and has no real end yet; jeraconv encodes that with a
# far-future sentinel year.  Any end year > ONGOING_THRESHOLD → null.
ONGOING_THRESHOLD = date.today().year + 5


def fetch_source() -> dict:
    print(f"Downloading {SOURCE_URL} ...")
    with urllib.request.urlopen(SOURCE_URL) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_iso(year: int, month: int, day: int) -> str:
    return f"{year:04d}-{month:02d}-{day:02d}"


def transform(source: dict) -> list[dict]:
    eras = []
    for kanji, entry in source.items():
        start = entry["start"]
        end   = entry["end"]

        start_iso = build_iso(start["year"], start["month"], start["day"])

        # Sentinel end years (e.g. 9999) → null (era is still ongoing)
        if end["year"] > ONGOING_THRESHOLD:
            end_iso = None
        else:
            end_iso = build_iso(end["year"], end["month"], end["day"])

        eras.append({
            "kanji": kanji,
            "kana":  entry["reading"]["jp"],
            "name":  entry["reading"]["en"],
            "start": start_iso,
            "end":   end_iso,
        })

    # jeraconv is already chronological, but sort explicitly for safety
    eras.sort(key=lambda e: e["start"])
    return eras


def main() -> None:
    source = fetch_source()
    eras   = transform(source)

    output = {
        "_source": {
            "name":       "jeraconv",
            "author":     "slangsoft",
            "repository": "https://github.com/slangsoft/jeraconv",
            "license":    "MIT License — Copyright (c) 2019 slangsoft",
            "note": (
                "Data downloaded and reformatted for Calendiorama Atlas Temporis. "
                "Original field names changed; content unchanged. "
                "Redistribution allowed under MIT License with this attribution."
            ),
        },
        "eras": eras,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Written {len(eras)} eras → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
