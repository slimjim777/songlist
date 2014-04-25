# -*- coding: utf-8 -*-
from music import app
import dropbox
import re


class Drive(object):
    """
    Wrapper to connect to Google Drive and retrieve the files.
    """
    PATTERN_EXT = re.compile(r'[^.]+$')

    def __init__(self):
        self.client = dropbox.client.DropboxClient(app.config['DROPBOX_ACCESS_TOKEN'])
 
    def files(self):
        """
        Get the song names by looking for sub-folders.
        """
        songs = {}
        for meta in self.client.metadata('/Songs/')['contents']:
            if not meta['is_dir']:
                continue
            
            # Folder name is the song name
            song = meta['path'][7:]
            
            # Store the files for the song
            songs[song] = self.song_files(meta['path'])
        
        return songs
        
    def file_details(self, f):
        # Get the file extension from the full path
        ext = self.PATTERN_EXT.search(f['path']).group(0)
        if ext == f['path']:
            ext = ''

        # Save the file details    
        filename = {
            'name': f['path'].split('/')[-1],
            'path': f['path'],
            'extension': ext,
            'size': f['size'],
            'mime_type': f['mime_type'],
            'url': self.client.media(f['path'])['url'],
        }
        return filename
    
    def song_files(self, path):
        # Get the files in the subfolder
        filenames = []
        for f in self.client.metadata(path)['contents']:
            if f['is_dir']:
                continue                   
            file_meta = self.file_details(f)
            filenames.append(file_meta)
            
        return filenames

    def file_contents(self, path):
        f = self.client.get_file(path)
        contents = f.read()
        f.close()
        return contents
    
        
        