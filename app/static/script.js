function onEachFeature(feature, layer) {
    if (feature.properties && feature.properties.name) {
      layer.bindPopup(
            "<h3>" + feature.properties.name + "</h3>"
          + "<dl>"
          + "  <dt>"+feature.properties.type+"</dt>"
          + "  <dd>"+feature.properties.value+"</dd>"
          + "  <dt>Altitude</dt>"
          + "  <dd>"+feature.properties.altitude+"</dd>"
          + "</dl>"
      );
    }
}


function setStyle(feature) {
  var hue = 30 + 240 * (50 - 2*feature.properties.value) / 60;
  return {
    "color": "hsl(" + [hue, '100%', '50%'] + ")",
    "weight": 0,
    "opacity": 0.65
  };
}


function getDate() {
  var max = parseInt($('.slider input').attr('max'));
  var val = parseInt($('.slider input').val());
  var offset = (max-val)*1000*60*60*24;
  var date = new Date(new Date().getTime() - offset);

  return date.getFullYear() + '-' +
         (parseInt(date.getMonth())+1) + '-' +
         date.getDate();
}


$(function() {
  // create leaflet map with grey tiles
  var map = L.map('map').setView([51.8, 10], 6);
  L.tileLayer('https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png', {
          maxZoom: 18,
          id: 'examples.map-20v6611k'
  }).addTo(map);

  //
  // geojson layer (leaflet-ajax plugin)
  //
  var geojsonLayer = new L.GeoJSON.AJAX("api/measurements/temperature",{
    onEachFeature: onEachFeature,
    style: setStyle,
    middleware: function(data) {
      // set date in slider info section
      var elem = $('.slider p');
      if (elem.length != 0) {
        elem.html(data.date);
      } else {
        $('.slider').append("<p>"+data.date+"</p>");
      }

      // if there is no data, add text to slider info section
      if (data.measurements.length == 0) {
        var span = "<span style=\"display:block;color:red\"> no data</span>";
        $('.slider p').append(span);
      }

      // return geojson data
      return data.measurements;
    }
  }).addTo(map);


  //
  //  Forecasts
  //
  var imageBounds = [[46.75,4.75], [56.25, 16.25]];
  var imageUrl = 'http://localhost:5000/api/forecasts/temperature'

  var forecastLayer = L.imageOverlay(imageUrl, imageBounds, {
      'opacity' : 0.5
  });

  //
  // slider control
  //
  L.Control.Slider = L.Control.extend(
  {
    options: { position: 'bottomleft' },
    onAdd: function (map) {
      var controlDiv = L.DomUtil.create('div', 'leaflet-draw-toolbar leaflet-bar slider');
      L.DomEvent
        // add functionality to reload data
        .addListener(controlDiv, 'change', function() {
          geojsonLayer.refresh("api/measurements/temperature/"+getDate());
          forecastLayer.setUrl("api/forecasts/temperate/"+getDate());
        })

        .addListener(controlDiv, 'click', L.DomEvent.stopPropagation)
        .addListener(controlDiv, 'click', L.DomEvent.preventDefault)

        // disable dragging for map otherwise slider is not useable
        .addListener(controlDiv, 'mouseover', function() {
            map.dragging.disable()
          })

        // enable dragging for map again
        .addListener(controlDiv, 'mouseout', function() {
          map.dragging.enable();
          })

      var controlUI = L.DomUtil.create('input', 'leaflet-draw-edit-remove full-width', controlDiv);
      controlUI.type = 'range';
      controlUI.min = '0';
      controlUI.max = '100';
      controlUI.value = '100';
      controlUI.step = '1';

      return controlDiv;
    }
  });

  //
  // GroupedLayers
  //
  var sliderControl = new L.Control.Slider();
  map.addControl(sliderControl);

  var baseLayers = {
    "Messung": geojsonLayer,
    "Vorhersage": forecastLayer
  };

  var options = {'collapsed' : false};
  var layerControl = L.control.groupedLayers(baseLayers, {}, options);
  map.addControl(layerControl);
});
