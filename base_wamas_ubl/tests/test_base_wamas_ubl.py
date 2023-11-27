# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from difflib import SequenceMatcher

from odoo.tests.common import TransactionCase
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestBaseWamas(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_wamas_ubl = cls.env["base.wamas.ubl"]
        cls.assertXmlTreeEqual = AccountTestInvoicingCommon.assertXmlTreeEqual
        cls.get_xml_tree_from_string = (
            AccountTestInvoicingCommon.get_xml_tree_from_string
        )
        cls._turn_node_as_dict_hierarchy = (
            AccountTestInvoicingCommon._turn_node_as_dict_hierarchy
        )

    def _is_string_similar(self, s1, s2, threshold=0.9):
        return SequenceMatcher(a=s1, b=s2).ratio() > threshold

    def _convert_wamas2ubl(self, input_file, expected_output_files):
        input = file_open(input_file, "r").read()
        outputs = self.base_wamas_ubl.parse_wamas2ubl(input)

        for i, output in enumerate(outputs):
            output_tree = self.get_xml_tree_from_string(output)
            expected_output = file_open(expected_output_files[i], "r").read()
            expected_output_tree = self.get_xml_tree_from_string(expected_output)
            self.assertXmlTreeEqual(output_tree, expected_output_tree)

    def _convert_ubl2wamas(self, input_file, expected_output_file, telegram_type):
        input = file_open(input_file, "r").read()
        output = self.base_wamas_ubl.parse_ubl2wamas(input, telegram_type)
        expected_output = file_open(expected_output_file, "r").read()
        self.assertTrue(self._is_string_similar(output, expected_output))

    # picking
    def test_convert_wamas2ubl_auskq_watekq_watepq(self):
        input_file = (
            "base_wamas_ubl/tests/files/WAMAS2UBL-SAMPLE_AUSKQ_WATEKQ_WATEPQ.wamas"
        )
        expected_output = (
            "base_wamas_ubl/tests/files/WAMAS2UBL-"
            "SAMPLE_AUSKQ_WATEKQ_WATEPQ-DESPATCH_ADVICE.xml"
        )
        self._convert_wamas2ubl(input_file, [expected_output])

    def test_convert_ubl2wamas_ausk_ausp(self):
        input_file = (
            "base_wamas_ubl/tests/files/UBL2WAMAS-SAMPLE_AUSK_AUSP-DESPATCH_ADVICE.xml"
        )
        expected_output = "base_wamas_ubl/tests/files/UBL2WAMAS-SAMPLE_AUSK_AUSP.wamas"
        self._convert_ubl2wamas(input_file, expected_output, "AUSK,AUSP")

    # reception
    def test_convert_wamas2ubl_weakq_weapq(self):
        input_file = "base_wamas_ubl/tests/files/WAMAS2UBL-SAMPLE_WEAKQ_WEAPQ.wamas"
        expected_output = (
            "base_wamas_ubl/tests/files/WAMAS2UBL-"
            "SAMPLE_WEAKQ_WEAPQ-DESPATCH_ADVICE.xml"
        )
        self._convert_wamas2ubl(input_file, [expected_output])

    def test_convert_ubl2wamas_weak_weap(self):
        input_file = (
            "base_wamas_ubl/tests/files/UBL2WAMAS-SAMPLE_WEAK_WEAP-DESPATCH_ADVICE.xml"
        )
        expected_output = "base_wamas_ubl/tests/files/UBL2WAMAS-SAMPLE_WEAK_WEAP.wamas"
        self._convert_ubl2wamas(input_file, expected_output, "WEAK,WEAP")
