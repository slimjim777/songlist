module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    emberTemplates: {
        compile: {
            options: {
                templateCompilerPath: 'bower_components/ember/ember-template-compiler.js',
                handlebarsPath: 'node_modules/handlebars/dist/handlebars.js',
                templateBasePath: /music\/templates\/handlebars\//,
                templateNamespace: 'HTMLBars'
            },
            files: {
                "music/static/js/dist/templates.js": ["music/templates/handlebars/*.handlebars"]
            }
        }
    },

    concat: {
      options: {
        separator: ';'
      },
      dist: {
        src: ['music/static/js/app/**/*.js'],
        dest: 'music/static/js/dist/<%= pkg.name %>.js'
      },
      vendor: {
        src: ['bower_components/ember/*.prod.js', 
              'bower_components/bootstrap/dist/js/**/*.min.js', 'bower_components/moment/min/moment.min.js',
              'bower_components/pikaday/pikaday.js'],
        dest: 'music/static/js/dist/vendor.js'
      },
      jquery: {
        // Just copy the jquery file
        src: ['bower_components/jquery/dist/*.min.js'],
        dest: 'music/static/js/dist/jquery.min.js'
      },
      jqueryMap: {
        // Just copy the jquery file
        src: ['bower_components/jquery/dist/*.min.map'],
        dest: 'music/static/js/dist/jquery.min.map'
      }
    },

    cssmin: {
      combine: {
        files: {
          'music/static/css/dist/music.css': ['music/static/bower_components/pikaday/css/pikaday.css', 'music/static/css/music.css']
        }
      },
      minify: {
        expand: true,
        cwd: 'music/static/css/dist/',
        src: ['*.css', '!*.min.css'],
        dest: 'music/static/css/dist/',
        ext: '.min.css'
      }
    },

    uglify: {
        options: {
          //compress: true
        },
        dist: {
            files: {
              'music/static/js/dist/<%= pkg.name %>.min.js': ['<%= concat.dist.dest %>'],
              'music/static/js/dist/vendor.min.js': ['<%= concat.vendor.dest %>'],
              'music/static/js/dist/templates.min.js': ['music/static/js/dist/templates.js']
            }
        }
    },

    watch: {
        emberTemplates: {
            files: ['music/templates/handlebars/*.handlebars'],
            tasks: ['emberTemplates', 'concat', 'uglify']
        },
        concat: {
            files: ['music/static/js/app/**/*.js'],
            tasks: ['concat', 'uglify']
        },
        cssmin: {
            files: ['music/static/css/app.css'],
            tasks: ['cssmin']
        }
    }

  });

  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-ember-templates');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Default task(s).
  grunt.registerTask('default', ['watch']);

};
