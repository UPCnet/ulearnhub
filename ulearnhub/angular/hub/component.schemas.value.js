(function() {
    'use strict';

    function baseInput(type, name, label, placeholder, default_value, classname) {
        return {
            key: name,
            type: 'input',
            defaultValue: default_value,
            className: classname,
            templateOptions: {
                type: type,
                label: label,
                placeholder: placeholder
            }
        };
    }

    function textInput(name, label, placeholder, default_value, classname) {
        return baseInput('input', name, label, placeholder, default_value, classname);
    }

    function passwordInput(name, label, placeholder, default_value, classname) {
        return baseInput('password', name, label, placeholder, default_value, classname);
    }

    function titleSeparator(title) {
        return {
            "template": '<hr /><div class="fieldgroup-title"><strong>' + title + '</strong></div>'
        };
    }

    function checkboxInput(name, label, classname) {
        return {
            key: name,
            type: 'checkbox',
            className: classname,
            templateOptions: {
                label: label
            }
        };
    }

    function fieldGroup(fields) {
        return {
            className: "display-flex",
            fieldGroup: fields
        };
    }

    angular
        .module('hub')
        .value('ComponentSchemas', {

            mongodbreplicamember: [
                fieldGroup([
                    textInput('name', 'Component Identifier', '', 'mongocluster', 'flex-1'),
                    textInput('title', 'Component Description', '', '', 'flex-1')
                ]),
                titleSeparator('Setup parameters:'),
                textInput('path', 'Setup path', '', '/var/mongodb', ''),
                fieldGroup([
                    textInput('server', 'Server where is installed', '', '', 'flex-2'),
                    textInput('host', 'Effective dns of member', '', '', 'flex-2'),
                    textInput('port', 'port', '', '27001', 'flex-1')
                ])

            ],

            ldapserver: [
                fieldGroup([
                    textInput('name', 'Component Identifier', '', 'mongocluster', 'flex-1'),
                    textInput('title', 'Component Description', '', '', 'flex-1')
                ]),
                titleSeparator('Server parameters:'),
                fieldGroup([
                    textInput('server', 'LDAP server uri', 'ldaps://server:port', '', 'flex-1'),
                    checkboxInput('readonly', 'Do not write to this server', 'flex-1')
                ]),
                titleSeparator('Security settings:'),
                fieldGroup([
                    textInput('admin_dn', 'LDAP bind dn', '', '', 'flex-1'),
                    textInput('admin_password', 'LDAP bind password', '', '', 'flex-1')
                ]),
                titleSeparator('Search parameters:'),
                fieldGroup([
                    textInput('users_base_dn', 'LDAP bind dn', '', '', 'flex-2'),
                    textInput('user_scope', 'LDAP bind password', '', '', 'flex-1')
                ]),
                fieldGroup([
                    textInput('group_base_dn', 'LDAP bind dn', '', '', 'flex-2'),
                    textInput('group_scope', 'LDAP bind password', '', '', 'flex-1')
                ])
            ],

            mongodbcluster: [
                fieldGroup([
                    textInput('name', 'Component Identifier', '', 'mongocluster', 'flex-1'),
                    textInput('title', 'Component Description', '', '', 'flex-1')
                ]),
                textInput('replicaset', 'Replicaset name for this cluster', '', '', 'input-small'),
                titleSeparator('Security settings:'),
                fieldGroup([
                    textInput('root_username', 'Mongodb "root" user', '', 'root', 'flex-1'),
                    passwordInput('root_password', 'Mongodb "root" password', 'password', '', 'flex-1')
                ]),
                fieldGroup([
                    textInput('db_username', 'Mongodb databases administrator user', '', 'admin', 'flex-1'),
                    passwordInput('db_password', 'Mongodb databases administrator password', 'password', '', 'flex-1')
                ]),
                textInput('admindb', 'Name of the database used for global authentication,\n leave blank to authenticate directly on working database.', '', '', 'input-small')
            ]
        });

})();
