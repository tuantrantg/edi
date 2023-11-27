#!/usr/bin/python3

import getopt
import logging
import re
import struct
import sys
from pprint import pprint

_logger = logging.getLogger("wamas2ubl")

# TODO: Find "clean" way to manage imports for both module & CLI contexts
try:
    from . import miniqweb
    from .utils import *
    from .wamas_grammar import auskq, watekq, watepq, weakq, weapq  # noqa: F401
except ImportError:
    import miniqweb
    from utils import *
    from wamas_grammar import auskq, watekq, watepq, weakq, weapq  # noqa: F401

##
# WAMAS FORMAT SPECS
##

telegram_header_grammar = {
    "Telheader_Quelle": 10,
    "Telheader_Ziel": 10,
    "Telheader_TelSeq": 6,
    "Telheader_AnlZeit": 14,
    "Satzart": 9,
}


class MappingDict(dict):
    """
    A dict that returns the key if there's no corresponding value
    """

    def __missing__(self, key):
        _logger.debug("No mapping found for key: %s", key)
        return key


MAPPING_WAMAS_TO_UBL = {
    # DespatchLine/DeliveredQuantity[unitCode]
    # https://docs.peppol.eu/poacc/upgrade-3/codelist/UNECERec20/
    "unitCode": MappingDict(
        {
            "BOT": "XBQ",  # plastic bottle
            "BOUT": "XBQ",  # plastic bottle
            "BOITE": "XBX",  # box
            "LITRE": "LTR",  # litre
            "PET": "XBO",  # glass bottle
            "TETRA": "X4B",  # tetra pack
            "": False,  # undefined,
        }
    )
}


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
    line = line.encode()
    if len(line) != expected_size:
        _logger.debug(
            "Line of length %d does not match expected length %d: %s",
            len(line),
            expected_size,
            line.decode(),
        )
        _logger.debug(repr(unpack(line)))

        if abs(len(line) - expected_size) == 1 and telegram_type in (
            "WATEKQ",
            "WATEPQ",
        ):
            _logger.debug("Length off by one only, fields not impacted, no fix needed.")

        elif telegram_type == "WATEPQ":
            ## line_WATEPQ_-_weirdly_encoded_01.wamas
            # - this case has a weird WATEPQ:IvTep_MId_Charge
            #   of incorrect size due to weirdly encoded chars inside:
            #   b'6423033A\xc3\xa9\xc2\xb0\xc2\xb0\xc3\xaf\xc2\xbf\xc2\xbd\xc3\xaf\xc2\xbf\xc2\xbd370063 '
            #   33 chars instead of expected 20 (when file is decoded as iso-8859-1)
            # - we clean it from non ascii chars and fill it with space to fix length
            #   and avoid impact on other fields
            to_fix = line.split(b" ")[0]
            to_keep_idx = len(to_fix) + 1
            line = (
                to_fix.decode().encode("ascii", "ignore").ljust(20, b" ")
                + line[to_keep_idx:]
            )

            if len(line) is expected_size:
                _logger.debug("Line corrected successfully.")
            else:
                _logger.debug(
                    "Line of length %d still does not match expected length %d: %s",
                    len(line),
                    expected_size,
                    line.decode(),
                )

    # actual parsing
    try:
        vals = tuple(s.decode() for s in unpack(line))
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


def wamas2dict(infile, verbose=False):
    header_len = sum(telegram_header_grammar.values())
    result = {}
    for line in infile.split("\n"):
        if not line:
            continue
        head = fw2dict(line[:header_len], telegram_header_grammar, "header")
        telegram_type, telegram_seq, dummy = re.split(r"(\d+)", head["Satzart"], 1)
        # ignore useless telegram types
        if telegram_type in ("AUSPQ", "TOURQ", "TAUSPQ"):
            continue
        if telegram_type not in ("AUSKQ", "WEAKQ", "WEAPQ", "WATEKQ", "WATEPQ"):
            raise Exception("Invalid telegram type: %s" % telegram_type)
        grammar = eval(telegram_type.lower()).grammar
        body = fw2dict(line[header_len:], grammar, telegram_type)
        val = result.setdefault(telegram_type, [])
        val.append(body)
    return result


def dict2ubl(template, data, verbose=False):
    t = miniqweb.QWebXml(template)
    # Convert dict to object to use dotted notation in template
    globals_dict = {
        "record": obj(data),
        "get_date": get_date,
        "get_time": get_time,
        "MAPPING": MAPPING_WAMAS_TO_UBL,
    }
    xml = t.render(globals_dict)
    return xml


##
# Data transformations
##


def _prepare_pickings(data):
    pickings = {}
    packages = {}

    for order in data["AUSKQ"]:
        order_id = order["IvAusk_AusId_AusNr"]
        if order_id not in pickings:
            order["lines"] = []
            pickings[order_id] = order
        else:
            _logger.debug(
                "Redundant AUSKQ (order) record found, ignoring: %s", order_id
            )

    for package in data["WATEKQ"]:
        package_id = package["IvTek_TeId"]
        if package_id not in packages:
            packages[package_id] = package
        else:
            _logger.debug(
                "Redundant WATEKQ (package) record found, ignoring: %s", package_id
            )

    for line in data["WATEPQ"]:
        order_id = line["IvAusp_UrAusId_AusNr"]
        if order_id not in pickings:
            _logger.debug(
                "Found WATEPQ (line) record for unknown AUSKQ (order), ignoring: %s",
                order_id,
            )
            continue
        pickings[order_id]["lines"].append(line)
        package_id = line["IvTep_TeId"]
        if package_id in packages:
            line["package"] = package
        else:
            _logger.debug(
                "Found WATEPQ (line) record with unknown WATEKQ (package), ignoring: %s",
                package_id,
            )

    return pickings


def wamas2ubl(infile, verbose=False):
    # 1) parse wamas file
    data = wamas2dict(infile, verbose)
    if verbose:
        pprint(data)

    # 2) analyze/transform wamas file content
    top_keys = list(data.keys())
    if top_keys == ["WEAKQ", "WEAPQ"]:
        template_type = "reception"
    elif top_keys == ["AUSKQ", "WATEKQ", "WATEPQ"]:
        template_type = "picking"
        pickings = _prepare_pickings(data)
        if verbose:
            _logger.debug("Number of pickings: %d", len(pickings))
            pprint(pickings)
    else:
        raise Exception(
            "Could not match input wamas file with a corresponding template type: %s"
            % top_keys
        )

    # 3) get template
    ubl_template = file_open(file_path(f"ubl_template/{template_type}.xml")).read()

    # 4) output
    if template_type == "reception":
        ubl = [dict2ubl(ubl_template, data, verbose)]
    elif template_type == "picking":
        ubl = []
        for picking in pickings.values():
            ubl.append(dict2ubl(ubl_template, picking, verbose))
    if verbose:
        _logger.debug("Number of UBL files generated: %d", len(ubl))
        for f in ubl:
            _logger.debug(f)
    return ubl


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
            infile = file_open(arg).read()
        elif opt in ("-v", "--verbose"):
            verbose = True
            logging.basicConfig(level=logging.DEBUG)
    if not infile:
        usage(argv)
        sys.exit()
    wamas2ubl(infile, verbose)


if __name__ == "__main__":
    main(sys.argv)
