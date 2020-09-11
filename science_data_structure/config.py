from core import Singleton, JSONObject
from pathlib import Path
from tools import files as file_tools
from author import Author


class ConfigManager(JSONObject,
                    metaclass=Singleton):

    def __init__(self,
                 path: Path = file_tools.config_location() / "config.json") -> None:
        self._selected_author = None
        self._path = path
        self._default_author = None

        try:
            self._read()
        except FileNotFoundError:
            pass
        
    def _read(self):
        content = ConfigManager.dict_from_json(self._path.read_text())
        self._default_author = Author.from_dict(content["default_author"])

    def __dict__(self):
        return {
            "default_author": self._default_author
        }

    @property
    def default_author(self):
        return self._default_author

    @default_author.setter
    def default_author(self, default_author):
        self._default_author = default_author

    def write(self) -> None:
        self._path.write_text(self.to_json())
