from pathlib import Path
import geopandas as gpd

DATA_DIR = Path(__file__).parent.parent / "data" / "geojson"

def get_available_years() -> list[int] :
    historical_map_dir = DATA_DIR / "historical"
    raw_map_list = [map_file for map_file in historical_map_dir.glob("*.geojson")]

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
def load_geojson(path: Path) -> gpd.GeoDataFrame:
    full_path = DATA_DIR / path
    if not full_path.exists():
        raise FileNotFoundError(f"File {full_path} does not exist.")
    return gpd.read_file(full_path)