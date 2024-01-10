# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import struct
from base64 import b64decode

from odoo import _, api, fields, models


class CheckWamasFileWizard(models.TransientModel):
    _name = "check.wamas.file.wizard"
    _description = "Check WAMAS File Wizard"

    wamas_file = fields.Binary(
        "WAMAS File",
        required=True,
    )
    wamas_filename = fields.Char("WAMAS Filename")
    output = fields.Text()

    @api.onchange("wamas_filename")
    def _onchange_wamas_filename(self):
        self.output = False

    def btn_check(self):
        self.ensure_one()
        wamas_file_decoded = b64decode(self.wamas_file).decode("iso-8859-1")

        bwu_obj = self.env["base.wamas.ubl"]
        try:
            data, lst_telegram_type, wamas_type = bwu_obj.get_wamas_type(
                wamas_file_decoded
            )

            self.output = (
                _(
                    """- WAMAS Type: %(wamas_type)s
- Telegram Type: %(telegram_type)s
- Data: %(data)s
            """
                )
                % dict(
                    wamas_type=wamas_type,
                    telegram_type=",".join(lst_telegram_type),
                    data=json.dumps(data, indent=4, sort_keys=True),
                )
            )
        except struct.error:
            self.output = _(
                """- Error: Length of line does not match expected length"""
            )
        except Exception as e:
            self.output = _("""- Error: %s""") % (e)

        return {
            "view_mode": "form",
            "res_model": "check.wamas.file.wizard",
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }
