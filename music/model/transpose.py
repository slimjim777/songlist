# -*- coding: utf-8 -*-
from music import app


class Transpose(object):
    """
    Based on algorithm written by +Mike Trahearn.
    """
    INVALID_NOTE = -1
    KEY_COUNT = 21
    SEMITONE_COUNT = 12
    KEY_TABLE = [
        ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"],
        # theoretical
        ["A#", "A", "B#", "C#", "C##", "D#", "D##", "E#", "F#", "F##", "G#",
            "G##"],
        ["Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A"],
        ["B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#"],
        # theoretical
        ["B#", "B##", "C##", "C###", "D##", "E#", "E##", "F##", "G#", "G##",
            "G###", "A##"],
        # theoretical
        ["Cb", "Dbb", "Db", "Ebb", "Eb", "Fb", "Gbb", "Gb", "Ab", "Ab", "Bbb",
            "Bb"],
        # Key of C uses popular flats/sharps
        ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        ["C#", "C##", "D#", "D##", "E#", "F#", "F##", "G#", "G##", "A#", "A##",
            "B#"],
        ["Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "C"],
        ["D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C", "C#"],
        # theoretical
        ["D#", "D##", "E#", "E##", "F##", "G#", "G##", "A#", "A##", "B#",
            "B##", "C##"],
        ["Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "C", "Db", "D"],
        ["E", "F", "F#", "G", "G#", "A", "A#", "B", "C", "C#", "D", "D#"],
        # theoretical
        ["E#", "E##", "F##", "F###", "G##", "A#", "A##", "B#", "B##", "C##",
            "C###", "D##"],
        # theoretical
        ["Fb", "Gbb", "Gb", "Abb", "Ab", "Bbb", "Cbb", "Cb", "Dbb", "Db",
            "Ebb", "Eb"],
        ["F", "Gb", "G", "Ab", "A", "Bb", "B", "C", "Db", "D", "Eb", "E"],
        ["F#", "G", "G#", "A", "A#", "B", "C", "C#", "D", "D#", "E", "E#"],
        ["Gb", "Abb", "Ab", "Bbb", "Bb", "Cb", "Dbb", "Db", "Ebb", "Eb", "Fb",
            "F"],
        ["G", "G#", "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#"],
        # theoretical
        ["G#", "G##", "A#", "A##", "B#", "C#", "C##", "D#", "D##", "E#", "E##",
            "F##"],
        ["Ab", "A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G"]]

    def __init__(self, song, new_key):
        self.song = song
        self.new_key = new_key
        self.new_key_value = self.key_number(new_key)
        self.key_value = self.key_number(self.song['Key'])
        self.transpose()

    def transpose(self):
        if not self.new_key or self.song['Key'] == self.new_key:
            return

        if self.new_key_value != self.INVALID_NOTE:
            self.transpose_song()
            self.song['Key'] = self.new_key

    def semitone_number(self, note):
        semi_no = self.INVALID_NOTE
        note = self.simply_posh_characters(note)

        # The note could contain multiple sharps OR flats.
        # We find the note in the list of semitones in the current key.
        for semi in range(self.SEMITONE_COUNT):
            if self.KEY_TABLE[self.key_value][semi] == note:
                semi_no = semi
                break

        return semi_no

    def transpose_song(self):
        """
        Go through the song line-by-line and transpose the chords.
        """
        # Go through each section and get the song lines
        for sect in self.song['display_order']:
            for line_index, line in enumerate(self.song[sect]):
                for chord_index, chord in enumerate(line.get('chords', [])):
                    ch = self.transpose_compound_chord(chord)
                    self.song[sect][line_index]['chords'][chord_index] = ch

    def transpose_compound_chord(self, chord):
        """
        Transpose the chord, handling compound chords e.g. G/B.
        """
        if '/' in chord:
            primary, bass = chord.split('/')
            primary = self.transpose_chord(primary.strip())
            bass = self.transpose_note(bass.strip())
            return '%s/%s' % (primary, bass)
        else:
            primary = self.transpose_chord(chord.strip())
            return primary

    def transpose_chord(self, chord):
        """
        Takes the chord e.g. Gbmaj7 and transposes the note part of the chord,
        whilst preserving the chord type.
        """
        if len(chord) == 0:
            return chord

        # Convert the fancy flat/sharp symbols
        chord = self.simply_posh_characters(chord)

        # Store the type of chord e.g. maj7, aug4 etc., and the note part
        chord_type = self.chord_type(chord)
        note_part = chord.replace(chord_type, '')

        # Transpose the note part and add the chordType back on
        return self.transpose_note(note_part) + chord_type

    def transpose_note(self, note):
        """
        The main transposition method that takes a note in one key and converts
        it to the equivalent in another key.
        """
        semi_no = self.semitone_number(note)

        if semi_no != self.INVALID_NOTE:
            # Use the noteSemitoneNumber to look up the new note from the
            # transpose table.
            new_note = self.KEY_TABLE[self.new_key_value][semi_no]

            # Return double sharps as "x" if there are an even number of them
            sharp_count = len(new_note.split('#')) - 1
            if sharp_count % 2:
                new_note = new_note.replace('##', 'x')
            return new_note
        else:
            # Don't transpose invalid notes
            return note

    @staticmethod
    def chord_type(chord):
        """
        Retrieve the type of chord e.g. maj7, aug4 etc.
        This method assumes that the chord has at most, one sharp, one
        double-sharp or flat.
        """
        end_note_part = max(chord.rfind('b'), chord.rfind('#'))
        if end_note_part > -1:
            # E.g. Gbmaj7
            ch_type = chord[end_note_part + 1:]

        else:
            # E.g. Gmaj7
            ch_type = chord[1:]

        return ch_type

    @staticmethod
    def simply_posh_characters(chord):
        ch = chord.replace("x", "##")
        #ch = ch.replace("♯", "#")
        #ch = ch.replace("♭", "b")
        return ch

    def key_number(self, key):
        """
        Find the key from the transpose table using the first entry from each
        row as the key name and return the row number. We don't simplify the
        key string - if we don't have it in the transpose table, we don't
        support it.
        """
        for k in range(self.KEY_COUNT):
            if self.KEY_TABLE[k][0] == key:
                return k

        return self.INVALID_NOTE


if __name__ == '__main__':
    from music.model.song import Onsong

    f = file('/Users/jjesudason/Downloads/Alive.onsong')
    s = f.read()
    f.close()
    o = Onsong(s)
    s = o.parsed
    app.logger.debug(s)
    t = Transpose(s, 'C#')
    app.logger.debug(s)
