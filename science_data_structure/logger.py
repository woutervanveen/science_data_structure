from config import ConfigManager
from core import JSONObject
from datetime import datetime
import uuid


class LogEntry(JSONObject):

    def __init__(self,
                 log_id,
                 date: datetime,
                 author,
                 action: str):
        self._author = author
        self._action = action
        self._date = date
        self._id = log_id

    @property
    def log_id(self):
        return self._id

    def __dict__(self):
        return {
            "date": self._date.strftime("%s:%m:%h %D-%M-%Y"),
            "author": self._author,
            "action": self._action,
        }

    @staticmethod
    def create_log(date, author, action):
        log_id = uuid.uuid4().int
        return LogEntry(log_id, date, author, action)


# define logging decorators
def logger(func):
    def wrapper(*args, **kwargs):
        config = ConfigManager()
        meta = (args[0]).meta
        meta.add_log_entry(LogEntry.create_log(datetime.today(), config.default_author, func.__name__))

        func(*args, **kwargs)
    return wrapper
