(function() {
    'use strict';

    angular.module('hub.domain', [
        'datatables',
        'datatables.bootstrap',
        'ui.bootstrap',
        'ui.router',
        'ui.select',
        'ui.jq',
        'ui.slimscroll',
        'ngSanitize',
        'ngCookies',
        'pascalprecht.translate',
        'puElasticInput',
        'ngJsonExplorer',
        'btford.markdown',

        'hub.sidebar',
        'hub.client',
        'max.client',
        'hub.users',
        'hub.contexts',
        'hub.translations'
    ]);

})();
