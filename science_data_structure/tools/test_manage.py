import unittest
from science_data_structure.tools import manage
from click.testing import CliRunner


class TestManage(unittest.TestCase):

    def test_author_creation(self):
        runner = CliRunner()
        result = runner.invoke(manage.create_author, ["Wouter van Veen"])


    def test_dataset_creation(self):
        runner = CliRunner()
        result = runner.invoke(manage.create_dataset, ["test_data_set"])
        print(result.output)

if __name__ == "__main__":
    unittest.main()
