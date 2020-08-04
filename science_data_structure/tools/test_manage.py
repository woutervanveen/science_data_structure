import unittest
from science_data_structure.tools import manage
from click.testing import CliRunner


class TestManage(unittest.TestCase):

    def test_author_creation(self):
        runner = CliRunner()
        result = runner.invoke(manage.create_author, ["Wouter van Veen"])
        

if __name__ == "__main__":
    unittest.main()
