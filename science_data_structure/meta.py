from pathlib import Path
from typing import List
from science_data_structure.author import Author
from science_data_structure.core import JSONObject
import uuid
import json
from typing import Dict
import abc


class NodeProperty(JSONObject):

    @abc.abstractproperty
    def name(self):
        raise NotImplementedError("Must override the property name")


class Meta(JSONObject):

    id_counter = 0

    def __init__(self,
                 path: Path,
                 dataset_id: int,
                 branch_id: int,
                 description: str = "",
                 authors: List[Author] = [],
                 additional_properties: Dict[str, NodeProperty] = {}):
        self._path = path
        self._dataset_id = dataset_id
        self._branch_id = branch_id
        self._description = description
        self._authors = authors

        self._additional_properties = additional_properties

    def write(self):
        self.path.write_text(self.to_json())

    def __str__(self):
        line = "meta information \n"
        line += "dataset id \t {:d} \n".format(self._dataset_id)
        line += "branch id \t {:d} \n".format(self._branch_id)
        line += "description \t {:s} \n".format(self._description)
        line += "\n"
        line += "authors: \n"
        for author in self.authors:
            line += "{:s} \n \n".format(str(author))

        line += "\n"
        for name in self._additional_properties.keys():
            line += "{:s}\n".format(str(self._additional_properties[name]))

        return line

    def __dict__(self):
        base_dict = {
            "dataset_id": self._dataset_id,
            "branch_id": self._branch_id,
            "authors": self._authors,
            "description": self._description
        }
        for property_name in self._additional_properties.keys():
            base_dict[property_name] = self._additional_properties[property_name].__dict__()

        return base_dict
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

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

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

    def add_property(self, node_property: NodeProperty):
        self._additional_properties[node_property.name] = node_property

    def __getitem__(self, name: str) -> NodeProperty:
        return self._additional_properties[name]


class FileProperty(NodeProperty):

    def __init__(self):
        # properties
        self._size = None  # type: int
        self._n_childs = None  # type: int

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def n_childs(self) -> int:
        return self._n_childs

    @n_childs.setter
    def n_childs(self, n_childs):
        self._n_childs = n_childs

    @staticmethod
    def from_dict(content: Dict) -> "FileProperty":
        file_property = FileProperty()
        file_property.size = int(content["size"])
        file_property.n_childs = int(content["n_childs"])
        return file_property

    def __dict__(self):
        return {
            "size": self._size,
            "n_childs": self._n_childs
        }

    @property
    def name(self) -> str:
        return "file_properties"
