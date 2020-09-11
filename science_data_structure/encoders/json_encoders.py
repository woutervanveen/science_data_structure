import json
from descriptions import Author


class AuthorEncoder(json.JSONEncoder):

    def default(self, author: Author):
        return author.to_dict()
