App = Ember.Application.create();

var MIN_TEMPO = 50;
var MAX_TEMPO = 200;


// Router

App.Router.map(function() {
    this.resource('songlists', { path: '/' });
    this.resource('songlist', { path: '/songlists/:songlist_id' }, function() {
        this.resource('song', { path: '/:id' });
        this.resource('addSong', { path: '/add_song'});
    });

});


// Routes

App.SonglistsRoute = Ember.Route.extend({
    model: function() {
        return App.Songlist.getAll().then( function(data) {
            return data.songlists.map( function(songlist) {
                return App.Songlist.create(songlist);
            });
        });
    }
});


App.SonglistRoute = Ember.Route.extend({
    model: function(params) {
        return App.Songlist.find(params.songlist_id).then( function(data) {
            return App.Songlist.create(data.songlist);
        });
    },

    actions: {
        reloadModel: function() {
            this.refresh();
        }
    }
});


App.SongRoute = Ember.Route.extend({
    model: function(params) {
        console.log('Song:' + params.id);
        /*
        return $.getJSON('/api/song/' + params.id).then( function(data) {
            return data;
        });
        */
        return App.Song.find(params.id).then( function(data) {
            return App.Song.create(data.record);
        });
    }
});

