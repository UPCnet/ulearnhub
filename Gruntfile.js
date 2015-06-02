'use strict';
module.exports = function(grunt) {
    // Configure
    var js_config = grunt.file.readJSON('ulearnhub/js/config.json');
    var uglify_options = {
        sourceMap: true,
        banner: '/*! <%= uglify.pkg.name %> - v<%= uglify.pkg.version %> - ' +
        '<%= grunt.template.today("yyyy-mm-dd") %> */'
    };
    grunt.initConfig({
        // The less task.
        less: {
            // This is the target's name "production".
            // You can run this task like this:
            //   grunt less:production
            production: {
                options: {
                    // Set the option to compress the resulting css.
                    yuicompress: false
                },
                files: {
                    // Create a file called "public/css/site.css" from "less/site.less".
                    // Note: If the directory public/css does not exist, it will be
                    // created by the task.
                    "ulearnhub/css/ulearnhub.css": "ulearnhub/less/ulearnhub.less"
                }
            }
        },

        watch: {
            // Keep an eye on those stylesheets.
            styles: {
                // The path 'less/**/*.less' will expand to match every less file in
                // the less directory.
                files: ['ulearnhub/less/*.less'],
                // The tasks to run
                tasks: ['less']
            }
        },

        uglify: {
            pkg: grunt.file.readJSON('package.json'),
            main: {
               options: uglify_options,
               files: {
                   'ulearnhub/js/main.min.js': js_config.main.development
              }
            },
            domain: {
               options: uglify_options,
               files: {
                   'ulearnhub/js/hub.domain.min.js': js_config.domain.development
              }
            },
            hub: {
               options: uglify_options,
               files: {
                   'ulearnhub/js/hub.min.js': js_config.hub.development
              }
            }

        },

        ngAnnotate: {
            options: {
                ngAnnotateOptions: {}
            },
            domain: { files: {'ulearnhub/js/hub.domain.js': js_config.domain.development }},
            hub: { files: {'ulearnhub/js/hub.js': js_config.hub.development }},
            main: { files: {'ulearnhub/js/main.js': js_config.main.development }}
        }
    });

    // Load tasks
    grunt.registerTask('dist', ['ngAnnotate', 'uglify']);
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-ng-annotate');
    grunt.loadNpmTasks('grunt-contrib-uglify');

};
