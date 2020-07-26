import unittest
import descriptions
import json
from pathlib import Path


class TestDescriptions(unittest.TestCase):


    def setUp(self) -> None:
        self._test_path = Path("../test_meta")
        self._test_path.mkdir(exist_ok=True)

    def test_author(self) -> None:
        author = descriptions.Author(0, "Wouter van Veen")


    def test_meta(self) -> None:
        path = self._test_path / ".meta.json"

        meta = descriptions.Meta.read(path)


if __name__ == "__main__":
    unittest.main()
