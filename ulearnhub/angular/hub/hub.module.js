(function() {
    'use strict';

    angular
        .module('hub', [
            'datatables',
            'datatables.bootstrap',
            'ui.bootstrap',
            'ui.router',
            'ui.select',
            'ngSanitize',
            'ngCookies',
            'pascalprecht.translate',

            'hub.sidebar',
            'hub.client',
            'hub.translations'
    ]);

})();
