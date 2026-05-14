from pathlib import Path
import geopandas as gpd
import json
from datetime import date

# Absolute path to data/geojson/, resolved from this file's location.
# Using __file__ avoids CWD-dependent relative paths that break under pytest.
DATA_DIR = Path(__file__).parent.parent / "data" / "geojson"

_GWCODE_ISO_PATH = Path(__file__).parent.parent / "data" / "calendars" / "gwcode_iso.json"

with _GWCODE_ISO_PATH.open() as f:
    _GWCODE_ISO: dict[str, str] = json.load(f)

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
    if not available:
        raise FileNotFoundError("No historical GeoJSON snapshots found in data/geojson/historical/")
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
    
    gdf = gpd.read_file(full_path)
    # Normalise to a consistent 'label' field consumed by JS buildStateLabels().
    # Both aourednik historical files and Natural Earth use the 'NAME' column.
    gdf['label'] = gdf['NAME']
    return gdf

def load_cshapes(target_date: date) -> gpd.GeoDataFrame:
    """
    Load CShapes 2.0 shapefile and return only the features active on target_date.

    CShapes stores one row per country per stable-border period, with integer
    start/end fields (gwsyear/gwsmonth/gwsday, gweyear/gwemonth/gweday).
    A row is active when: start <= target_date <= end.

    ISO_A2 is added via the module-level _GWCODE_ISO mapping (gwcode → ISO alpha-2).

    Args:
        target_date: The date to filter on.

    Returns:
        GeoDataFrame with columns: gwcode, cntry_name, ISO_A2, geometry.
    """
    cshapes_dir = DATA_DIR / "cshapes"
    shp_files = list(cshapes_dir.glob("*.shp"))
    if not shp_files:
        raise FileNotFoundError(f"No shapefile found in {cshapes_dir}")
    cshapes = gpd.read_file(shp_files[0])

    year, month, day = target_date.year, target_date.month, target_date.day

    # Row is active if start date <= target_date (lexicographic tuple logic on year/month/day)
    after_start = (cshapes['gwsyear'] < year) | \
                  ((cshapes['gwsyear'] == year) & (cshapes['gwsmonth'] < month)) | \
                  ((cshapes['gwsyear'] == year) & (cshapes['gwsmonth'] == month) & (cshapes['gwsday'] <= day))

    # Row is active if end date >= target_date
    before_end = (cshapes['gweyear'] > year) | \
                 ((cshapes['gweyear'] == year) & (cshapes['gwemonth'] > month)) | \
                 ((cshapes['gweyear'] == year) & (cshapes['gwemonth'] == month) & (cshapes['gweday'] >= day))

    # .copy() avoids SettingWithCopyWarning when adding ISO_A2 to the slice
    filtered = cshapes[after_start & before_end].copy()
    filtered['ISO_A2'] = filtered['gwcode'].astype(str).map(_GWCODE_ISO)
    filtered['label']  = filtered['cntry_name']

    return filtered[['gwcode', 'cntry_name', 'label', 'ISO_A2', 'geometry']]
