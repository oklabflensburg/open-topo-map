import maplibregl from 'maplibre-gl'
import Papa from 'papaparse'

import 'maplibre-gl/dist/maplibre-gl.css'

const map = new maplibregl.Map({
    container: 'map',
    style: {
        version: 8,
        sources: {
            customRasterTiles: {
                type: 'raster',
                tiles: ['https://tiles.oklabflensburg.de/fosm/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: "© My Custom Tiles"
            }
        },
        layers: [{
            id: 'custom-tiles',
            type: 'raster',
            source: 'customRasterTiles',
            minzoom: 0,
            maxzoom: 18
        }]
    },
    center: [9.4, 54.8],
    zoom: 10
})

function getColorFromValue(value, min, max) {
    value = Math.max(min, Math.min(max, value));
    const normalizedValue = (value - min) / (max - min);
    const grayscale = Math.floor(normalizedValue * 255);
    return `rgb(${grayscale}, ${grayscale}, ${grayscale})`;
}

function getColorFromHeight(h) {
    const clamped = Math.max(0, Math.min(150, h))
    let hue;
    if (clamped <= 50) {
        hue = 240 - (clamped / 50) * 120;
    } else if (clamped <= 100) {
        hue = 120 - ((clamped - 50) / 50) * 120;
    } else {
        hue = ((clamped - 100) / 50) * 60;
    }
    return `hsl(${hue}, 100%, 50%)`;
}

function rowToFeature(row) {
    if (row.length < 11) return null;

    const tileNumberIndex = 0;
    const dateIndex = 1;
    const coordIndex = 4;
    const minValueIndex = 12;
    const maxValueIndex = 13;
    const meanValueIndex = 14;
    const coords = [
        [parseFloat(row[coordIndex]), parseFloat(row[coordIndex + 1])],
        [parseFloat(row[coordIndex + 2]), parseFloat(row[coordIndex + 3])],
        [parseFloat(row[coordIndex + 4]), parseFloat(row[coordIndex + 5])],
        [parseFloat(row[coordIndex + 6]), parseFloat(row[coordIndex + 7])],
        [parseFloat(row[coordIndex]), parseFloat(row[coordIndex + 1])]
    ];

    const meanHeight = parseFloat(row[row.length - 2]);
    const color = getColorFromHeight(meanHeight);

    const tile = row[tileNumberIndex];
    const date = row[dateIndex];
    const valueCount = row[3];
    const min = row[minValueIndex];
    const max = row[maxValueIndex];
    const mean = row[meanValueIndex];

    const label = `Tile: ${tile}\nDate: ${date}\nValues: ${valueCount}\nMin: ${min}\nMax: ${max}\nMean: ${mean}`;

    return {
        type: "Feature",
        properties: { label, color, tile },
        geometry: {
            type: "Polygon",
            coordinates: [coords]
        }
    };
}

map.on('load', () => {
    const csvUrl = '/topo-tiles-meta.csv';
    fetch(csvUrl)
        .then(res => res.text())
        .then(csvText => {
            const features = [];

            Papa.parse(csvText, {
                skipEmptyLines: true,
                complete: function (results) {
                    for (const row of results.data) {
                        const feature = rowToFeature(row);
                        if (feature) features.push(feature);
                    }

                    const geojson = {
                        type: "FeatureCollection",
                        features
                    };

                    map.addSource("polygons", {
                        type: "geojson",
                        data: geojson
                    });

                    map.addLayer({
                        id: "polygons-fill",
                        type: "fill",
                        source: "polygons",
                        paint: {
                            "fill-color": ["get", "color"],
                            "fill-opacity": 0.5
                        }
                    });

                    map.addLayer({
                        id: "polygons-outline",
                        type: "line",
                        source: "polygons",
                        paint: {
                            "line-color": "#444",
                            "line-width": 0.5
                        }
                    });

                    // Add a highlight layer
                    map.addLayer({
                        id: 'highlighted-polygon',
                        type: 'line',
                        source: 'polygons',
                        paint: {
                            'line-color': 'rgba(0, 0, 0, 1)', // Red color for the outline
                            'line-width': 3 // Adjust this value for the thickness of the outline
                        },
                        filter: ['==', 'tile', ''] // Start with an empty filter (no tiles are highlighted initially)
                    });

                    // Variable to keep track of the currently open popup
                    let currentPopup = null;

                    // Add click event to show popup when clicking on a polygon
                    map.on('click', 'polygons-fill', function (e) {
                        const feature = e.features[0];
                        const labelRaw = feature.properties.label;

                        // Convert \n to <br> for HTML popup
                        const labelHtml = labelRaw.replace(/\n/g, '<br>');

                        // If a popup is already open, remove it
                        if (currentPopup) {
                            currentPopup.remove();
                        }

                        // Create a new popup
                        currentPopup = new maplibregl.Popup()
                            .setLngLat(e.lngLat)
                            .setHTML(`<div style="font-family: monospace;">${labelHtml}</div>`)
                            .addTo(map);

                        // Highlight the clicked tile by setting filter on the highlight layer
                        map.setFilter('highlighted-polygon', ['==', 'tile', feature.properties.tile]);
                    });

                    // Remove the popup when clicking anywhere else (empty area)
                    map.on('click', function (e) {
                        const features = map.queryRenderedFeatures(e.point);
                        if (!features.length) {  // No features were clicked, remove the popup
                            if (currentPopup) {
                                currentPopup.remove();
                            }

                            // Clear the highlight
                            map.setFilter('highlighted-polygon', ['==', 'tile', '']);
                        }
                    });

                    map.on('mouseenter', 'polygons-fill', () => {
                        map.getCanvas().style.cursor = 'pointer';
                    });

                    map.on('mouseleave', 'polygons-fill', () => {
                        map.getCanvas().style.cursor = '';
                    });
                }
            });
        });
});