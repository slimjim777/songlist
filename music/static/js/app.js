App = Ember.Application.create();
App.ApplicationAdapter = DS.FixtureAdapter.extend();

var MIN_TEMPO = 50;
var MAX_TEMPO = 200;

App.Router.map(function() {
    this.resource('songlists', { path: '/' });
    this.resource('songlist', { path: '/songlist/:songlist_id' }, function() {
        this.resource('song', { path: '/:id' });
    });

});


App.SonglistsRoute = Ember.Route.extend({
    model: function() {
        console.log('List Songlists');
        return this.store.find('songlist');
    }
});

App.SonglistRoute = Ember.Route.extend({
    model: function(params) {
        console.log('Single Songlist ' + params.songlist_id);
        return this.store.find('songlist', params.songlist_id);
    }
});

App.SongRoute = Ember.Route.extend({
    model: function(params) {
        return this.store.find('song', params.id);
    }
});


// Controllers
App.SongController = Ember.Controller.extend({

    // Metronome state
    isMetroStarted: false,
    metronome: null,

    actions: {
        metroMinus: function() {
            // Decrement the tempo
            var tempo = this.get('model').get('tempo');
            tempo--;
            if (tempo < MIN_TEMPO) {
                tempo = MIN_TEMPO;
            }
            this.get('model').set('tempo', tempo);
        },

        metroPlus: function() {
            // Increment the tempo
            var tempo = this.get('model').get('tempo');
            tempo++;
            if (tempo > MAX_TEMPO) {
                tempo = MAX_TEMPO;
            }
            this.get('model').set('tempo', tempo);
        },

        startMetronome: function() {
            console.log('Start Metronome');
            this.set('isMetroStarted', true);
            //this.set('metronome', MetronomeService.create({
            //    delay: this.get('model').get('delay'),
            //    bpb: this.get('model').get('bpb')
            //}));

            //tempo = this.get('model').get('tempo')
            //bpb = this.get('model').get('bpb');

            scheduler();
        },

        stopMetronome: function() {
            console.log('Stop Metronome');
            this.set('isMetroStarted', false);
            //this.get('metronome').destroy();
            window.clearTimeout(timerID);
        }
    },

    // Observers
    metroTempoChange: function() {
        var tempo = this.get('model').get('tempo');
        setTempo(tempo);
    }.observes('model.tempo'),

    metroBPBChange: function() {
        var bpb = this.get('model').get('bpb');
        setBPB(bpb);
    }.observes('model.bpb')
});


/*

// Metronome Service

function metroTick(beatCount) {
    if (beatCount == 1) {
        document.getElementById('beepOne').play();
    } else {
        document.getElementById('beep').play();
    }
}

var MetronomeService = Ember.Object.extend({
    _milli: 0,
    delay: 250,
    pulse: Ember.computed.oneWay('milli').readOnly(),
    beatCount: 1,
    bpb: 4,
    lastTick: 0,
    delta: 0,

    tick: function() {
        if (!this) {
            return;
        }
        this.set('lastTick', new Date().getTime());
        var metronome = this;

        Ember.run.later(function() {
            try {
                metronome.set('delta', new Date().getTime() - metronome.get('lastTick'));
            } catch(e) {}
            // Trigger the change by setting _milli
            var milli = metronome.get('_milli');
            if (typeof milli === 'number') {
                metronome.set('_milli', milli + metronome.get('delay'));
            }

            var beatCount = metronome.get('beatCount');
            metroTick(beatCount);
            beatCount += 1;
            if (beatCount > metronome.get('bpb')) {
                beatCount = 1;
            }
            try {
                metronome.set('beatCount', beatCount);
            } catch(e) {}
        }, metronome.get('delay'));
    }.observes('_milli').on('init')

});

Ember.Application.initializer({
    name: 'metronomeServiceInitializer',
    initialize: function(container, application) {
        container.register('clock:service', MetronomeService);
        application.inject('controller:interval', 'clock', 'clock:service');
    }
});

*/

