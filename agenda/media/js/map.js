function initialize_map(map_id, geojson_features) {

    // If useDefaultLeafletIcon is true, don't use our custom icons but the default
    // provided by Leaflet
    var useDefaultLeafletIcon = true;

    // Define our marker icons, one for each region
    var BaseLeafletIcon = L.Icon.extend({
        options: {
            iconUrl: '/media/js/leaflet/images/marker-icon.png',
            //shadowUrl: 'http://leafletjs.com/docs/images/leaf-shadow.png',

            iconSize: [32, 32], // size of the icon
            //shadowSize:   [50, 64], // size of the shadow
            //iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
            shadowAnchor: [10, 50],  // the same for the shadow
            popupAnchor:  [0, -32] // point from which the popup should open relative to the iconAnchor
        }
    });
    var CentreSudLeafletIcon = BaseLeafletIcon.extend({
        options: {
            iconUrl: '/media/img/leaflet-icons/marker-icon-centre-sud.png'
        }
    });
    var EstErdreLeafletIcon = BaseLeafletIcon.extend({
        options: {
            iconUrl: '/media/img/leaflet-icons/marker-icon-est-erdre.png'
        }
    });
    var NordLeafletIcon = BaseLeafletIcon.extend({
        options: {
            iconUrl: '/media/img/leaflet-icons/marker-icon-nord.png'
        }
    });
    var OuestLeafletIcon = BaseLeafletIcon.extend({
        options: {
            iconUrl: '/media/img/leaflet-icons/marker-icon-ouest.png'
        }
    });
    // Map region > marker icon
    var customMarkerIcons = {
        'region-0': new CentreSudLeafletIcon(),
        'region-1': new OuestLeafletIcon(),
        'region-2': new NordLeafletIcon(),
        'region-3': new EstErdreLeafletIcon()
    };

    function pointStyle(feature) {
        return feature.properties && feature.properties.style;
    }

    function pointToLayer(feature, latlng) {
        if (useDefaultLeafletIcon === true && feature.properties && feature.properties.regionId != undefined) {
            return L.marker(latlng, {icon: customMarkerIcons['region-' + feature.properties.regionId]});
        } else {
            return L.marker(latlng);
        }
    }

    function onEachFeature(feature, layer) {
        var popupContent = "";
        if (feature.properties) {
            if (feature.properties.popupContent) {
                popupContent += feature.properties.popupContent;
            }
        }
        layer.bindPopup(popupContent);
    }

    // Create the map
    var map = L.map(map_id, {
        center: new L.LatLng(47.2139293,-1.5640955),  // Nantes
        zoom: 12,
    });

    // Add OpenStreetMap layer
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Create the geoJson layer
    var eventsLayer = L.geoJson(geojson_features, {
        style: pointStyle,
        pointToLayer: pointToLayer,
        onEachFeature: onEachFeature
    });

    // Create a cluster, add our event layer, then add the cluster to the map
    // => Allow to have multiple markers on the same lat/long
    var cluster = L.markerClusterGroup({
        maxClusterRadius: 20,
        showCoverageOnHover: false
    });
    cluster.addLayer(eventsLayer)
    map.addLayer(cluster);

    // Fit the map bounds to features
    map.fitBounds(eventsLayer.getBounds(), {padding: [50, 50]});

}
