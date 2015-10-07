define(["data/config", "data/templates", "data/version"],
function(config, templates, version) {

// FIXME: See https://github.com/wq/wq.app/issues/38
var rconf = config.attachmentTypes.result;
rconf.getTypeFilter = function(page, context) {
    return {'campaign_id': context.campaign_id}
};
rconf.getDefaults = function(type, context) {
    return {
        'type_id': type.id,
        'type_label': type.name,
        'type': type
    };
};

config.router = {
    'base_url': ''
}

config.template = {
    'templates': templates,
    'defaults': {
        'version': version,
        'date': function() {
            var date = new Date();
            return (
                date.getFullYear() + '-' +
                (date.getMonth() < 9 ? '0' : '') +
                (date.getMonth() + 1) + '-' +
                (date.getDate() <= 9 ? '0' : '') +
                date.getDate()
            );
        }
    }
};

config.store = {
    'service': config.router.base_url,
    'defaults': {'format': 'json'}
}

config.outbox = {};

config.backgroundSync = -1;

config.transitions = {
    'default': "slide",
    'save': "flip"
};

return config;

});
