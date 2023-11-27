#!/usr/bin/python3

import getopt
import logging
import sys
from datetime import date, datetime

import xmltodict
from dateutil.parser import parse
from dotty_dict import Dotty

_logger = logging.getLogger("wamas2ubl")

# TODO: Find "clean" way to manage imports for both module & CLI contexts
try:
    from .utils import *
    from .wamas_grammar import ausk, ausp, weak, weap  # noqa: F401
except ImportError:
    from utils import *
    from wamas_grammar import ausk, ausp, weak, weap  # noqa: F401


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


def _get_sequence_number(val=0):
    return val


def _get_current_datetime(val=0):
    return datetime.utcnow()


def ubl2list_str(infile, telegram_type):
    res = []

    my_dict = Dotty(xmltodict.parse(infile))
    lst_telegram_type = telegram_type.split(",")
    lst_to_check = ["WEAK", "WEAP", "AUSK", "AUSP"]

    if not all(x in lst_to_check for x in lst_telegram_type):
        raise Exception("Invalid telegram types: %s" % telegram_type)

    dict_telegram_type_loop = {
        "WEAP": "DespatchAdvice.cac:DespatchLine",
        "AUSP": "DespatchAdvice.cac:DespatchLine",
    }

    idx = 0
    for telegram_type in lst_telegram_type:
        grammar = eval(telegram_type.lower()).grammar

        loop_element = dict_telegram_type_loop.get(telegram_type, False)
        len_loop = (
            loop_element
            and isinstance(my_dict[loop_element], list)
            and len(my_dict[loop_element])
            or 1
        )

        for idx_loop in range(len_loop):
            idx += 1
            line = ""
            for _key in grammar:
                val = ""
                ttype = grammar[_key]["type"]
                length = grammar[_key]["length"]
                dp = grammar[_key]["dp"]
                ubl_path = grammar[_key]["ubl_path"]
                df_val = grammar[_key]["df_val"]
                df_func = grammar[_key]["df_func"]

                if ubl_path:
                    if len_loop > 1:
                        ubl_path = (
                            "%s" in ubl_path and ubl_path % str(idx_loop) or ubl_path
                        )
                    else:
                        ubl_path = (
                            "%s" in ubl_path and ubl_path.replace(".%s", "") or ubl_path
                        )

                    if isinstance(ubl_path, list):
                        lst_val = []
                        for _item in ubl_path:
                            lst_val.append(my_dict[_item])
                        if lst_val:
                            val = " ".join(lst_val)
                    elif isinstance(ubl_path, dict):
                        for _key in ubl_path:
                            if my_dict.get(_key, False):
                                val = my_dict[ubl_path[_key]]
                    elif isinstance(ubl_path, str):
                        val = my_dict[ubl_path]
                    else:
                        val = ""
                elif df_val:
                    val = df_val
                elif df_func:
                    val = eval(df_func)(idx)

                line += set_value_to_string(val, ttype, length, dp)

            if line:
                res.append(line)

    return res


def ubl2wamas(infile, telegram_type, verbose=False):
    lst_of_str_wamas = ubl2list_str(infile, telegram_type)
    wamas = "\n".join(lst_of_str_wamas)
    if verbose:
        _logger.debug(wamas)
    return wamas


def usage(argv):
    _logger.debug("%s -i <inputfile> -t <telegram_types>" % argv[0])


def main(argv):
    infile = ""
    verbose = False
    opts, args = getopt.getopt(argv[1:], "hi:t:v", ["ifile=", "teletype=", "verbose"])
    for opt, arg in opts:
        if opt == "-h":
            usage(argv)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            infile = file_open(arg).read()
        elif opt in ("-v", "--verbose"):
            verbose = True
            logging.basicConfig(level=logging.DEBUG)
        elif opt in ("-t", "--teletype"):
            telegram_type = arg
    if not infile:
        usage(argv)
        sys.exit()
    ubl2wamas(infile, telegram_type, verbose)


if __name__ == "__main__":
    main(sys.argv)
