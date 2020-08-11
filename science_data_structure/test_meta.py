import unittest
import numpy
from science_data_structure.meta import Meta
from science_data_structure.author import Author
from science_data_structure.structures import StructuredDataSet
from tools import files as file_tools
from pathlib import Path
import random
import time


class TestMeta(unittest.TestCase):

    def setUp(self):
        self._test_path = Path("../test")
        self._test_path.mkdir(exist_ok=True)

    def tearDown(self):
        for child in self._test_path.iterdir():
            dataset = StructuredDataSet.read(child)
            dataset.remove()

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

    def test_file_properties(self):
        # create a dataset
        author = Author.create_author("Wouter van Veen")

        path = self._test_path 
        meta = Meta.create_top_level_meta(None,
                                          author,
                                          "")
        dataset = StructuredDataSet.create_dataset(path,
                                                   "test_meta_file_properties",
                                                   meta)

        dataset["x"] = numpy.random.random((100, 1000))
        dataset["x"].meta.description = "Dit is een variabele om de file grote te testen"

        dataset.write()
        file_tools.set_file_properties(dataset["x"].leaf_path)

        # the variable x should not contain any branch
        dataset.write()
        self.assertEqual(dataset["x"].meta["file_properties"].n_childs, 0)

        # Add a branch
        branch = dataset["xx"]

        n_branches = int(random.random() * 100)

        for i_branch in range(n_branches):
            branch["branch_{:d}".format(i_branch)]

        dataset.write()
        file_tools.set_file_properties(dataset["xx"].path)
        self.assertEqual(dataset["xx"].meta["file_properties"].n_childs, n_branches)


if __name__ == "__main__":
    unittest.main()
