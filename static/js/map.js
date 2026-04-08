// Initialize Leaflet map centered on the world
const map = L.map('map').setView([20, 0], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Empty GeoJSON layer for borders, added to map immediately.
// clearLayers() + addData() updates it in-place without re-creating the layer.
const bordersLayer = L.geoJSON(null, {
    style: {
        color: '#e63946',       // border stroke color
        weight: 1,              // border stroke width in pixels
        fillColor: '#457b9d',   // polygon fill color
        fillOpacity: 0.2        // polygon fill transparency (0=invisible, 1=opaque)
    }
}).addTo(map);

// ---------------------------------------------------------------------------
// API call
// ---------------------------------------------------------------------------

// Fetch borders from the API for a given year (integer) and update the map layer.
// Called with no argument → /api/borders (contemporary Natural Earth data).
// Called with a year    → /api/borders?year=<int> (historical snapshot).
function updateBorders(year) {
    const url = (year !== undefined) ? '/api/borders?year=' + year : '/api/borders';
    fetch(url)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            bordersLayer.clearLayers();
            bordersLayer.addData(data);
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
