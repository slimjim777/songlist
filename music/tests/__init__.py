import os
import music
import unittest
import tempfile

class MusicTestCase(unittest.TestCase):

    def setUp(self):
        #self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        music.app.config['TESTING'] = True
        self.app = music.app.test_client()
        #flaskr.init_db()

    def tearDown(self):
        #os.close(self.db_fd)
        #os.unlink(music.app.config['DATABASE'])
        pass

if __name__ == '__main__':
    unittest.main()
