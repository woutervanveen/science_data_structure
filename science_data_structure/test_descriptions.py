import unittest
import descriptions
import json
from pathlib import Path


class TestDescriptions(unittest.TestCase):

    def setUp(self) -> None:
        self._test_path = Path("../test_meta")
        self._test_path.mkdir(exist_ok=True)

    def test_meta(self) -> None:
        meta = descriptions.Meta(self._test_path / ".meta.json")

        # create an author
        author = descriptions.Author(0, "Wouter van Veen")
        meta.add_author(author)
        with self.assertRaises(KeyError):
            meta.add_author(author)

        

if __name__ == "__main__":
    unittest.main()
