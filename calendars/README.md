# Calendar Conversion Engine

This module converts any date expressed as a **Julian Day Number (JDN)** into a date
in one of 8 historical calendar systems.

---

## What is a Julian Day Number (JDN)?

A JDN is a universal integer count of days since January 1, 4713 BCE (Julian calendar).
It is used in astronomy and chronology as a calendar-neutral pivot.

**Why use JDN here?**
Every calendar system has its own epoch (year 0) and month structure. Converting
directly between two calendars (e.g. Hebrew → Persian) would require 56 converter pairs.
Instead, all converters share a single interface: `from_jdn(jdn)` and `to_jdn(date)`.
Any two calendars can be compared by going through JDN as the common intermediary.

**How to compute a JDN from a Python date:**
```python
from datetime import date
jdn = date(2024, 6, 15).toordinal() + 1721425
```
`1721425` is the fixed offset between Python's ordinal epoch (day 1 = Jan 1, year 1 CE)
and the JDN epoch (day 1 = Jan 1, 4713 BCE). This offset never changes.

---

## Architecture

```
base.py          CalendarDate dataclass + CalendarConverter ABC
dispatcher.py    Routes a (region, jdn) pair to the right converter(s)
gregorian.py     Gregorian calendar
julian.py        Julian calendar
hebrew.py        Hebrew (Jewish) calendar
hijri.py         Islamic Hijri calendar
persian.py       Persian (Jalali / Solar Hijri) calendar
japanese.py      Japanese Imperial era calendar
coptic.py        Coptic (Alexandrian) calendar
ethiopian.py     Ethiopian (Ge'ez) calendar
```

`dispatcher.py` uses `data/calendars/region_calendar_map.json` to decide which
calendar(s) apply to a given ISO 3166-1 region code (e.g. `"IR"` → Persian + Gregorian).

---

## out_of_range guard (Phase 10)

Each calendar has a historical epoch — a date before which it did not exist.
Passing a JDN before that epoch to a library can either crash the server or return
nonsensical values (year ≤ 0, month = 0).

`CalendarDate` carries an `out_of_range: bool = False` field. When a converter
receives a JDN before its epoch, it returns early:
```python
return CalendarDate(year=0, month=0, day=0, calendar_name="...", formatted="", out_of_range=True)
```

The API then excludes these entries from the map overlay (no color for that region)
and displays `"— (before calendar epoch)"` in the sidebar panel.

---

## Converters

### Gregorian — `gregorian.py`
The international civil calendar introduced in 1582 by Pope Gregory XIII as a reform
of the Julian calendar. Used worldwide today.

- **Library:** Python's built-in `datetime.date`
- **out_of_range threshold:** JDN < 1704987 (~45 BCE)
- **Why that threshold?** `datetime.date` only supports year ≥ 1 in Python, and
  the Julian calendar reform that Gregorian is based on dates to ~45 BCE. Any JDN
  below this ordinal makes `date.fromordinal()` raise a `ValueError`.

---

### Julian — `julian.py`
The predecessor to the Gregorian calendar, introduced by Julius Caesar in 46 BCE.
Still used by some Orthodox churches for liturgical dates.

- **Library:** `convertdate.julian`
- **out_of_range threshold:** none
- **Why no guard?** `convertdate.julian` uses pure arithmetic with no dependency on
  `datetime.date`. It handles BCE dates natively, returning negative years in
  astronomical notation (year 0 = 1 BCE, year −1 = 2 BCE, etc.). Tested down to 3000 BCE.

---

### Hebrew — `hebrew.py`
The Jewish lunisolar calendar counting from the creation of the world (Anno Mundi).
Year 1 AM corresponds to approximately 3761 BCE. Used for Jewish religious observance.
Contains 12 months in ordinary years, 13 in leap years (7 leap years every 19 years,
Metonic cycle). Month names follow the religious year starting from Nisan.

- **Library:** `pyluach`
- **out_of_range threshold:** JDN < 1721426 (year 1 CE)
- **Why that threshold?** The Hebrew calendar theoretically extends to 3761 BCE, but
  `pyluach` converts via `datetime.date` internally. `datetime.date` requires year ≥ 1 CE,
  so all BCE dates crash before reaching pyluach. This is a **Python limitation**, not a
  calendar limitation. A future improvement (Option B) would use pyluach's direct
  constructor `HebrewDate(year, month, day)` to bypass `datetime.date` entirely.

---

### Hijri (Islamic) — `hijri.py`
The Islamic lunar calendar counting from the Hijra (migration of the Prophet Muhammad
from Mecca to Medina) in 622 CE. Year 1 AH = July 16, 622 CE. Pure lunar calendar:
12 months of 29 or 30 days = 354 days/year, drifting ~11 days/year against Gregorian.

Two calculation systems exist — this converter uses both depending on the date:
- **Umm al-Qura** (astronomical, Saudi Arabia standard): `hijridate` library,
  valid only for 1356–1500 AH (1937–2077 CE).
- **Tabular Islamic** (arithmetic rule, ±1–2 day margin): `convertdate.islamic`,
  valid for all dates after 622 CE.

- **out_of_range threshold:** JDN < 1948439 (622 CE, the Hijra)
- **Why that threshold?** Before 622 CE, the Islamic calendar did not exist.
  `convertdate.islamic` could return a mathematically extrapolated negative Hijri year,
  but this would be historically meaningless and would break `MONTH_NAMES[month]`
  lookup if month = 0.

---

### Persian (Jalali / Solar Hijri) — `persian.py`
The Solar Hijri calendar, official calendar of Iran and Afghanistan. Year 1 = Nowruz
(vernal equinox) of the Hijra year, 622 CE. Currently ~621 years behind Gregorian.
12 months: first 6 have 31 days, next 5 have 30, last has 29 (or 30 in leap year).

- **Library:** `convertdate.persian`
- **out_of_range threshold:** JDN < 2122292 (~1079 CE)
- **Why that threshold?** The modern Jalali calendar was established by the reform of
  Omar Khayyam in 1079 CE, which introduced the precise astronomical rules still in use.
  Before that date, `convertdate.persian` may return inconsistent results.

---

### Japanese Imperial — `japanese.py`
The Japanese calendar uses the same months, days and year length as the Gregorian
calendar, but labels years by imperial era (元号, *gengō*). Each era begins when a
new emperor ascends the throne.

The converter loads all 248 eras from `data/calendars/japanese_eras.json` at init
and performs a linear scan to find the matching era for a given date.

- **Library:** none (arithmetic via `datetime.date` + JSON era lookup)
- **out_of_range threshold:** JDN < 1947154 (645 CE, era Taika — first recorded era)
- **Why that threshold?** The imperial era system begins with Taika (大化) on
  645-07-17 CE. Before that date there is no era name, so a Japanese calendar date
  cannot be expressed. The guard also prevents a `datetime.date` crash on BCE inputs.

---

### Coptic (Alexandrian) — `coptic.py`
The liturgical calendar of the Coptic Orthodox Church, derived from the ancient
Egyptian solar calendar. Year 1 = Era of the Martyrs (Diocletian), starting 284 CE.
12 months of exactly 30 days each + 1 intercalary month (Nasie) of 5 or 6 days.
Currently ~283 years behind Gregorian.

- **Library:** `convertdate.coptic`
- **out_of_range threshold:** JDN < 1825030 (284 CE, Coptic epoch)
- **Why that threshold?** `convertdate.coptic` is pure arithmetic and will not crash
  before the epoch, but it returns year ≤ 0, which is meaningless in the Coptic system.
  The guard ensures only valid Coptic dates are returned.

---

### Ethiopian (Ge'ez) — `ethiopian.py`
The official calendar of Ethiopia. Structurally identical to the Coptic calendar
(also derived from the ancient Egyptian calendar) but with a different epoch.
Year 1 = 8 CE (Incarnation era). Currently ~7–8 years behind Gregorian.
13 months: 12 × 30 days + Pagumē (5 or 6 epagomenal days).

There is no dedicated `convertdate.ethiopian` module. The converter reuses
`convertdate.coptic.from_jd()` and applies a fixed year offset:

```
Ethiopian year = Coptic year + 276
```

This works because both calendars share the same month and day structure —
only their epoch differs by exactly 276 years (284 CE − 8 CE = 276).

- **Library:** `convertdate.coptic` (reused with offset)
- **out_of_range threshold:** JDN < 1724221 (8 CE, Ethiopian epoch)
- **Why that threshold?** 8 CE = 284 CE (Coptic epoch) − 276 solar years ≈
  276 × 365.25 = 100,809 days. JDN 1724221 = 1825030 − 100809.
  Before this date, the Coptic year + 276 offset would produce a year ≤ 0.
