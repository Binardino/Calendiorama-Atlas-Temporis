from pathlib import Path
import geopandas as gpd

DATA_DIR = Path(__file__).parent.parent / "data" / "geojson"

def load_geojson(path: Path) -> gpd.GeoDataFrame:
    full_path = DATA_DIR / path
    if not full_path.exists():
        raise FileNotFoundError(f"File {full_path} does not exist.")
    return gpd.read_file(full_path)