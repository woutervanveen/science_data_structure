import unittest
import structures
import pathlib
import numpy


class TestStructuredDataset(unittest.TestCase):
    """
    Test case for testing the basic class StructuredDataset
    """

    def setUp(self):
        self._test_path = pathlib.Path("../test")
        self._test_path.mkdir(exist_ok=True)

    def test_writing(self):
        leaf_name = "leaf_1"
        # create an empty data-set
        dataset = structures.StructuredDataset(self._test_path,
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
        dataset = structures.StructuredDataset(self._test_path,
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



        # test nested auto branching
        data_set.enable_auto_branching = True
        leaf_branched = data_set[leaf_name_1][leaf_name_1][leaf_name_1]
        leaf_nested_path = leaf_branched.path
        self.assertTrue((data_set.path / leaf_name_1 / leaf_name_1 / leaf_name_1) == leaf_nested_path)

        data_set.write(exist_ok=True)
        self.assertTrue(leaf_nested_path.exists())



    def test_kill(self) -> None:
        data_set = structures.StructuredDataset(self._test_path,
                                                "test_kill",
                                                {})

        x = numpy.linspace(0, 10, 1000)
        # add branches with nested branches and data
        n_branches = 3
        for i_branch in range(n_branches):
            leaf = data_set.add_leaf("leaf_{:d}".format(i_branch))
            self.add_leafes_recursive(leaf, i_branch)
            self.add_data_in_last_leaf(leaf, x)
        data_set.write(exist_ok=True)

        # remove some leafes
        with self.assertRaises(PermissionError):
            data_set["leaf_2"] = None

        # toggle overwrite
        data_set.overwrite = True
        data_set["leaf_2"] = None
        data_set.enable_auto_branching = False  # need to turn off auto branching otherwise the call of data_set["leaf_2"] will create a new branch

        with self.assertRaises(KeyError):
            data_set["leaf_2"]

        data_set.write(exist_ok=True, hard=True)

        # check if the leaf still exist on disk
        self.assertFalse((data_set.path / "leaf_2").exists())

        # try to remove the entire data-set
        path = data_set.path
        data_set.overwrite = False
        with self.assertRaises(PermissionError):
            data_set.remove()
        self.assertTrue(path.exists())

        data_set.overwrite = True
        data_set.remove()
        self.assertFalse(path.exists())

    def add_leafes_recursive(self, parent_leaf: structures.Leaf, depth) -> None:
        if depth > 0:
            for i_leaf in range(depth):
                leaf = parent_leaf.add_leaf("leaf_{:d}".format(i_leaf))
                self.add_leafes_recursive(leaf, depth-1)

    def add_data_in_last_leaf(self, leaf: structures.Leaf, data: numpy.ndarray, name: str = "data") -> None:
        if not leaf.has_leaves:
            leaf.add_data(name, data)
        else:
            for key in leaf.keys():
                if isinstance(leaf[key], structures.Leaf):
                    self.add_data_in_last_leaf(leaf[key], data, name)

    def tearDown(self):
        for test_structure in self._test_path.iterdir():
            if test_structure.suffix == ".struct":
                data_set = structures.StructuredDataset.read(test_structure)
                data_set.overwrite = True
                data_set.remove()
        self._test_path.rmdir()
        
if __name__ == "__main__":
    unittest.main()
