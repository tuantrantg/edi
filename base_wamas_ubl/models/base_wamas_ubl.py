# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

from ..lib.wamas.ubl2wamas import ubl2wamas
from ..lib.wamas.wamas2ubl import dict2ubl, wamas2dict, wamas2ubl


class BaseWamasUbl(models.AbstractModel):
    _name = "base.wamas.ubl"
    _description = "Methods to convert WAMAS to UBL XML files and vice versa"

    @api.model
    def parse_wamas2dict(self, str_file):
        return wamas2dict(str_file)

    @api.model
    def parse_dict2ubl(self, template, data):
        return dict2ubl(template, data)

    @api.model
    def parse_wamas2ubl(self, str_file):
        return wamas2ubl(str_file)

    @api.model
    def parse_ubl2wamas(self, str_file, telegram_type):
        return ubl2wamas(str_file, telegram_type)
