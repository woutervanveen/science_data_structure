import unittest
import structures
import pathlib
import numpy


class TestStructuredDataset(unittest.TestCase):
    """
    Test case for testing the basic class StructuredDataset
    """

    def setUp(self):
        pass

    def test_writing(self):
        leaf_name = "leaf_1"
        # create an empty data-set
        dataset = structures.StructuredDataset(pathlib.Path("/home/wgvanveen/Desktop"),
                                               "test_set",
                                               {})
        dataset.write(exist_ok=True)

        # write the data-set
        self.assertTrue(dataset.path.exists())

        # check if it will overwrite, if not permitted
        with self.assertRaises(FileExistsError):
            dataset.write(exist_ok=False)

        # add a leaf
        leaf = dataset.add_leaf(leaf_name)
        dataset.write(exist_ok=True)
        self.assertTrue(leaf.path.exists)

        # add data
        x = numpy.linspace(0, 10, 1000)
        y = x ** 2

        data_x = leaf.add_data("x", x, exist_ok=True)
        data_y = leaf.add_data("y", y, exist_ok=True)

        dataset.write(exist_ok=True)

        self.assertTrue(data_x.path.exists)
        self.assertTrue(data_y.path.exists)

    def test_leaves(self):
        leaf_name = "leaf_1"
        # create an empty data-set
        dataset = structures.StructuredDataset(pathlib.Path("/home/wgvanveen/Desktop"),
                                               "test_set",
                                               {})

        dataset.add_leaf(leaf_name)
        # try to add a leaf that already exists
        with self.assertRaises(FileExistsError):
            dataset.add_leaf(leaf_name)

        # add duplicate, overwriting the original leaf
        try:
            dataset.add_leaf(leaf_name, exist_ok=True)
        except FileExistsError:
            self.fail("dataset.add_leaf raised a FileExistsError")

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
