App = Ember.Application.create();

var MIN_TEMPO = 50;
var MAX_TEMPO = 200;


// Utilities

function ajax (url, options) {
  return new Ember.RSVP.Promise(function (resolve, reject) {
    options = options || {};
    options.url = url;

    Ember.$.ajax(options).done(function (data) {
        if (data.response == 'Success') {
            resolve(data);
        } else {
            // Return error for validation errors
            reject(new Error(data.message));
        }
    }).fail(function (jqxhr, status, something) {
        reject(new Error("AJAX: `" + url + "` failed with status: [" + status + "] " + something));
    });
  });
}



// Models

App.Songlist = Ember.Object.extend({});

App.Songlist.reopenClass({
    url: '/api/songlists',
    saveRecord: function(model) {
        var url;
        var data = {
            id: model.get('id'),
            name: model.get('name'),
            event_date: model.get('event_date')
        };
        if (model.get('id')) {
            data.id = model.get('id');
            url = this.url + '/' + model.get('id');
        } else {
            url = this.url;
        }

        return ajax(url, {
            //url: url,
            type: 'POST',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    },

    getAll: function() {
        return $.getJSON(this.url).then( function(data) {
            return data.songlists.map( function(songlist) {
                return App.Songlist.create(songlist);
            });
        });
    }
});


// Router

App.Router.map(function() {
    this.resource('songlists', { path: '/' });
    this.resource('songlist', { path: '/songlists/:songlist_id' }, function() {
        this.resource('song', { path: '/:id' });
    });
});


// Routes

App.SonglistsRoute = Ember.Route.extend({
    model: function() {
        return App.Songlist.getAll();
    }
});


App.SonglistRoute = Ember.Route.extend({
    model: function(params) {
        return $.getJSON('/api/songlists/' + params.songlist_id).then( function(data) {
            console.log('Single Songlist');
            return data;
        });
    }
});


App.SongRoute = Ember.Route.extend({
    model: function(params) {
        console.log('Song:' + params.id);
        return $.getJSON('/api/song/' + params.id).then( function(data) {
            return data;
        });
    }
});


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
            // Save new songlist
            console.log('Save Edit Songlist');
        },

        cancelSonglistEdit: function () {
            console.log('Cancel Songlist');
            this.set('isEditing', false);
            this.set('error', false);
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


App.CalendarDatePicker = Ember.TextField.extend({
    _picker: null,


    modelChangedValue: function(){
        var picker = this.get("_picker");
        if (picker){
            picker.setDate(this.get("value"));
        }
    }.observes("value"),

    didInsertElement: function(){
        var currentYear = (new Date()).getFullYear();
        var formElement = this.$()[0];
        var picker = new Pikaday({
            field: formElement,
            yearRange: [1900,currentYear+2],
            format: 'YYYY-MM-DD'
        });
        this.set("_picker", picker);
    },

    willDestroyElement: function(){
        var picker = this.get("_picker");
        if (picker) {
            picker.destroy();
        }
        this.set("_picker", null);
    }
});

