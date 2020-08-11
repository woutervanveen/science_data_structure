import unittest
from author import Author
from pathlib import Path
import time


class TestAuthor(unittest.TestCase):

    def setUp(self):
        self._test_path = Path("../test_config")
        self._test_path.mkdir(exist_ok=True)

    def test_author_creation(self):
        author = Author.create_author("Test")
        time.sleep(1)
        author_second = Author.create_author("Test 2")

        self.assertNotEqual(author,
                            author_second)


if __name__ == "__main__":
    unittest.main()
