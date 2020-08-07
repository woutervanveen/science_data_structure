from datetime import datetime
import uuid
from science_data_structure.core import JSONObject


class Author(JSONObject):

    def __init__(self,
                 author_id: hex,
                 name: str,
                 created_on: datetime) -> None:
        self._id = author_id
        self._name = name
        self._created_on = created_on

    def __str__(self) -> str:
        return "Author \n id \t\t {:s} \n name \t\t {:s} \n created \t {:s}".format(str(self._id), self._name, self._created_on.strftime("%Y-%M-%d"))

    def __dict__(self):
        return {
            "id": str(self._id),
            "name": self._name,
            "created_on": self._created_on.strftime("%Y-%m-%d")
        }

    def __eq__(self, other):
        return (self._id == other.author_id)

    @property
    def author_id(self):
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def created_on(self):
        return self._create_on

    @staticmethod
    def create_author(name: str) -> "Author":
        return Author(uuid.uuid4().int,
                      name,
                      datetime.now())

    @staticmethod
    def from_dict(content):
        author_id = int(content["id"])
        name = content["name"]
        created_on = datetime.strptime(content["created_on"], "%Y-%M-%d")

        return Author(author_id,
                      name,
                      created_on)
