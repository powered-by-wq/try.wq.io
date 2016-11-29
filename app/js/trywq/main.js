define(['wq/app', 'wq/map', 'wq/patterns', 'wq/photos', 'wq/locate',
        './config'],
function(app, map, patterns, photos, locate, config) {

// Register plugins
app.use(map);
app.use(patterns);
app.use(photos);
app.use(locate);

// Anonymous plugin
app.use({
    'onsave': function(item, result) {
        // Parameter is registered as a nested serializer on campaign, and is
        // is also registered separately.  This dual usage is not officially
        // supported by wq (see https://wq.io/docs/nested-forms), so we need to
        // refresh the parameter model whenever a campaign is saved.
        if (item && item.options &&
                item.options.modelConf &&
                item.options.modelConf.name == 'campaign') {
            app.models.parameter.prefetch();
        }
    }
});

config.presync = presync;
config.postsync = postsync;

// Initialize
app.init(config).then(function() {
    app.jqmInit();
    app.prefetchAll();
});

// Make external login links work on iOS
if (window.navigator.standalone) {
    $('body').on('click', 'a[rel=external]', function(evt) {
        evt.preventDefault();
        window.location = this.href;
    });
}

// Sync UI
function presync() {
    $('button.sync').html("Syncing...");
    $('li a.ui-icon-minus, li a.ui-icon-alert')
       .removeClass('ui-icon-minus')
       .removeClass('ui-icon-alert')
       .addClass('ui-icon-refresh');
}

function postsync(items) {
    $('button.sync').html("Sync Now");
    app.syncRefresh(items);
}

});
