import json


class JSONObject:

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__(),
                          sort_keys=True,
                          indent=4)

