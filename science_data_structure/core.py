import json
from typing import Dict


class JSONObject:

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__(),
                          sort_keys=True,
                          indent=4)

    @staticmethod
    def dict_from_json(text: str) -> Dict:
        return json.loads(text)

class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]

