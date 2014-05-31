//var ONEMIN = 60000.0;

/*

App.Songlist = DS.Model.extend({
    event_date: DS.attr('date'),
    name: DS.attr('string'),
    owner: DS.attr('string'),
    //songs: DS.hasMany('song')
});

App.Song = DS.Model.extend({
    songlist: DS.belongsTo('songlist'),
    //songlist: DS.attr('int'),
    name: DS.attr('string'),
    tempo: DS.attr('string'),
    time_signature: DS.attr('string'),

    nextSong: function() {
        // Find the next song in the song list
        var songs = this.get('songlist').get('songs');
        var currentSongIndex = songs.toArray().indexOf(this);
        var next;
        if (songs.toArray().length > currentSongIndex + 1) {
            next = songs.toArray()[currentSongIndex + 1];
        } else {
            next = songs.toArray()[0];
        }
        return next;
    }.property(),

    previousSong: function() {
        // Find the previous song in the song list
        var songs = this.get('songlist').get('songs');
        var currentSongIndex = songs.toArray().indexOf(this);
        var prev;
        if (currentSongIndex - 1 >= 0) {
            prev = songs.toArray()[currentSongIndex - 1];
        } else {
            prev = songs.toArray()[songs.toArray().length - 1];
        }
        return prev;
    }.property(),

    bpb: function() {
        var bpb = 4;
        switch(this.get('time_signature')) {
            case '3/4':
                bpb = 3;
                break;
            case '6/8':
                bpb = 6;
                break;
        }
        return bpb;
    }.property('time_signature'),

    delay: function() {
        var tempo = this.get('tempo');
        if (!tempo) {
            tempo = MIN_TEMPO;
        }

        return (ONEMIN / parseInt(tempo));
    }.property('tempo')
});


// Test fixtures

App.Songlist.FIXTURES = [
    {
        id: 1,
        event_date: '2014-05-24',
        name: 'Champions League Final',
        owner: 'Cristiano Ronaldo',
        songs: [1,4,3]
    },
    {
        id: 2,
        event_date: '2014-05-25',
        name: 'Madrid Celebration',
        owner: 'Unknown',
        songs: [2]
    },
    {
        id: 3,
        event_date: '2014-07-04',
        name: 'Fourth of July Celebration',
        owner: 'Michelle Obama'
    }
];

App.Song.FIXTURES = [
    {
        id: 1,
        songlist: 1,
        name: 'Oh Happy Day!',
        tempo: '100',
        time_signature: '4/4'
    },
    {
        id: 2,
        songlist: 2,
        name: 'We are the champions',
        tempo: '90',
        time_signature: '6/8'
    },
    {
        id: 3,
        songlist: 1,
        name: 'Beautiful Day',
        tempo: '110',
        time_signature: '4/4'
    },
    {
        id: 4,
        songlist: 1,
        name: 'Sweet Home, Alabama',
        tempo: '96',
        time_signature: '4/4'
    }
];

*/
