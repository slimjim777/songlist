# -*- coding: utf-8 -*-
from music import app
from cStringIO import StringIO
import re


class Onsong(object):
    """
    Parser for the Onsong Chord Chart file format.
    """
    NOT_SECTIONS = ['Title', 'Artist', 'Copyright', 'CCLI', 'Key', 'Capo', 'Tempo', 'Time',
                    'Duration', 'Flow', 'Book', 'Number', 'Keywords', 'Topic', 'Restrictions']
    PATTERN = re.compile(r'\[([^]]+)\]')

    def __init__(self, contents):
        self.stream = StringIO(contents)
        self.song = {
            'Title': '',
            'Artist': '',
            'Copyright': '',
            'CCLI': '',
        }

    def parse(self):
        section = ''
        lines = []
        derived_flow = []

        for index, line in enumerate(self.stream.readlines()):
            if len(line.strip()) == 0:
                continue
            elif ':' in line:
                key = self.name_pair(line)
                if key not in self.NOT_SECTIONS:
                    # Must be a section of the song e.g. Verse 1, Chorus etc.
                    if len(section) > 0:
                        self.song[section] = lines
                    section = key
                    lines = []
                    derived_flow.append(key)
                continue
            elif index == 0:
                # Untagged title
                self.song['Title'] = line.strip()
                continue
            elif index == 1:
                # Untagged artist
                self.song['Artist'] = line.strip()
                continue                

            # Must be a line for the current section
            l = self.song_line(line)
            lines.append(l)

        if len(section) > 0:
            self.song[section] = lines
        self.stream.close()

        # If the file didn't provide a flow, then use our derived flow
        if len(self.song.get('Flow', [])) == 0:
            self.song['Flow'] = derived_flow

        # Define the sections for the display
        self.song['display_order'] = self.song_sections()
        
        app.logger.debug(self.song)
        return self.song

    def name_pair(self, line):
        parts = line.split(':')
        self.song[parts[0]] = ''.join(parts[1:]).replace('\r\n', '').strip()

        # The 'flow' is a comma-separated list of items
        if parts[0] == 'Flow':
            self.song[parts[0]] = self.song[parts[0]].split(',')
        return parts[0]

    def song_line(self, line):
        """
        Parse the chords and lyrics into separate lists. The even elements are the lyrics
        and the odd elements are the chords.
        """
        # Split the line on the start of each chord
        parts = self.PATTERN.split(line)

        chords = []
        lyrics = []
        for index, p in enumerate(parts):
            if self.is_odd(index):
                chords.append(p.replace('\r\n', ''))
            else:
                lyrics.append(p.replace('\r\n', ''))

        # If the line doesn't start with a chord, then prefix chord list with a blank chords
        if line[0] != '[':
            chords.insert(0, '')

        return {'chords': chords, 'lyrics': lyrics}

    def is_odd(self, num):
        return num & 0x1

    def song_sections(self):
        """
        Get the unique sections (verse1, chorus...) of the song from the 'flow'.
        """
        sections = []
        for f in self.song['Flow']:
            if f not in sections:
                sections.append(f)
        return sections


class Transpose(object):
    INVALID_NOTE = -1
    NOTENAMES = ["Ab", "A", "A#", "Bb", "B", "Cb", "C", "C#", "Db", "D", "D#", "Eb", "E", "E#", "Fb", "F", "F#", "Gb", "G", "G#"]
    KEYTABLE = [["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"],
                ["Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A"],
                ["B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#"],
                # Key of C uses popular flats/sharps
                ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
                ["Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "C"],
                ["D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C", "C#"],
                ["Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "C", "Db", "D"],
                ["E", "F", "F#", "G", "G#", "A", "A#", "B", "C", "C#", "D", "D#"],
                ["F", "Gb", "G", "Ab", "A", "Bb", "B", "C", "Db", "D", "Eb", "E"],
                ["F#", "G", "G#", "A", "A#", "B", "C", "C#", "D", "D#", "E", "E#"],
                ["G", "G#", "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#"],
                ["Ab", "A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G"]]

    # The notes values converts note index (0~19) of NOTENAMES which has pitch equivalent names into a semitone number
    SEMITONE_NOS = [11, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 7, 8, 9, 9, 10, 11]
                 #  Ab  A  A# Bb B  Cb C  C# Db D  D# Eb E  E# Fb F  F# Gb  G  G#

    def transpose(self, song, new_key):
        self.song = song
        if not new_key or song['Key'] == new_key:
            return song

        self.key_value = self.semitone_number(self.song['Key'])
        self.new_key_value = self.semitone_number(new_key)

        if self.new_key_value != self.INVALID_NOTE:
            self.transpose_song()
            self.song['Key'] = new_key

        return self.song

    def semitone_number(self, note):
        semi_no = self.INVALID_NOTE
        note = self.simply_posh_characters(note)

        # Get the note letter (without sharps/flats) and get it's semitone number to start with
        note_letter = note[0]

        for n in range(len(self.NOTENAMES)):
            if self.NOTENAMES[n] == note_letter:
                semi_no = self.SEMITONE_NOS[n]
                break

        if semi_no != self.INVALID_NOTE:
            # Then add or subtract that semitone number by the number of flats and sharps in the Note
            sharp_count = len(note.split('#')) - 1
            flat_count = len(note.split('b')) - 1

            semi_no += sharp_count
            semi_no -= flat_count
            return self.normalise_semitone_number(semi_no)
        else:
            return self.INVALID_NOTE

    def transpose_song(self):
        """
        Go through the song line-by-line and transpose the chords.
        """
        # Get the unique sections of the song
        sections = self.song_sections()

        # Go through each section and get the song lines
        for sect in sections:
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
        Takes the chord e.g. Gbmaj7 and transposes the note part of the chord, whilst
        preserving the chord type.
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
        The main transposition method that takes a note in one key and converts it to the
        equivalent in another key.
        """
        semi_no = self.semitone_number(note)

        if semi_no != self.INVALID_NOTE:
            # Find the offset of this note from the current key of the song
            semi_diff = semi_no - self.key_value
            semi_no = self.normalise_semitone_number(semi_diff)

            # Find the equivalent note in the new key
            return self.KEYTABLE[self.new_key_value][semi_no]
        else:
            # Don't transpose invalid notes
            return note

    def chord_type(self, chord):
        """
        Retrieve the type of chord e.g. maj7, aug4 etc.
        This method assumes that the chord has at most, one sharp, one double-sharp or flat.
        """
        end_note_part = max(chord.rfind('b'), chord.rfind('#'), chord.rfind('x'))
        if end_note_part > -1:
            # E.g. Gbmaj7
            ch_type = chord[end_note_part + 1:]

        else:
            # E.g. Gmaj7
            ch_type = chord[1:]

        return ch_type

    def song_sections(self):
        """
        Get the unique sections (verse1, chorus...) of the song from the 'flow'.
        """
        sections = []
        for f in self.song['Flow']:
            if f not in sections:
                sections.append(f)
        return sections

    def normalise_semitone_number(self, semi_no):
        if semi_no > 11:
            semi_no -= 12
        elif semi_no < 0:
            semi_no += 12
        return semi_no

    def simply_posh_characters(self, chord):
        ch = chord.replace("x", "##")
        #ch = ch.replace("♯", "#")
        #ch = ch.replace("♭", "b")
        return ch


if __name__ == '__main__':
    f = file('/Users/jjesudason/Downloads/Alive.onsong')
    s = f.read()
    f.close()
    o = Onsong(s)
    s = o.parse()
    t = Transpose()
    t.transpose(s, 'G')
