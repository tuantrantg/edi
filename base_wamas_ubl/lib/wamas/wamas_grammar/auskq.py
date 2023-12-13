from collections import OrderedDict

grammar = {
    "IvAusk_AusId_Mand": 3,
    "IvAusk_AusId_AusNr": 20,
    "IvAusk_AusId_HostAusKz": 5,
    "IvAusk_ExtRef": 20,
    "IvAusk_KST_Mand": 3,
    "IvAusk_KST_KuNr": 13,
    "IvAusk_LiefTerm": 14,
    "IvAusk_StartZeit": 14,
    "IvAusk_FertZeit": 14,
    "IvAusk_RahmenTourId_TourNr": 20,
    "IvAusk_RahmenTourId_HostTourKz": 5,
    "IvAusk_Info2Host": 77,
}

grammar_convert = OrderedDict(
    {
        "Telheader_Quelle": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": "WAMAS",
            "df_func": False,
        },
        "Telheader_Ziel": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": "SYSLOG",
            "df_func": False,
        },
        "Telheader_TelSeq": {
            "type": "int",
            "length": 6,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_sequence_number",
        },
        "Telheader_AnlZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_current_datetime",
        },
        "Satzart": {
            "type": "str",
            "length": 9,
            "dp": False,
            "dict_key": False,
            "df_val": "AUSKQ0052",
            "df_func": False,
        },
        "IvAusk_AusId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": "RxAusk_AusId_Mand",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_AusId_AusNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxAusk_AusId_AusNr",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_AusId_HostAusKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": "RxAusk_AusId_HostAusKz",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_ExtRef": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxAusk_ExtRef",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_KST_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": "RxAusk_KST_Mand",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_KST_KuNr": {
            "type": "str",
            "length": 13,
            "dp": False,
            "dict_key": "RxAusk_KST_KuNr",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_LiefTerm": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": "RxAusk_LiefTerm",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_StartZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_FertZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_RahmenTourId_TourNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxAusk_AusId_Mand",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_RahmenTourId_HostTourKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": "RxAusk_RahmenTourId_HostTourKz",
            "df_val": False,
            "df_func": False,
        },
        "IvAusk_Info2Host": {
            "type": "str",
            "length": 77,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
    }
)
