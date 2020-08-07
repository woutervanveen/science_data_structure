from pathlib import Path
from typing import List
from science_data_structure.author import Author
from science_data_structure.core import JSONObject
import uuid
import json


class Meta(JSONObject):

    id_counter = 0

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
            "authors": self._authors,
            "description": self._description
        }

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def dataset_id(self):
        return self._dataset_id

    @property
    def branch_id(self):
        return self._branch_id

    @property
    def authors(self):
        return self._authors

    @staticmethod
    def create_top_level_meta(path: Path,
                              author: Author,
                              description: str = ""):
        # create a uuid for the dataset
        dataset_id = uuid.uuid4().int
        branch_id = 0
        Meta.id_counter += 1
        meta = Meta(path,
                    dataset_id,
                    branch_id,
                    description,
                    [author])
        return meta

    @staticmethod
    def create_meta(top_level_meta: "Meta",
                    path):
        dataset_id = top_level_meta.dataset_id
        branch_id = Meta.id_counter
        Meta.id_counter += 1
        meta = Meta(path / ".meta.json", dataset_id, branch_id)
        return meta

    @staticmethod
    def from_json(path: Path) -> "Meta":
        text = path.read_text()
        json_data = json.loads(text)
        authors = list(map(lambda author_content: Author.from_dict(author_content), json_data["authors"]))

        return Meta(path, int(json_data["dataset_id"]),
                    int(json_data["branch_id"]),
                    json_data["description"], authors)
