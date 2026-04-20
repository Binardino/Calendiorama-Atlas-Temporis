// Initialize Leaflet map centered on the world
const map = L.map('map').setView([20, 0], 2);

// CartoDB Positron: minimal light-gray basemap designed for data overlays.
// Much less visual noise than standard OSM tiles → calendar fill colors are clearly visible.
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>'
}).addTo(map);

// ---------------------------------------------------------------------------
// Calendar panel helpers
// ---------------------------------------------------------------------------

const calendarPanel = document.getElementById('calendar-panel');

// Show the calendar panel for the clicked country by calling the HTMX panel endpoint.
// htmx.ajax() triggers an HTTP GET and swaps the HTML response into #calendar-panel.
// This is the "HTML over the wire" pattern: Flask renders the UI, not this JS function.
//
// Guards (do nothing if):
//   - feature has no ISO_A2 property  → historical layer (aourednik has no ISO codes)
//   - ISO_A2 is unresolvable ("-99" with no EH fallback) → disputed territory
//   - year < 1  → datetime.date does not support BCE dates
function showCalendarPanel(feature, year, month, day) {
    const props = feature.properties;

    // Historical layers (aourednik/historical-basemaps) have no ISO_A2 field.
    // Contemporary Natural Earth layer has ISO_A2 (sometimes "-99" for edge cases).
    if (!props || props.ISO_A2 === undefined) return;

    // Resolve ISO code: try ISO_A2, fall back to ISO_A2_EH (e.g. Norway, France
    // overseas territories appear as "-99" in the 110m Natural Earth dataset).
    let iso = props.ISO_A2;
    if (iso === '-99') iso = props.ISO_A2_EH || '-99';
    if (iso === '-99') {
        // Disputed territory with no resolvable ISO code — show panel with no-data message.
        calendarPanel.style.display = 'block';
        calendarPanel.innerHTML = '<p class="error">No calendar data available for this territory.</p>';
        return;
    }

    // Calendar API requires year >= 1 (Python datetime.date minimum is year 1 CE).
    if (year < 1) return;

    // Build ISO date string from the current year/month/day (from slider + date input).
    // padStart(4) on year: Python's date.fromisoformat() also requires 4-digit years.
    const yyyy    = String(year).padStart(4, '0');
    const mm      = String(month).padStart(2, '0');
    const dd      = String(day).padStart(2, '0');
    const dateStr = yyyy + '-' + mm + '-' + dd;

    // Pass the country display name as a query param so Flask can show it in the panel
    // without a second lookup. encodeURIComponent handles names with spaces/accents.
    const name    = encodeURIComponent(props.NAME || iso);
    const url     = '/api/calendars/panel?date=' + dateStr + '&region=' + iso + '&name=' + name;

    // Make the panel visible before the request completes so the user sees immediate feedback.
    calendarPanel.style.display = 'block';

    // htmx.ajax() sends the GET request and swaps the response HTML into #calendar-panel.
    // 'innerHTML' replaces the panel content without removing the panel element itself.
    htmx.ajax('GET', url, { target: '#calendar-panel', swap: 'innerHTML' });
}

// Called by Leaflet once per feature when addData() populates the layer.
// Attaches the click handler that triggers the calendar panel.
// onEachFeature is re-called for every feature on each updateBorders() call
// (clearLayers + addData), so click handlers stay in sync after year changes.
function onEachFeature(feature, layer) {
    layer.on('click', function() {
        const year  = parseInt(slider.value, 10);
        // Read month/day from the date input; fall back to June 15 if input is empty (BCE mode).
        const parts = dateInput.value ? dateInput.value.split('-') : [year, 6, 15];
        const month = parseInt(parts[1], 10);
        const day   = parseInt(parts[2], 10);
        showCalendarPanel(feature, year, month, day);
    });
}

// ---------------------------------------------------------------------------
// Calendar overlay — colors + date labels per country
// ---------------------------------------------------------------------------

// Fill color per calendar system. Keys match "primary_calendar" from /api/calendars/overlay.
// Saturated enough to be distinguishable over the OSM tile background.
const CALENDAR_COLORS = {
    gregorian: '#5b9bd5',  // medium blue
    julian:    '#7ec8e3',  // cyan
    hijri:     '#e8902a',  // orange
    persian:   '#9b59b6',  // purple
    hebrew:    '#d4ac0d',  // gold
    japanese:  '#e74c8c',  // pink
    coptic:    '#27ae60',  // green
    ethiopian: '#1a5276',  // dark navy
};

// Separate LayerGroup for label markers — independent from bordersLayer.
// Clearing labels does not affect polygons or their click handlers.
const labelsLayer = L.layerGroup().addTo(map);

// Last fetched overlay payload. Kept in memory so zoom changes can
// rebuild labels without triggering a new API call.
let overlayData = null;

// Build (or rebuild) one L.divIcon label marker per visible country.
// Called after a successful overlay fetch AND on every zoomend event.
function rebuildLabels() {
    labelsLayer.clearLayers();
    if (!overlayData) return;
    // Below zoom 4 the world view is too small: labels overlap heavily.
    // Clearing layers (above) hides them; they reappear when the user zooms in.
    if (map.getZoom() < 4) return;

    // Scale font size with zoom level: small at zoom 2, larger as user zooms in.
    const zoom     = map.getZoom();
    const fontSize = Math.max(8, Math.round(zoom * 2 + 4)) + 'px';

    // Iterate over features currently loaded in the borders layer.
    // This avoids a second fetch — we reuse whatever borders are displayed.
    bordersLayer.eachLayer(function(layer) {
        const props = layer.feature.properties;
        if (!props) return;

        // Resolve ISO code (same logic as showCalendarPanel).
        let iso = props.ISO_A2;
        if (iso === '-99') iso = props.ISO_A2_EH || '-99';
        if (iso === '-99') return;

        const data = overlayData[iso];
        if (!data) return;

        // LABEL_Y / LABEL_X: pre-computed visual centroids in Natural Earth.
        // More accurate than the geometric centroid for elongated/non-convex countries.
        const lat = props.LABEL_Y;
        const lng = props.LABEL_X;
        if (lat == null || lng == null) return;

        // L.divIcon renders arbitrary HTML at a map coordinate.
        // className applies .calendar-label + .cal-<system> CSS rules.
        // style inline overrides font-size dynamically based on current zoom.
        const icon = L.divIcon({
            className: 'calendar-label cal-' + data.primary_calendar,
            html: '<span style="font-size:' + fontSize + '">' + data.formatted + '</span>',
            iconSize: null,  // let CSS control sizing; null disables Leaflet's default 12×12px box
        });

        // interactive: false lets click events pass through to the polygon below.
        L.marker([lat, lng], { icon: icon, interactive: false })
            .addTo(labelsLayer);
    });
}

// Fetch calendar overlay data and apply colors + labels to the borders layer.
// Only meaningful for year > 2010: aourednik historical features have no ISO_A2,
// so calendar mapping is impossible. Historical years reset to default style.
function updateCalendarOverlay(year, month, day) {
    if (year <= 2010) {
        // Reset fill to default blue and hide all labels.
        bordersLayer.setStyle({ fillColor: '#457b9d', fillOpacity: 0.2 });
        labelsLayer.clearLayers();
        overlayData = null;
        return;
    }

    // Pass month and day so the overlay reflects the exact selected date, not June 15.
    fetch('/api/calendars/overlay?year=' + year + '&month=' + month + '&day=' + day)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            overlayData = data;

            // eachLayer iterates each polygon and calls layer.setStyle() individually.
            // More reliable than setStyle(fn) across Leaflet versions.
            // Click handlers attached by onEachFeature survive setStyle calls.
            bordersLayer.eachLayer(function(layer) {
                const props = layer.feature.properties;
                let iso = props.ISO_A2;
                if (iso === '-99') iso = props.ISO_A2_EH || '-99';
                const calData = (iso !== '-99') ? data[iso] : null;
                // Specify all path properties explicitly — Leaflet may reset to
                // defaults (blue stroke, weight 3) if only partial style is passed.
                layer.setStyle({
                    color:       '#e63946',  // border stroke color
                    weight:      1,          // border stroke width
                    fillColor:   calData ? (CALENDAR_COLORS[calData.primary_calendar] || '#457b9d') : '#457b9d',
                    fillOpacity: calData ? 0.45 : 0.2,
                });
            });

            rebuildLabels();
        })
        .catch(function(err) {
            console.error('Failed to load calendar overlay:', err);
        });
}

// Rebuild labels on zoom so font size stays proportional to the zoom level.
// overlayData is already in memory — no new fetch needed.
map.on('zoomend', rebuildLabels);

// ---------------------------------------------------------------------------
// Borders layer
// ---------------------------------------------------------------------------

// Empty GeoJSON layer for borders, added to map immediately.
// clearLayers() + addData() updates it in-place without re-creating the layer.
const bordersLayer = L.geoJSON(null, {
    style: {
        color: '#e63946',       // border stroke color
        weight: 1,              // border stroke width in pixels
        fillColor: '#457b9d',   // polygon fill color
        fillOpacity: 0.2        // polygon fill transparency (0=invisible, 1=opaque)
    },
    // onEachFeature wires up the click → calendar panel for every feature loaded.
    onEachFeature: onEachFeature
}).addTo(map);

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------

// Fetch borders from the API for the given date and update the map layer.
// year/month/day map to the three-source pipeline in api/borders.py:
//   year > 2019 or absent → Natural Earth, year 1886-2019 → CShapes, year < 1886 → aourednik.
// month and day are only meaningful for the CShapes range (1886-2019).
function updateBorders(year, month, day) {
    let url;
    if (year === undefined || year > 2019) {
        url = '/api/borders';
    } else {
        url = '/api/borders?year=' + year + '&month=' + month + '&day=' + day;
    }
    fetch(url)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            bordersLayer.clearLayers();
            bordersLayer.addData(data);
            // Calendar overlay runs after borders are loaded: rebuildLabels() iterates
            // bordersLayer.eachLayer(), so features must exist before it is called.
            const y = year !== undefined ? year : parseInt(slider.value, 10);
            updateCalendarOverlay(y, month, day);
        })
        .catch(function(err) {
            console.error('Failed to load borders:', err);
        });
}

// ---------------------------------------------------------------------------
// Year label formatting
// ---------------------------------------------------------------------------

// Convert a signed integer year to a human-readable string.
// JS Date is unreliable before 100 CE, so we use plain integers throughout.
//   formatYear(2010)  → "2010 CE"
//   formatYear(0)     → "Year 0"
//   formatYear(-500)  → "500 BCE"
function formatYear(year) {
    if (year > 2010) return 'Present';
    if (year > 0) return year + ' CE';
    if (year === 0) return 'Year 0';
    return Math.abs(year) + ' BCE';
}

// ---------------------------------------------------------------------------
// Slider
// ---------------------------------------------------------------------------

const slider      = document.getElementById('year-slider');
const yearTooltip = document.getElementById('year-tooltip');
const dateInput   = document.getElementById('date-input');

const SLIDER_MIN = -3000;
const SLIDER_MAX = 2100;

// Debounce timer handle. Reused on every slider move to avoid firing the API
// on every pixel of movement — we wait until the user pauses for 300ms.
let debounceTimer = null;

// Read current month/day from the date input.
// Falls back to June 15 in BCE mode (type="text", value="BCE 432" — not a parseable date).
function getCurrentMonthDay() {
    if (dateInput.type === 'date' && dateInput.value) {
        const parts = dateInput.value.split('-');
        return { month: parseInt(parts[1], 10), day: parseInt(parts[2], 10) };
    }
    return { month: 6, day: 15 };
}

// ---------------------------------------------------------------------------
// Tick marks + year tooltip
// ---------------------------------------------------------------------------

// Move the year tooltip badge above the slider thumb.
// The thumb doesn't travel the full track width — the browser reserves thumbWidth/2
// of padding on each side so the thumb center aligns with the track endpoints.
// Without this correction the badge drifts left at the start and right at the end.
function updateTooltip(year) {
    const thumbWidth = 18;  // matches #year-slider::-webkit-slider-thumb width in CSS
    const percent    = (year - SLIDER_MIN) / (SLIDER_MAX - SLIDER_MIN);
    const trackWidth = slider.offsetWidth;
    const left       = percent * (trackWidth - thumbWidth) + thumbWidth / 2;
    yearTooltip.style.left    = left + 'px';
    yearTooltip.textContent   = formatYear(year);
}

// Generate tick marks inside #ticks once the slider width is known.
// BCE range is sparse (millennia only); CE range shows a tick every century
// with a label every 500 years to avoid crowding.
function buildTicks() {
    const ticks = document.getElementById('ticks');
    ticks.innerHTML = '';

    function addTick(year, major) {
        const percent = (year - SLIDER_MIN) / (SLIDER_MAX - SLIDER_MIN) * 100;
        const el      = document.createElement('div');
        el.className  = 'tick';
        el.style.left = percent + '%';
        if (major) {
            // Label above + longer line below
            const label     = document.createElement('span');
            label.className = 'tick-label';
            label.textContent = year < 0 ? Math.abs(year) + ' BCE'
                              : year === 0 ? '0'
                              : year + ' CE';
            const line      = document.createElement('div');
            line.className  = 'tick-line major';
            el.appendChild(label);
            el.appendChild(line);
        } else {
            const line     = document.createElement('div');
            line.className = 'tick-line minor';
            el.appendChild(line);
        }
        ticks.appendChild(el);
    }

    // BCE: label only at millennia — range is too wide for century labels
    for (let y = SLIDER_MIN; y < 0; y += 1000) addTick(y, true);

    // Year 0: major label
    addTick(0, true);

    // CE: minor tick every 100 years, major label every 500 years
    for (let y = 100; y <= 2000; y += 100) {
        addTick(y, y % 500 === 0);
    }
}

// Rebuild ticks when window is resized — offsets are pixel-based.
window.addEventListener('resize', function() {
    buildTicks();
    updateTooltip(parseInt(slider.value, 10));
});

// ---------------------------------------------------------------------------
// Slider
// ---------------------------------------------------------------------------

// Slider moved → sync date input year, keep current month/day, trigger API.
slider.addEventListener('input', function() {
    const year = parseInt(this.value, 10);

    // Update tooltip position and text immediately for instant drag feedback.
    updateTooltip(year);

    if (year < 1) {
        // <input type="date"> does not support BCE years.
        // Switch to type="text" to display a readable label ("BCE 432") instead of an empty field.
        dateInput.type     = 'text';
        dateInput.value    = 'BCE ' + Math.abs(year);
        dateInput.readOnly = true;
    } else {
        // Restore type="date" when returning to CE years.
        dateInput.type     = 'date';
        dateInput.readOnly = false;
        // Update only the year part of the date input, preserving month and day.
        // padStart(4) required: <input type="date"> rejects years shorter than 4 digits.
        const { month, day } = getCurrentMonthDay();
        const yyyy = String(year).padStart(4, '0');
        const mm   = String(month).padStart(2, '0');
        const dd   = String(day).padStart(2, '0');
        dateInput.value = yyyy + '-' + mm + '-' + dd;
    }

    // Hide the calendar panel when the date changes — displayed calendars must
    // always correspond to the currently visible map snapshot.
    calendarPanel.style.display = 'none';
    calendarPanel.innerHTML     = '';

    // Cancel the previous pending request (if the user is still moving).
    clearTimeout(debounceTimer);

    // Schedule the API call 300ms after the last movement.
    debounceTimer = setTimeout(function() {
        const { month, day } = getCurrentMonthDay();
        updateBorders(year, month, day);
    }, 300);
});

// Date input changed → sync slider to the new year, trigger API.
dateInput.addEventListener('change', function() {
    if (!this.value) return;
    const parts = this.value.split('-');
    const year  = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10);
    const day   = parseInt(parts[2], 10);

    // Clamp year to slider range and sync.
    slider.value = Math.min(Math.max(year, -3000), 2100);
    updateTooltip(year);

    calendarPanel.style.display = 'none';
    calendarPanel.innerHTML     = '';

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function() {
        updateBorders(year, month, day);
    }, 300);
});

// ---------------------------------------------------------------------------
// Initial load
// ---------------------------------------------------------------------------

// Load the snapshot matching the slider's default value on page load.
// buildTicks() and updateTooltip() run after layout so offsetWidth is non-zero.
const _init = getCurrentMonthDay();
buildTicks();
updateTooltip(parseInt(slider.value, 10));
updateBorders(parseInt(slider.value, 10), _init.month, _init.day);
