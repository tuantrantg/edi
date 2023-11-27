import codecs
import os
from datetime import datetime

from dateutil.parser import parse


def file_path(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path)


def file_open(path):
    return codecs.open(path, "r", "iso-8859-1")


class obj:
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(v, (list, tuple)):
                setattr(self, k, [obj(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, obj(v) if isinstance(v, dict) else v)


def get_date(val):
    val = parse(val)
    if isinstance(val, datetime):
        val = val.strftime("%Y-%m-%d")
    return val


def get_time(val):
    val = parse(val)
    if isinstance(val, datetime):
        val = val.strftime("%H:%M:%S")
    return val
