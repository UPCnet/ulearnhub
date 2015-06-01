(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('LanguageSelectorController', LanguageSelectorController);

    /**
     * @desc
     */
    /* @nInject */
    function LanguageSelectorController($cookies, $translate, $state) {
        var self = this;
        var valid_cookie_language = $cookies.currentLang === 'ca';
        self.currentLang = {
            code: $cookies.currentLang === undefined ? 'ca' : $cookies.currentLang
        };
        self.languages = [{
            code: 'ca',
            name: 'Català'
        }, {
            code: 'es',
            name: 'Castellano'
        }, {
            code: 'en',
            name: 'English'
        }];

        self.changeLanguage = changeLanguage;

        /////////////////////////////

        function changeLanguage (){
            $translate.use(self.currentLang.code);
            $cookies.currentLang = self.currentLang.code;
            $state.go('domain', {
                domain: $cookies.currentDomain
            });
        }
    }
})();
