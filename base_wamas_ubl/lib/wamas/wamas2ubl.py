#!/usr/bin/python3

import codecs
import getopt
from pprint import pprint
import re
import struct
import sys

import miniqweb

from datetime import datetime
from dateutil.parser import parse

from wamas_grammar import weakq, weapq, watekq, watepq  # noqa: F401

telegram_header_grammar = {
    "Telheader_Quelle": 10,
    "Telheader_Ziel": 10,
    "Telheader_TelSeq": 6,
    "Telheader_AnlZeit": 14,
    "Satzart": 9,
}


def fw2dict(line, grammar):
    """
    Convert a fixed width to a dict

    definition: { "k1": 3, "k2": 5 }
    line: abcdefgh
    """
    fieldwidths = grammar.values()
    fmtstring = ' '.join('{}{}'.format(abs(fw), 's') for fw in fieldwidths)
    unpack = struct.Struct(fmtstring).unpack_from
    try:
        vals = tuple(s.decode().rstrip() for s in unpack(line.encode()))
    except struct.error as e:
        print(line)
        raise e
    res = dict(zip(grammar.keys(), vals))
    return res


def wamas2dict(infile):
    header_len = sum(telegram_header_grammar.values())
    result = {}
    for line in infile.split("\n"):
        if not line:
            continue
        head = fw2dict(line[:header_len], telegram_header_grammar)
        telegram_type, telegram_seq, dummy = re.split(r"(\d+)", head["Satzart"], 1)
        if telegram_type not in ("WEAKQ", "WEAPQ", "WATEKQ", "WATEPQ"):
            raise Exception("Invalid telegram type: %s" % telegram_type)
        grammar = eval(telegram_type.lower()).grammar
        body = fw2dict(line[header_len:], grammar)
        # FIXME: check how to structure result
        val = result.setdefault(telegram_type, [])
        val.append(body)
    return result


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
        val = val.strftime('%Y-%m-%d')
    return val


def get_time(val):
    val = parse(val)
    if isinstance(val, datetime):
        val = val.strftime('%H:%M:%S')
    return val


def dict2ubl(template, data):
    t = miniqweb.QWebXml(template)
    # Convert dict to object to use dotted notation in template
    globals_dict = {
        'record': obj(data),
        'get_date': get_date,
        'get_time': get_time,
    }
    xml = t.render(globals_dict)
    return xml


def wamas2ubl(infile):
    data = wamas2dict(infile)
    pprint(data)
    top_keys = list(data.keys())
    if top_keys == ["WEAKQ", "WEAPQ"]:
        template_type = "reception"
    elif top_keys == ["WATEKQ", "WATEPQ"]:
        template_type = "picking"
    else:
        raise Exception(
            "Could not match input wamas file with a corresponding template type: %s"
            % top_keys)
    ubl_template = open(f"ubl_template/{template_type}.xml").read()
    ubl = dict2ubl(ubl_template, data)
    print(ubl)


def usage(argv):
    print("%s -i <inputfile>" % argv[0])


def main(argv):
    infile = ""
    opts, args = getopt.getopt(argv[1:], "hi:", ["ifile="])
    for opt, arg in opts:
        if opt == "-h":
            usage(argv)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            infile = codecs.open(arg, 'r', 'iso-8859-15').read()
    if not infile:
        usage(argv)
        sys.exit()
    wamas2ubl(infile)


if __name__ == "__main__":
    main(sys.argv)
