from collections import OrderedDict

grammar = {
    "IvWevk_WevId_Mand": 3,
    "IvWevk_WevId_WevNr": 20,
    "HostWeaKz": 5,
    "IvWevk_LiefTerm": 14,
    "IvWevk_LkwFahrer": 40,
    "IvWevk_LkwKz": 10,
    "IvWevk_EinfahrtZeit": 14,
    "IvWevk_StartZeit": 14,
    "IvWevk_FertZeit": 14,
    "IvWevk_AnmZeit": 14,
    "IvWevk_Info2Host": 77,
    "LST_Mand": 3,
    "LST_LiefNr": 13,
}

grammar_convert = OrderedDict(
    {
        "Telheader_Quelle": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_source_q",
        },
        "Telheader_Ziel": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_destination_q",
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
            "df_val": "WEAKQ0051",
            "df_func": False,
        },
        "IvWevk_WevId_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": "RxWeak_WeaId_Mand",
            "df_val": False,
            "df_func": False,
        },
        "IvWevk_WevId_WevNr": {
            "type": "str",
            "length": 20,
            "dp": False,
            "dict_key": "RxWeak_WeaId_WeaNr",
            "df_val": False,
            "df_func": False,
        },
        "HostWeaKz": {
            "type": "str",
            "length": 5,
            "dp": False,
            "dict_key": "RxWeak_WeaId_HostWeaKz",
            "df_val": False,
            "df_func": False,
        },
        "IvWevk_LiefTerm": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": "19700101010000",
            "df_func": False,
        },
        "IvWevk_LkwFahrer": {
            "type": "str",
            "length": 40,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvWevk_LkwKz": {
            "type": "str",
            "length": 10,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvWevk_EinfahrtZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": "19700101010000",
            "df_func": False,
        },
        "IvWevk_StartZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvWevk_FertZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": "get_current_datetime",
        },
        "IvWevk_AnmZeit": {
            "type": "datetime",
            "length": 14,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "IvWevk_Info2Host": {
            "type": "str",
            "length": 77,
            "dp": False,
            "dict_key": False,
            "df_val": False,
            "df_func": False,
        },
        "LST_Mand": {
            "type": "str",
            "length": 3,
            "dp": False,
            "dict_key": "RxWeak_LST_Mand",
            "df_val": False,
            "df_func": False,
        },
        "LST_LiefNr": {
            "type": "str",
            "length": 13,
            "dp": False,
            "dict_key": "RxWeak_LST_LiefNr",
            "df_val": False,
            "df_func": False,
        },
    }
)
