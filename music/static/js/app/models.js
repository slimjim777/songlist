// Utilities

// Ajax wrapper that returns a promise
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


// Date picker widget for view
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




// Models

App.Songlist = Ember.Object.extend({});

App.Songlist.reopenClass({
    url: '/api/songlists',
    saveRecord: function(model) {
        var url;
        var data = {
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
            type: 'POST',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    },

    getAll: function() {
        return ajax(this.url, {
            type: 'GET',
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    },

    find: function(modelId) {
        return ajax(this.url + '/' + modelId, {
            type: 'GET',
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    },

    songOrder: function(modelId, song_order) {
        return ajax(this.url + '/' + + modelId + '/song_order', {
            type: 'POST',
            data: JSON.stringify({song_order: song_order}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    },

    removeSong: function(modelId, songId) {
        return ajax(this.url + '/' + + modelId + '/remove_song', {
            type: 'POST',
            data: JSON.stringify({song_id: songId}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    },

    removeSonglist: function(modelId) {
        return ajax(this.url + '/' + + modelId, {
            type: 'DELETE',
            data: JSON.stringify({songlist_id: modelId}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    }
});


App.Song = Ember.Object.extend({});

App.Song.reopenClass({
    url: '/api/song',

    findSongs: function (q) {
        return ajax(this.url + '/find', {
            type: 'POST',
            data: JSON.stringify({q:q}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    },

    find: function(modelId) {
        return ajax(this.url + '/' + modelId, {
            type: 'GET',
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    },

    saveRecord: function(model) {
        var url;
        var data = {
            name: model.get('name'),
            key: model.get('key'),
            songlist_id: model.get('songlist'),
            tempo: model.get('tempo'),
            time_signature: model.get('time_signature')
        };

        if (model.get('id')) {
            data.id = model.get('id');
            url = this.url + '/' + model.get('id');
        } else {
            url = this.url;
        }

        return ajax(url, {
            type: 'POST',
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    }

});

