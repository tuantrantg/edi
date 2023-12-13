import codecs
import os
from datetime import date, datetime
from random import randint, randrange

from dateutil.parser import parse

# TODO: Find "clean" way to manage imports for both module & CLI contexts
try:
    from .const import SYSTEM_ERP, SYSTEM_WAMAS
except ImportError:
    from const import SYSTEM_ERP, SYSTEM_WAMAS


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


def get_current_date():
    return datetime.utcnow().strftime("%Y-%m-%d")


def get_source(*args):
    return SYSTEM_ERP


def get_destination(*args):
    return SYSTEM_WAMAS


def get_sequence_number(val=0):
    return val


def get_current_datetime(val=0):
    return datetime.utcnow()


def _set_string(val, length, dp):
    return str(val or "").ljust(length)[:length]


def _set_string_int(val, length, dp):
    return str(val).rjust(length, "0")[:length]


def _set_string_float(val, length, dp):
    res = str(float(val or 0))

    # Check if it is int / float or not
    if not res.replace(".", "", 1).isdigit():
        raise Exception(
            "The value '%s' is not the float type. Please check it again!" % res
        )

    str_whole_number, str_decimal_portion = res.split(".")
    str_whole_number = str_whole_number.rjust(length - dp, "0")
    str_decimal_portion = str_decimal_portion.ljust(dp, "0")

    return (str_whole_number + str_decimal_portion)[:length]


def _set_string_date(val, length, dp):
    res = isinstance(val, str) and val != "" and parse(val) or val

    if isinstance(res, date):
        res = res.strftime("%Y%m%d")
    elif isinstance(res, datetime):
        res = res.date().strftime("%Y%m%d")
    elif isinstance(res, str):
        res = res.ljust(length)
    else:
        raise Exception(
            "The value '%s' is not the date type. Please check it again!" % res
        )

    return res[:length]


def _set_string_datetime(val, length, dp):
    res = isinstance(val, str) and val != "" and parse(val) or val

    if isinstance(res, (date, datetime)):
        res = res.strftime("%Y%m%d%H%M%S")
    elif isinstance(res, str):
        res = res.ljust(length)
    else:
        raise Exception(
            "The value '%s' is not the date type. Please check it again!" % res
        )

    return res.ljust(length)[:length]


def _set_string_bool(val, length, dp):
    return (val or "N")[:length]


def set_value_to_string(val, ttype, length, dp):
    setters = dict(
        str=_set_string,
        int=_set_string_int,
        float=_set_string_float,
        date=_set_string_date,
        datetime=_set_string_datetime,
        bool=_set_string_bool,
    )
    return setters[ttype](val, length, dp)


def get_random_str_num(*args):
    range_start = 10 ** (args[0] - 1)
    range_end = (10 ** args[0]) - 1
    return str(randint(range_start, range_end))


def get_random_int_num(*args):
    return randrange(9999)


def get_parent_id(*args):
    dict_parent_id, dict_child_key, field, telegram_type_out = args
    return dict_parent_id[dict_child_key[telegram_type_out][field]]


def get_random_quai(*args):
    return "QUAI-%d" % randint(1, 999)
