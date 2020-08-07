import unittest
from pathlib import Path
from science_data_structure.structures import StructuredDataSet
from science_data_structure.meta import Meta
from science_data_structure.author import Author
from science_data_structure.tools import files
import numpy


class TestFiles(unittest.TestCase):

    def setUp(self):
        self._test_path = Path("../../test/test_files")
        self._test_path.mkdir(exist_ok=True)

        author = Author.create_author("Test Author")
        meta = Meta.create_top_level_meta(None, author, description="Testing a data-set discovery")
        self._dataset = StructuredDataSet.create_dataset(self._test_path,
                                                         "test_dataset",
                                                         meta)
        x = self._dataset["x"]["x"]
        x["xx"] = numpy.zeros(100)
        self._dataset.write()

    def test_top_level_meta(self):
        testing_path = self._dataset.path / "x" / "x" / "xx.leaf"

        meta = files.find_top_level_meta(testing_path)

        self.assertEqual(meta.branch_id, 0)
        self.assertEqual(meta.dataset_id,
                         self._dataset.meta.dataset_id)

        # check the author
        author = meta.authors[0]
        self.assertEqual(author.author_id,
                         self._dataset.meta.authors[0].author_id)

if __name__ == "__main__":
    unittest.main()

