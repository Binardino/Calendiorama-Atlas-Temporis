# Historical Calendar Mapping Roadmap

## Objective
To transform the current static calendar assignment system into a dynamic, historically accurate database. The system must determine which calendar(s) an entity used based on its geographical location *and* the specific date (Julian Day Number) being queried on the timeline.

## 1. Current State Assessment
- **Strengths:** 
  - Robust backend calendar converters (`Gregorian`, `Julian`, `Hijri`, `Hebrew`, `Persian`, `Japanese`, `Coptic`, `Ethiopian`).
  - Solid universal pivot using Julian Day Number (JDN).
  - Geographical data pipeline resolving both historical snapshots (`aourednik`) and modern high-precision borders (`CShapes`).
- **Weaknesses:**
  - `region_calendar_map.json` is entirely static, mapping modern ISO alpha-2 codes to a fixed list of calendars. It ignores the temporal dimension.
  - Pre-modern geographic entities (e.g., "Mamluke Sultanate") do not map cleanly to modern ISO codes, causing them to fall back to the default calendar.
  - Missing significant historical calendars (e.g., French Republican Calendar, North Korean Juche).

---

## 2. Architectural Blueprint

### 2.1. The Temporal Database
We will migrate from a static `region_calendar_map.json` to a time-aware `historical_calendar_map.json` (or a set of structured CSVs compiled into JSON during build).

**Target Data Schema (JSON):**
```json
{
  "FR": [
    { "until_jdn": 2299226, "calendars": ["julian"] }, 
    { "from_jdn": 2299227, "until_jdn": 2376200, "calendars": ["gregorian"] },
    { "from_jdn": 2376201, "until_jdn": 2380686, "calendars": ["gregorian", "revolutionary"] },
    { "from_jdn": 2380687, "calendars": ["gregorian"] }
  ]
}
```
*Note: Storing JDN directly in the compiled JSON optimizes the runtime lookup, though the source files maintained by humans/AIs should use human-readable ISO dates.*

### 2.2. Entity Resolution Strategy
To handle entities across different eras, we need a multi-tiered resolution strategy in `dispatcher.py`:

1.  **CShapes Era (1886 - Present):** Entities are identified by `gwcode`. We will map `gwcode` to historical calendar rules.
2.  **Snapshot Era (-3000 - 1885):** Entities are identified by the `NAME` property in the GeoJSON.
    - We will create an `entity_tradition_map.json` that maps historical names (e.g., "Castille", "Wattasid Caliphate") to macro-regions or "Calendar Traditions" (e.g., "Catholic_Europe", "Islamic_Maghreb").
3.  **Tradition Fallbacks:** If a specific entity isn't mapped, it falls back to its Tradition's rules.

---

## 3. Implementation Roadmap

### Phase 1: Engine Refactoring (The Backbone)
1.  **Update `dispatcher.py`:**
    - Rewrite `get_calendars(region_id, jdn)` to evaluate the `jdn` against the new temporal database.
    - Implement the multi-tiered entity resolution (Entity ID -> Tradition -> Default).
2.  **Add Missing Converters:**
    - Implement `calendars/revolutionary.py` for the French Republican Calendar.
    - Implement `calendars/juche.py` (optional but recommended for modern completeness).

### Phase 2: Deep Research & Data Entry (The Knowledge Base)
*This is an iterative process heavily reliant on AI research.*

1.  **The Gregorian Adoption:**
    - Compile a comprehensive list of Gregorian adoption dates by country/region.
    - Account for the "Lost Days" (e.g., Oct 4, 1582 followed by Oct 15, 1582). The JDN logic natively handles this, but the mapping must define the exact cut-off JDNs.
2.  **The Islamic World:**
    - Map historical Islamic empires to the Hijri calendar as primary.
    - Determine when civil administration in these regions shifted to Gregorian.
3.  **Asian Traditions:**
    - Map the transition of China, Japan, and Korea from lunisolar calendars to the Gregorian calendar (late 19th/early 20th century).
4.  **Special Cases:**
    - Revolutionary calendars, Soviet calendar experiments (if feasible), Swedish cantonal oddities.

### Phase 3: Integration & Map UI Updates
1.  **Build Script:** Create a Python script (`scripts/build_calendar_db.py`) that takes easy-to-edit CSV files (with ISO dates) and compiles them into the optimized `historical_calendar_map.json` (with JDNs) for the Flask app.
2.  **Map Click Event:** Ensure that when a user clicks a historical polygon on the map, the API receives both the `NAME`/`gwcode` and the current timeline year to fetch the precise local date.

---

## 4. Immediate Next Step: Gregorian Adoption Research
**Action:** Initiate a deep-dive research session to build `data/calendars/gregorian_adoption.csv`. 

**Target Columns:**
`Entity_Name, ISO/GWCode, Julian_End_Date, Gregorian_Start_Date, Notes`

This dataset will serve as the foundation for testing the new temporal logic in `dispatcher.py`.