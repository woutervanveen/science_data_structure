import unittest
from science_data_structure.tools import manage
from science_data_structure.meta import Meta
from click.testing import CliRunner
from pathlib import Path


class TestManage(unittest.TestCase):

    def test_author_creation(self):
        runner = CliRunner()
        result = runner.invoke(manage.create_author, ["Wouter van Veen"])


    def test_dataset_creation(self):
        runner = CliRunner()
        result = runner.invoke(manage.create_dataset, ["test_data_set"])
        print(result.output)

    def test_list_authors(self):
        path = Path("../../test_new.struct/.meta.json")

        meta = Meta.from_json(path)


if __name__ == "__main__":
    unittest.main()
