import unittest
import numpy
from meta import Meta
from author import Author
from structures import StructuredDataSet
from pathlib import Path


class TestMeta(unittest.TestCase):

    def setUp(self):
        self._test_path = Path("../test")
        self._test_path.mkdir(exist_ok=True)

    def test_top_level_meta(self):
        author = Author.create_author("Wouter van Veen")

        path = self._test_path 
        meta = Meta.create_top_level_meta(None,
                                          author,
                                          "")
        dataset = StructuredDataSet.create_dataset(path,
                                                   "test_meta",
                                                   meta)
        dataset.write()

    def test_branching(self):
        author = Author.create_author("Wouter van Veen")

        path = self._test_path 
        meta = Meta.create_top_level_meta(None,
                                          author,
                                          "")
        dataset = StructuredDataSet.create_dataset(path,
                                                   "test_meta_branching",
                                                   meta)

        x = dataset["x"]

        x["xx"] = numpy.zeros(30)

        dataset.write()
        x.meta.write()

if __name__ == "__main__":
    unittest.main()
