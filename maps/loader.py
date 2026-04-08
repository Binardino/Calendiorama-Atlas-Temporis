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
    for map_file in raw_map_list:
        try:
            name     = map_file.stem      # e.g. "map_1500"
            year_str = name.split("_")[1] # e.g. "1500"
            
            if year_str.startswith("bc"):
                year_str = year_str[2:]   # strip the _bc string e.g. "bc_500" → "500"
                year     = -int(year_str) # e.g. "bc_500" → "-500"
            else:
                year = int(year_str)
            year_list.append(year)
        
        except (IndexError, ValueError) as e:
            print(f"Skipping file {map_file.name}: {e}")

    return sorted(year_list)

def find_nearest_year(year: int, available: list[int]) -> int:
    candidates = [y for y in available if y <= year]
    return max(candidates) if candidates else available[0]
    
def load_geojson(path: Path) -> gpd.GeoDataFrame:
    full_path = DATA_DIR / path
    if not full_path.exists():
        raise FileNotFoundError(f"File {full_path} does not exist.")
    return gpd.read_file(full_path)