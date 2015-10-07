requirejs.config({
    'baseUrl': '/js/lib',
    'paths': {
        'trywq': '../trywq',
        'data': '../data/'
    }
});

requirejs(['trywq/main']);
