module.exports = function(grunt) {
    // Configure
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
            hubdomain: {
               options: {
                sourceMap: true,
                banner: '/*! <%= uglify.pkg.name %> - v<%= uglify.pkg.version %> - ' +
                  '<%= grunt.template.today("yyyy-mm-dd") %> */'
              },

              files: {
                'ulearnhub/js/hub.domain.min.js': ['ulearnhub/js/hub.domain.js']
              }
            }

        },

        ngAnnotate: {
            options: {
                ngAnnotateOptions: {

                }
            },
            hubdomain: {
                files: {
                  'ulearnhub/js/hub.domain.js': [
                      'ulearnhub/angular/hub.domain/hub.domain.module.js',
                      'ulearnhub/angular/hub.domain/*.js',
                      'ulearnhub/angular/hub.domain/users/users.module.js',
                      'ulearnhub/angular/hub.domain/users/*.js',
                      'ulearnhub/angular/hub.domain/contexts/contexts.module.js',
                      'ulearnhub/angular/hub.domain/contexts/*.js',
                      'ulearnhub/angular/hub.domain/*.js',
                      'ulearnhub/angular/hub.sidebar/hub.sidebar.module.js',
                      'ulearnhub/angular/hub.sidebar/*.js',
                      'ulearnhub/angular/hub.client/hub.client.module.js',
                      'ulearnhub/angular/hub.client/*.js',
                      'ulearnhub/angular/max.client/max.client.module.js',
                      'ulearnhub/angular/max.client/*.js'
                      ]
                }
            }
        }

    });

    // Load tasks
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-ng-annotate');
    grunt.loadNpmTasks('grunt-contrib-uglify');

};
