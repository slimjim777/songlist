from music import app
from cStringIO import StringIO
import re


class ChordPro(object):
    """
    Parser for the ChordPro Chord Chart file format.
    """
    NOT_SECTIONS = ['title', 't', 'artist', 'subtitle', 'st', 'su', 'album', 'a', 'key', 'capo', 'tempo', 'time',
                    'duration', 'flow', 'comment', 'c', 'guitar_comment', 'gc', 'start_of_tab', 'sot', 'end_of_tab', 'eot'
                    'define', 'copyright', 'footer', 'book', 'number', 'keywords', 'ccli', 'restrictions', 'textsize',
                    'textfont', 'chordsize', 'chordfont', 'zoom-android', 'metronome',
                    'Title', 'Artist', 'Copyright', 'CCLI', 'Key', 'Capo', 'Tempo', 'Time',
                    'Duration', 'Flow', 'Book', 'Number', 'Keywords', 'Topic', 'Restrictions'
                    ]
    MAPPING = {
        'title': 'Title', 't': 'Title',
        'artist': 'Artist', 'subtitle': 'Artist', 'su': 'Artist', 'st': 'Artist',
        'key': 'Key',
    }

    # Get the text in curly brackets e.g. {title: ALIVE} => title: ALIVE
    PATTERN = re.compile(r'{([^\}]+)}')
    PATTERN_soh_eoh = re.compile(r'({eoh}|{soh})')
    NEWLINE = re.compile(r'[\r\n]')
    COMMENTS = re.compile(r'^#')
    CHORD_LINE = re.compile(r'\[([^]]+)\]')


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
            elif self.COMMENTS.match(line.strip()):
                # Ignore comment lines
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
        # Remove the soh/eoh sections
        line = self.PATTERN_soh_eoh.sub('', line)

        # Remove curly brackets, if they are there
        g = self.PATTERN.search(line)
        if g:
            line = g.groups(1)[0]

        # Normalise the key
        parts = line.split(':')
        parts[0] = parts[0].replace('#', '')
        key = self.MAPPING.get(parts[0], parts[0])

        # Remove the newline characters
        value = self.NEWLINE.sub('', ''.join(parts[1:])).strip()

        # Don't overwrite the song-key with an empty key
        if key == 'Key':
            if len(value) > 0:
                self.song[key] = value
        else:
            self.song[key] = value

        # The 'flow' is a comma-separated list of items
        if key == 'Flow':
        #    self.song[key] = self.song[key].split(',')
            self.song['Flow'] = []

        #app.logger.debug([key, self.song[key]])
        return key

    def song_line(self, line):
        """
        Parse the chords and lyrics into separate lists. The even elements are the lyrics
        and the odd elements are the chords.
        """
        # Split the line on the start of each chord
        parts = self.CHORD_LINE.split(line)

        chords = []
        lyrics = []
        for index, p in enumerate(parts):
            if self.is_odd(index):
                chords.append(self.NEWLINE.sub('', p))
            else:
                lyrics.append(self.NEWLINE.sub('', p))

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

if __name__ == '__main__':
    f = file('/Users/jjesudason/Downloads/Alive (ChordPro).pro')
    s = f.read()
    f.close()
    o = ChordPro(s)
    s = o.parse()

