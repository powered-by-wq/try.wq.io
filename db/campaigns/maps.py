mqcdn = "https://otile{s}-s.mqcdn.com/tiles/1.0.0/{layer}/{z}/{x}/{y}.png"

# _attribution (https://gist.github.com/mourner/1804938)
osm_attr = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
aerial_attr = 'Imagery &copy; NASA/JPL-Caltech and U.S. Depart. of Agriculture, Farm Service Agency'
mq_tiles_attr = 'Tiles &copy; <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="https://developer.mapquest.com/content/osm/mq_logo.png" />'

basemaps = [{
    'name': "Street",
    'type': 'tile',
    'url': mqcdn,
    'subdomains': '1234',
    'layer': 'map',
    'attribution': osm_attr + ', ' + mq_tiles_attr
}, {
    'name': "Aerial",
    'type': 'tile',
    'url': mqcdn,
    'subdomains': '1234',
    'layer': 'sat',
    'attribution': aerial_attr + ', ' + mq_tiles_attr
}]

event_list = {
    'name': 'Observations',
    'type': 'geojson',
    'url': 'events.geojson',
    'popup': 'event',
    'cluster': True,
}

event_detail = {
    'name': 'Observation',
    'type': 'geojson',
    'url': 'events/{{id}}.geojson',
}

index_map = {
    'defaults': {
        'layers': [event_list]
    }
}

event_map = {
    'list': {
        'layers': [event_list]
    },
    'detail': {
        'layers': [event_detail]
    }
}
