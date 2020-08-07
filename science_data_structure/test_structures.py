import unittest
import structures
import pathlib
import numpy
from meta import Meta
from author import Author


class TestStructuredDataset(unittest.TestCase):
    """
    Test case for testing the basic class StructuredDataset
    """

    def setUp(self):
        self._test_path = pathlib.Path("../test_structures")
        self._test_path.mkdir(exist_ok=True)

    def test_data_formats(self) -> None:
        author = Author.create_author("Test_author")
        meta = Meta.create_top_level_meta(None, author)
        dataset = structures.StructuredDataSet.create_dataset(self._test_path,
                                                              "data_formats",
                                                              meta)
        dataset["branch_1"]["branch_2"]["leaf"] \
            = numpy.random.random((10, 100))

        dataset.write()

    def test_writing(self):
        branch_name = "branch_1"
        # create an empty data-set
        author = Author.create_author("Test_author")
        meta = Meta.create_top_level_meta(None, author)
        dataset = structures.StructuredDataSet.create_dataset(self._test_path,
                                                              "test_set",
                                                              meta)
        
        dataset.write()

        # write the data-set 
        self.assertTrue(dataset.path.exists())

        # add a branch
        branch = dataset.add_branch(branch_name)
        self.assertTrue(branch.path.exists)

        # add data
        x = numpy.linspace(0, 10, 1000)
        y = x ** 2

        data_x = branch.add_data("x", x)
        data_y = branch.add_data("y", y)

        dataset.write()

        self.assertTrue(data_x.path.exists)
        self.assertTrue(data_y.path.exists)

    def test_leaves(self):
        branch_name = "branch_1"
        # create an empty data-set
        author = Author.create_author("Test_author")
        meta = Meta.create_top_level_meta(None, author)
        dataset = structures.StructuredDataSet.create_dataset(self._test_path,
                                                              "test_set",
                                                              meta)
 
        dataset.add_branch(branch_name)
        # try to add a branch that already exists
        with self.assertRaises(FileExistsError):
            dataset.add_branch(branch_name)

    def test_kill(self) -> None:
        # create an empty data-set
        author = Author.create_author("Test_author")
        meta = Meta.create_top_level_meta(None, author)
        dataset = structures.StructuredDataSet.create_dataset(self._test_path,
                                                              "test_kill",
                                                              meta)
 
        x = numpy.linspace(0, 10, 1000)
        # add branches with nested branches and data
        n_branches = 3
        for i_branch in range(n_branches):
            branch = dataset.add_branch("branch_{:d}".format(i_branch))
            self.add_branches_recursive(branch, i_branch)
            self.add_data_in_last_branch(branch, x)
        dataset.write()

        dataset["branch_2"] = None
        self.assertFalse("branch_2" in dataset.keys())

        dataset.write()

        # check if the branch still exist on disk
        self.assertFalse((dataset.path / "branch_2").exists())

        # try to remove the entire data-set
        path = dataset.path
        self.assertTrue(path.exists())

        dataset.overwrite = True
        dataset.remove()
        self.assertFalse(path.exists())

    def test_remove(self):
        # create an empty data-set
        author = Author.create_author("Test_author")
        meta = Meta.create_top_level_meta(None, author)
        dataset = structures.StructuredDataSet.create_dataset(self._test_path,
                                                              "test_kill",
                                                              meta)
 
        branch = dataset["mosquito"]["free"]
        branch["x"] = numpy.linspace(0, 1000, 1000)
        branch["y"] = numpy.linspace(0, 1000, 1000)

        dataset.write()

        path_x = branch["x"].path
        branch["x"] = None

        dataset.write()

        self.assertFalse(path_x.exists())


    def test_read(self) -> None:
        # create an empty data-set
        author = Author.create_author("Test_author")
        meta = Meta.create_top_level_meta(None, author)
        dataset = structures.StructuredDataSet.create_dataset(self._test_path,
                                                              "read_write",
                                                              meta)
 
        # fill up the data-set with random data
        n_branches = 10
        depth = 3
        for i_branch in range(n_branches):
            branch = dataset["branch_{:d}".format(i_branch)]
            self.add_branches_recursive(branch, depth)

            # place a random variable in each branch
            self.add_data_in_all_branches(branch,
                                          numpy.random.random((100, 100)),
                                          name="data_{:d}".format(i_branch))
        dataset.write()

        dataset_read = structures.StructuredDataSet.read(dataset.path)
        
        # compare the two data-sets
        self.assertEqual(dataset_read, dataset)

        # remove part of the data_set_read
        dataset_read["branch_0"] = None
        self.assertNotEqual(dataset_read, dataset)

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


