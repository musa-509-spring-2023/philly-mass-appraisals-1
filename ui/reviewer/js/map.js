mapboxgl.accessToken = 'pk.eyJ1IjoieWVzZW5pYW8iLCJhIjoiY2tlZjAyM3p5MDNnMjJycW85bmpjenFkOCJ9.TDYe7XRNP8CnAto0kLA5zA';

const map = new mapboxgl.Map({
    container: 'map', // container ID
    // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
    style: 'mapbox://styles/mapbox/light-v9', // style URL
    center: [-75.116728, 39.993436], // starting position [lng, lat],
    zoom: 13, // starting zoom
});

// window.map = map;

map.on('load', () => {
     map.addSource('tileSet', {
         type: 'vector',
         'tileSize': 512,
         scheme: "xyz",
         tiles: ['https://storage.googleapis.com/musa509s23_team01_public/tiles/properties/{z}/{x}/{y}.pbf']
     });

     map.addLayer({
         'id': 'my-layer',
         'type': 'fill',
         'source': 'tileSet',
         'source-layer': 'property_tile_info',
         'paint': {
             // Use a match expression to create a property value-dependent style
             'fill-color': [
                'match',
                ['get', 'assessed_value'],
                // Breakpoints and corresponding colors
                0, '#ffeda0',
                100000, '#feb24c',
                200000, '#f03b20',
                500000, '#bd0026',
                1000000, '#800026',
                // Default color if the value doesn't match any of the above breakpoints
                '#000000'
            ],
            'fill-opacity': 0.8
         }
     });
    })




    // map.addLayer({
    //     'id': 'my-layer',
    //     'type': 'raster',
    //     'source': 'vector',
    //     'paint': {
    //         'fill-color': 'red'
    //     }
    // });
