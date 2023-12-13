from collections import OrderedDict

grammar = {
    "IvKretk_KretId_Mand": 3,
    "IvKretk_KretId_KretNr": 20,
    "IvKretk_KretId_HostKretKz": 5,
    "IvKretk_ExtRef": 20,
    "IvKretk_KST_Mand": 3,
    "IvKretk_KST_KuNr": 13,
    "IvKretk_LiefTerm": 14,
    "IvKretk_StartZeit": 14,
    "IvKretk_FertZeit": 14,
    "IvKretk_Info2Host": 77,
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
            "df_val": "KRETKQ050",
            "df_func": False,
        },
        "IvKretk_KretId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": "RxKretk_KretId_Mand",
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_KretId_KretNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxKretk_KretId_KretNr",
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_KretId_HostKretKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": "RxKretk_KretId_HostKretKz",
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_ExtRef": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxKretk_ExtRef",
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_KST_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": "RxKretk_KST_Mand",
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_KST_KuNr": {
            "type": "str",
            "length": 13,
            "dp": False,
            "dict_key": "RxKretk_KST_KuNr",
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_LiefTerm": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": "RxKretk_LiefTerm",
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_StartZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_FertZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvKretk_Info2Host": {
            "type": "str",
            "length": 77,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
    }
)
