# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import codecs
import filecmp
import os
import tempfile

from odoo.tests.common import TransactionCase
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tools import file_open, file_path


class TestBaseWamas(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_wamas_ubl = cls.env["base.wamas.ubl"]
        cls.assertXmlTreeEqual = AccountTestInvoicingCommon.assertXmlTreeEqual
        cls.get_xml_tree_from_string = AccountTestInvoicingCommon.get_xml_tree_from_string
        cls._turn_node_as_dict_hierarchy = AccountTestInvoicingCommon._turn_node_as_dict_hierarchy

    def _convert_wamas2ubl(self, input_file, expected_output_files):
        input = file_open(input_file, "r").read()
        outputs = self.base_wamas_ubl.parse_wamas2ubl(input)

        for i, output in enumerate(outputs):
            output_tree = self.get_xml_tree_from_string(output)
            from lxml.etree import tostring
            print(output)
            expected_output = file_open(expected_output_files[i], "r").read()
            expected_output_tree = self.get_xml_tree_from_string(expected_output)
            self.assertXmlTreeEqual(output_tree, expected_output_tree)

    # picking
    def test_convert_wamas2ubl_auskq_watekq_watepq(self):
        input_file = "base_wamas_ubl/tests/files/WAMAS2UBL-SAMPLE_AUSKQ_WATEKQ_WATEPQ.txt"
        expected_output = "base_wamas_ubl/tests/files/WAMAS2UBL-SAMPLE_AUSKQ_WATEKQ_WATEPQ-DESPATCH_ADVICE.xml"
        self._convert_wamas2ubl(input_file, [expected_output])

    # reception
    def test_convert_wamas2ubl_weakq_weapq(self):
        input_file = "base_wamas_ubl/tests/files/WAMAS2UBL-SAMPLE_WEAKQ_WEAPQ.txt"
        expected_output = "base_wamas_ubl/tests/files/WAMAS2UBL-SAMPLE_WEAKQ_WEAPQ-DESPATCH_ADVICE.xml"
        self._convert_wamas2ubl(input_file, [expected_output])
