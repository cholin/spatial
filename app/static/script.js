function setStyle(feature) {
  var hue = 30 + 240 * (50 - 2*feature.properties.value) / 60;
  return {
    "color": "hsl(" + [hue, '100%', '50%'] + ")",
    "weight": 0,
    "opacity": 0.65
  };
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
  var geojsonMarkerOptions = {
    radius: 4,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
  };
  var geojsonLayer = new L.GeoJSON.AJAX("api/measurements/temperature",{
    onEachFeature: onEachFeature,
    style: setStyle,
    middleware: function(data) {
      // return geojson data
      return data.measurements;
    },
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, geojsonMarkerOptions);
    }
  }).addTo(map);

  function highlightFeature(feature, layer) {

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

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
    });
  }

function resetHighlight(e) {
    geojsonLayer.resetStyle(e.target);
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: function(e) {
          if (feature.properties && feature.properties.name) {
            e.target.bindPopup(
                  "<h3>" + feature.properties.name + "</h3>"
                + "<dl>"
                + "  <dt>"+feature.properties.type+"</dt>"
                + "  <dd>"+feature.properties.value+"</dd>"
                + "  <dt>Altitude</dt>"
                + "  <dd>"+feature.properties.altitude+"</dd>"
                + "</dl>"
            );
          e.target.setStyle({
              weight: 5,
              color: '#666',
              dashArray: '',
          });
          }

        },
        mouseout: resetHighlight
    });
}

  //
  // DatePicker
  //

  L.Control.DateTimePicker = L.Control.extend(
  {
    options: { position: 'bottomleft' },
    onAdd: function (map) {
      var controlDiv = L.DomUtil.create('div', 'info');
      var controlUI = L.DomUtil.create('input', '', controlDiv);
      controlUI.type = 'text';
      controlUI.id = 'dateTimePicker';
      controlUI.placeholder = 'Pick your date';

      return controlDiv;
    }
  });

  var dateTimePickerControl = new L.Control.DateTimePicker();
  map.addControl(dateTimePickerControl);
  $('#dateTimePicker').datetimepicker({
    format: "d.m.Y H:i",
    allowTimes: [
      '00:00', '06:00', '12:00', '18:00'
    ],
    defaultTime : '00:00',
    closeOnDateSelect : true,
    onChangeDateTime:function(dp,input){
      var date = new Date(dp).dateFormat('Y-m-d/H');
      $.get("api/forecasts/temperate/"+date, function( data ) {
          info.update(new Date(dp), data);

          var elem = $('#measurement');
          elem.prop('checked', true);
          elem.change();
      });

    }
  });

  var info = L.control();
  info.onAdd = function (map) {
      this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
      var p = L.DomUtil.create('p', '', this._div);
      p.innerHTML = 'No data selected';

      return this._div;
  };

  // method that we will use to update the control based on feature properties passed
  info.update = function (date, data) {
    var dateFormatted = date.dateFormat('Y-m-d/H');
    var html = ['<h4 id="date" data="'+dateFormatted+'">'+date.dateFormat('d.m.Y H:i')+'</h4>'];

    html.push('<label>');
    html.push('<input id="measurement" type="radio" class="leaflet-control-layers-selector" name="leaflet-base-layers" />');
    html.push('<span>Messung</span>');
    html.push('</label>');

    if (data && 'forecasts' in data && data.forecasts.length > 0) {
      html.push('<h5>Forecasts</h5>');
      for (var i=0; i < data.forecasts.length; ++i) {
        var elem = data.forecasts[i];
        var date = new Date(elem.date).dateFormat('d.m.Y H:i');
        html.push('<label class="forecast-entry">');
        html.push('<input type="radio" value="'+elem.rid+'" class="forecast-selector leaflet-control-layers-selector" name="leaflet-base-layers" />');
        html.push('<span>'+date+' ('+elem.interval+'h ago)</span>');
        html.push('</label>');
      }
    } else {
      html.push("<p>No forecasts available</p>");
    }

    this._div.innerHTML = html.join("");

    $('input[type=radio]').on('change', reloadLayers);
  };


  //
  //  Forecasts
  //
  var imageBounds = [[46.5,4.5], [56.5, 16.5]];
  var forecastLayer = L.imageOverlay("", imageBounds, {
      'opacity' : 0.5
  }).addTo(map);

  info.addTo(map);

function reloadLayers(elem) {
    var elem = $(this);
    if (elem.attr('class').indexOf('forecast-selector') >= 0) {
      map.removeLayer(geojsonLayer);
      map.addLayer(forecastLayer);

      var rid = elem.val();
      var url = "api/forecasts/raster/temperature/"+rid;
      if (forecastLayer._url !== url) {
        map.spin(true);
        forecastLayer.setUrl("api/forecasts/raster/temperature/"+rid);
        forecastLayer.on('load', function() {
            map.spin(false);
            map.addLayer(forecastLayer);
        });
      } else {
        map.addLayer(forecastLayer);
      }
    } else {
      map.removeLayer(forecastLayer);
      map.addLayer(geojsonLayer);

      var date = $('h4').attr('data');
      geojsonLayer.refresh("api/measurements/temperature/"+date);
    }
}



});
