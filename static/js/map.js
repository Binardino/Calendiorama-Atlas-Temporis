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
function showCalendarPanel(feature, year) {
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

    // Build date string: default to January 1st of the selected year.
    // The slider provides year-level precision; Jan 1 is a safe, unambiguous default.
    const dateStr = year + '-01-01';

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
        const year = parseInt(document.getElementById('year-slider').value, 10);
        showCalendarPanel(feature, year);
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
function updateCalendarOverlay(year) {
    if (year <= 2010) {
        // Reset fill to default blue and hide all labels.
        bordersLayer.setStyle({ fillColor: '#457b9d', fillOpacity: 0.2 });
        labelsLayer.clearLayers();
        overlayData = null;
        return;
    }

    fetch('/api/calendars/overlay?year=' + year)
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

// Fetch borders from the API for a given year (integer) and update the map layer.
// Called with no argument → /api/borders (contemporary Natural Earth data).
// Called with a year    → /api/borders?year=<int> (historical snapshot).
function updateBorders(year) {
    // year > 2010: no historical snapshot exists → use contemporary Natural Earth
    const url = (year !== undefined && year <= 2010)
    ? '/api/borders?year=' + year : '/api/borders';
    fetch(url)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            bordersLayer.clearLayers();
            bordersLayer.addData(data);
            // Calendar overlay runs after borders are loaded: rebuildLabels() iterates
            // bordersLayer.eachLayer(), so features must exist before it is called.
            updateCalendarOverlay(year !== undefined ? year : parseInt(slider.value, 10));
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

const slider    = document.getElementById('year-slider');
const yearLabel = document.getElementById('year-label');

// Debounce timer handle. Reused on every slider move to avoid firing the API
// on every pixel of movement — we wait until the user pauses for 300ms.
let debounceTimer = null;

slider.addEventListener('input', function() {
    const year = parseInt(this.value, 10);

    // Update the label immediately so feedback is instant while dragging
    yearLabel.textContent = formatYear(year);

    // Hide the calendar panel when the year changes — the displayed calendars
    // must always correspond to the currently visible map snapshot.
    calendarPanel.style.display = 'none';
    calendarPanel.innerHTML     = '';

    // Cancel the previous pending request (if the user is still moving)
    clearTimeout(debounceTimer);

    // Schedule the API call 300ms after the last movement
    debounceTimer = setTimeout(function() {
        updateBorders(year);
    }, 300);
});

// ---------------------------------------------------------------------------
// Initial load
// ---------------------------------------------------------------------------

// Load the snapshot matching the slider's default value on page load.
updateBorders(parseInt(slider.value, 10));
