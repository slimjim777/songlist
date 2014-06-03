// Controllers
App.SonglistsController = Ember.ArrayController.extend({
    error: null,
    isEditing: false,
    newSonglist: null,

    actions: {
        newSonglist: function() {
            // Display the new Songlist form
            this.set('newSonglist', App.Songlist.create({}));
            this.set('isEditing', true);
        },

        saveSonglist: function() {
            // Save new songlist
            console.log('Save New Songlist');
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
            console.log('Cancel Songlist');
            this.set('isEditing', false);
            this.set('error', false);
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
            console.log('Save Edit Songlist');

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
            console.log('Cancel Songlist');
            this.set('isEditing', false);
            this.set('error', false);
            this.send('reloadModel');   // Calls action on the route
        }

    }
})


App.SongController = Ember.ObjectController.extend({

    // Metronome state
    isMetroStarted: false,
    metronome: null,

    time_signatures: ['', '4/4', '3/4', '6/8'],
    keys: ['','C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B'],

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
            console.log('Start Metronome');
            this.set('isMetroStarted', true);

            resetMetronome();
            scheduler();
        },

        stopMetronome: function() {
            console.log('Stop Metronome');
            this.set('isMetroStarted', false);

            window.clearTimeout(timerID);
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
            console.log('Song AddSongController');
            console.log(this.get('model'));
            console.log('Find ' + this.get('search'));
            var controller = this;
            App.Song.findSongs(this.get('search')).then(function(value) {
                var folders = value.folders.map( function(f) {
                    f.id = null;
                    f.songlist_id = controller.get('model').get('id');
                    return App.Song.create(f);
                });
                console.log(folders);
                controller.set('folders', folders);
            });
        },

        selectSong: function(folder) {
            console.log('select song');
            console.log(folder);
            var newSong = {
                id: folder.get('id'),
                songlist_id: this.get('model').get('id'),
                name: folder.get('name'),
                tempo: folder.get('tempo'),
                key: '',
                time_signature: folder.get('time_signature')
            }
            var controller = this;

            App.Song.saveRecord(newSong).then(function(value) {
                // Add the song to the list of songs
                controller.get('model').get('songs').addObject(value.record);

                // Remove the folder from the folders list
                controller.get('folders').removeObject(folder);
            });

        },

        closeFind: function() {
            console.log('Close find');
            this.set('search', '');
            this.set('folders', []);
            this.transitionToRoute('songlist', this.get('model').get('id'));
        },

        cancelSong: function() {
            console.log('cancel song');
            this.set('folders', []);
            this.set('search', '');
            this.transitionToRoute('songlist', this.get('model').get('id'));
        }
    }
});