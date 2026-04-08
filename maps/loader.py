from pathlib import Path
import geopandas as gpd

# Absolute path to data/geojson/, resolved from this file's location.
# Using __file__ avoids CWD-dependent relative paths that break under pytest.
DATA_DIR = Path(__file__).parent.parent / "data" / "geojson"


def get_available_years() -> list[int]:
    """
    Scan data/geojson/historical/ and return all available snapshot years as
    a sorted list of integers. BCE years are negative (e.g. -3000).

    File naming convention (aourednik/historical-basemaps):
        world_1500.geojson   →  1500  (CE)
        world_bc3000.geojson → -3000  (BCE)
        world_0.geojson      →     0  (year zero)

    Files that do not match the expected pattern are skipped with a warning.
    """
    historical_map_dir = DATA_DIR / "historical"
    year_list = []

    for map_file in historical_map_dir.glob("*.geojson"):
        try:
            name     = map_file.stem        # e.g. "world_1500" or "world_bc3000"
            year_str = name.split("_")[1]   # e.g. "1500" or "bc3000"

            if year_str.startswith("bc"):
                year = -int(year_str[2:])   # "bc3000" → -3000
            else:
                year = int(year_str)        # "1500"   →  1500

            year_list.append(year)

        except (IndexError, ValueError) as e:
            print(f"Skipping file {map_file.name}: {e}")

    return sorted(year_list)


def find_nearest_year(year: int, available: list[int]) -> int:
    """
    Return the largest year in `available` that is <= `year`.

    We never predict the future: if the requested year is 1523 and the
    available snapshots are [..., 1500, 1530, ...], we return 1500.

    If `year` is before all available snapshots (e.g. -200000), we fall back
    to the oldest available snapshot (available[0], since the list is sorted).

    Args:
        year:      The target year (integer, negative for BCE).
        available: Sorted list of snapshot years from get_available_years().

    Returns:
        The closest available snapshot year that does not exceed `year`.
    """
    candidates = [y for y in available if y <= year]
    return max(candidates) if candidates else available[0]


def load_geojson(path: Path) -> gpd.GeoDataFrame:
    """
    Load a GeoJSON file relative to DATA_DIR and return a GeoDataFrame.

    Args:
        path: Path relative to data/geojson/ (e.g. Path("raw/ne_110m.geojson")).

    Raises:
        FileNotFoundError: If the resolved path does not exist.
    """
    full_path = DATA_DIR / path
    if not full_path.exists():
        raise FileNotFoundError(f"File {full_path} does not exist.")
    return gpd.read_file(full_path)