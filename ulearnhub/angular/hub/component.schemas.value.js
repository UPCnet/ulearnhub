(function() {
    'use strict';

    angular
        .module('hub')
        .value('ComponentSchemas', {

            mongodbcluster: [{
                className: "display-flex",
                fieldGroup: [{
                    key: 'name',
                    type: 'input',
                    defaultValue: 'mongocluster',
                    className: 'flex-1',
                    templateOptions: {
                        label: 'Component identifier',
                        placeholder: ''
                    }
                }, {
                    key: 'title',
                    type: 'input',
                    className: 'flex-1',
                    templateOptions: {
                        label: 'Component description',
                        placeholder: 'Deployment X mongo cluster'
                    }
                }]
            }, {
                key: 'replicaset',
                type: 'input',
                className: 'input-small',
                templateOptions: {
                    required: true,
                    label: 'Replicaset name for this cluster',
                    placeholder: ''
                }
            }, {
                "template": '<hr /><div class="fieldgroup-title"><strong>Security settings:</strong></div>'
            }, {
                className: "display-flex",
                fieldGroup: [{
                    key: 'username',
                    type: 'input',
                    className: 'flex-1',
                    templateOptions: {
                        label: 'Mongodb administrator username',
                        placeholder: ''
                    }
                }, {
                    key: 'password',
                    type: 'input',
                    className: 'flex-1',
                    templateOptions: {
                        type: 'password',
                        label: 'Mongodb administrator password',
                        placeholder: 'Password'
                    }
                }]
            }, {
                key: 'admindb',
                type: 'input',
                className: 'input-small',
                templateOptions: {
                    label: 'Name of the database used for global authentication, leave blank to authenticate directly on selected database.',
                    placeholder: ''
                }
            }]
        });

})();
