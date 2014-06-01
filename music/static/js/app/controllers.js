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

