define(['wq/locate', 'wq/map', 'leaflet', 'jquery.mobile', './config'],
function(locate, map, L, jqm, config) {
return {
    'name': 'reports',
    'init': function(){},
    'run': function(page, mode) {
        if (page != 'report' || mode != 'edit') {
            return;
        }

        var $page = jqm.activePage;
        // Create Leaflet map
        var m = L.map('report-new-map').fitBounds(config.map.bounds);
        map.createBasemaps().Street.addTo(m);

        // Configure Locator
        var fields = {
            'toggle': $page.find('input[name=mode]'),
            'latitude': $page.find('input[name="event[site][latitude]"]'),
            'longitude': $page.find('input[name="event[site][longitude]"]'),
            'accuracy': $('input[name=accuracy]')
        };

        locate.locator(m, fields);
    }
};
});
