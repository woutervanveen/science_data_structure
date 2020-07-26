import json
from typing import Dict, List
import json
from pathlib import Path
import abc


class JSONObject:

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__(),
                          sort_keys=True,
                          indent=4)


class Author(JSONObject):

    def __init__(self,
                 author_id: int,
                 name: str) -> None:
        self._author_id = author_id
        self._name = name

    def __dict__(self):
        return {
            "id": self._author_id,
            "name": self._name
        }

    def __str__(self) -> str:
        return "{:d} {:s}".format(self._author_id,
                                  self._name)

    @staticmethod
    def from_json(json_data: Dict) -> Dict[int, "Author"]:
        content = list(json_data.items())
        return dict(map(lambda item: (int(item[0]), Author(item[1]["id"], item[1]["name"])), content))


class Meta(JSONObject):

    def __init__(self,
                 path: Path) -> None:
        self._path = path

        self._authors = {}  # type: Dict[int, Author]

    def __dict__(self) -> Dict:
        result = {
            "path": str(self._path),
            "authors": self._authors
        }

        return result

    def write(self) -> None:
        output_line = self.to_json()
        self._path.write_text(output_line)


    @staticmethod
    def read(path: Path) -> "Meta":
        with path.open("r") as content:
            text = content.read()

            return Meta.from_json(path, json.loads(text))

    @staticmethod
    def from_json(path: Path, json_data: Dict) -> "Meta":
        meta = Meta(path)
        meta.authors = Author.from_json(json_data["authors"])

        return meta

    @property
    def authors(self) -> Dict[int, Author]:
        return self._authors

    @authors.setter
    def authors(self,
                authors: Dict[int, Author]) -> None:
        self._authors = authors

    def __str__(self) -> None:
        line = "{:s} authors = ".format(str(self._path))
        line += str(self._authors)
        return line

    def remove(self) -> None:
        self._path.unlink()
