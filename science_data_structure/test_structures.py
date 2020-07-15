import unittest
import structures
import pathlib
import numpy


class TestStructuredDataset(unittest.TestCase):
    """
    Test case for testing the basic class StructuredDataset
    """

    def setUp(self):
        self._test_path = pathlib.Path("/home/wgvanveen/Desktop/test")
        self._test_path.mkdir(exist_ok=True)

    def test_writing(self):
        leaf_name = "leaf_1"
        # create an empty data-set
        dataset = structures.StructuredDataset(pathlib.Path("/home/wgvanveen/Desktop"),
                                               "test_set",
                                               {},
                                               overwrite=True)
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

        data_x = leaf.add_data("x", x)
        data_y = leaf.add_data("y", y)

        dataset.write(exist_ok=True)

        self.assertTrue(data_x.path.exists)
        self.assertTrue(data_y.path.exists)

    def test_leaves(self):
        leaf_name = "leaf_1"
        # create an empty data-set
        dataset = structures.StructuredDataset(pathlib.Path("/home/wgvanveen/Desktop"),
                                               "test_set",
                                               {},
                                               overwrite=False)

        dataset.add_leaf(leaf_name)
        # try to add a leaf that already exists
        with self.assertRaises(FileExistsError):
            dataset.add_leaf(leaf_name)

        # add duplicate, overwriting the original leaf
        dataset.overwrite = True
        try:
            dataset.add_leaf(leaf_name)
        except FileExistsError:
            self.fail("dataset.add_leaf raised a FileExistsError")

    def test_auto_branching(self) -> None:
        data_set = structures.StructuredDataset(self._test_path,
                                                "test_auto_branching",
                                                {},
                                                enable_auto_branching=True)
        leaf_name_1 = "auto_branched"
        leaf_name_2 = "not_auto_branched"
        try:
            leaf = data_set[leaf_name_1]
            self.assertNotEqual(leaf, None)

            data_set.write(exist_ok=True)
            self.assertTrue(leaf.path.exists())
        except KeyError:
            self.fail("Did not auto-branch")


        # now disable autobranching
        data_set.enable_auto_branching = False
        with self.assertRaises(KeyError):
            data_set[leaf_name_2]
        data_set.write(exist_ok=True)
        # check if the second leaf exists
        self.assertFalse((data_set.path / leaf_name_2).exists())

        # test auto branching with variables
        data_set.enable_auto_branching = True
        x = numpy.linspace(0, 100, 1000)
        data_set[leaf_name_1]["x"] = x
        try:
            data_set[leaf_name_1]["x"]

        except KeyError:
            self.fail("auto branching failed")

        # try to overwrite the value in x
        with self.assertRaises(FileExistsError):
            data_set[leaf_name_1]["x"] = x


        # disable auto branching
        data_set.enable_auto_branching = False
        with self.assertRaises(PermissionError):
            data_set[leaf_name_1]["x_2"] = x

        with self.assertRaises(KeyError):
            data_set[leaf_name_1]["x_2"]


    def tearDown(self):
        # clean up the test environment
        # TODO First need to write the delete function (again)
        pass

if __name__ == "__main__":
    unittest.main()
