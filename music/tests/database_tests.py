from music import app
import unittest
from music.model.database import Database


class DatabaseTestCase(unittest.TestCase):
    TEST_KEYS = ['test_key']
    
    def setUp(self):
        self.db = Database()
        
    def tearDown(self):
        """
        Remove the test keys.
        """
        for k in self.TEST_KEYS:
            self.db.delete(k)

    def test_get_all_keys(self):
        keys = self.db.r.keys()
        app.logger.debug(keys)
        self.assertTrue(isinstance(keys, list))
        
    def test_set_get_key(self):
        result1 = self.db.set('test_key', 'Test Value')
        result2 = self.db.get('test_key')
        result3 = self.db.delete('test_key')
        result4 = self.db.get('test_key')
        
        self.assertTrue(result1)
        self.assertEqual(result2, 'Test Value')
        self.assertTrue(result3)
        self.assertEqual(result4, None)


if __name__ == '__main__':
    unittest.main()
