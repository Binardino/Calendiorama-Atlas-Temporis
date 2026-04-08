# Calendiorama Atlas Temporis

Interactive historical world map — for any date on a timeline, shows historical borders and local calendar dates (Gregorian, Hijri, Hebrew, Persian, Japanese Imperial, Julian, Coptic, Ethiopian).

## Stack

Python · Flask · GeoPandas · Leaflet.js · Poetry

## Running

```bash
poetry install
flask run --debug
```

## Data Sources

| Dataset | Author | Licence | Usage |
|---|---|---|---|
| [Natural Earth 110m](https://www.naturalearthdata.com/) | Natural Earth | Public Domain | Contemporary country borders |
| [historical-basemaps](https://github.com/aourednik/historical-basemaps) | Alexandre Ourednik | [GPL v3](https://github.com/aourednik/historical-basemaps/blob/master/LICENSE) | Historical borders (-123000 to 2010 CE) |

### GPL v3 notice — historical-basemaps

Historical border data (`data/geojson/historical/`) is sourced from
[aourednik/historical-basemaps](https://github.com/aourednik/historical-basemaps)
by Alexandre Ourednik, distributed under the GNU General Public License v3.

The data files are not included in this repository (listed in `.gitignore`).
To use this project, download the GeoJSON files from the source repository
and place them in `data/geojson/historical/`.

A copy of the GPL v3 licence is available at:
https://www.gnu.org/licenses/gpl-3.0.en.html
