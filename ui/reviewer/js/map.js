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
                'case',
                ['all', ['>=', ['get', 'current_assessed_value'], 0], ['<=', ['get', 'current_assessed_value'], 100000]],
                'red',
                'blue',
              ],
            'fill-opacity': 0.8,
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
