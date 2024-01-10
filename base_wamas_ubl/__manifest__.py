# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base WAMAS UBL",
    "summary": """Base module to aggregate WAMAS - UBL features.""",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Hidden",
    "website": "https://github.com/OCA/edi",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "depends": ["base_edi", "base_ubl"],
    "external_dependencies": {
        "python": ["xmltodict", "dotty-dict", "pytz"],
    },
    "data": [
        "security/ir.model.access.csv",
        "wizard/check_wamas_file_wizard.xml",
        "wizard/simulate_wamas_file_wizard.xml",
        "views/wamas_menu.xml",
    ],
}
