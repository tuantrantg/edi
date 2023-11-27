import io
import unittest
from pprint import pprint

from wamas2ubl import file_open, file_path, wamas2dict


class TestWamas2ubl(unittest.TestCase):

    knownValuesLines = (
        (
            file_open(file_path("tests/line_WATEPQ_-_normal.wamas")).read(),
            file_open(file_path("tests/line_WATEPQ_-_normal.dict")).read(),
        ),
        (
            file_open(file_path("tests/line_WATEPQ_-_weirdly_encoded_01.wamas")).read(),
            file_open(file_path("tests/line_WATEPQ_-_weirdly_encoded_01.dict")).read(),
        ),
        (
            file_open(
                file_path("tests/line_WATEKQ_-_length_off_by_one_01.wamas")
            ).read(),
            file_open(
                file_path("tests/line_WATEKQ_-_length_off_by_one_01.dict")
            ).read(),
        ),
    )

    def testWamas2dict(self):
        for str_input, expected_output in self.knownValuesLines:
            # pprint(wamas2dict(str_input), open('tmp.dict', 'w'))
            output_prettified = io.StringIO()
            pprint(wamas2dict(str_input), output_prettified)
            output_prettified = output_prettified.getvalue()
            self.assertEqual(output_prettified, expected_output)


if __name__ == "__main__":
    unittest.main()
