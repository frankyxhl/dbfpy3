import unittest
from io import BytesIO

from dbfpy3.memo import MemoFile


class FieldsTest(unittest.TestCase):

    def test_memo(self):
        stream = BytesIO()
        memo = MemoFile(stream, new=True)
        self.assertEqual(memo.write(b'test'), 1)
        data = stream.getvalue()
        self.assertEqual(len(data), 1024)
        self.assertEqual(data[:8], b'\x00\x00\x00\x02\x00\x00\x02\x00')
