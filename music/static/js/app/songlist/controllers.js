// Controllers

var MIN_TEMPO = 50;
var MAX_TEMPO = 200;


App.SonglistsController = Ember.ArrayController.extend({
    error: null,
    isEditing: false,
    newSonglist: null,
    isDeleting: false,
    title: null,
    message: null,
    toDelete: null,

    actions: {
        newSonglist: function() {
            // Display the new Songlist form
            this.set('newSonglist', App.Songlist.create({}));
            this.set('isEditing', true);
        },

        saveSonglist: function() {
            // Save new songlist
            var controller = this;
            App.Songlist.saveRecord(this.get('newSonglist')).then(function(value) {
                controller.set('isEditing', false);
                controller.set('error', null);
                controller.addObject(App.Songlist.create(value.record));
                controller.set('newSonglist', null);
                controller.transitionToRoute('songlist', value.record.id);
            }).catch( function (error) {
                controller.set('error', error.message);
            });
        },

        cancelSonglistEdit: function () {
            this.set('isEditing', false);
            this.set('error', false);
        },

        removeSonglist: function(songlist) {
            console.log('Remove songlist: ' + songlist.name);
            this.set('title', 'Confirm Deletion');
            this.set('message', 'Delete song list "' + songlist.name + '"?');
            this.set('toDelete', songlist);
            this.set('isDeleting', true);
        },

        cancelDelete: function() {
            this.set('isDeleting', false);
            this.set('title', null);
            this.set('message', null);
            this.set('toDelete', null);
        },

        confirmDelete: function() {
            var controller = this;

            App.Songlist.removeSonglist(this.get('toDelete').get('id')).then(function() {
                // Remove the songlist from the array
                var index = controller.get('model').indexOf(controller.get('toDelete'))
                controller.get('model').removeAt(index, 1);

                // Reset
                controller.set('isDeleting', false);
                controller.set('title', null);
                controller.set('message', null);
                controller.set('toDelete', null);
            });
        }

    }
});


App.SonglistController = Ember.ObjectController.extend({
    error: null,
    isEditing: false,

    actions: {
        editSonglist: function() {
            // Display the new Songlist form
            this.set('isEditing', true);
        },

        saveSonglist: function() {
            // Save changed songlist
            var controller = this;
            App.Songlist.saveRecord(this.get('model')).then(function(value) {
                // Success
                controller.set('isEditing', false);
                controller.set('error', false);
            }).catch(function(error) {
                // Error
                controller.set('error', error.message);
            });
        },

        cancelSonglistEdit: function () {
            this.set('isEditing', false);
            this.set('error', false);
            this.send('reloadModel');   // Calls action on the route
        },

        songOrder: function(song, direction) {
            // Move the song up/down in the songlist
            var controller = this;
            var index = this.get('model').get('songs').indexOf(song);
            var songs = controller.get('model').get('songs');

            // Check if the song is already at the top/bottom
            if ((direction === 'up') && (index === 0)) {
                return;
            }
            if ((direction === 'down') && (index === songs.length - 1)) {
                return;
            }

            // Reorganise the list
            songs.splice(index, 1);
            if (direction === 'up') {
                songs.splice(index - 1, 0, song);
            } else {
                songs.splice(index + 1, 0, song);
            }

            // Store the IDs of the songs in order
            var song_order = [];
            songs.forEach(function(sng) {
                song_order.push(sng.get('id'));
            });

            // Save the updated songs in order
            controller.get('model').get('songs').setObjects(songs);
            App.Songlist.songOrder(controller.get('model').get('id'), song_order);
        },

        removeSong: function(song) {
            // Remove song from the songlist
            var controller = this;
            App.Songlist.removeSong(controller.get('model').get('id'), song.get('id')).then(function() {
                controller.get('model').get('songs').removeObject(song);
            });
        }

    }
})


App.SongController = Ember.ObjectController.extend({
    // Link to the Songlist controller
    needs: "songlist",
    songlist: Ember.computed.alias("controllers.songlist"),

    // Metronome state
    isMetroStarted: false,
    metronome: null,

    time_signatures: ['', '4/4', '3/4', '6/8'],
    keys: ['','C','C#','Db','D','D#','Eb','E','F','F#','Gb','G','G#','Ab','A','A#','Bb','B'],

    actions: {
        metroMinus: function() {
            // Decrement the tempo
            var tempo = this.get('model.tempo');
            tempo--;
            if (tempo < MIN_TEMPO) {
                tempo = MIN_TEMPO;
            }
            this.set('model.tempo', tempo);

        },

        metroPlus: function() {
            // Increment the tempo
            var tempo = this.get('model.tempo');
            tempo++;
            if (tempo > MAX_TEMPO) {
                tempo = MAX_TEMPO;
            }
            this.set('model.tempo', tempo);
        },

        startMetronome: function() {
            this.set('isMetroStarted', true);

            resetMetronome();
            scheduler();
        },

        stopMetronome: function() {
            this.set('isMetroStarted', false);
            window.clearTimeout(timerID);
        },

        saveSong: function(song) {
            var controller = this;

            App.Song.saveRecord(song).then(function(value) {
                var savedSong = App.Song.create(value.record);

                // Update the songlist with the changed song
                var index = -1;
                var i = -1;
                controller.get('songlist').get('songs').forEach(function(song) {
                    i += 1;
                    if (song.get('id') == savedSong.get('id')) {
                        index = i;
                        return;
                    }
                });
                if (index != -1) {
                    var songs = controller.get('songlist').get('songs');
                    songs[index] = savedSong;
                    controller.get('songlist').get('songs').setObjects(songs);
                }
            });
        },

        nextSong: function() {
            var song = this.get('songlist').get('model').get('songs').findBy('id', this.get('model').get('id'));
            var currentSongIndex = this.get('songlist').get('model').get('songs').indexOf(song);
            var next;
            if (this.get('songlist').get('model').get('songs').length > currentSongIndex + 1) {
                next = this.get('songlist').get('model').get('songs')[currentSongIndex + 1];
            } else {
                next = this.get('songlist').get('model').get('songs')[0];
            }

            this.transitionToRoute('song', next.id);
        },

        previousSong: function() {
            var song = this.get('songlist').get('model').get('songs').findBy('id', this.get('model').get('id'));
            var currentSongIndex = this.get('songlist').get('model').get('songs').indexOf(song);
            var prev;
            if (currentSongIndex - 1 >= 0) {
                prev = this.get('songlist').get('model').get('songs')[currentSongIndex - 1];
            } else {
                prev = this.get('songlist').get('model').get('songs')[this.get('songlist').get('model').get('songs').length - 1];
            }

            this.transitionToRoute('song', prev.id);
        }
    },

    // Observers
    metroTempoChange: function() {
        var tempo = this.get('model.tempo');
        setMetronomeTempo(tempo);
    }.observes('model.tempo'),

    metroBPBChange: function() {
        var bpb = 4;
        switch(this.get('model.time_signature')) {
            case '3/4':
                bpb = 3;
                break;
            case '6/8':
                bpb = 6;
                break;
        }
        setBPB(bpb);
    }.observes('model.time_signature')
});


App.AddSongController = Ember.ObjectController.extend({
    search: '',
    folders: [],

    actions: {
        findSong: function () {
            var controller = this;
            App.Song.findSongs(this.get('search')).then(function(value) {
                var folders = value.folders.map( function(f) {
                    f.id = null;
                    f.songlist_id = controller.get('model').get('id');
                    return App.Song.create(f);
                });
                controller.set('folders', folders);
            });
        },

        selectSong: function(folder) {
            // Save the selected folder as a song
            var newSong = App.Song.create({
                id: folder.get('id'),
                songlist: this.get('model').get('id'),
                name: folder.get('name'),
                tempo: folder.get('tempo'),
                key: '',
                time_signature: folder.get('time_signature')
            });
            var controller = this;

            App.Song.saveRecord(newSong).then(function(value) {
                // Add the song to the list of songs
                var sng = App.Song.create(value.record);
                controller.get('model').get('songs').addObject(sng);

                // Remove the folder from the folders list
                controller.get('folders').removeObject(folder);
            });

        },

        addUnlistedSong: function() {
            // Add an untitled song
            var newSong = App.Song.create({
                name: 'Untitled',
                songlist: this.get('model').get('id')
            });

            var controller = this;
            App.Song.saveRecord(newSong).then(function(value) {
                // Add the song to the list of songs
                var sng = App.Song.create(value.record);
                controller.get('model').get('songs').addObject(sng);
            });
        },

        closeFind: function() {
            this.set('search', '');
            this.set('folders', []);
            this.transitionToRoute('songlist', this.get('model').get('id'));
        },

        cancelSong: function() {
            this.set('folders', []);
            this.set('search', '');
            this.transitionToRoute('songlist', this.get('model').get('id'));
        }
    }
});


// Views

App.SongView = Ember.View.extend({
    didInsertElement: function() {
        // Make sure this view has focus
        return this.$().attr({tabindex: 1}), this.$().focus();
    },

    keyDown: function(event, view) {
        if (event.target.tagName=="INPUT") {
            // Ignore keypress when we are on text elements
            // ...otherwise we can't type spaces
            return;
        }

        if (event.keyCode === 32) {
            // Space: toggle the metronome
            if (this.get('controller').get('isMetroStarted')) {
                this.get('controller').send('stopMetronome');
            } else {
                this.get('controller').send('startMetronome');
            }
            return false;
        } else if (event.keyCode === 38) {
            // Up Arrow: increase metronome speed
            this.get('controller').send('metroPlus');
            return false;
        } else if (event.keyCode === 40) {
            // Down Arrow: decrease metronome speed
            this.get('controller').send('metroMinus');
            return false;
        } else if (event.keyCode === 39) {
            // Right Arrow: next song
            this.get('controller').send('nextSong');
            return false;
        } else if (event.keyCode === 37) {
            // Left Arrow: previous song
            this.get('controller').send('previousSong');
            return false;
        }
    }
});
