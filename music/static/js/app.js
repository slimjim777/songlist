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
                var songs = songlist.songs.map(function(song) {
                    return App.Song.create(song);
                });
                songlist.songs = songs;
                return App.Songlist.create(songlist);
            });
        });
    }
});


App.SonglistRoute = Ember.Route.extend({
    model: function(params) {
        console.log('SonglistRoute');
        return App.Songlist.find(params.songlist_id).then( function(data) {
            var songs = data.songlist.songs.map(function(song) {
                return App.Song.create(song);
            });
            data.songlist.songs = songs;
            return App.Songlist.create(data.songlist)
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

        return App.Song.find(params.id).then( function(data) {
            return App.Song.create(data.record);
        });
    }
});


App.AddSongRoute = Ember.Route.extend({
    renderTemplate: function() {
        this.render({ outlet: 'addSong' });
    }
});
