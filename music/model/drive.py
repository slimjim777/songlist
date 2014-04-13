from music import app
import requests


class Drive(object):
    """
    Wrapper to connect to Google Drive and retrieve the files.
    """
    def files(self):
        """
        Get the files from Google Drive.
        TODO: Pagination
        """
        r = requests.get(app.config['DRIVE_FILES'])
        result = r.json()
        return result.get('files', {})
