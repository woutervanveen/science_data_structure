import unittest
import structures
import pathlib
import numpy


class TestStructuredDataset(unittest.TestCase):
    """
    Test case for testing the basic class StructuredDataset
    """

    def setUp(self):
        self._test_path = pathlib.Path("../test_structures")
        self._test_path.mkdir(exist_ok=True)

    def test_data_formats(self) -> None:
        data_set = structures.StructuredDataSet(self._test_path,
                                                "data_formats",
                                                {})

        data_set["branch_1"]["branch_2"]["leaf"] \
            = numpy.random.random((10, 100))

        data_set.write(exist_ok=True)

    def test_writing(self):
        branch_name = "branch_1"
        # create an empty data-set
        dataset = structures.StructuredDataSet(self._test_path,
                                               "test_set",
                                               {})
        dataset.write(exist_ok=True)

        # write the data-set 
        self.assertTrue(dataset.path.exists())

        # check if it will overwrite, if not permitted
        with self.assertRaises(FileExistsError):
            dataset.write(exist_ok=False)

        # add a branch
        branch = dataset.add_branch(branch_name)
        dataset.write(exist_ok=True)
        self.assertTrue(branch.path.exists)

        # add data
        x = numpy.linspace(0, 10, 1000)
        y = x ** 2

        data_x = branch.add_data("x", x)
        data_y = branch.add_data("y", y)

        dataset.write(exist_ok=True)

        self.assertTrue(data_x.path.exists)
        self.assertTrue(data_y.path.exists)

    def _test_leaves(self):
        branch_name = "branch_1"
        # create an empty data-set
        dataset = structures.StructuredDataSet(self._test_path,
                                               "test_set",
                                               {})

        dataset.add_branch(branch_name)
        # try to add a branch that already exists
        with self.assertRaises(FileExistsError):
            dataset.add_branch(branch_name)

        # add duplicate, overwriting the original branch
        try:
            dataset.add_branch(branch_name)
        except FileExistsError:
            self.fail("dataset.add_branch raised a FileExistsError")

    def test_kill(self) -> None:
        data_set = structures.StructuredDataSet(self._test_path,
                                                "test_kill",
                                                {})

        x = numpy.linspace(0, 10, 1000)
        # add branches with nested branches and data
        n_branches = 3
        for i_branch in range(n_branches):
            branch = data_set.add_branch("branch_{:d}".format(i_branch))
            self.add_branches_recursive(branch, i_branch)
            self.add_data_in_last_branch(branch, x)
        data_set.write(exist_ok=True)

        # toggle overwrite
        data_set.overwrite = True
        data_set["branch_2"] = None
        self.assertFalse("branch_2" in data_set.keys())

        data_set.write(exist_ok=True)

        # check if the branch still exist on disk
        self.assertFalse((data_set.path / "branch_2").exists())

        # try to remove the entire data-set
        path = data_set.path
        data_set.overwrite = False
        self.assertTrue(path.exists())

        data_set.overwrite = True
        data_set.remove()
        self.assertFalse(path.exists())

    def test_remove(self):
        data_set = structures.StructuredDataSet(self._test_path,
                                                "test_remove",
                                                {})
        branch = data_set["mosquito"]["free"]
        branch["x"] = numpy.linspace(0, 1000, 1000)
        branch["y"] = numpy.linspace(0, 1000, 1000)

        data_set.write(exist_ok=True)

        data_set.overwrite = True
        path_x = branch["x"].path
        branch["x"] = None

        data_set.write(exist_ok=True)

        self.assertFalse(path_x.exists())

        path_y = branch["y"].path
        branch["y"] = structures.Branch(branch.path, "y", {})

        data_set.write(exist_ok=True)

        self.assertFalse(path_y.exists())

    def test_read(self) -> None:
        data_set = structures.StructuredDataSet(self._test_path,
                                                "read_write",
                                                {})

        # fill up the data-set with random data
        n_branches = 10
        depth = 3
        for i_branch in range(n_branches):
            branch = data_set["branch_{:d}".format(i_branch)]
            self.add_branches_recursive(branch, depth)

            # place a random variable in each branch
            self.add_data_in_all_branches(branch,
                                          numpy.random.random((100, 100)),
                                          name="data_{:d}".format(i_branch))
        data_set.write(exist_ok=True)

        data_set_read = structures.StructuredDataSet.read(data_set.path)
        
        # compare the two data-sets
        self.assertEqual(data_set_read, data_set)

        # remove part of the data_set_read
        data_set_read.overwrite = True
        data_set_read["branch_0"] = None
        self.assertNotEqual(data_set_read, data_set)


    def add_leafs_recursive(self, parent_leaf: structures.Leaf, depth) -> None:
        if depth > 0:
            for i_leaf in range(depth):
                leaf = parent_leaf.add_leaf("leaf_{:d}".format(i_leaf))
                self.add_leafs_recursive(leaf, depth-1)

    def add_branches_recursive(self,
                               parent_branch: structures.Branch,
                               depth: int) -> None:
        if depth > 0:
            for i_branch in range(depth):
                branch \
                    = parent_branch.add_branch("branch_{:d}".format(i_branch))
                self.add_branches_recursive(branch, depth-1)

    def add_data_in_last_branch(self, branch: structures.Branch,
                                data: numpy.ndarray,
                                name: str = "data") -> None:
        if not branch.has_leaves:
            branch.add_data(name, data)
        else:
            for key in branch.keys():
                if isinstance(branch[key], structures.Branch):
                    self.add_data_in_last_branch(branch[key], data, name)

    def add_data_in_all_branches(self, branch: structures.Branch, data:
                                 numpy.ndarray, name: str = "data") -> None:
        for sub_branch in branch.branches:
            self.add_data_in_all_branches(sub_branch,
                                          data,
                                          name=name)
            sub_branch[name] = data

    def tearDown(self):
        for test_structure in self._test_path.iterdir():
            if test_structure.suffix == ".struct":
                data_set = structures.StructuredDataSet.read(test_structure)
                data_set.overwrite = True
                data_set.remove()
        self._test_path.rmdir()


if __name__ == "__main__":
    unittest.main()


