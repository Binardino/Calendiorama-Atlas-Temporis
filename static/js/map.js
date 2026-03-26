// Initialize Leaflet map centered on the world
const map = L.map('map').setView([20, 0], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Empty GeoJSON layer for national borders, added to map immediately
const bordersLayer = L.geoJSON(null, {
    style: {
        color: '#e63946',       // border stroke color
        weight: 1,              // border stroke width in pixels
        fillColor: '#457b9d',   // polygon fill color
        fillOpacity: 0.2        // polygon fill transparency (0=invisible, 1=opaque)
    }
}).addTo(map);

// Fetch borders from the API for a given date and update the map layer
function updateBorders(date) {
    fetch('/api/borders?date=' + date)
        .then(function(response) { return response.json(); })
        .then(function(data) {
            bordersLayer.clearLayers();
            bordersLayer.addData(data);
        })
        .catch(function(err) {
            console.error('Failed to load borders:', err);
        });
}

// Load contemporary borders on startup
updateBorders('2024-01-01');
