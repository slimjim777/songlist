App = Ember.Application.create();

// Router

App.Router.map(function() {
    this.resource('songlists', { path: '/' });
    this.resource('songlist', { path: '/songlists/:songlist_id' }, function() {
        this.resource('song', { path: '/:id' });
        this.resource('addSong', { path: '/add_song'});
    });

});


