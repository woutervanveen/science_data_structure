import unittest
import structures
from pathlib import Path
from config import ConfigManager


class TestLogger(unittest.TestCase):

    def setUp(self):
        self._test_path = Path("../test_logger")
        
    def test_logger(self):
        author = ConfigManager().default_author
        dataset = structures.StructuredDataSet.create_dataset(self._test_path, "test_logger", author)

        # create a branch
        dataset["x"]["xx"]


        dataset.write()

if __name__ == "__main__":
    unittest.main()
