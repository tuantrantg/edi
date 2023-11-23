# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

from ..lib.wamas.wamas2ubl import wamas2dict, dict2ubl, wamas2ubl


class BaseWamasUbl(models.AbstractModel):
    _name = "base.wamas.ubl"
    _description = "Common methods to generate and parse between WAMAS and UBL XML files"

    @api.model
    def parse_wamas2dict(self, str_file):
        return wamas2dict(str_file)

    @api.model
    def parse_dict2ubl(self, template, data):
        return dict2ubl(template, data)

    @api.model
    def parse_wamas2ubl(self, str_file):
        return wamas2ubl(str_file)
