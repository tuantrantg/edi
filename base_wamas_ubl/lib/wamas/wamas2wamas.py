#!/usr/bin/python3

import getopt
import logging
import re
import sys
from collections import OrderedDict
from pprint import pprint

# TODO: Find "clean" way to manage imports for both module & CLI contexts
try:
    from .ubl2wamas import DICT_WAMAS_GRAMMAR, set_value_to_string  # noqa: F401
    from .utils import *  # noqa: F403
    from .wamas2ubl import fw2dict, telegram_header_grammar
    from .wamas_grammar import (  # noqa: F401
        ausk,
        auskq,
        ausp,
        kretk,
        kretkq,
        kretp,
        kretpq,
        watekq,
        watepq,
        weak,
        weakq,
        weap,
        weapq,
    )
except ImportError:
    from ubl2wamas import DICT_WAMAS_GRAMMAR, set_value_to_string  # noqa: F401
    from utils import *  # noqa: F403
    from wamas2ubl import fw2dict, telegram_header_grammar
    from wamas_grammar import (  # noqa: F401
        ausk,
        auskq,
        ausp,
        kretk,
        kretkq,
        kretp,
        kretpq,
        watekq,
        watepq,
        weak,
        weakq,
        weap,
        weapq,
    )

_logger = logging.getLogger("wamas2wamas")


LST_VALID_TELEGRAM_IN = [
    "AUSK",
    "AUSP",
    "KRETK",
    "KRETP",
    "WATEK",
    "WATEP",
    "WEAK",
    "WEAP",
]


DICT_CONVERT_WAMAS_TYPE = {
    "AUSK": ["AUSKQ", "WATEKQ"],
    "AUSP": ["WATEPQ"],
    "AUSKQ": ["AUSK"],
    "KRETK": ["KRETKQ"],
    "KRETP": ["KRETPQ"],
    "WEAK": ["WEAKQ"],
    "WEAP": ["WEAPQ"],
}


DICT_WAMAS_GRAMMAR_OUT = {
    "auskq": auskq.grammar_convert,
    "kretkq": kretkq.grammar_convert,
    "kretpq": kretpq.grammar_convert,
    "watekq": watekq.grammar_convert,
    "watepq": watepq.grammar_convert,
    "weakq": weakq.grammar_convert,
    "weapq": weapq.grammar_convert,
}


DICT_PARENT_KEY = {"WATEKQ": ["IvTek_TeId"]}


DICT_CHILD_KEY = {"WATEPQ": {"IvTep_TeId": "IvTek_TeId"}}


def get_simple_grammar(telegram_type):
    grammar = DICT_WAMAS_GRAMMAR[telegram_type.lower()]
    simple_grammar = OrderedDict()
    for field in grammar:
        if field in telegram_header_grammar.keys():
            continue
        simple_grammar[field] = grammar[field]["length"]
    return simple_grammar


def _process_wamas_in(infile):
    header_len = sum(telegram_header_grammar.values())
    res = {}
    lst_telegram_type_in = []
    for line in infile.splitlines():
        if not line:
            continue
        head = fw2dict(line[:header_len], telegram_header_grammar, "header")
        telegram_type, telegram_seq, dummy = re.split(r"(\d+)", head["Satzart"], 1)
        if telegram_type not in LST_VALID_TELEGRAM_IN:
            raise Exception("Invalid telegram type: %s" % telegram_type)
        lst_telegram_type_in.append(telegram_type)
        grammar = get_simple_grammar(telegram_type)
        body = fw2dict(line[header_len:], grammar, telegram_type)
        val = res.setdefault(telegram_type, [])
        val.append(body)
    lst_telegram_type_in = list(set(lst_telegram_type_in))
    return res, lst_telegram_type_in


def _process_wamas_out(dict_wamas_in, lst_telegram_type_in):
    res = []

    if not all(x in LST_VALID_TELEGRAM_IN for x in lst_telegram_type_in):
        raise Exception("Invalid telegram types: %s" % ", ".join(lst_telegram_type_in))

    idx = 0
    dict_parent_id = {}
    for telegram_type_in in dict_wamas_in:
        for telegram_type_out in DICT_CONVERT_WAMAS_TYPE[telegram_type_in]:
            grammar_out = DICT_WAMAS_GRAMMAR_OUT[telegram_type_out.lower()]

            for dict_item in dict_wamas_in[telegram_type_in]:
                idx += 1
                line = ""

                for _key in grammar_out:
                    val = ""
                    ttype = grammar_out[_key]["type"]
                    length = grammar_out[_key]["length"]
                    dp = grammar_out[_key]["dp"]
                    dict_key = grammar_out[_key]["dict_key"]
                    df_val = grammar_out[_key]["df_val"]
                    df_func = grammar_out[_key]["df_func"]

                    if dict_key:
                        val = dict_item.get(dict_key, "").strip()
                    if not val and df_val:
                        val = df_val
                    if not val and df_func:
                        args = (idx,)
                        if df_func == "get_parent_id":
                            args = (
                                dict_parent_id,
                                DICT_CHILD_KEY,
                                _key,
                                telegram_type_out,
                            )
                        elif df_func in ["get_random_str_num", "get_random_int_num"]:
                            args = (length,)
                        val = globals()[df_func](*args)

                    # Ignore string of float/int/date/datetime type to move entire value
                    if (
                        not val
                        or _key in ["Telheader_TelSeq", "Telheader_AnlZeit"]
                        or df_func
                        or ttype not in ["float", "int", "date", "datetime"]
                    ):
                        val = set_value_to_string(val, ttype, length, dp)
                    line += val

                    lst_parent_key = DICT_PARENT_KEY.get(telegram_type_out, False)
                    if lst_parent_key and _key in lst_parent_key:
                        dict_parent_id[_key] = val
                if line:
                    res.append(line)

    return res


def wamas2wamas(infile, verbose=False):
    dict_wamas_in, lst_telegram_type_in = _process_wamas_in(infile)
    if verbose:
        _logger.debug(dict_wamas_in)
    wamas_out_lines = _process_wamas_out(dict_wamas_in, lst_telegram_type_in)
    wamas_out = "\n".join(wamas_out_lines)
    if verbose:
        pprint(wamas_out)
    return wamas_out


def usage(argv):
    _logger.debug("%s -i <inputfile>" % argv[0])


def main(argv):
    infile = ""
    verbose = False
    opts, args = getopt.getopt(argv[1:], "hi:v", ["ifile=", "verbose"])
    for opt, arg in opts:
        if opt == "-h":
            usage(argv)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            infile = file_open(arg).read()  # noqa: F405
        elif opt in ("-v", "--verbose"):
            verbose = True
            logging.basicConfig(level=logging.DEBUG)
    if not infile:
        usage(argv)
        sys.exit()
    wamas2wamas(infile, verbose)


if __name__ == "__main__":
    main(sys.argv)
