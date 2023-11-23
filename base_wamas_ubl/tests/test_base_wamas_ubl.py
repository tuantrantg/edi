# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import codecs
import filecmp
import os
import tempfile

from odoo.tests.common import TransactionCase
from odoo.tools import file_open, file_path


class TestBaseWamas(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_wamas_ubl = cls.env["base.wamas.ubl"]

    def _convert_wamas2ubl(self, path, path_to_compare):
        str_file = file_open(path, "r").read()

        res = self.base_wamas_ubl.parse_wamas2ubl(str_file)

        if res:
            tmpfile_path = tempfile.mkstemp(suffix=".xml")[1]

            open(tmpfile_path, "w").close()
            with open(tmpfile_path, "w") as f2:
                f2.write(res)

        # Compare 2 files
        self.assertTrue(filecmp.cmp(file_path(path_to_compare), tmpfile_path))

        if os.path.exists(tmpfile_path):
            os.remove(tmpfile_path)

    def test_convert_wamas2ubl_weakq_weapq(self):
        path = "base_wamas_ubl/tests/files/WAMAS2XML-SAMPLE_WEAKQ_WEAPQ.txt"
        path_to_compare = "base_wamas_ubl/tests/files/WAMAS2XML-SAMPLE_WEAKQ_WEAPQ-DESPATCH_ADVICE.xml"
        self._convert_wamas2ubl(path, path_to_compare)

    def test_convert_wamas2ubl_watekq_watepq(self):
        path = "base_wamas_ubl/tests/files/WAMAS2XML-SAMPLE_WATEKQ_WATEPQ.txt"
        path_to_compare = "base_wamas_ubl/tests/files/WAMAS2XML-SAMPLE_WATEKQ_WATEPQ-DESPATCH_ADVICE.xml"
        self._convert_wamas2ubl(path, path_to_compare)
