# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from base64 import b64decode, b64encode

from odoo import _, api, fields, models


class SimulateWamasFileWizard(models.TransientModel):
    _name = "simulate.wamas.file.wizard"
    _description = "Simulate WAMAS File Wizard"

    wamas_file = fields.Binary(
        "WAMAS File",
        required=True,
    )
    wamas_filename = fields.Char("WAMAS Filename")
    output_wamas_file = fields.Binary("Output WAMAS File")
    output_wamas_filename = fields.Char("Output WAMAS Filename")
    output = fields.Text()

    @api.onchange("wamas_filename")
    def _onchange_wamas_filename(self):
        self.output_wamas_file = False
        self.output_wamas_filename = False
        self.output = False

    def btn_simulate(self):
        self.ensure_one()
        wamas_file_decoded = b64decode(self.wamas_file).decode("iso-8859-1")

        try:
            bwu_obj = self.env["base.wamas.ubl"]
            output_wamas = bwu_obj.wamas2wamas(wamas_file_decoded).encode("iso-8859-1")

            self.output_wamas_file = b64encode(output_wamas)
            self.output_wamas_filename = "OUTPUT_" + self.wamas_filename
        except Exception as e:
            self.output = _("""- Error: %s""") % (e)

        return {
            "view_mode": "form",
            "res_model": "simulate.wamas.file.wizard",
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }
