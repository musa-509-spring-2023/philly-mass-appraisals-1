mapboxgl.accessToken = 'pk.eyJ1IjoieWVzZW5pYW8iLCJhIjoiY2tlZjAyM3p5MDNnMjJycW85bmpjenFkOCJ9.TDYe7XRNP8CnAto0kLA5zA';

const map = new mapboxgl.Map({
    container: 'map', // container ID
    // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
    style: 'mapbox://styles/mapbox/light-v9', // style URL
    center: [-75.116728, 39.993436], // starting position [lng, lat],
    zoom: 11.2, // starting zoom
});

window.map = map;

let mydata = {};

// $.ajax({
//     url: "https://phl.carto.com/api/v2/sql?filename=opa_properties_public&format=geojson&skipfields=cartodb_id&q=SELECT+*+FROM+opa_properties_public",
//     type: "GET",
//     dataType: "json",
//     async: false,
//     success: function(data) {
//         mydata = data;
//     },
//     error: function (err) {
//         console.log(err);
//     },
// });
//
// console.log(mydata)