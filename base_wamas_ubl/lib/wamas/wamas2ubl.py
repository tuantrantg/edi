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
    from . import miniqweb  # noqa: F403
    from .utils import *  # noqa: F403
    from .wamas_grammar import (  # noqa: F401
        auskq,
        kretkq,
        kretpq,
        watekq,
        watepq,
        weakq,
        weapq,
    )
except ImportError:
    import miniqweb  # noqa: F403
    from utils import *  # noqa: F403
    from wamas_grammar import (  # noqa: F401
        auskq,
        kretkq,
        kretpq,
        watekq,
        watepq,
        weakq,
        weapq,
    )

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


DICT_WAMAS_GRAMMAR = {
    "auskq": auskq.grammar,
    "kretkq": kretkq.grammar,
    "kretpq": kretpq.grammar,
    "watekq": watekq.grammar,
    "watepq": watepq.grammar,
    "weakq": weakq.grammar,
    "weapq": weapq.grammar,
}


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


DICT_TUPLE_KEY_RECEPTION = {
    ("WEAKQ", "WEAPQ"): (
        "ubl_template/reception_wea.xml",
        ("WEAKQ", "IvWevk_WevId_WevNr"),
        ("WEAPQ", "IvWevp_WevId_WevNr"),
    ),
    ("KRETKQ", "KRETPQ"): (
        "ubl_template/reception_kret.xml",
        ("KRETKQ", "IvKretk_KretId_KretNr"),
        ("KRETPQ", "IvKretp_KretId_KretNr"),
    ),
}


DICT_TUPLE_KEY_PICKING = {
    ("AUSKQ", "WATEKQ", "WATEPQ"): "ubl_template/picking.xml",
}


DICT_FLOAT_FIELD = {
    "IvWevp_LiefMngs_Mng": (12, 3),
    "IvKretp_AnmMngs_Mng": (12, 3),
    "Mngs_Mng": (12, 3),
    "IvTek_GesGew": (12, 3),
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
    for line in infile.splitlines():
        if not line:
            continue
        head = fw2dict(line[:header_len], telegram_header_grammar, "header")
        telegram_type, telegram_seq, dummy = re.split(r"(\d+)", head["Satzart"], 1)
        # ignore useless telegram types
        if telegram_type in ("AUSPQ", "TOURQ", "TAUSPQ"):
            continue
        if telegram_type not in (
            "AUSKQ",
            "WEAKQ",
            "WEAPQ",
            "WATEKQ",
            "WATEPQ",
            "KRETKQ",
            "KRETPQ",
        ):
            raise Exception("Invalid telegram type: %s" % telegram_type)
        grammar = DICT_WAMAS_GRAMMAR[telegram_type.lower()]
        body = fw2dict(line[header_len:], grammar, telegram_type)
        val = result.setdefault(telegram_type, [])
        val.append(body)
    return result


def dict2ubl(template, data, verbose=False, extra_data=False):
    t = miniqweb.QWebXml(template)
    # Convert dict to object to use dotted notation in template
    globals_dict = {
        "record": obj(data),  # noqa: F405
        "get_date": get_date,  # noqa: F405
        "get_time": get_time,  # noqa: F405
        "get_current_date": get_current_date,  # noqa: F405
        "MAPPING": MAPPING_WAMAS_TO_UBL,
        "extra_data": extra_data,
    }
    xml = t.render(globals_dict)
    return xml


##
# Data transformations
##


def _get_float(val, length=12, decimal_place=3):
    res = val.strip()

    try:
        if len(res) >= length:
            str_whole_number = res[: length - decimal_place]
            str_decimal_portion = res[decimal_place * -1 :]

            res = str_whole_number + "." + str_decimal_portion

            res = float(res.strip())
    except TypeError:
        _logger.debug("Cannot convert value '%s' to float type", val)

    return res


def _convert_float_field(data):
    for _field in DICT_FLOAT_FIELD:
        val_field = data.get(_field, False)
        if val_field:
            data[_field] = _get_float(
                val_field, DICT_FLOAT_FIELD[_field][0], DICT_FLOAT_FIELD[_field][1]
            )


def _prepare_receptions(data, order_name, order_key, line_name, line_key):
    orders = {}

    for order in data[order_name]:
        order_id = order[order_key]
        _convert_float_field(order)
        if order_id not in orders:
            order["lines"] = []
            orders[order_id] = order
        else:
            _logger.debug(
                "Redundant %s (order) record found, ignoring: %s", order_name, order_id
            )

    for line in data[line_name]:
        order_id = line[line_key]
        _convert_float_field(line)
        if order_id not in orders:
            _logger.debug(
                "Found %s (line) record for unknown %s (order), ignoring: %s",
                line_name,
                order_name,
                order_id,
            )
            continue
        orders[order_id]["lines"].append(line)

    return orders


def _prepare_pickings(data):
    pickings = {}
    packages = {}

    for order in data["AUSKQ"]:
        order_id = order["IvAusk_AusId_AusNr"]
        _convert_float_field(order)
        if order_id not in pickings:
            order["lines"] = []
            order["packages"] = set()
            pickings[order_id] = order
        else:
            _logger.debug(
                "Redundant AUSKQ (order) record found, ignoring: %s", order_id
            )

    for package in data["WATEKQ"]:
        package_id = package["IvTek_TeId"]
        _convert_float_field(package)
        if package_id not in packages:
            packages[package_id] = package
        else:
            _logger.debug(
                "Redundant WATEKQ (package) record found, ignoring: %s", package_id
            )

    for line in data["WATEPQ"]:
        order_id = line["IvAusp_UrAusId_AusNr"]
        _convert_float_field(line)
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
            pickings[order_id]["packages"].add(package_id)
        else:
            _logger.debug(
                "Found WATEPQ (line) record with unknown WATEKQ (package), ignoring: %s",
                package_id,
            )

    return pickings


def wamas2ubl(
    infile,
    verbose=False,
    dict_mapping_reception=False,
    dict_mapping_picking=False,
    extra_data=False,
):
    if extra_data is False:
        extra_data = {"DeliveryCustomerParty": False, "DespatchSupplierParty": False}

    if not dict_mapping_reception:
        dict_mapping_reception = DICT_TUPLE_KEY_RECEPTION

    if not dict_mapping_picking:
        dict_mapping_picking = DICT_TUPLE_KEY_PICKING

    # 1) parse wamas file
    data = wamas2dict(infile, verbose)
    if verbose:
        pprint(data)

    # 2) analyze/transform wamas file content
    top_keys = list(data.keys())
    top_keys.sort()
    top_keys = tuple(top_keys)
    tmpl_path = False
    if top_keys in dict_mapping_reception.keys():
        template_type = "reception"
        tmpl_path = dict_mapping_reception[top_keys][0]
        order_name = dict_mapping_reception[top_keys][1][0]
        order_key = dict_mapping_reception[top_keys][1][1]
        line_name = dict_mapping_reception[top_keys][2][0]
        line_key = dict_mapping_reception[top_keys][2][1]
        receptions = _prepare_receptions(
            data, order_name, order_key, line_name, line_key
        )
    elif top_keys in dict_mapping_picking.keys():
        template_type = "picking"
        tmpl_path = dict_mapping_picking[top_keys]
        pickings = _prepare_pickings(data)
        if verbose:
            _logger.debug("Number of pickings: %d", len(pickings))
            for order_id, picking in pickings.items():
                _logger.debug("Order ID: %s", order_id)
                _logger.debug(
                    "Number of packages: %s", len(pickings[order_id]["packages"])
                )
                pprint(picking)
    else:
        raise Exception(
            "Could not match input wamas file with a corresponding template type: %s"
            % str(top_keys)
        )

    # 3) get template
    tmpl_file = file_open(file_path(tmpl_path))  # noqa: F405
    ubl_template = tmpl_file.read()
    tmpl_file.close()

    # 4) output
    if template_type == "reception":
        ubl = []
        for reception in receptions.values():
            ubl.append(dict2ubl(ubl_template, reception, verbose, extra_data))
    elif template_type == "picking":
        ubl = []
        for picking in pickings.values():
            ubl.append(dict2ubl(ubl_template, picking, verbose, extra_data))
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
            infile = file_open(arg).read()  # noqa: F405
        elif opt in ("-v", "--verbose"):
            verbose = True
            logging.basicConfig(level=logging.DEBUG)
    if not infile:
        usage(argv)
        sys.exit()
    wamas2ubl(infile, verbose)


if __name__ == "__main__":
    main(sys.argv)
