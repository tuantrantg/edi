# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from io import BytesIO

from lxml import etree

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import file_open, float_is_zero, float_round

from ..lib.wamas.wamas2ubl import wamas2dict, dict2ubl, wamas2ubl

logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
    from PyPDF2.generic import NameObject
except ImportError:
    logger.debug("Cannot import PyPDF2")


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
