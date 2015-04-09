# -*- coding: utf-8 -*-
from cStringIO import StringIO
from music import app
import re


class Song(object):
    """
    Base Parser class for all song formats
    """
    NOT_SECTIONS = [
        'Title', 'Artist', 'Copyright', 'CCLI', 'Key', 'Capo', 'Tempo', 'Time',
        'Duration', 'Flow', 'Book', 'Number', 'Keywords', 'Topic',
        'Restrictions', 'OriginalKey']

    # Regular expression patterns
    NEWLINE = re.compile(r'[\r\n]')
    CHORD_LINE = re.compile(r'\[([^]]+)\]')

    def __init__(self, contents):
        self.stream = StringIO(contents)
        self.song = {
            'Title': '',
            'Artist': '',
            'Copyright': '',
            'CCLI': '',
            'Flow': [],
        }

    @property
    def song_sections(self):
        """
        Get the unique sections (verse1, chorus...) of the song from the 'flow'
        """
        sections = []
        for section in self.song['Flow']:
            if section not in sections:
                sections.append(section)
        return sections

    @staticmethod
    def is_odd(num):
        return num & 0x1

    def song_line(self, line):
        """
        Parse the chords and lyrics into separate lists. The even elements are
        the lyrics and the odd elements are the chords.
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

        # If the line doesn't start with a chord, then prefix chord list with a
        # blank chords
        if line[0] != '[':
            chords.insert(0, '')

        # There is a blank lyric when the line starts with a chord - remove it
        if line[0] == '[':
            lyrics.pop(0)

        return {'chords': chords, 'lyrics': lyrics}


class Onsong(Song):
    """
    Parser for the Onsong Chord Chart file format.
    """
    @property
    def parsed(self):
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
        if 0 == len(self.song.get('Flow', [])):
            self.song['Flow'] = derived_flow

        # Define the sections for the display
        self.song['display_order'] = self.song_sections

        return self.song

    def name_pair(self, line):
        parts = line.split(':')
        self.song[parts[0]] = self.NEWLINE.sub('', ''.join(parts[1:])).strip()

        # The 'flow' is a comma-separated list of items
        if parts[0] == 'Flow':
            self.song[parts[0]] = self.song[parts[0]].split(',')
        return parts[0]


class ChordPro(Song):
    """
    Parser for the ChordPro Chord Chart file format.
    """
    NOT_SECTIONS = [
        'title', 't', 'artist', 'subtitle', 'st', 'su', 'album', 'a', 'key',
        'capo', 'tempo', 'time', 'duration', 'flow', 'comment', 'c',
        'guitar_comment', 'gc', 'start_of_tab', 'sot', 'end_of_tab', 'eot',
        'define', 'copyright', 'footer', 'book', 'number', 'keywords', 'ccli',
        'restrictions', 'textsize', 'textfont', 'chordsize', 'chordfont',
        'zoom-android', 'metronome', 'Title', 'Artist', 'Copyright', 'CCLI',
        'Key', 'Capo', 'Tempo', 'Time', 'Duration', 'Flow', 'Book', 'Number',
        'Keywords', 'Topic', 'Restrictions', 'OriginalKey']
    MAPPING = {
        'title': 'Title', 't': 'Title',
        'artist': 'Artist', 'subtitle': 'Artist', 'su': 'Artist',
        'st': 'Artist', 'key': 'Key',
    }

    # Get the text in curly brackets e.g. {title: ALIVE} => title: ALIVE
    PATTERN_CURLY = re.compile(r'{([^\}]+)}')
    PATTERN_soh_eoh = re.compile(r'(\{eoh\}|\{soh\})')
    COMMENTS = re.compile(r'^#')

    @property
    def parsed(self):
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
        if 0 == len(self.song.get('Flow', [])):
            self.song['Flow'] = derived_flow

        # Define the sections for the display
        self.song['display_order'] = self.song_sections

        return self.song

    def name_pair(self, line):
        # Remove the soh/eoh sections
        line = self.PATTERN_soh_eoh.sub('', line)

        # Remove curly brackets, if they are there
        g = self.PATTERN_CURLY.search(line)
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
            # Don't use the provided flow from ChordPro files as they don't
            # match the section names
            self.song['Flow'] = []

        return key


if __name__ == '__main__':
    f = file('/Users/jjesudason/Dropbox/Songs/Alive/Alive.onsong')
    s = f.read()
    f.close()
    o = Onsong(s)
    s = o.parsed
    app.logger.debug(s)
