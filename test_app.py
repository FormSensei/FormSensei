import unittest
from unittest.mock import patch, MagicMock
#from deleteDB import *
from backend import add_post, get_latest_post
import sqlite3

class TestSocialMediaApp(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT NOT NULL,
            text TEXT NOT NULL,
            user TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_insert_post(self):
        # Insert a post
        add_post(self.conn, self.cursor, 'test_image.jpg', 'Test comment', 'TestUser')

        # Verify insertion
        self.cursor.execute('SELECT * FROM posts')
        posts = self.cursor.fetchall()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0][1], 'test_image.jpg')
        self.assertEqual(posts[0][2], 'Test comment')
        self.assertEqual(posts[0][3], 'TestUser')

    def test_retrieve_latest_post(self):
        # Insert multiple posts
        posts = [
            {'image': 'image1.jpg', 'text': 'First post', 'user': 'Alice'},
            {'image': 'image2.jpg', 'text': 'Second post', 'user': 'Bob'}
        ]
        for post in posts:
            add_post(self.conn, self.cursor, post['image'], post['text'], post['user'])

        # Retrieve latest post
        
        latest_post = get_latest_post(self.cursor)
        self.assertEqual(latest_post['image'], 'image2.jpg')
        self.assertEqual(latest_post['text'], 'Second post')
        self.assertEqual(latest_post['user'], 'Bob')

    # TO-DO: uncomment when deleteDB has a function
    """
    @patch("os.path.exists")
    @patch("os.remove")
    def test_delete_database_exists(self, mock_remove, mock_exists):
        # Simulate the file exists
        mock_exists.return_value = True
        
        # Call the function
        delete_database()
        
        # Check if os.remove was called
        mock_remove.assert_called_once_with("posts.db")

    @patch("os.path.exists")
    def test_database_not_found(self, mock_exists):
        # Simulate the file does not exist
        mock_exists.return_value = False
        
        # Capture the output during the function call
        with self.assertLogs(level="INFO") as log:
            delete_database()
        
        # Check if the correct message was printed
        self.assertIn("Database 'posts.db' not found.", log.output[0])

    @patch("os.path.exists")
    @patch("os.remove")
    def test_delete_database_error(self, mock_remove, mock_exists):
        # Simulate the file exists, but remove raises an error
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")
        
        # Capture the output during the function call
        with self.assertLogs(level="INFO") as log:
            delete_database()
        
        # Check if the error message was printed
        self.assertIn("Error deleting database file: Permission denied", log.output[0])
    """

if __name__ == '__main__':
    unittest.main()
