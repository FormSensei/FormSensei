import unittest
from unittest.mock import patch, MagicMock

class TestSocialMediaApp(unittest.TestCase):

    def setUp(self):
        print("test")

    def tearDown(self):
        print("test done")

    def test_insert_post(self):
        
        self.assertEqual(1, 1)

    def test_retrieve_latest_post(self):
        
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()