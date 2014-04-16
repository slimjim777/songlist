from music import app
from cStringIO import StringIO
import re


class Onsong(object):
    """
    Parser for the Onsong Chord Chart file format.
    """
    SECTIONS = ['Intro','Verse1','Verse2','Verse3','Verse4','PreChorus','Chorus','ShortPreChorus','Link','Instrumental']
    PATTERN = re.compile(r'\[([^]]+)\]')
    
    def __init__(self, contents):
        self.stream = StringIO(contents)
        self.song = {}
        
    def parse(self):
        section = ''
        lines = []

        for line in self.stream.readlines():
            if len(line.strip()) == 0:
                continue
            elif ':' in line:
                key = self.name_pair(line)
                if key in self.SECTIONS:
                    # TODO: save previous section
                    if len(section) > 0:
                        self.song[section] = lines 
                    section = key
                    lines = []
                continue
                
            # Must be a line for the current section
            l = self.song_line(line)
            lines.append(l)
            
        if len(section) > 0:
            self.song[section] = lines
        app.logger.debug(self.song)
        
        self.stream.close()
        return self.song

    def name_pair(self, line):
        parts = line.split(':')
        self.song[parts[0]] = ''.join(parts[1:]).replace('\r\n','')
        
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
        parts =  self.PATTERN.split(line)

        chords = []
        lyrics = []
        for index, p in enumerate(parts):
            if self.is_odd(index):
                chords.append(p.replace('\r\n',''))
            else:
                lyrics.append(p.replace('\r\n',''))
        
        # If the line doesn't start with a chord, then prefix chord list with a blank chords
        if line[0] != '[':
            chords.insert(0, '')
        
        return {'chords': chords, 'lyrics': lyrics}
        
    def is_odd(self, num):
        return num & 0x1
    
    
if __name__=='__main__':
    f = file('/Users/jjesudason/Downloads/Alive.onsong')
    s = f.read()
    f.close()
    o = Onsong(s)
    o.parse()
    