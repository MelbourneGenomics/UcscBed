import ucsc_bed
import unittest


class TestAll(unittest.TestCase):
    def test_compare_sources(self):
        sql = ucsc_bed.generate_bed('hg38', 'sql')
        ftp = ucsc_bed.generate_bed('hg38', 'ftp', email='test@test.com')
        self.assertEqual(sql, ftp)
