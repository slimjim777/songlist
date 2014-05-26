var audioContext = null;
var current16thNote = 0;        // What note is currently last scheduled?
var nextNoteTime = 0.0;         // when the next note is due.
var timerID = 0;                // setInterval identifier.
var scheduleAheadTime = 0.1;    // How far ahead to schedule audio (sec)
var notesInQueue = [];          // the notes that have been put into the web audio,
var lookahead = 25.0;           // How frequently to call scheduling function (ms)
var tempo = 120.0;              // tempo (in beats per minute)
var bpb = 4;

var NOTE_LENGTH = 0.010;     // length of "beep" (in seconds)
var BEAT_ONE_FREQUENCY = 1440.0;
var BEAT_OTHER_FREQUENCY = 880.0;

function scheduler() {
    // while there are notes that will need to play before the next interval,
    // schedule them and advance the pointer.
    while (nextNoteTime < audioContext.currentTime + scheduleAheadTime ) {
        scheduleNote( current16thNote, nextNoteTime );
        nextNote();
    }
    timerID = window.setTimeout( scheduler, lookahead );
}

function scheduleNote( beatNumber, time ) {
    // Push the note on the queue, even if we're not playing.
    notesInQueue.push( { note: beatNumber, time: time } );

    if (beatNumber%4)
        return; // we're not playing non-quarter notes

    // Create an oscillator
    var osc = audioContext.createOscillator();
    osc.connect( audioContext.destination );
    if (beatNumber % (4 * bpb) === 0)    // beat 1 == high pitch
        osc.frequency.value = BEAT_ONE_FREQUENCY;
    else                                 // other beats = low pitch
        osc.frequency.value = BEAT_OTHER_FREQUENCY;

    osc.start( time );
    osc.stop( time + NOTE_LENGTH );
}

function nextNote() {
    // Advance current note and time by a 16th note...
    // Notice this picks up the CURRENT tempo value to calculate beat length.
    var secondsPerBeat = 60.0 / tempo;
    nextNoteTime += 0.25 * secondsPerBeat;    // Add a quarter of beat length to last beat time

    current16thNote++;    // Advance the beat number, wrap to zero
    if (current16thNote == 4 * bpb) {
        current16thNote = 0;
    }
}

function toggleMetronome() {
    tempo = getTempo();

    // Stop or start the metronome
    var button = $('#metro_start_stop');

    if ($(button).hasClass('btn-success')) {
        // Start the metronome
        $(button).toggleClass('btn-success', false);
        $(button).toggleClass('btn-danger', true);
        $(button).text('Stop');

        // Reset the metronome
        current16thNote = 0;
        bpb = beatsPerBar();
        nextNoteTime = audioContext.currentTime;

        // Start the metronome
        scheduler();
    } else {
        // Stop the metronome
        window.clearTimeout(timerID);
        $(button).toggleClass('btn-success', true);
        $(button).toggleClass('btn-danger', false);
        $(button).text('Start');
    }
}

function initializeAudio() {
    // Initialise the audio engine
    audioContext = new AudioContext();
}

// Getters and Setters to provide access from other files
function setTempo(bpm) {
    tempo = bpm;
}

function setBPB(beatsPerBarValue) {
    bpb = beatsPerBarValue;
}
