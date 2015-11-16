define(['jquery.mobile', 'wq/template'], function(jqm, tmpl) {
return {
    'name': 'campaigns',
    'init': function(){},
    'run': function(page, mode) {
        if (page != 'campaign' || mode != 'edit') {
            return;
        }
        jqm.activePage.find('button#add-parameter').click(function() {
            var $param = $(tmpl.render("{{>parameter_inline}}", {
                '@index': $.mobile.activePage.find('li.parameter').length
            }));
            $(this).parents('li').before($param);
            $param.enhanceWithin();
            $param.parents('ul').listview('refresh');
        });
    }
};
});
