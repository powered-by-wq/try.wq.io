define(['wq/app', 'wq/map', 'wq/photos',
        './campaigns', './reports', './config'],
function(app, map, photos, campaigns, reports, config) {

// Register plugins
app.use(map);
app.use(photos);
app.use(campaigns);
app.use(reports);

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
