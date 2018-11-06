var markerSource = new ol.source.Vector()
var select = new ol.interaction.Select({
        condition: ol.events.condition.click
      });

var markerStyle = new ol.style.Style({
      image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
        anchor: [0.5, 46],
        anchorXUnits: 'fraction',
        anchorYUnits: 'pixels',
        opacity: 1,
        src: 'https://openlayers.org/en/v5.3.0/examples/data/icon.png'
      }))
    });

var map = new ol.Map({
        layers: [
          new ol.layer.Tile({
            source: new ol.source.OSM()
          }),
          new ol.layer.Vector({
            source: markerSource,
            style: markerStyle,
          })
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([165.4572000, -21.6763100]),
            zoom: 8
        })
    });
function init_map(){
    map = new ol.Map({
        layers: [
          new ol.layer.Tile({
            source: new ol.source.OSM()
          }),
          new ol.layer.Vector({
            source: markerSource,
            style: markerStyle,
          })
        ],
        target: document.getElementById('map'),
        view: new ol.View({
            center: ol.proj.fromLonLat([165.4572000, -21.6763100]),
            zoom: 8
        })
    });
    map.addInteraction(select);
}


function addMarker(data) {

  var iconFeatures = [];

  var iconFeature = new ol.Feature({
    type: 'icon',
    geometry: new ol.geom.Point(ol.proj.transform([data['longitude'], data['latitude']], 'EPSG:4326',
      'EPSG:3857')),
    name: data['id'],
  });
  iconFeature.setProperties(
      {"id" : data['id'],
       "longitude" : data['longitude'],
       "latitude": data['latitude'],
       "loc": data['loc'],
       "default_loc": data['default_loc']
       }
  );

  markerSource.addFeature(iconFeature);
}

function update_map(){
    var taxon = django.jQuery("#id_taxon").val();
    django.jQuery.get('/fatercal/update_map', {taxon: taxon}, function(data){
               if (data == null){
                   console.log('echec');
               } else {
                    console.log('good');
                    markerSource.clear();
                    for (var i = 0; i < data.length; i++ ){
                        addMarker(data[i])
                    }
               }
    });
};

select.on('select', function(e) {
    var divIcon = document.getElementById("selected_icon");
    divIcon.innerHTML = "";
    e.selected.forEach(function(element){
        console.log(element)
        divIcon.innerHTML = divIcon.innerHTML +
        "<a href=/fatercal/prelevement/" + element.get("id") + "/>Lien vers le prélèvement</a>" +
        "<br> Lontitude: " + element.get("longitude") +", Latitude: " + element.get("latitude") + "<br>";
        if (element.get("loc") == null){
            divIcon.innerHTML = divIcon.innerHTML + "Ce prélèvement n'a pas de localisation associé.";
        } else {
            divIcon.innerHTML = divIcon.innerHTML + "Localisation: " + element.get("loc");
            if (element.get("default_loc") == true){
                divIcon.innerHTML = divIcon.innerHTML + "<br>Ce prélèvement à les coordonnées par défaut de sa localisation";
            }
        }
        divIcon.innerHTML = divIcon.innerHTML + "<br><br>";
    })
});