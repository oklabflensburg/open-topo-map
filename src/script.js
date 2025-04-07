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
    // Ensure the value is clamped within the min-max range
    value = Math.max(min, Math.min(max, value));

    // Calculate the normalized value between 0 and 1
    const normalizedValue = (value - min) / (max - min);

    // Convert the normalized value to a grayscale value between 0 (black) and 255 (white)
    const grayscale = Math.floor(normalizedValue * 255);

    // Return the color as a string in rgb format
    return `rgb(${grayscale}, ${grayscale}, ${grayscale})`;
}

function getColorFromHeight(h) {
    // Clamp between 0 and 150
    const clamped = Math.max(0, Math.min(150, h))

    // Use HSL where 240 (blue) → 120 (green) → 0 (red) → 60 (yellow)
    let hue
    if (clamped <= 50) {
        hue = 240 - (clamped / 50) * 120 // 240 to 120
    } else if (clamped <= 100) {
        hue = 120 - ((clamped - 50) / 50) * 120 // 120 to 0
    } else {
        hue = ((clamped - 100) / 50) * 60 // 0 to 60
    }

    return `hsl(${hue}, 100%, 50%)`
}

function rowToFeature(row) {
    if (row.length < 11) return null

    const tileNumberIndex = 0
    const dateIndex = 1
    const daysSince1970Index = 2
    const valueCountIndex = 3
    const coordIndex= 4
    const minValueIndex= 12
    const maxValueIndex= 13
    const meanValueIndex= 14
    const errCodeIndex= 15
    const coords = [
        [parseFloat(row[coordIndex]), parseFloat(row[coordIndex + 1])],
        [parseFloat(row[coordIndex + 2]), parseFloat(row[coordIndex + 3])],
        [parseFloat(row[coordIndex + 4]), parseFloat(row[coordIndex + 5])],
        [parseFloat(row[coordIndex + 6]), parseFloat(row[coordIndex + 7])],
        [parseFloat(row[coordIndex]), parseFloat(row[coordIndex + 1])]
    ]

    const meanHeight = parseFloat(row[row.length - 2]) // 2nd last column
    // const color = getColorFromValue(parseInt(row[daysIndex]), 12815, 19420)
    const color = getColorFromHeight(meanHeight)

    const tile = row[tileNumberIndex]
    const date = row[dateIndex]
    const valueCount = row[valueCountIndex]
    const min = row[minValueIndex]
    const max = row[maxValueIndex]
    const mean = row[meanValueIndex]

    const label =
        `Tile: ${tile}\nDate: ${date}\nValues: ${valueCount}\nMin: ${min}\nMax: ${max}\nMean: ${mean}`

    return {
        type: "Feature",
        properties: { label, color },
        geometry: {
            type: "Polygon",
            coordinates: [coords]
        }
    }
}

map.on('load', () => {
    const csvUrl = '/topo-tiles-meta.csv'
    fetch(csvUrl)
        .then(res => res.text())
        .then(csvText => {
            const features = []

            Papa.parse(csvText, {
                skipEmptyLines: true,
                complete: function (results) {
                    for (const row of results.data) {
                        const feature = rowToFeature(row)
                        if (feature) features.push(feature)
                    }

                    const geojson = {
                        type: "FeatureCollection",
                        features
                    }

                    map.addSource("polygons", {
                        type: "geojson",
                        data: geojson
                    })

                    map.addLayer({
                        id: "polygons-fill",
                        type: "fill",
                        source: "polygons",
                        paint: {
                            "fill-color": ["get", "color"],
                            "fill-opacity": 0.5
                        }
                    })

                    map.addLayer({
                        id: "polygons-outline",
                        type: "line",
                        source: "polygons",
                        paint: {
                            "line-color": "#444",
                            "line-width": 0.5
                        }
                    })

                    // Add click event to show popup
                    map.on('click', 'polygons-fill', function (e) {
                        const feature = e.features[0];
                        const labelRaw = feature.properties.label;

                        // Convert \n to <br> for HTML popup
                        const labelHtml = labelRaw.replace(/\n/g, '<br>');

                        new maplibregl.Popup()
                            .setLngLat(e.lngLat)
                            .setHTML(`<div style="font-family: monospace;">${labelHtml}</div>`)
                            .addTo(map);
                    });

                    map.on('mouseenter', 'polygons-fill', () => {
                        map.getCanvas().style.cursor = 'pointer'
                    })

                    map.on('mouseleave', 'polygons-fill', () => {
                        map.getCanvas().style.cursor = ''
                    })
                }
            })
        })
})