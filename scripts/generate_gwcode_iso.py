"""
generate_gwcode_iso.py — One-shot script to build data/calendars/gwcode_iso.json.

Maps each CShapes gwcode (integer) to an ISO 3166-1 alpha-2 country code (string).

Strategy:
  1. For each unique gwcode, take the most recent CShapes row (latest gweyear).
  2. Spatial join: does the capital point fall inside a Natural Earth polygon?
     → 226/252 gwcodes matched automatically this way.
  3. Apply MANUAL overrides for the 26 gwcodes whose capitals fall in the sea
     (Natural Earth 110m polygons are too coarse to capture small islands).

Run once from the project root:
    python scripts/generate_gwcode_iso.py
"""

from pathlib import Path
import geopandas as gpd
import json
from shapely.geometry import Point

# ---------------------------------------------------------------------------
# Paths (resolved relative to this script's location)
# ---------------------------------------------------------------------------
BASE = Path(__file__).parent.parent
CSHAPES_DIR = BASE / 'data' / 'geojson' / 'cshapes' / 'shapefile'
NE_PATH     = BASE / 'data' / 'geojson' / 'raw' / 'ne_110m_admin_0_countries.geojson'
OUT_PATH    = BASE / 'data' / 'calendars' / 'gwcode_iso.json'

# ---------------------------------------------------------------------------
# Manual overrides for the 26 gwcodes not matched by spatial join.
# These are small islands or territories whose capitals fall outside the
# Natural Earth 110m polygons (too coarse for small islands).
# ---------------------------------------------------------------------------
MANUAL = {
    31:   'BS',   # Bahamas
    53:   'BB',   # Barbados
    65:   'GP',   # Guadeloupe
    66:   'MQ',   # Martinique
    165:  'UY',   # Uruguay
    338:  'MT',   # Malta
    402:  'CV',   # Cape Verde
    411:  'GQ',   # Equatorial Guinea
    451:  'SL',   # Sierra Leone
    511:  'TZ',   # Zanzibar (now part of Tanzania)
    522:  'DJ',   # Djibouti
    581:  'KM',   # Comoros
    585:  'RE',   # Réunion
    590:  'MU',   # Mauritius
    620:  'LY',   # Libya
    692:  'BH',   # Bahrain
    698:  'OM',   # Oman
    780:  'LK',   # Sri Lanka (Ceylon)
    781:  'MV',   # Maldives
    823:  'MY',   # Sabah / North Borneo (now Malaysia)
    851:  'ID',   # West Irian / Dutch New Guinea (now Indonesia)
    930:  'NC',   # New Caledonia
    960:  'PF',   # French Polynesia
    6021: 'MA',   # Southern zone of Spanish Morocco (now Morocco)
    6511: 'PS',   # Gaza
    9401: 'SB',   # German Solomon Islands (now Solomon Islands)
    # Natural Earth returns ISO_A2='-99' for these countries — override manually
    120:  'GF',   # French Guyana
    220:  'FR',   # France (NE quirk: France metro gets -99)
    347:  'XK',   # Kosovo (non-standard but widely used ISO code)
    352:  'CY',   # Cyprus
    385:  'NO',   # Norway
    521:  'SO',   # British Somaliland (now Somalia)
    1201: 'GF',   # Inini (historical French territory, now part of French Guiana)
}


def main():
    # -----------------------------------------------------------------------
    # Step 1 — Load CShapes, keep one row per gwcode (most recent period)
    # -----------------------------------------------------------------------
    print("Loading CShapes shapefile...")
    cshapes = gpd.read_file(CSHAPES_DIR)
    print(f"  {len(cshapes)} features, {cshapes['gwcode'].nunique()} unique gwcodes")

    # Sort by gweyear descending, then keep first row per gwcode → latest period.
    latest = (
        cshapes
        .sort_values('gweyear', ascending=False)
        .groupby('gwcode', as_index=False)
        .first()
    )

    # -----------------------------------------------------------------------
    # Step 2 — Build a GeoDataFrame of capital points
    # -----------------------------------------------------------------------
    latest = latest.copy()
    latest['geometry'] = latest.apply(
        lambda r: Point(r['caplong'], r['caplat']), axis=1
    )
    capitals_gdf = gpd.GeoDataFrame(latest, geometry='geometry', crs='EPSG:4326')

    # -----------------------------------------------------------------------
    # Step 3 — Spatial join: capital point within Natural Earth polygon?
    # -----------------------------------------------------------------------
    print("Loading Natural Earth...")
    ne = gpd.read_file(NE_PATH)[['ISO_A2', 'geometry']]

    print("Running spatial join (capital points within NE polygons)...")
    joined = gpd.sjoin(
        capitals_gdf[['gwcode', 'cntry_name', 'geometry']],
        ne,
        how='left',
        predicate='within',
    )

    matched   = joined['ISO_A2'].notna().sum()
    unmatched = joined['ISO_A2'].isna().sum()
    print(f"  Matched automatically: {matched}")
    print(f"  Unmatched (will use MANUAL): {unmatched}")

    # -----------------------------------------------------------------------
    # Step 4 — Build result dict: MANUAL overrides take priority
    # -----------------------------------------------------------------------
    result = {}
    for _, row in joined.iterrows():
        gwcode = int(row['gwcode'])
        iso    = MANUAL.get(gwcode) or row.get('ISO_A2')
        if iso and str(iso) not in ('nan', '-99', ''):
            result[str(gwcode)] = str(iso)

    # -----------------------------------------------------------------------
    # Step 5 — Write JSON
    # -----------------------------------------------------------------------
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, sort_keys=True)

    print(f"\nWritten {len(result)} entries → {OUT_PATH}")

    # Summary of unresolved gwcodes (neither spatial match nor manual override)
    unresolved = joined[joined['ISO_A2'].isna() & ~joined['gwcode'].isin(MANUAL)]
    if not unresolved.empty:
        print(f"\nWARNING — {len(unresolved)} gwcodes without ISO mapping:")
        for _, r in unresolved.iterrows():
            print(f"  gwcode={int(r['gwcode'])}  {r['cntry_name']}")


if __name__ == '__main__':
    main()
