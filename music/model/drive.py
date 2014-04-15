from music import app
import dropbox


class Drive(object):
    """
    Wrapper to connect to Google Drive and retrieve the files.
    """
    def __init__(self):
        self.client = dropbox.client.DropboxClient(app.config['DROPBOX_ACCESS_TOKEN'])
 
    def files(self):
        """
        Get the song names by looking for subfolders.
        TODO: Pagination
        """
        songs = {}
        for meta in self.client.metadata('/Songs/')['contents']:
            if not meta['is_dir']:
                continue
            
            # Folder name is the song name 
            song = meta['path'][7:]
            
            # Get the files in the subfolder
            filenames = []
            for f in self.client.metadata(meta['path'])['contents']:
                if f['is_dir']:
                    continue                   
                file_meta = self.file_details(f)
                filenames.append(file_meta)
                
            # Store the files for the song
            songs[song] = filenames
        
        return songs
        
    def file_details(self, f):
        filename = {
            'name': f['path'].split('/')[-1],
            'path': f['path'],
            'size': f['size'],
            'mime_type': f['mime_type'],
            'url': self.client.media(f['path'])['url'],
        }
        return filename
        