import os
from pathlib import Path
import platform
from science_data_structure.core import JSONObject
import json


def default_path() -> Path:
    home_folder = Path(os.environ["HOME"])
    if platform.system() == "Linux":
        folder = home_folder / ".local/share/science_data_structure"
        folder.mkdir(exist_ok=True)
        return folder


class ConfigFile(JSONObject):

    def __init__(self,
                 author,
                 path: Path = default_path() / "config.json"):
        self._path = path
        self._author = author

    def write(self, overwrite: bool = False):
        if self._path.exists() and not overwrite:
            raise FileExistsError("Config file already exist, you must set theoverwrite explicitly")

        self._path.write_text(self.to_json())

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author

    def __dict__(self):
        return {
            "author": self._author
        }

    @staticmethod
    def read(path: Path = default_path() / "config.json") -> "ConfigFile":
        with path.open("r") as content:
            text = content.read()
            json_content = json.loads(text)
            from science_data_structure.author import Author
            author = Author.from_dict(json_content["author"])
            return ConfigFile(author, path)
        
