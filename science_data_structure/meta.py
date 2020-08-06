from pathlib import Path
from typing import List
from science_data_structure.author import Author
from science_data_structure.core import JSONObject
import uuid


class Meta(JSONObject):

    def __init__(self,
                 path: Path,
                 dataset_id: hex,
                 branch_id: int,
                 description: str = "",
                 authors: List[Author] = []):
        self._path = path
        self._dataset_id = dataset_id
        self._branch_id = branch_id
        self._description = description
        self._authors = authors

    def write(self):
        self.path.write_text(self.to_json())

    def __dict__(self):
        return {
            "dataset_id": self._dataset_id,
            "branch_id": self._branch_id,
            "authors": self._authors
        }


    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @staticmethod
    def create_top_level_meta(path: Path,
                              author: Author,
                              description: str = ""):
        # create a uuid for the dataset
        dataset_id = uuid.uuid4().hex
        branch_id = 0

        meta = Meta(path,
                    dataset_id,
                    branch_id,
                    description,
                    [author])
        return meta
