import unittest
from music import app
from music.model.drive import Drive


class DriveTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_files(self):
        """
        Get the names of the files from Google Drive.
        """
        d = Drive()
        files = d.files()
        self.assertEqual(len(files) > 0 , True)


if __name__ == '__main__':
    unittest.main()
