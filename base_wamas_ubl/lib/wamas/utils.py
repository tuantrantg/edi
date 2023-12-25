import codecs
import logging
import os
import re
import struct
from collections import OrderedDict
from datetime import date, datetime
from pprint import pprint

from dateutil.parser import parse

_logger = logging.getLogger("wamas_utils")

# TODO: Find "clean" way to manage imports for both module & CLI contexts
try:
    from . import miniqweb
    from .const import (
        DICT_WAMAS_GRAMMAR,
        LST_FIELD_UNIT_CODE,
        LST_TELEGRAM_TYPE_IGNORE_W2D,
        LST_TELEGRAM_TYPE_SUPPORT_D2W,
        LST_TELEGRAM_TYPE_SUPPORT_W2D,
        MAPPING_UNITCODE_UBL_TO_WAMAS,
        MAPPING_UNITCODE_WAMAS_TO_UBL,
        SYSTEM_ERP,
        SYSTEM_WAMAS,
        TELEGRAM_HEADER_GRAMMAR,
    )
    from .structure import obj
except ImportError:
    import miniqweb
    from const import (
        DICT_WAMAS_GRAMMAR,
        LST_FIELD_UNIT_CODE,
        LST_TELEGRAM_TYPE_IGNORE_W2D,
        LST_TELEGRAM_TYPE_SUPPORT_D2W,
        LST_TELEGRAM_TYPE_SUPPORT_W2D,
        MAPPING_UNITCODE_UBL_TO_WAMAS,
        MAPPING_UNITCODE_WAMAS_TO_UBL,
        SYSTEM_ERP,
        SYSTEM_WAMAS,
        TELEGRAM_HEADER_GRAMMAR,
    )
    from structure import obj


def file_path(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path)


def file_open(path):
    return codecs.open(path, "r", "iso-8859-1")


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
    return SYSTEM_ERP  # noqa: F405


def get_destination(*args):
    return SYSTEM_WAMAS  # noqa: F405


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


def convert_unit_code(key, val):
    if key in LST_FIELD_UNIT_CODE:
        return MAPPING_UNITCODE_UBL_TO_WAMAS["unitCode"].get(val, val)
    return val


def generate_wamas_line(dict_item, grammar, **kwargs):
    res = ""
    for _key in grammar:
        val = ""
        ttype = grammar[_key].get("type", False)
        length = grammar[_key].get("length", False)
        dp = grammar[_key].get("dp", False)
        ubl_path = grammar[_key].get("ubl_path", False)
        dict_key = grammar[_key].get("dict_key", False)
        df_val = grammar[_key].get("df_val", False)
        df_func = grammar[_key].get("df_func", False)

        if ubl_path:
            # Get the `ubl_path` if it has multi lines
            len_loop = kwargs.get("len_loop", False)
            idx_loop = kwargs.get("idx_loop", False)
            if len_loop and len_loop > 1:
                ubl_path = "%s" in ubl_path and ubl_path % str(idx_loop) or ubl_path
            else:
                ubl_path = "%s" in ubl_path and ubl_path.replace(".%s", "") or ubl_path
            # Handle the type of `ubl_path`
            if isinstance(ubl_path, list):
                lst_val = []
                for _item in ubl_path:
                    lst_val.append(dict_item.get(_item, ""))
                if lst_val:
                    val = " ".join(lst_val)
            elif isinstance(ubl_path, dict):
                for _key in ubl_path:
                    if dict_item.get(_key, False):
                        val = dict_item.get(ubl_path[_key], "")
            elif isinstance(ubl_path, str):
                val = dict_item.get(ubl_path, "")
            else:
                val = ""
        if not val and dict_key:
            val = dict_item.get(dict_key, "")
        if not val and df_val:
            val = df_val
        if not val and df_func:
            args = (kwargs.get("line_idx", 0),)
            val = globals()[df_func](*args)

        val = convert_unit_code(_key, val)
        res += set_value_to_string(val, ttype, length, dp)
    return res


def dict2wamas(dict_input, telegram_type):
    wamas_lines = []
    lst_telegram_type = telegram_type.split(",")

    if not all(x in LST_TELEGRAM_TYPE_SUPPORT_D2W for x in lst_telegram_type):
        raise Exception("Invalid telegram types: %s" % telegram_type)

    line_idx = 0
    for telegram_type in lst_telegram_type:
        line_idx += 1
        grammar = DICT_WAMAS_GRAMMAR[telegram_type.lower()]
        line = generate_wamas_line(dict_input, grammar, line_idx=line_idx)
        if line:
            wamas_lines.append(line)

    return "\n".join(wamas_lines).encode("iso-8859-1")


def _get_grammar(telegram_type, use_simple_grammar=False):
    if use_simple_grammar:
        grammar = DICT_WAMAS_GRAMMAR[telegram_type.lower()]
        if not isinstance(list(grammar.values())[0], dict):
            return grammar
        simple_grammar = OrderedDict()
        for field in grammar:
            if field in TELEGRAM_HEADER_GRAMMAR.keys():
                continue
            simple_grammar[field] = grammar[field]["length"]
        return simple_grammar
    return DICT_WAMAS_GRAMMAR[telegram_type.lower()]


def fw2dict(line, grammar, telegram_type, verbose=False):
    """
    Convert a fixed width to a dict

    definition: { "k1": 3, "k2": 5 }
    line: abcdefgh
    """

    # prepare format
    fieldwidths = grammar.values()
    fmtstring = " ".join("{}{}".format(abs(fw), "s") for fw in fieldwidths)
    unpack = struct.Struct(fmtstring).unpack_from

    # sanity checks
    expected_size = sum(fieldwidths)
    line = line.encode("iso-8859-1")
    if len(line) != expected_size:
        _logger.debug(
            "Line of length %d does not match expected length %d: %s",
            len(line),
            expected_size,
            line.decode("iso-8859-1"),
        )
        _logger.debug(repr(unpack(line)))

        if abs(len(line) - expected_size) == 1 and telegram_type in (
            "WATEKQ",
            "WATEPQ",
        ):
            _logger.debug("Length off by one only, fields not impacted, no fix needed.")

        elif telegram_type == "WATEPQ":
            # line_WATEPQ_-_weirdly_encoded_01.wamas
            # - this case has a weird WATEPQ:IvTep_MId_Charge
            #   of incorrect size due to weirdly encoded chars inside:
            #   b'6423033A\xc3\xa9\xc2\xb0\xc2\xb0\xc3\xaf\xc2\xbf\xc2\xbd
            #   \xc3\xaf\xc2\xbf\xc2\xbd370063 '
            #   33 chars instead of expected 20 (when file is decoded as iso-8859-1)
            # - we clean it from non ascii chars and fill it with space to fix length
            #   and avoid impact on other fields
            to_fix = line.split(b" ")[0]
            to_keep_idx = len(to_fix) + 1
            line = (
                to_fix.decode("iso-8859-1").encode("ascii", "ignore").ljust(20, b" ")
                + line[to_keep_idx:]
            )

            if len(line) is expected_size:
                _logger.debug("Line corrected successfully.")
            else:
                _logger.debug(
                    "Line of length %d still does not match expected length %d: %s",
                    len(line),
                    expected_size,
                    line.decode("iso-8859-1"),
                )

    # actual parsing
    try:
        vals = tuple(s.decode("iso-8859-1") for s in unpack(line))
    except struct.error as e:
        _logger.debug(line)
        raise e

    # cleaning
    vals = [v.strip() for v in vals]
    vals_with_keys = list(zip(grammar.keys(), vals))
    vals_with_lengths = list(zip(vals_with_keys, fieldwidths, list(map(len, vals))))
    if verbose:
        pprint(vals_with_lengths)
    res = dict(vals_with_keys)
    return res


def wamas2dict(
    infile, lst_valid_telgram=False, use_simple_grammar=False, verbose=False
):
    header_len = sum(TELEGRAM_HEADER_GRAMMAR.values())
    result = {}
    lst_telegram_type_in = []

    if not lst_valid_telgram:
        lst_valid_telgram = LST_TELEGRAM_TYPE_SUPPORT_W2D

    for line in infile.splitlines():
        if not line:
            continue
        head = fw2dict(line[:header_len], TELEGRAM_HEADER_GRAMMAR, "header")
        telegram_type, telegram_seq, dummy = re.split(r"(\d+)", head["Satzart"], 1)
        # ignore useless telegram types
        if telegram_type in LST_TELEGRAM_TYPE_IGNORE_W2D:
            continue
        if telegram_type not in lst_valid_telgram:
            raise Exception("Invalid telegram type: %s" % telegram_type)
        lst_telegram_type_in.append(telegram_type)
        grammar = _get_grammar(telegram_type, use_simple_grammar)
        body = fw2dict(line[header_len:], grammar, telegram_type)
        val = result.setdefault(telegram_type, [])
        val.append(body)
    lst_telegram_type_in = list(set(lst_telegram_type_in))
    if verbose:
        pprint(result)
    return result, lst_telegram_type_in


def dict2ubl(template, data, verbose=False, extra_data=False):
    t = miniqweb.QWebXml(template)
    # Convert dict to object to use dotted notation in template
    globals_dict = {
        "record": obj(data),
        "get_date": get_date,
        "get_time": get_time,
        "get_current_date": get_current_date,
        "MAPPING": MAPPING_UNITCODE_WAMAS_TO_UBL,
        "extra_data": extra_data,
    }
    xml = t.render(globals_dict)
    if verbose:
        pprint(xml)
    return xml
